"""Persistent jobs: idempotent enqueue, leases, crash recovery, bounded retries, cancellation,
resumable batches. SYNTHETIC records; the pipeline is replaced by fake process functions, and
time by a fake clock, so every interleaving is exact.

The interleaving property checks state consistency (every job and record defined, none
stranded, one pipeline result per record). That a late worker's result is refused is a
separate property, pinned by ``test_a_late_result_from_an_expired_lease_is_discarded``: a
mutation check showed the random interleavings reach that sequence only at the thorough
profile."""

import sqlite3
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from tests.support.synthetic_dwca import row

from localitylens.domain.status import RecordStatus
from localitylens.extract.llm_client import FailureCategory, ModelCallError
from localitylens.ingest.specimens import to_record
from localitylens.jobs.queue import Job, JobQueue, JobState
from localitylens.jobs.worker import work
from localitylens.review.store import STORE_SCHEMA_VERSION, ReviewStore

TERMINAL = {
    RecordStatus.READY_FOR_REVIEW,
    RecordStatus.NEEDS_INFORMATION,
    RecordStatus.UNSUPPORTED,
    RecordStatus.FAILED,
}


class Clock:
    def __init__(self) -> None:
        self.t = 1_000_000.0

    def __call__(self) -> float:
        return self.t


def _store(path: Path, n: int = 4) -> tuple[ReviewStore, list[str]]:
    store = ReviewStore(path)
    ids = [
        store.add_record(to_record(row(i, f"Testa Lake {i}.")), "gbif-synthetic")
        for i in range(1, n + 1)
    ]
    return store, ids


def _queue(store: ReviewStore, clock: Clock, **kw: float) -> JobQueue:
    return JobQueue(
        store,
        clock=clock,
        lease_s=kw.get("lease_s", 60.0),
        max_attempts=int(kw.get("max_attempts", 3)),
    )


def _enqueue(q: JobQueue, ids: list[str]) -> str:
    return q.enqueue(
        ids,
        system="rules",
        release="test",
        snapshot_id="gbif-synthetic",
        gazetteer="gnis-synthetic",
        extractor="rules-test",
    )


def _writer(store: ReviewStore) -> Callable[[str], Callable[[], None]]:
    """A pipeline stand-in: every record ends needs_information (no interpretation)."""

    def process(record_id: str) -> Callable[[], None]:
        def write() -> None:
            store.add_pipeline_result(
                record_id,
                system="rules",
                extractor_version="rules-test",
                release="test",
                gazetteer_snapshot="gnis-synthetic",
                interpretation=None,
                candidates=(),
                proposal=None,
            )

        return write

    return process


def _raising(
    exc: Exception, store: ReviewStore, times: int | None = None
) -> Callable[[str], Callable[[], None]]:
    calls: Counter[str] = Counter()
    ok = _writer(store)

    def process(record_id: str) -> Callable[[], None]:
        calls[record_id] += 1
        if times is None or calls[record_id] <= times:
            raise exc
        return ok(record_id)

    return process


def check_invariants(store: ReviewStore) -> None:
    """Every job and its record are in a defined, consistent state; no record is stranded."""
    con = store.connection
    for j in con.execute("SELECT * FROM job"):
        status = store.status(j["record_id"])
        state = JobState(j["state"])
        if state in (JobState.PENDING, JobState.CANCELLED):
            assert status is RecordStatus.QUEUED, (state, status)
        elif state is JobState.LEASED:
            assert status is RecordStatus.PROCESSING, (state, status)
            assert j["lease_owner"]
            assert j["lease_expires"] is not None
        else:
            assert status in TERMINAL, (state, status)
        assert j["attempts"] >= 0
    leased = {r["record_id"] for r in con.execute("SELECT record_id FROM job WHERE state='leased'")}
    for r in store.records(RecordStatus.PROCESSING):
        assert r["record_id"] in leased, "a record is processing without a lease"
    for r in con.execute(
        "SELECT record_id, COUNT(*) n FROM proposal WHERE origin='pipeline' GROUP BY record_id"
    ):
        assert r["n"] == 1, "a record got two pipeline results"


# --- enqueue, claim, complete ----------------------------------------------------------------


