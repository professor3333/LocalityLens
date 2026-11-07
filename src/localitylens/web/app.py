"""The local review screen: a queue and a record page over the review store (FastAPI + Jinja2).

* **Local only.** :func:`serve` refuses any host but loopback; there are no accounts, so a
  shared deployment needs authenticated sessions first. The one exception is
  the container image (``LOCALITYLENS_CONTAINER=1``), which must bind ``0.0.0.0`` inside its
  own network namespace; Docker Compose publishes that port on the host's 127.0.0.1 only.
* **Readiness:** ``/readyz`` (and ``/api/version``) report every pinned version and answer 503
  until the store exists and the release manifest matches the code
  (:mod:`localitylens.web.readiness`).
* **No model calls and no geometry here.** Records are imported and processed by
  ``localitylens review import``. Decisions go through :meth:`ReviewStore.decide`, which checks
  the transition, recomputes an edited proposal with the same deterministic code, refuses an
  approval without a full region, and stores an identical retry only once.
* **Label text is untrusted.** Templates autoescape everything; no route renders raw HTML from
  data.
* **A JSON API** under ``/api`` (:mod:`localitylens.web.api`) serves the same store: batch
  status, streamed progress, cancel/resume, records, decisions and export.
* **Export** writes the approved Darwin Core CSV, its GeoJSON and the unresolved report with
  the same functions as ``localitylens review export``, to fixed paths, and serves only those
  three files.
* **Forms work without JavaScript.** With HTMX a decision reports its error in place; without
  it the page is re-rendered with the error, and a success redirects to the record.
"""

from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Final
from urllib.parse import urlsplit

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from localitylens.domain.status import RecordStatus
from localitylens.export.darwin_core import export_approved, export_unresolved
from localitylens.export.geojson import MEDIA_TYPE as GEOJSON_MEDIA_TYPE
from localitylens.export.geojson import export_geojson
from localitylens.geo.extents import ExtentStore
from localitylens.review.store import Action, ReviewError, ReviewStore
from localitylens.web.api import build_router
from localitylens.web.readiness import report as readiness_report
from localitylens.web.views import queue_view, record_view

HERE: Final = Path(__file__).parent
REVIEWER_ENV: Final = "LOCALITYLENS_REVIEWER"
LOOPBACK: Final = frozenset({"127.0.0.1", "localhost", "::1"})
CONTAINER_ENV: Final = "LOCALITYLENS_CONTAINER"
APPROVABLE: Final = frozenset({RecordStatus.READY_FOR_REVIEW, RecordStatus.NEEDS_INFORMATION})


@dataclass(frozen=True, slots=True)
class ReviewConfig:
    db: Path
    extents: ExtentStore | None = None  # supplies a newly chosen feature's reviewed extent
    reviewer: str | None = None  # from LOCALITYLENS_REVIEWER; asked on the form when unset
    export_out: Path = Path("data/review/export/occurrences.csv")
    geojson_out: Path | None = None  # default: export_out with the suffix .geojson
    unresolved_out: Path = Path("data/review/export/unresolved.csv")
    release: Path = Path("release/manifest.json")
    index: Path = Path("data/derived/gazetteer.sqlite")  # for imports (gazetteer snapshot)
    extents_problem: str | None = None  # an extent store that failed its check (not ready)
    replay: Replay | None = None  # set only when freezing the screen into the static replay


@dataclass(frozen=True, slots=True)
class Replay:
    """What the static replay banner says: which run is shown, and that nothing runs live."""

    system: str  # e.g. "hybrid-1: rules-6, then llm-x2g2-qwen3.5-4b-q4km where rules find nothing"
    records: str  # which records, and where they come from
    built: str  # commit and date of the run that produced the pages
    attribution: str  # data citation (CC BY 4.0 needs it on every page)


def config_from_env(
    db: Path,
    extents: ExtentStore | None = None,
    export_out: Path | None = None,
    unresolved_out: Path | None = None,
    geojson_out: Path | None = None,
) -> ReviewConfig:
    reviewer = os.environ.get(REVIEWER_ENV, "").strip() or None
    config = ReviewConfig(db=db, extents=extents, reviewer=reviewer)
    if export_out is not None:
        config = dataclasses.replace(config, export_out=export_out)
    if unresolved_out is not None:
        config = dataclasses.replace(config, unresolved_out=unresolved_out)
    if geojson_out is not None:
        config = dataclasses.replace(config, geojson_out=geojson_out)
    return config


def _same_origin(request: Request) -> bool:
    """A browser form post from another site carries its own Origin: refuse it."""
    origin = request.headers.get("origin")
    if origin is None or origin == "null":
        return origin is None
    return urlsplit(origin).netloc == request.headers.get("host", "")


def _number(text: str | None, what: str) -> float | None:
    if text is None or not text.strip():
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise ReviewError(f"{what} must be a number") from exc


