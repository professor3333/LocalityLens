"""Annotator agreement and the blind calibration copy. SYNTHETIC records and annotations."""

import csv
import json
from pathlib import Path

from tests.support.synthetic_dwca import row

from localitylens.cli import main
from localitylens.evaluation.agreement import agreement
from localitylens.evaluation.annotations import Annotation
from localitylens.evaluation.audit import AuditItem, AuditSample, load_sample
from localitylens.extract.schema import RelationType
from localitylens.ingest.specimens import to_record


def _ann(
    aid: str, ids: frozenset[int], distance: str = "", qualifiers: frozenset[str] = frozenset()
) -> Annotation:
    return Annotation(
        audit_id=aid,
        locality="x",
        description_type="named_feature",
        relation=RelationType.NAMED_FEATURE,
        supported=True,
        reference_features=("X",),
        acceptable_ids=ids,
        reference_absent=not ids,
        distance=distance,
        unit=None,
        direction=None,
        qualifiers=qualifiers,
        missing=frozenset(),
        unsure_columns=frozenset(),
        notes="",
    )


def test_agreement_counts_each_field_and_every_field() -> None:
    a = [_ann("C1", frozenset({1})), _ann("C2", frozenset()), _ann("C3", frozenset({3}), "2")]
    b = [_ann("V1", frozenset({1})), _ann("V2", frozenset({2})), _ann("V3", frozenset({3}), "2.0")]
    r = agreement(a, b, {"C1": "V1", "C2": "V2", "C3": "V3"})
    assert r.rows == 3
    assert r.by_field["acceptable_gnis_ids"] == 2  # absent vs an ID disagrees
    assert r.by_field["distance"] == 3  # "2" and "2.0" are the same distance
    assert r.by_field["category"] == 2
    assert r.every_field == 2
    assert r.categories_a == {"answerable": 2, "reference_absent": 1}


def test_the_calibration_copy_is_renumbered_blank_and_paired(tmp_path: Path) -> None:
    items = tuple(
        AuditItem(audit_id=f"V{i:02d}", group_size=1, record=to_record(row(i, f"Place {i}.")))
        for i in range(1, 6)
    )
    src = AuditSample(
        snapshot_id="s",
        screen_version="1",
        grouping_version="1",
        seed="x",
        eligible_records=5,
        eligible_groups=5,
        items=items,
        name="validation",
    )
    (tmp_path / "v.json").write_text(src.model_dump_json(), encoding="utf-8")
    out = tmp_path / "cal"
    argv = [
        "audit",
        "calibration-set",
        "--source",
        str(tmp_path / "v.json"),
        "--name",
        "cal",
        "--seed",
        "s/1",
        "--prefix",
        "C",
        "--out",
        str(out),
    ]
    assert main(argv) == 0
    cal = load_sample(out / "cal.json")
    pairs = json.loads((out / "pairs.json").read_text())["pairs"]
    assert [i.audit_id for i in cal.items] == ["C1", "C2", "C3", "C4", "C5"]
    assert sorted(pairs.values()) == [f"V{i:02d}" for i in range(1, 6)]
    by_id = {i.audit_id: i.record.gbif_id for i in items}
    assert all(c.record.gbif_id == by_id[pairs[c.audit_id]] for c in cal.items)  # same records
    with (out / "worksheet.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert all(not r["acceptable_gnis_ids"] for r in rows)  # blank: nothing to copy from
    assert main(argv) == 2  # written once


def test_the_calibration_copy_can_keep_only_listed_records(tmp_path: Path) -> None:
    items = tuple(
        AuditItem(audit_id=f"P{i:02d}", group_size=1, record=to_record(row(i, f"Place {i}.")))
        for i in range(1, 6)
    )
    src = AuditSample(
        snapshot_id="s",
        screen_version="1",
        grouping_version="1",
        seed="x",
        eligible_records=5,
        eligible_groups=5,
        items=items,
        name="test-x",
    )
    (tmp_path / "t.json").write_text(src.model_dump_json(), encoding="utf-8")
    (tmp_path / "ids.txt").write_text("P02\nP04\n\n", encoding="utf-8")
    base = ["audit", "calibration-set", "--source", str(tmp_path / "t.json"), "--name", "rev",
            "--seed", "r/1", "--prefix", "R"]  # fmt: skip
    assert main([*base, "--out", str(tmp_path / "rev"), "--ids", str(tmp_path / "ids.txt")]) == 0
    pairs = json.loads((tmp_path / "rev" / "pairs.json").read_text())["pairs"]
    assert sorted(pairs.values()) == ["P02", "P04"]
    assert len(load_sample(tmp_path / "rev" / "rev.json").items) == 2
    (tmp_path / "bad.txt").write_text("P09\n", encoding="utf-8")
    assert main([*base, "--out", str(tmp_path / "bad"), "--ids", str(tmp_path / "bad.txt")]) == 2
