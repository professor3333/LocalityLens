"""The local review screen: a queue and a record page over the review store (FastAPI + Jinja2).

* **Local only.** :func:`serve` refuses any host but loopback; there are no accounts, so a
  shared deployment needs authenticated sessions first (CLAUDE.md §10).
* **No model calls and no geometry here.** Records are imported and processed by
  ``localitylens review import``. Decisions go through :meth:`ReviewStore.decide`, which checks
  the transition, recomputes an edited proposal with the same deterministic code, refuses an
  approval without a full region, and stores an identical retry only once.
* **Label text is untrusted.** Templates autoescape everything; no route renders raw HTML from
  data.
* **Export** writes the approved Darwin Core CSV and the unresolved report with the same
  functions as ``localitylens review export``, to fixed paths, and serves only those two files.
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
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from localitylens.domain.status import RecordStatus
from localitylens.export.darwin_core import export_approved, export_unresolved
from localitylens.geo.extents import ExtentStore
from localitylens.review.store import Action, ReviewError, ReviewStore
from localitylens.web.views import queue_view, record_view

HERE: Final = Path(__file__).parent
REVIEWER_ENV: Final = "LOCALITYLENS_REVIEWER"
LOOPBACK: Final = frozenset({"127.0.0.1", "localhost", "::1"})
APPROVABLE: Final = frozenset({RecordStatus.READY_FOR_REVIEW, RecordStatus.NEEDS_INFORMATION})


@dataclass(frozen=True, slots=True)
class ReviewConfig:
    db: Path
    extents: ExtentStore | None = None  # supplies a newly chosen feature's reviewed extent
    reviewer: str | None = None  # from LOCALITYLENS_REVIEWER; asked on the form when unset
    export_out: Path = Path("data/review/export/occurrences.csv")
    unresolved_out: Path = Path("data/review/export/unresolved.csv")


def config_from_env(
    db: Path,
    extents: ExtentStore | None = None,
    export_out: Path | None = None,
    unresolved_out: Path | None = None,
) -> ReviewConfig:
    reviewer = os.environ.get(REVIEWER_ENV, "").strip() or None
    config = ReviewConfig(db=db, extents=extents, reviewer=reviewer)
    if export_out is not None:
        config = dataclasses.replace(config, export_out=export_out)
    if unresolved_out is not None:
        config = dataclasses.replace(config, unresolved_out=unresolved_out)
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
    if not config.db.is_file():
        raise FileNotFoundError(f"{config.db}: no review database (run `review import` first)")
    app = FastAPI(title="LocalityLens review", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")

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

    exports = {"occurrences.csv": config.export_out, "unresolved.csv": config.unresolved_out}

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
            unresolved = export_unresolved(s, config.unresolved_out)
        result = {
            "approved": approved,
            "unresolved": unresolved,
            "out": str(config.export_out),
            "unresolved_out": str(config.unresolved_out),
        }
        return render_queue(request, None, exported=result)

    @app.get("/export/{name}")
    def download(name: str) -> Response:
        path = exports.get(name)  # only the two export files, never an arbitrary path
        if path is None or not path.is_file():
            raise HTTPException(status_code=404, detail="no such export (export first)")
        return FileResponse(path, media_type="text/csv", filename=name)

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


def serve(config: ReviewConfig, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the review screen with uvicorn, on a loopback address only."""
    if host not in LOOPBACK:
        raise ValueError(f"refusing to bind {host!r}: the review screen is local only")
    import uvicorn

    uvicorn.run(create_app(config), host=host, port=port, log_level="warning")
