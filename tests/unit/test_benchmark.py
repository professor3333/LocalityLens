"""Held-out split drawing (SYNTHETIC records). Never reads eval/benchmark/test (CLAUDE.md §7)."""

import json
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row

from localitylens.evaluation.benchmark import (
    DEFAULT_LOCK,
    LockExistsError,
    draw_splits,
    event_key,
    leakage_components,
    load_lock,
    write_lock,
)
from localitylens.evaluation.dev_sample import load_registry
from localitylens.ingest.specimens import SpecimenRecord, to_record


def rec(i: int, text: str, who: str = "", date: str = "") -> SpecimenRecord:
    return to_record(row(i, text, recordedBy=who, eventDate=date))


def test_event_key_needs_a_collector_and_an_exact_day() -> None:
    assert event_key(rec(1, "x", "A. Smith", "1950-07-04")) == ("a. smith", "1950-07-04")
    assert event_key(rec(1, "x", "A.  SMITH", "1950-07-04T00:00:00")) == ("a. smith", "1950-07-04")
    assert event_key(rec(1, "x", "A. Smith", "1950-07")) is None
    assert event_key(rec(1, "x", "A. Smith", "1950-07-01/1950-07-31")) is None
    assert event_key(rec(1, "x", "", "1950-07-04")) is None


RECORDS = [
    rec(1, "Alpha Peak.", "A. Smith", "1950-07-04"),
    rec(2, "Alpha Peak, summit.", "A. Smith", "1950-07-04"),  # same trip, other wording
    rec(3, "Beta Lake.", "B. Jones", "1960-01-01"),
    rec(4, "Gamma Creek.", "C. Lee", "1970-01-01"),
    rec(5, "Delta Hill.", "C. Lee", "1970-01-01"),
    rec(6, "Epsilon Draw."),
    rec(7, "Zeta Flat."),
    rec(8, "Eta Mesa."),
]


def test_shared_collecting_events_join_groups() -> None:
    _, _, component = leakage_components(RECORDS)
    g = [r.group_key for r in RECORDS]
    assert component[g[0]] == component[g[1]]
    assert component[g[3]] == component[g[4]]
    assert component[g[0]] != component[g[2]]
    assert len(set(component.values())) == 6


def test_splits_are_independent_and_avoid_viewed_components() -> None:
    g = [r.group_key for r in RECORDS]
    viewed = {g[1]}  # taints the whole A. Smith component, including g[0]
    splits, lock = draw_splits(RECORDS, {"test": 2, "validation": 2}, "s", viewed,
                               {"test": "T", "validation": "V"})  # fmt: skip
    chosen = [i.record.group_key for items in splits.values() for i in items]
    assert len(chosen) == len(set(chosen)) == 4
    assert g[0] not in chosen
    assert g[1] not in chosen
    _, _, component = leakage_components(RECORDS)
    assert len({component[k] for k in chosen}) == 4  # one group per component
    assert set(chosen) <= set(lock["reserved_groups"])
    if g[3] in chosen or g[4] in chosen:  # a chosen group reserves its whole component
        assert {g[3], g[4]} <= set(lock["reserved_groups"])
    assert lock["excluded_viewed_components"] == 1
    assert [i.audit_id for i in splits["test"]] == ["T001", "T002"]


def test_too_few_components_is_refused() -> None:
    with pytest.raises(ValueError, match="independent components"):
        draw_splits(RECORDS, {"test": 7}, "s", set(), {"test": "T"})


def test_lock_is_write_once_and_tamper_evident(tmp_path: Path) -> None:
    _, lock = draw_splits(RECORDS, {"test": 2}, "s", set(), {"test": "T"})
    path = tmp_path / "splits.lock.json"
    write_lock(path, lock)
    write_lock(path, lock)  # identical regeneration is allowed
    with pytest.raises(LockExistsError):
        write_lock(path, {**lock, "seed": "other"})
    data = json.loads(path.read_text())
    data["splits"]["test"] = data["splits"]["test"][:1]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="digest"):
        load_lock(path)


@pytest.mark.skipif(not DEFAULT_LOCK.exists(), reason="no committed split lock yet")
def test_committed_lock_is_intact_and_disjoint_from_development() -> None:
    lock = load_lock()
    assert lock is not None
    viewed = set(load_registry())
    reserved = set(lock["reserved_groups"])
    held_out = [set(keys) for keys in lock["splits"].values()]
    assert not reserved & viewed
    assert all(keys <= reserved for keys in held_out)
    assert not held_out[0] & held_out[1]
