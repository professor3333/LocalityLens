"""Held-out split drawing (SYNTHETIC records). Never reads eval/benchmark/test."""

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


def test_an_extra_split_excludes_viewed_reserved_repeated_wording_and_their_trips() -> None:
    from localitylens.evaluation.audit import AuditItem
    from localitylens.evaluation.benchmark import EXTRA_VERSION, draw_extra, wording_matches

    records = [
        *RECORDS,
        to_record(row(9, "Alpha Peak.", county="Other")),  # same wording as group 1, other county
        rec(10, "Theta Butte.", "D. Kim", "1980-05-05"),
        rec(11, "Iota Gulch.", "D. Kim", "1980-05-05"),  # same trip as 10
    ]
    key = {r.gbif_id: r.group_key for r in records}
    viewed = {key["1"], key["10"]}  # viewed: Alpha Peak (Alpha county) and Theta Butte
    assert wording_matches(records, viewed) == {key["1"], key["9"], key["10"]}
    old = AuditItem(audit_id="V001", group_size=1, record=rec(99, "Kappa Ridge."))
    items, mapping, lock = draw_extra(records, name="t2", size=3, seed="s", prefix="H",
                                      exclude=viewed, repeats=[old])  # fmt: skip
    chosen = {i.record.gbif_id for i in items}
    # 1, 2 (same trip as 1), 9 (same words as 1), 10 and 11 (same trip as 10) are never drawn
    assert chosen.isdisjoint({"1", "2", "9", "10", "11"})
    assert len(items) == 4
    assert [i.audit_id for i in items] == ["H001", "H002", "H003", "H004"]
    assert list(mapping.values()) == ["V001"]
    assert next(i for i in items if i.audit_id in mapping).record.gbif_id == "99"
    assert old.record.group_key not in lock["splits"]["t2"]  # the lock lists new groups only
    assert len(lock["splits"]["t2"]) == 3
    assert lock["extra_version"] == EXTRA_VERSION
    assert lock["excluded_wording_groups"] == 1
    again = draw_extra(records, name="t2", size=3, seed="s", prefix="H", exclude=viewed,
                       repeats=[old])  # fmt: skip
    assert again[0] == items  # deterministic


def test_split_repeats_separates_new_rows_from_blind_repeats(tmp_path: Path) -> None:
    import csv

    from localitylens.evaluation.audit import AuditItem, AuditSample, load_sample, write_sample
    from localitylens.evaluation.benchmark import split_repeats

    items = tuple(AuditItem(audit_id=f"H00{i}", group_size=1, record=rec(i, f"Place {i}."))
                  for i in (1, 2, 3))  # fmt: skip
    sample = AuditSample(snapshot_id="s", screen_version="1", grouping_version="1", seed="x",
                         eligible_records=3, eligible_groups=3, items=items, name="t2")  # fmt: skip
    folder = tmp_path / "t2"
    write_sample(sample, folder, "t2")
    (folder / "repeats.json").write_text(json.dumps({"repeats": {"H002": "V009"}}))
    assert split_repeats(folder / "t2.json", folder / "worksheet.csv", folder / "repeats.json",
                         folder / "scoring") == (2, 1)  # fmt: skip
    new = load_sample(folder / "scoring" / "t2-new.json")
    assert [i.audit_id for i in new.items] == ["H001", "H003"]
    with (folder / "scoring" / "worksheet-new.csv").open(encoding="utf-8") as fh:
        assert [r["audit_id"] for r in csv.DictReader(fh)] == ["H001", "H003"]
    with (folder / "scoring" / "repeats-annotated.csv").open(encoding="utf-8") as fh:
        assert [(r["original_id"], r["audit_id"]) for r in csv.DictReader(fh)] == [("V009", "H002")]
    with pytest.raises(FileExistsError):
        split_repeats(folder / "t2.json", folder / "worksheet.csv", folder / "repeats.json",
                      folder / "scoring")  # fmt: skip


def test_an_extra_split_can_be_limited_to_one_kind_of_label() -> None:
    from localitylens.evaluation.benchmark import draw_extra

    items, _, lock = draw_extra(
        RECORDS,
        name="t3",
        size=2,
        seed="s",
        prefix="P",
        exclude=set(),
        eligible=lambda r: "Peak" in r.locality or "Lake" in r.locality,
    )
    assert {i.record.gbif_id for i in items} <= {"1", "2", "3"}
    assert len(lock["splits"]["t3"]) == 2
