"""JSON API under ``/api``: batch status (also streamed), cancel/resume, records, decisions,
export. Same store and rules as the review screen; local only, like it.

* **The worker is a separate process** (``localitylens review work``): the API reports and
  controls batches but never runs the pipeline, so a slow model call cannot block a request.
* **POSTs take JSON** (``application/json``, which a browser cannot send cross-site without a
  CORS preflight, and no CORS is allowed) and pass the same-origin check as the forms.
* **Decisions are idempotent.** The response says whether the decision was ``created`` (201)
  or already stored (200); a retried request never adds a decision or an export row.
* **Errors are explicit:** 400 for a refused decision (with the store's reason), 404 for an
  unknown record or batch, 415 for a non-JSON body, 403 for a cross-site request.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator, Callable
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from localitylens.domain.status import RecordStatus
from localitylens.export.darwin_core import export_approved, export_unresolved
from localitylens.jobs.queue import Batch, JobQueue
from localitylens.review.store import Action, ReviewError, ReviewStore
from localitylens.web.views import summary_line

API_VERSION = "api-1"
OPEN_STATES = ("pending", "leased")


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["approve", "reject", "request_research"]
    reviewer: str | None = None  # defaults to LOCALITYLENS_REVIEWER
    rationale: str
    feature_id: int | None = None
    extent_m: float | None = Field(default=None, gt=0)
    extent_note: str | None = None
    key: str | None = Field(default=None, max_length=128)  # idempotency key


def _batch_json(b: Batch) -> dict[str, Any]:
    total = sum(b.jobs.values())
    finished = sum(n for s, n in b.jobs.items() if s not in OPEN_STATES)
    return {
        "batch_id": b.batch_id, "state": b.state.value, "system": b.system,
        "release": b.release, "snapshot_id": b.snapshot_id, "created_at": b.created_at,
        "jobs": dict(sorted(b.jobs.items())), "total": total, "finished": finished,
        "open": total - finished,
    }  # fmt: skip


def build_router(
    store: Callable[[], ReviewStore],
    *,
    reviewer: str | None,
    extent_lookup: Callable[[int], Any] | None,
    exports: dict[str, Any],
    same_origin: Callable[[Request], bool],
) -> APIRouter:
    api = APIRouter(prefix="/api")

    def guard(request: Request) -> None:
        if not same_origin(request):
            raise HTTPException(status_code=403, detail="cross-site requests are refused")
        ctype = request.headers.get("content-type", "").split(";")[0].strip()
        if ctype != "application/json":
            raise HTTPException(status_code=415, detail="send application/json")

    def queue(s: ReviewStore) -> JobQueue:
        return JobQueue(s, clock=time.time)

    def find_batch(s: ReviewStore, batch_id: str) -> Batch:
        try:
            return queue(s).batch(batch_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "api": API_VERSION}

    # --- batches ------------------------------------------------------------------------------

    @api.get("/batches")
    def batches() -> list[dict[str, Any]]:
        with store() as s:
            return [_batch_json(b) for b in queue(s).batches()]

    @api.get("/batches/{batch_id}")
    def batch(batch_id: str) -> dict[str, Any]:
        with store() as s:
            return _batch_json(find_batch(s, batch_id))

    @api.get("/batches/{batch_id}/events")
    async def batch_events(batch_id: str, interval: float = 1.0, timeout: float = 600.0) -> Any:
        """Server-Sent Events: a ``progress`` event whenever the job counts change, then a
        final ``end`` event when nothing is pending or leased (or the batch is cancelled and
        idle), or a ``timeout`` event."""
        with store() as s:
            find_batch(s, batch_id)
        interval = min(max(interval, 0.05), 30.0)

        async def events() -> AsyncIterator[str]:
            last: dict[str, Any] | None = None
            deadline = time.monotonic() + timeout
            while True:
                with store() as s:
                    now = _batch_json(queue(s).batch(batch_id))
                if now != last:
                    yield f"event: progress\ndata: {json.dumps(now)}\n\n"
                    last = now
                if now["open"] == 0 or (
                    now["state"] == "cancelled" and not now["jobs"].get("leased")
                ):
                    yield f"event: end\ndata: {json.dumps(now)}\n\n"
                    return
                if time.monotonic() > deadline:
                    yield f"event: timeout\ndata: {json.dumps(now)}\n\n"
                    return
                await asyncio.sleep(interval)

        return StreamingResponse(events(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache"})  # fmt: skip

    @api.post("/batches/{batch_id}/cancel", dependencies=[Depends(guard)])
    def cancel(batch_id: str) -> dict[str, Any]:
        with store() as s:
            find_batch(s, batch_id)
            stopped = queue(s).cancel(batch_id)
            return {"cancelled_jobs": stopped, "batch": _batch_json(queue(s).batch(batch_id))}

    @api.post("/batches/{batch_id}/resume", dependencies=[Depends(guard)])
    def resume(batch_id: str) -> dict[str, Any]:
        with store() as s:
            find_batch(s, batch_id)
            again = queue(s).resume(batch_id)
            return {"resumed_jobs": again, "batch": _batch_json(queue(s).batch(batch_id))}

    # --- records ------------------------------------------------------------------------------

    @api.get("/records")
    def records(status: str | None = None) -> list[dict[str, Any]]:
        try:
            wanted = RecordStatus(status) if status else None
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"unknown status {status!r}") from exc
        with store() as s:
            out = []
            for r in s.records(wanted):
                try:
                    summary = summary_line(s.latest_pipeline_proposal(r["record_id"]))
                except ReviewError:
                    summary = "not processed yet"
                out.append({"record_id": r["record_id"], "status": r["status"],
                            "county": r["county"], "summary": summary})  # fmt: skip
            return out

    @api.get("/records/{record_id}")
    def record(record_id: str) -> dict[str, Any]:
        with store() as s:
            try:
                rec = dict(s.record(record_id))
            except ReviewError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            try:
                p = s.latest_pipeline_proposal(record_id)
            except ReviewError:
                p = None
            return {
                "record": rec,
                "proposal": None if p is None else {
                    "proposal_id": p.proposal_id, "system": p.system,
                    "extractor_version": p.extractor_version, "release": p.release,
                    "gazetteer_snapshot": p.gazetteer_snapshot, "outcome": p.outcome,
                    "interpretation": p.interpretation.model_dump(mode="json")
                    if p.interpretation else None,
                    "candidates": [c.model_dump(mode="json") for c in p.candidates],
                    "region": p.proposal.model_dump(mode="json") if p.proposal else None,
                    "trace_id": s.trace_for_proposal(p.proposal_id),
                },
                "decisions": [
                    {"decision_id": d.decision_id, "action": d.action.value,
                     "reviewer": d.reviewer, "rationale": d.rationale, "edits": d.edits,
                     "final_proposal": d.final_proposal, "decided_at": d.decided_at}
                    for d in s.decisions(record_id)
                ],
            }  # fmt: skip

    @api.post("/records/{record_id}/decisions", dependencies=[Depends(guard)])
    def decide(record_id: str, body: DecisionIn) -> JSONResponse:
        who = body.reviewer or reviewer or ""
        with store() as s:
            try:
                s.record(record_id)
            except ReviewError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            try:
                d = s.decide(
                    record_id, Action(body.action), reviewer=who, rationale=body.rationale,
                    feature_id=body.feature_id, extent_m=body.extent_m,
                    extent_note=body.extent_note, key=body.key, extent_lookup=extent_lookup,
                )  # fmt: skip
            except ReviewError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            status = s.status(record_id).value
        payload = {"decision_id": d.decision_id, "created": d.created, "status": status,
                   "edits": d.edits, "final_proposal": d.final_proposal}  # fmt: skip
        return JSONResponse(payload, status_code=201 if d.created else 200)

    # --- export -------------------------------------------------------------------------------

    @api.post("/exports", dependencies=[Depends(guard)])
    def export() -> dict[str, Any]:
        with store() as s:
            approved = export_approved(s, exports["occurrences.csv"])
            unresolved = export_unresolved(s, exports["unresolved.csv"])
        return {"approved": approved, "unresolved": unresolved,
                "files": {k: str(v) for k, v in exports.items()}}  # fmt: skip

    return api
