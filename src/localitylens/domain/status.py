"""Record lifecycle: the only place where status transitions are decided.

    queued -> processing -> ready_for_review | needs_information | unsupported | failed
                         -> (curator) approved | rejected

Every status change in the application must go through :func:`transition` so that an
illegal move (for example exporting a record that was never reviewed) fails loudly.
"""

from __future__ import annotations

from enum import StrEnum


class RecordStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY_FOR_REVIEW = "ready_for_review"
    NEEDS_INFORMATION = "needs_information"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


class InvalidTransitionError(ValueError):
    """Raised when a status change is not allowed by the lifecycle."""

    def __init__(self, current: RecordStatus, target: RecordStatus) -> None:
        super().__init__(f"illegal status transition {current.value} -> {target.value}")
        self.current = current
        self.target = target


_S = RecordStatus

ALLOWED_TRANSITIONS: dict[RecordStatus, frozenset[RecordStatus]] = {
    _S.QUEUED: frozenset({_S.PROCESSING}),
    # QUEUED again covers lease expiry / bounded retry / cancellation of in-flight work.
    _S.PROCESSING: frozenset(
        {_S.READY_FOR_REVIEW, _S.NEEDS_INFORMATION, _S.UNSUPPORTED, _S.FAILED, _S.QUEUED}
    ),
    # NEEDS_INFORMATION here is the curator's "request further research" decision.
    _S.READY_FOR_REVIEW: frozenset({_S.APPROVED, _S.REJECTED, _S.NEEDS_INFORMATION}),
    # Once the blocking question is answered the record is reprocessed, or the curator
    # resolves it directly (approve with edits) or rejects it.
    _S.NEEDS_INFORMATION: frozenset({_S.QUEUED, _S.APPROVED, _S.REJECTED}),
    _S.UNSUPPORTED: frozenset({_S.NEEDS_INFORMATION, _S.REJECTED}),
    _S.FAILED: frozenset({_S.QUEUED}),
    _S.APPROVED: frozenset(),
    _S.REJECTED: frozenset(),
}

PIPELINE_OUTCOMES: frozenset[RecordStatus] = frozenset(
    {_S.READY_FOR_REVIEW, _S.NEEDS_INFORMATION, _S.UNSUPPORTED, _S.FAILED}
)
CURATOR_DECISIONS: frozenset[RecordStatus] = frozenset({_S.APPROVED, _S.REJECTED})
EXPORTABLE: frozenset[RecordStatus] = frozenset({_S.APPROVED})


def can_transition(current: RecordStatus, target: RecordStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def transition(current: RecordStatus, target: RecordStatus) -> RecordStatus:
    """Return ``target`` if the move is legal, otherwise raise :class:`InvalidTransitionError`."""
    if not can_transition(current, target):
        raise InvalidTransitionError(current, target)
    return target