def create_app(config: ReviewConfig) -> FastAPI:
    app = FastAPI(title="LocalityLens review", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.globals["replay"] = config.replay

    def store() -> ReviewStore:
        return ReviewStore(config.db)  # one connection per request: SQLite stays in one thread

    def render_record(
        request: Request,
        record_id: str,
        *,
        error: str | None = None,
        form: dict[str, str] | None = None,
        status_code: int = 200,
    ) -> Response:
        with store() as s:
            try:
                view = record_view(s, record_id)
            except ReviewError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
        status = RecordStatus(view.record["status"])
        return templates.TemplateResponse(
            request,
            "record.html",
            {
                "v": view,
                "error": error,
                "form": form or {},
                "reviewer": config.reviewer,
                "can_approve": status in APPROVABLE and bool(view.candidates),
            },
            status_code=status_code,
        )

    def render_queue(
        request: Request, status: str | None, exported: dict[str, object] | None = None
    ) -> Response:
        try:
            wanted = RecordStatus(status) if status else None
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"unknown status {status!r}") from exc
        with store() as s:
            view = queue_view(s, wanted)
        files = {name: path.is_file() for name, path in exports.items()}
        return templates.TemplateResponse(
            request, "queue.html", {"q": view, "exported": exported, "files": files}
        )

    geojson_out = config.geojson_out or config.export_out.with_suffix(".geojson")
    exports = {
        "occurrences.csv": config.export_out,
        "occurrences.geojson": geojson_out,
        "unresolved.csv": config.unresolved_out,
    }
    app.include_router(
        build_router(
            store,
            reviewer=config.reviewer,
            extent_lookup=config.extents.get if config.extents else None,
            exports=exports,
            same_origin=_same_origin,
            index=config.index,
            release=config.release,
        )
    )

    @app.get("/readyz")
    def readyz() -> JSONResponse:
        ready, payload = readiness_report(config.db, config.release, _extra(config))
        return JSONResponse(payload, status_code=200 if ready else 503)

    @app.get("/api/version")
    def version() -> JSONResponse:
        return JSONResponse(readiness_report(config.db, config.release, _extra(config))[1])

    @app.get("/", response_class=HTMLResponse)
    def queue(request: Request, status: str | None = None) -> Response:
        return render_queue(request, status)

    @app.post("/export", response_class=HTMLResponse)
    def export(request: Request) -> Response:
        """Approved records as Darwin Core CSV, everything unresolved in its own report."""
        if not _same_origin(request):
            raise HTTPException(status_code=403, detail="cross-site form posts are refused")
        with store() as s:
            approved = export_approved(s, config.export_out)
            export_geojson(s, geojson_out)
            unresolved = export_unresolved(s, config.unresolved_out)
        result = {
            "approved": approved,
            "unresolved": unresolved,
            "out": str(config.export_out),
            "geojson_out": str(geojson_out),
            "unresolved_out": str(config.unresolved_out),
        }
        return render_queue(request, None, exported=result)

    @app.get("/export/{name}")
    def download(name: str) -> Response:
        path = exports.get(name)  # only the export files, never an arbitrary path
        if path is None or not path.is_file():
            raise HTTPException(status_code=404, detail="no such export (export first)")
        media = GEOJSON_MEDIA_TYPE if name.endswith(".geojson") else "text/csv"
        return FileResponse(path, media_type=media, filename=name)

    @app.get("/records/{record_id}", response_class=HTMLResponse)
    def record(request: Request, record_id: str) -> Response:
        return render_record(request, record_id)

    @app.post("/records/{record_id}/decision")
    def decide(
        request: Request,
        record_id: str,
        action: Annotated[str, Form()],
        rationale: Annotated[str, Form()] = "",
        reviewer: Annotated[str, Form()] = "",
        feature_id: Annotated[str, Form()] = "",
        extent_m: Annotated[str, Form()] = "",
        extent_note: Annotated[str, Form()] = "",
    ) -> Response:
        if not _same_origin(request):
            raise HTTPException(status_code=403, detail="cross-site form posts are refused")
        form = {
            "action": action,
            "rationale": rationale,
            "reviewer": reviewer,
            "feature_id": feature_id,
            "extent_m": extent_m,
            "extent_note": extent_note,
        }
        htmx = request.headers.get("hx-request") == "true"
        who = config.reviewer or reviewer
        try:
            chosen = Action(action)
            fid = _number(feature_id, "the feature")
            with store() as s:
                s.record(record_id)  # raises for an unknown record
                proposed = s.latest_pipeline_proposal(record_id).proposal
                proposed_fid = proposed.feature_id if proposed else None
                s.decide(
                    record_id,
                    chosen,
                    reviewer=who,
                    rationale=rationale,
                    # the form always sends the selected candidate; only a change is an edit
                    feature_id=int(fid) if fid is not None and int(fid) != proposed_fid else None,
                    extent_m=_number(extent_m, "the extent"),
                    extent_note=extent_note or None,
                    extent_lookup=config.extents.get if config.extents else None,
                )
        except ValueError as exc:  # ReviewError, an unknown action, a malformed number
            message = str(exc) if isinstance(exc, ReviewError) else f"invalid input: {exc}"
            if "no record" in message:
                raise HTTPException(status_code=404, detail=message) from exc
            if htmx:
                return templates.TemplateResponse(
                    request, "_error.html", {"error": message}, status_code=400
                )
            return render_record(request, record_id, error=message, form=form, status_code=400)
        target = f"/records/{record_id}"
        if htmx:
            return Response(status_code=200, headers={"HX-Redirect": target})
        return RedirectResponse(target, status_code=303)

    return app


def _extra(config: ReviewConfig) -> list[str]:
    return [f"extent store: {config.extents_problem}"] if config.extents_problem else []


def serve(config: ReviewConfig, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the review screen with uvicorn, on a loopback address only (or 0.0.0.0 inside the
    container image, whose port Compose publishes on the host's loopback)."""
    in_container = os.environ.get(CONTAINER_ENV) == "1"
    if host not in LOOPBACK and not (in_container and host == "0.0.0.0"):
        raise ValueError(f"refusing to bind {host!r}: the review screen is local only")
    import uvicorn

    uvicorn.run(create_app(config), host=host, port=port, log_level="warning")