def test_enqueue_is_idempotent(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    q = _queue(store, Clock())
    b1, b2 = _enqueue(q, ids), _enqueue(q, list(reversed(ids)))
    assert b1 == b2
    assert q.batch(b1).jobs == {"pending": 4}
    check_invariants(store)


def test_claim_leases_and_complete_closes(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    q = _queue(store, Clock())
    _enqueue(q, ids)
    job = q.claim("w1")
    assert job is not None
    assert job.record_id == ids[0]
    assert job.attempts == 1
    assert store.status(ids[0]) is RecordStatus.PROCESSING
    check_invariants(store)
    assert q.complete(job, _writer(store)(job.record_id))
    assert store.status(ids[0]) is RecordStatus.NEEDS_INFORMATION
    check_invariants(store)


def test_work_processes_the_batch_in_order(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    q = _queue(store, Clock())
    b = _enqueue(q, ids)
    assert work(q, _writer(store), owner="w1") == Counter(done=4)
    assert q.batch(b).jobs == {"done": 4}
    assert work(q, _writer(store), owner="w1") == Counter()  # nothing left
    check_invariants(store)


# --- crashes and leases ----------------------------------------------------------------------


def test_a_crashed_worker_is_recovered_after_its_lease(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    clock = Clock()
    q = _queue(store, clock)
    _enqueue(q, ids)
    q.claim("crashed")  # the worker dies here: no complete, no fail
    assert store.status(ids[0]) is RecordStatus.PROCESSING
    clock.t += 30
    assert q.recover() == 0  # lease still valid
    clock.t += 31
    assert q.recover() == 1
    assert store.status(ids[0]) is RecordStatus.QUEUED
    check_invariants(store)
    assert work(q, _writer(store), owner="w2") == Counter(done=4)
    attempts = store.connection.execute(
        "SELECT attempts FROM job WHERE record_id=?", (ids[0],)
    ).fetchone()[0]
    assert attempts == 2
    check_invariants(store)


def test_a_late_result_from_an_expired_lease_is_discarded(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    clock = Clock()
    q = _queue(store, clock)
    _enqueue(q, ids[:1])
    slow = q.claim("slow")
    assert slow is not None
    clock.t += 61
    fast = q.claim("fast")  # recovers and re-leases the same record
    assert fast is not None
    assert fast.record_id == slow.record_id
    assert not q.complete(slow, _writer(store)(slow.record_id))  # nothing written
    assert not q.fail(slow, "model_server_unavailable", retryable=True)
    assert q.complete(fast, _writer(store)(fast.record_id))
    check_invariants(store)  # exactly one pipeline result


def test_repeated_crashes_end_failed_with_a_category(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite", n=1)
    clock = Clock()
    q = _queue(store, clock, max_attempts=2)
    _enqueue(q, ids)
    for _ in range(2):
        q.claim("crashes")
        clock.t += 61
        q.recover()
        check_invariants(store)
    assert store.status(ids[0]) is RecordStatus.FAILED
    assert store.latest_pipeline_proposal(ids[0]).outcome == "failed:lease_expired"


def test_an_orphaned_processing_record_is_requeued(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    store.start_processing(ids[0])  # a crash outside the queue
    q = _queue(store, Clock())
    assert q.recover() == 1
    assert store.status(ids[0]) is RecordStatus.QUEUED


# --- failures --------------------------------------------------------------------------------


def test_transient_failures_are_retried_then_fail(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite", n=1)
    q = _queue(store, Clock())
    _enqueue(q, ids)
    down = ModelCallError(FailureCategory.MODEL_SERVER_UNAVAILABLE, "connection refused")
    assert work(q, _raising(down, store), owner="w") == Counter(retried=2, failed=1)
    assert store.status(ids[0]) is RecordStatus.FAILED
    p = store.latest_pipeline_proposal(ids[0])
    assert p.outcome == "failed:model_server_unavailable"
    assert (p.extractor_version, p.gazetteer_snapshot) == ("rules-test", "gnis-synthetic")
    check_invariants(store)


def test_a_transient_failure_then_success(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite", n=1)
    q = _queue(store, Clock())
    _enqueue(q, ids)
    down = ModelCallError(FailureCategory.MODEL_SERVER_UNAVAILABLE, "restarting")
    assert work(q, _raising(down, store, times=1), owner="w") == Counter(retried=1, done=1)
    assert store.status(ids[0]) is RecordStatus.NEEDS_INFORMATION


def test_deterministic_model_failures_are_not_retried(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite", n=1)
    q = _queue(store, Clock())
    _enqueue(q, ids)
    bad = ModelCallError(FailureCategory.MALFORMED_MODEL_OUTPUT, "invalid JSON twice")
    assert work(q, _raising(bad, store), owner="w") == Counter(failed=1)
    assert store.latest_pipeline_proposal(ids[0]).outcome == "failed:malformed_model_output"


def test_unexpected_errors_are_categorized_retried_and_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    store, ids = _store(tmp_path / "r.sqlite", n=1)
    q = _queue(store, Clock())
    _enqueue(q, ids)
    assert work(q, _raising(RuntimeError("boom"), store), owner="w") == Counter(retried=2, failed=1)
    assert store.latest_pipeline_proposal(ids[0]).outcome == "failed:internal_error"
    assert "RuntimeError" in caplog.text
    assert "Testa Lake" not in caplog.text  # never label text in logs


# --- cancellation and resuming ---------------------------------------------------------------


def test_cancel_leaves_unstarted_records_queued_and_resume_finishes(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "r.sqlite")
    q = _queue(store, Clock())
    b = _enqueue(q, ids)
    assert work(q, _writer(store), owner="w", max_jobs=1) == Counter(done=1)
    leased = q.claim("w")  # in flight when the batch is cancelled
    assert q.cancel(b) == 2
    assert [store.status(i) for i in ids[2:]] == [RecordStatus.QUEUED] * 2  # untouched
    assert q.claim("w") is None  # nothing more is started
    assert leased is not None
    assert q.complete(leased, _writer(store)(leased.record_id))  # the in-flight job finishes
    check_invariants(store)
    assert q.resume(b) == 2
    assert work(q, _writer(store), owner="w") == Counter(done=2)
    assert q.batch(b).jobs == {"done": 4}
    check_invariants(store)


def test_an_interrupted_batch_resumes_to_the_same_result(tmp_path: Path) -> None:
    store, ids = _store(tmp_path / "a.sqlite")
    q = _queue(store, Clock())
    _enqueue(q, ids)
    work(q, _writer(store), owner="w", max_jobs=2)  # interrupted
    store.close()
    store = ReviewStore(tmp_path / "a.sqlite")  # a restart
    q = _queue(store, Clock())
    _enqueue(q, ids)  # re-running the import finds the same batch
    assert work(q, _writer(store), owner="w") == Counter(done=2)
    assert {store.status(i) for i in ids} == {RecordStatus.NEEDS_INFORMATION}
    check_invariants(store)


# --- schema ----------------------------------------------------------------------------------


def test_a_review_1_store_is_upgraded_in_place(tmp_path: Path) -> None:
    path = tmp_path / "old.sqlite"
    store, ids = _store(path)
    store.close()
    con = sqlite3.connect(path)
    con.executescript(
        "DROP TABLE job; DROP TABLE batch; UPDATE meta SET value='review-1' WHERE key='schema';"
    )
    con.close()
    store = ReviewStore(path)
    assert (
        store.connection.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0]
        == STORE_SCHEMA_VERSION
    )
    assert store.status(ids[0]) is RecordStatus.QUEUED  # records untouched
    q = _queue(store, Clock())
    _enqueue(q, ids)
    assert work(q, _writer(store), owner="w") == Counter(done=4)


# --- any interleaving --------------------------------------------------------------------------

OPS = st.lists(
    st.tuples(
        st.sampled_from(
            [
                "claim",
                "complete",
                "fail_transient",
                "fail_bad",
                "crash",
                "advance",
                "recover",
                "cancel",
                "resume",
            ]
        ),
        st.integers(min_value=0, max_value=3),
    ),
    max_size=40,
)


@settings(deadline=None)
@given(OPS)
def test_any_interleaving_keeps_every_record_in_a_defined_state(
    tmp_path_factory: pytest.TempPathFactory, ops: list[tuple[str, int]]
) -> None:
    store, ids = _store(tmp_path_factory.mktemp("j") / "r.sqlite", n=3)
    clock = Clock()
    q = _queue(store, clock, lease_s=25.0, max_attempts=2)  # most "advance" steps expire a lease
    b = _enqueue(q, ids)
    held: list[Job] = []
    for op, k in ops:
        if op == "claim" and (job := q.claim(f"w{k}")) is not None:
            held.append(job)
        elif op in ("complete", "fail_transient", "fail_bad", "crash") and held:
            job = held.pop(k % len(held))
            if op == "complete":
                q.complete(job, _writer(store)(job.record_id))
            elif op == "fail_transient":
                q.fail(job, "model_server_unavailable", retryable=True)
            elif op == "fail_bad":
                q.fail(job, "malformed_model_output", retryable=False)
            # "crash": the job is simply forgotten; its lease must expire
        elif op == "advance":
            clock.t += 20 * (k + 1)
        elif op == "recover":
            q.recover()
        elif op == "cancel":
            q.cancel(b)
        elif op == "resume":
            q.resume(b)
        check_invariants(store)
    # Whatever happened, finishing the work leaves no record in flight.
    q.resume(b)
    clock.t += 1000
    work(q, _writer(store), owner="final")
    check_invariants(store)
    assert all(store.status(i) in TERMINAL for i in ids)
