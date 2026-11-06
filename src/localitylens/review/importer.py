"""Import records into the review store and process them through the persistent job queue.

The proposal uses the top-ranked candidate and, when the reviewed-extent store has one, that
feature's extent. Importing the same records again is harmless: originals are stored once, the
batch ID is a hash of what is processed, and only records still ``queued`` get a job. A crash
mid-import leaves every record ``queued``, ``processing`` (lease, recovered on expiry) or in its
outcome status; working the batch again resumes it. Only the model-input allowlist reaches an
extractor.
"""

from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable, Iterable

from localitylens.extract.validate import VALIDATION_VERSION, Severity
from localitylens.gazetteer.index import Gazetteer
from localitylens.geo.extents import ExtentStore
from localitylens.geo.georeference import propose
from localitylens.geo.uncertainty import POLICY_ID
from localitylens.ingest.specimens import SpecimenRecord
from localitylens.jobs.queue import Clock, JobQueue, default_owner
from localitylens.jobs.worker import Process, work
from localitylens.pipeline.hybrid import interpret_hybrid
from localitylens.pipeline.interpret import Extractor, InterpretResult, interpret
from localitylens.review.store import ReviewStore


def import_records(
    store: ReviewStore,
    records: Iterable[SpecimenRecord],
    snapshot_id: str,
    gazetteer: Gazetteer,
    *,
    system: str,
    rules: Extractor,
    llm: Extractor | None,
    release: str,
    extents: ExtentStore | None = None,
    clock: Clock = time.time,
    owner: str | None = None,
    process_now: bool = True,
) -> Counter[str]:
    """Add the records, queue a job for each still-``queued`` one, and (unless ``process_now``
    is False) work the batch through. Returns the count per new status of the records that
    reached one in this call. An interrupted import is resumed by working the same batch."""
    if system not in ("rules", "llm", "hybrid"):
        raise ValueError(f"unknown system {system!r}")
    if system != "rules" and llm is None:
        raise ValueError(f"system {system!r} needs an LLM extractor")
    ids = [store.add_record(r, snapshot_id) for r in records]  # originals first, once each
    queue = JobQueue(store, clock=clock)
    batch_id = queue.enqueue(
        ids, system=system, release=release, snapshot_id=snapshot_id,
        gazetteer=gazetteer.snapshot_id, extractor=_version(system, rules, llm),
    )  # fmt: skip
    if not process_now:
        return Counter()
    return work_batch(store, queue, batch_id, gazetteer, rules=rules, llm=llm, extents=extents,
                      owner=owner)  # fmt: skip


def work_batch(
    store: ReviewStore,
    queue: JobQueue,
    batch_id: str,
    gazetteer: Gazetteer,
    *,
    rules: Extractor,
    llm: Extractor | None,
    extents: ExtentStore | None = None,
    owner: str | None = None,
    max_jobs: int | None = None,
    should_stop: Callable[[], bool] = lambda: False,
) -> Counter[str]:
    """Work one batch's pending jobs. Returns the count per final status reached."""
    batch = queue.batch(batch_id)
    process = pipeline_step(store, gazetteer, system=batch.system, rules=rules, llm=llm,
                            release=batch.release, extents=extents)  # fmt: skip
    before = _job_states(store, batch_id)
    work(
        queue,
        process,
        owner=owner or default_owner(),
        batch_id=batch_id,
        max_jobs=max_jobs,
        should_stop=should_stop,
    )
    outcome: Counter[str] = Counter()
    for record_id, state in _job_states(store, batch_id).items():
        if state in ("done", "failed") and before.get(record_id) != state:
            outcome[store.status(record_id).value] += 1
    return outcome


def pipeline_step(
    store: ReviewStore,
    gazetteer: Gazetteer,
    *,
    system: str,
    rules: Extractor,
    llm: Extractor | None,
    release: str,
    extents: ExtentStore | None = None,
) -> Process:
    """``process(record_id)`` for the worker: run the pipeline on the record's allowlisted
    fields (locality text and supplied county) and return the writer of its result."""

    def process(record_id: str) -> Step:
        row = store.record(record_id)
        started = time.perf_counter()
        county = row["county"] or None
        result, llm_called, llm_used, llm_error = _run(
            system, row["locality"], county, rules, llm, gazetteer
        )
        interp = result.validation.interpretation
        candidates = result.retrieval.candidates if result.retrieval else ()
        top = candidates[0] if candidates else None
        extent = extents.get(top.feature_id) if extents is not None and top else None
        t0 = time.perf_counter()
        proposal = propose(interp, top, extent) if interp is not None else None
        done = time.perf_counter()

        def write() -> str:
            return store.add_pipeline_result(
                record_id, system=system, extractor_version=result.extractor_version,
                release=release, gazetteer_snapshot=gazetteer.snapshot_id,
                interpretation=interp, candidates=tuple(candidates), proposal=proposal,
            )  # fmt: skip

        model = None
        call = getattr(llm, "last_trace", None) if llm_called else None
        if llm_called:
            model = {
                "called": True, "used": llm_used,
                "prompt_sha256": getattr(call, "prompt_sha256", "") or None,
                "prompt_tokens": getattr(call, "prompt_tokens", 0),
                "completion_tokens": getattr(call, "completion_tokens", 0),
                "attempts": getattr(call, "attempts", 0),
                "cache_hits": getattr(call, "cache_hits", 0),
                "seconds": round(getattr(call, "seconds", 0.0), 3),
                "error": llm_error,
            }  # fmt: skip
        fields: dict[str, object] = {
            "uncertainty_policy": proposal.policy_id if proposal else POLICY_ID,
            "validation_version": VALIDATION_VERSION,
            "candidate_count": len(candidates),
            "validation_errors": tuple(sorted({i.code.value for i in result.validation.issues
                                               if i.severity is Severity.ERROR})),
            "stages": {**{k: round(v, 3) for k, v in result.stage_ms.items()},
                       "propose_ms": round((done - t0) * 1000, 3),
                       "total_ms": round((done - started) * 1000, 3)},
            "model": model,
        }  # fmt: skip
        return Step(write, fields)

    return process


class Step:
    """The worker's writer for one record, with the fields for the attempt's trace."""

    def __init__(self, write: Callable[[], str], trace_fields: dict[str, object]) -> None:
        self._write = write
        self.trace_fields = trace_fields

    def __call__(self) -> str:
        return self._write()


def _job_states(store: ReviewStore, batch_id: str) -> dict[str, str]:
    rows = store.connection.execute(
        "SELECT record_id, state FROM job WHERE batch_id=?", (batch_id,)
    )
    return {r["record_id"]: r["state"] for r in rows}


def _run(
    system: str,
    locality: str,
    county: str | None,
    rules: Extractor,
    llm: Extractor | None,
    gazetteer: Gazetteer,
) -> tuple[InterpretResult, bool, bool, str | None]:
    """(result, LLM called, LLM reading used, LLM error category in hybrid)."""
    if system == "hybrid":
        assert llm is not None
        h = interpret_hybrid(locality, rules, llm, gazetteer, supplied_county=county)
        return h.result, h.llm_called, h.source == "llm", h.llm_error
    extractor = rules if system == "rules" else llm
    assert extractor is not None
    used = system == "llm"
    return interpret(locality, extractor, gazetteer, supplied_county=county), used, used, None


def _version(system: str, rules: Extractor, llm: Extractor | None) -> str:
    if system == "rules" or llm is None:
        return rules.version
    return llm.version if system == "llm" else f"hybrid-1({rules.version}+{llm.version})"
