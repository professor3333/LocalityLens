"""The worker loop: lease a job, run the pipeline on its record, write the result or fail it.

Failure categories:

* ``model_server_unavailable`` is transient: the job goes back to ``queued`` and is retried,
  up to the queue's ``max_attempts``.
* Other model failures are deterministic under greedy decoding (malformed output after the
  extractor's own retry, model-supplied coordinates, context budget, delimiter in the input):
  retrying would repeat them, so the record ends ``failed`` with that category at once.
* Anything unexpected is ``internal_error``: retried like a transient failure, then ``failed``.
  It is logged with the job ID and exception type only, never label text.
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Callable
from typing import Final

from localitylens.extract.llm_client import FailureCategory, ModelCallError
from localitylens.jobs.queue import JobQueue

log = logging.getLogger(__name__)

TRANSIENT: Final = frozenset({FailureCategory.MODEL_SERVER_UNAVAILABLE})
INTERNAL_ERROR: Final = "internal_error"

# process(record_id) runs the pipeline and returns a writer that stores its result and returns
# the proposal ID. A writer may carry ``trace_fields`` (timings, counts, model use) for the
# attempt's trace. Raising ModelCallError (or anything else) fails the attempt.
Process = Callable[[str], Callable[[], str | None]]


def work(
    queue: JobQueue,
    process: Process,
    *,
    owner: str,
    batch_id: str | None = None,
    max_jobs: int | None = None,
    should_stop: Callable[[], bool] = lambda: False,
) -> Counter[str]:
    """Process jobs until none is pending (or ``max_jobs``, or ``should_stop``). Returns counts:
    ``done``, ``retried``, ``failed`` and ``lost`` (a lease that expired while working)."""
    counts: Counter[str] = Counter()
    claimed = 0
    while not should_stop() and (max_jobs is None or claimed < max_jobs):
        job = queue.claim(owner, batch_id)
        if job is None:
            break
        claimed += 1
        try:
            write = process(job.record_id)
        except ModelCallError as exc:
            retry = exc.category in TRANSIENT
            _count(counts, queue.fail(job, exc.category.value, retryable=retry), job.attempts,
                   queue.max_attempts, retry)  # fmt: skip
            continue
        except Exception as exc:  # categorized below: never swallowed, never a silent drop
            log.error("job %s attempt %d: %s", job.job_id, job.attempts, type(exc).__name__)
            _count(counts, queue.fail(job, INTERNAL_ERROR, retryable=True), job.attempts,
                   queue.max_attempts, True)  # fmt: skip
            continue
        fields = getattr(write, "trace_fields", None)
        counts["done" if queue.complete(job, write, fields) else "lost"] += 1
    return counts


def _count(counts: Counter[str], held: bool, attempts: int, max_attempts: int, retry: bool) -> None:
    if not held:
        counts["lost"] += 1
    elif retry and attempts < max_attempts:
        counts["retried"] += 1
    else:
        counts["failed"] += 1
