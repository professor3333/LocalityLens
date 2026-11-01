from collections import deque

import pytest

from localitylens.domain.status import (
    ALLOWED_TRANSITIONS,
    EXPORTABLE,
    PIPELINE_OUTCOMES,
    InvalidTransitionError,
    RecordStatus,
    transition,
)

S = RecordStatus


def test_every_status_has_a_transition_entry() -> None:
    assert set(ALLOWED_TRANSITIONS) == set(RecordStatus)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (S.QUEUED, S.PROCESSING),
        (S.PROCESSING, S.READY_FOR_REVIEW),
        (S.PROCESSING, S.QUEUED),
        (S.READY_FOR_REVIEW, S.APPROVED),
        (S.READY_FOR_REVIEW, S.NEEDS_INFORMATION),
        (S.FAILED, S.QUEUED),
    ],
)
def test_legal_transitions(current: RecordStatus, target: RecordStatus) -> None:
    assert transition(current, target) is target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (S.QUEUED, S.APPROVED),  # never approved without processing and review
        (S.PROCESSING, S.APPROVED),  # the pipeline cannot approve its own output
        (S.FAILED, S.APPROVED),
        (S.UNSUPPORTED, S.APPROVED),
        (S.APPROVED, S.REJECTED),
        (S.REJECTED, S.QUEUED),
    ],
)
def test_illegal_transitions_raise(current: RecordStatus, target: RecordStatus) -> None:
    with pytest.raises(InvalidTransitionError):
        transition(current, target)


def test_only_approved_is_exportable() -> None:
    assert {S.APPROVED} == EXPORTABLE


def test_approval_always_passes_through_a_pipeline_outcome() -> None:
    # Search every path from QUEUED to APPROVED that avoids pipeline outcomes: there must be none.
    seen = {S.QUEUED}
    frontier = deque([S.QUEUED])
    while frontier:
        node = frontier.popleft()
        for nxt in ALLOWED_TRANSITIONS[node]:
            if nxt in PIPELINE_OUTCOMES or nxt in seen:
                continue
            assert nxt is not S.APPROVED
            seen.add(nxt)
            frontier.append(nxt)


def test_every_status_reachable_from_queued() -> None:
    seen = {S.QUEUED}
    frontier = deque([S.QUEUED])
    while frontier:
        for nxt in ALLOWED_TRANSITIONS[frontier.popleft()]:
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    assert seen == set(RecordStatus)
