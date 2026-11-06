"""Persistent job queue over the review store: idempotent keys, leases, bounded retries,
cancellation and resumable batches.

Every operation is one transaction that changes a job and its record together, so a crash at
any point leaves both in a defined state:

* **pending** job ↔ record ``queued``; **leased** job ↔ record ``processing``;
* **done** or **failed** job ↔ record in its outcome status (``failed`` carries a category);
* **cancelled** job ↔ record still ``queued`` (untouched).

A worker that dies holding a lease leaves its record ``processing``; once the lease has expired,
:meth:`JobQueue.recover` (also run at the start of every claim) puts it back to ``queued``, or to
``failed`` (``lease_expired``) when its attempts are used up. A result from a worker whose lease
has expired is discarded, so a record never gets two pipeline results from one batch.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import socket
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from localitylens.domain.status import RecordStatus
from localitylens.review.store import ReviewStore
from localitylens.telemetry.trace import RecordTrace, emit, input_sha256, new_trace_id, now_iso

JOBS_VERSION: Final = "jobs-1"
DEFAULT_LEASE_S: Final = 300.0  # an LLM call takes seconds to tens of seconds (p95 ~ 30 s)
DEFAULT_MAX_ATTEMPTS: Final = 3
log = logging.getLogger(__name__)

Clock = Callable[[], float]


class JobState(StrEnum):
    PENDING = "pending"
    LEASED = "leased"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchState(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Job:
    job_id: str
    batch_id: str
    record_id: str
    attempts: int
    lease_owner: str
    lease_expires: float


@dataclass(frozen=True, slots=True)
class Batch:
    batch_id: str
    system: str
    release: str
    snapshot_id: str
    state: BatchState
    created_at: str
    jobs: dict[str, int]  # job state → count


def default_owner() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _hash(*parts: object) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


class JobQueue:
    def __init__(
        self,
        store: ReviewStore,
        *,
        clock: Clock,
        lease_s: float = DEFAULT_LEASE_S,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> None:
        if lease_s <= 0 or max_attempts < 1:
            raise ValueError("lease_s must be positive and max_attempts at least 1")
        self.store = store
        self._con = store.connection
        self._clock = clock
        self.lease_s = lease_s
        self.max_attempts = max_attempts

    # --- batches ------------------------------------------------------------------------------

    def enqueue(
        self,
        record_ids: Iterable[str],
        *,
        system: str,
        release: str,
        snapshot_id: str,
        gazetteer: str,
        extractor: str,
    ) -> str:
        """One job per still-``queued`` record. The batch ID is a hash of what is processed, so
        enqueueing the same records again returns the same batch and adds no job."""
        ids = list(dict.fromkeys(record_ids))
        batch_id = "b-" + _hash(JOBS_VERSION, system, release, snapshot_id, gazetteer, sorted(ids))
        with self.store.transaction():
            self._con.execute(
                "INSERT OR IGNORE INTO batch VALUES (?,?,?,?,?,?,?,?,NULL)",
                (batch_id, system, release, snapshot_id, gazetteer, extractor,
                 BatchState.ACTIVE.value, _now_iso()),
            )  # fmt: skip
            for seq, record_id in enumerate(ids):
                if self.store.status(record_id) is not RecordStatus.QUEUED:
                    continue  # already processed: nothing to do
                self._con.execute(
                    "INSERT OR IGNORE INTO job VALUES (?,?,?,?,?,0,NULL,NULL,NULL,?)",
                    (_hash(batch_id, record_id), batch_id, record_id, seq,
                     JobState.PENDING.value, _now_iso()),
                )  # fmt: skip
        return batch_id

    def batch(self, batch_id: str) -> Batch:
        r = self._con.execute("SELECT * FROM batch WHERE batch_id=?", (batch_id,)).fetchone()
        if r is None:
            raise KeyError(f"no batch {batch_id}")
        counts = Counter(
            {s: n for s, n in self._con.execute(
                "SELECT state, COUNT(*) FROM job WHERE batch_id=? GROUP BY state", (batch_id,))}
        )  # fmt: skip
        return Batch(
            r["batch_id"],
            r["system"],
            r["release"],
            r["snapshot_id"],
            BatchState(r["state"]),
            r["created_at"],
            dict(counts),
        )

    def batches(self) -> list[Batch]:
        rows = self._con.execute("SELECT batch_id FROM batch ORDER BY created_at, batch_id")
        return [self.batch(r["batch_id"]) for r in list(rows)]

    def cancel(self, batch_id: str) -> int:
        """Stop a batch: its pending jobs are cancelled and their records stay ``queued``. A job
        already leased finishes (or its lease expires) normally. Returns the jobs cancelled."""
        self.batch(batch_id)  # raises for an unknown batch
        with self.store.transaction():
            self._con.execute(
                "UPDATE batch SET state=?, cancelled_at=? WHERE batch_id=?",
                (BatchState.CANCELLED.value, _now_iso(), batch_id),
            )
            cur = self._con.execute(
                "UPDATE job SET state=?, updated_at=? WHERE batch_id=? AND state=?",
                (JobState.CANCELLED.value, _now_iso(), batch_id, JobState.PENDING.value),
            )
        return cur.rowcount

    def resume(self, batch_id: str) -> int:
        """Reactivate a cancelled batch: its cancelled jobs become pending again (their records
        are still ``queued``). Returns the jobs reactivated."""
        self.batch(batch_id)
        with self.store.transaction():
            self._con.execute(
                "UPDATE batch SET state=?, cancelled_at=NULL WHERE batch_id=?",
                (BatchState.ACTIVE.value, batch_id),
            )
            cur = self._con.execute(
                "UPDATE job SET state=?, updated_at=? WHERE batch_id=? AND state=?",
                (JobState.PENDING.value, _now_iso(), batch_id, JobState.CANCELLED.value),
            )
        return cur.rowcount

    # --- leases -------------------------------------------------------------------------------

    def recover(self) -> int:
        """Return every job whose lease has expired, as a failed attempt (``lease_expired``),
        and put back to ``queued`` any record left ``processing`` without a live lease (a crash
        outside the queue). Returns how many were recovered."""
        now = self._clock()
        orphans = list(self._con.execute(
            "SELECT record_id FROM record WHERE status=? AND record_id NOT IN "
            "(SELECT record_id FROM job WHERE state=?)",
            (RecordStatus.PROCESSING.value, JobState.LEASED.value),
        ))  # fmt: skip
        for r in orphans:
            with self.store.transaction():
                if self.store.status(r["record_id"]) is RecordStatus.PROCESSING:
                    self.store.requeue(r["record_id"])
                    log.warning(
                        "requeued orphaned record %s (processing, no lease)", r["record_id"]
                    )
        expired = list(self._con.execute(
            "SELECT job_id, record_id, attempts FROM job WHERE state=? AND lease_expires < ?",
            (JobState.LEASED.value, now),
        ))  # fmt: skip
        for r in expired:
            with self.store.transaction():
                still = self._con.execute(
                    "SELECT state, lease_expires FROM job WHERE job_id=?", (r["job_id"],)
                ).fetchone()
                if still["state"] != JobState.LEASED.value or still["lease_expires"] >= now:
                    continue  # completed or re-leased meanwhile
                trace = self._retry_or_fail(
                    r["job_id"],
                    r["record_id"],
                    r["attempts"],
                    "lease_expired",
                    retryable=True,
                    fields=None,
                )
            emit(trace)
            log.warning("lease expired: job %s, attempt %d", r["job_id"], r["attempts"])
        return len(expired) + len(orphans)

    def claim(self, owner: str, batch_id: str | None = None) -> Job | None:
        """Lease the next pending job of an active batch, or None when there is none."""
        self.recover()
        now = self._clock()
        with self.store.transaction():
            query = (
                "SELECT j.job_id, j.batch_id, j.record_id, j.attempts FROM job j "
                "JOIN batch b ON b.batch_id = j.batch_id WHERE j.state=? AND b.state=?"
            )
            args: list[object] = [JobState.PENDING.value, BatchState.ACTIVE.value]
            if batch_id is not None:
                query, args = query + " AND j.batch_id=?", [*args, batch_id]
            r = self._con.execute(query + " ORDER BY b.created_at, j.seq LIMIT 1", args).fetchone()
            if r is None:
                return None
            if self.store.status(r["record_id"]) is not RecordStatus.QUEUED:
                # processed meanwhile (another batch, a direct import): nothing left to do
                self._set_job(r["job_id"], JobState.DONE, error="already_processed")
                return self.claim(owner, batch_id)
            attempts = r["attempts"] + 1
            expires = now + self.lease_s
            self._con.execute(
                "UPDATE job SET state=?, attempts=?, lease_owner=?, lease_expires=?, "
                "updated_at=? WHERE job_id=?",
                (JobState.LEASED.value, attempts, owner, expires, _now_iso(), r["job_id"]),
            )
            self.store.start_processing(r["record_id"])
        return Job(r["job_id"], r["batch_id"], r["record_id"], attempts, owner, expires)

    def holds_lease(self, job: Job) -> bool:
        r = self._con.execute(
            "SELECT state, lease_owner, attempts, lease_expires FROM job WHERE job_id=?",
            (job.job_id,),
        ).fetchone()
        return (
            r is not None
            and r["state"] == JobState.LEASED.value
            and r["lease_owner"] == job.lease_owner
            and r["attempts"] == job.attempts
            and r["lease_expires"] >= self._clock()
        )

    def complete(
        self,
        job: Job,
        write_result: Callable[[], str | None],
        fields: dict[str, object] | None = None,
    ) -> bool:
        """Write the pipeline result, close the job and store its trace, atomically. A worker
        whose lease has expired (or was taken over) writes nothing and gets False."""
        with self.store.transaction():
            if not self.holds_lease(job):
                return False
            proposal_id = write_result()  # add_pipeline_result: processing → outcome status
            self._set_job(job.job_id, JobState.DONE)
            outcome = self.store.status(job.record_id).value
            trace = self._trace(job.job_id, job.batch_id, job.record_id, job.attempts, outcome,
                                proposal_id, fields)  # fmt: skip
        emit(trace)
        return True

    def fail(
        self, job: Job, category: str, *, retryable: bool, fields: dict[str, object] | None = None
    ) -> bool:
        """A failed attempt. Transient failures go back to ``queued`` while attempts remain;
        the rest end ``failed`` with their category. False if the lease was already lost."""
        with self.store.transaction():
            if not self.holds_lease(job):
                return False
            trace = self._retry_or_fail(job.job_id, job.record_id, job.attempts, category,
                                        retryable=retryable, fields=fields)  # fmt: skip
        emit(trace)
        return True

    # --- internals (inside a transaction) -----------------------------------------------------

    def _retry_or_fail(
        self,
        job_id: str,
        record_id: str,
        attempts: int,
        category: str,
        *,
        retryable: bool,
        fields: dict[str, object] | None,
    ) -> RecordTrace:
        batch_id = self._con.execute(
            "SELECT batch_id FROM job WHERE job_id=?", (job_id,)
        ).fetchone()["batch_id"]
        if retryable and attempts < self.max_attempts:
            self._set_job(job_id, JobState.PENDING, error=category)
            self.store.requeue(record_id)
            return self._trace(job_id, batch_id, record_id, attempts, f"retry:{category}", None,
                               fields)  # fmt: skip
        self._set_job(job_id, JobState.FAILED, error=category)
        row = self._con.execute(
            "SELECT b.system, b.release, b.gazetteer, b.extractor FROM job j JOIN batch b "
            "ON b.batch_id = j.batch_id WHERE j.job_id=?", (job_id,)
        ).fetchone()  # fmt: skip
        proposal_id = self.store.add_pipeline_result(
            record_id, system=row["system"], extractor_version=row["extractor"],
            release=row["release"], gazetteer_snapshot=row["gazetteer"], interpretation=None,
            candidates=(), proposal=None, failure=category,
        )  # fmt: skip
        return self._trace(job_id, batch_id, record_id, attempts, f"failed:{category}",
                           proposal_id, fields)  # fmt: skip

    def _trace(
        self,
        job_id: str,
        batch_id: str,
        record_id: str,
        attempt: int,
        outcome: str,
        proposal_id: str | None,
        fields: dict[str, object] | None,
    ) -> RecordTrace:
        """Build, validate and store one attempt's trace (inside the step's transaction)."""
        b = self._con.execute("SELECT * FROM batch WHERE batch_id=?", (batch_id,)).fetchone()
        rec = self.store.record(record_id)
        base: dict[str, object] = {
            "trace_id": new_trace_id(), "at": now_iso(), "job_id": job_id, "batch_id": batch_id,
            "record_id": record_id, "attempt": attempt,
            "input_sha256": input_sha256(rec["locality"], rec["county"] or None),
            "system": b["system"], "extractor_version": b["extractor"],
            "release": b["release"], "gazetteer_snapshot": b["gazetteer"],
            "outcome": outcome, "proposal_id": proposal_id,
        }  # fmt: skip
        trace = RecordTrace.model_validate({**(fields or {}), **base})  # identity fields win
        self.store.add_trace(trace.trace_id, job_id, record_id, proposal_id, trace.at, outcome,
                             trace.model_dump_json(exclude_none=True))  # fmt: skip
        return trace

    def _set_job(self, job_id: str, state: JobState, *, error: str | None = None) -> None:
        self._con.execute(
            "UPDATE job SET state=?, lease_owner=NULL, lease_expires=NULL, "
            "last_error=COALESCE(?, last_error), updated_at=? WHERE job_id=?",
            (state.value, error, _now_iso(), job_id),
        )
