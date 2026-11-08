"""Audit sampling, worksheet and the rules run, on SYNTHETIC records and gazetteer."""

import csv
import json
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row, write_snapshot

from localitylens.cli import main
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.evaluation.audit import (
    WORKSHEET_COLUMNS,
    AuditSample,
    annotations_by,
    load_sample,
    run_rules,
    sample_groups,
    write_report,
    write_sample,
)
from localitylens.gazetteer.index import build_index
from localitylens.ingest.specimens import to_record

RECORDS = [
    to_record(row(i, text, county=county))
    for i, text, county in [
        (30, "Testa Peak.", "Alpha"),
        (10, "TESTA PEAK", "Alpha"),  # same group as 30, lower id
        (20, "2 mi NE of Testa Lake.", "Alpha"),
        (40, "Testa Peak.", "Beta"),
        (50, "1.9 miles up Testa Road.", "Alpha"),
        (60, "Nowhere Hill.", "Gamma"),
    ]
]


def test_sample_takes_one_representative_per_group() -> None:
    items, total, groups = sample_groups(RECORDS, 10, "seed")
    assert (total, groups, len(items)) == (6, 5, 5)
    by_text = {i.record.locality: i for i in items}
    assert by_text["TESTA PEAK"].record.gbif_id == "10"  # lowest gbifID represents the group
    assert by_text["TESTA PEAK"].group_size == 2
    assert [i.audit_id for i in items] == ["A01", "A02", "A03", "A04", "A05"]


def test_sample_is_reproducible_and_seeded() -> None:
    first = [i.record.gbif_id for i in sample_groups(RECORDS, 3, "seed")[0]]
    again = [i.record.gbif_id for i in sample_groups(list(reversed(RECORDS)), 3, "seed")[0]]
    assert first == again  # input order does not matter
    orders = {tuple(i.record.gbif_id for i in sample_groups(RECORDS, 5, s)[0]) for s in "abcdef"}
    assert len(orders) > 1  # the seed changes the order


def _sample(n: int = 10) -> AuditSample:
    items, total, groups = sample_groups(RECORDS, n, "seed")
    return AuditSample(
        snapshot_id="gbif-synthetic", screen_version="1", grouping_version="1", seed="seed",
        eligible_records=total, eligible_groups=groups, items=tuple(items),
    )  # fmt: skip


def test_worksheet_has_text_but_no_system_output(tmp_path: Path) -> None:
    sample_path, worksheet, written = write_sample(_sample(), tmp_path)
    assert written
    assert load_sample(sample_path) == _sample()
    with worksheet.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    assert tuple(rows[0]) == WORKSHEET_COLUMNS
    assert all(len(r) == 4 for r in rows[1:])  # id, gbif id, county, text; the rest is blank
    assert "decimalLatitude" not in sample_path.read_text()
    assert "40.123456" not in sample_path.read_text()


@pytest.fixture
def index_path(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def test_rules_report_covers_every_record(index_path: Path, tmp_path: Path) -> None:
    report = run_rules(_sample(), index_path)
    assert len(report["records"]) == 5
    assert sum(report["counts"]["relation"].values()) == 5
    by_text = {r["locality"]: r for r in report["records"]}
    assert by_text["2 mi NE of Testa Lake."]["relation"] == "distance_and_direction"
    assert by_text["2 mi NE of Testa Lake."]["top_candidate"]["county"] == "Alpha"
    assert by_text["1.9 miles up Testa Road."]["proposal"] == "unsupported"
    # A bare name the gazetteer does not know is not detected as a place by the rules.
    assert by_text["Nowhere Hill."]["retrieval"] == "no_reference_feature"
    json_path, md_path = write_report(report, tmp_path)
    assert json.loads(json_path.read_text())["specimen_snapshot"] == "gbif-synthetic"
    assert md_path.name == "audit-50-rules-6.md"
    assert md_path.read_text().count("\n| A") == 5


def test_audit_cli_end_to_end(
    index_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rows = [row(1, "Testa Peak."), row(2, "Elsewhere.", stateProvince="Utah")]
    write_snapshot(tmp_path / "snap", rows)
    assert main(["ingest", "scan", "--snapshot", str(tmp_path / "snap")]) == 0
    out = capsys.readouterr().out
    assert "eligible" in out
    assert "outside_colorado" in out
    audit_dir, reports = tmp_path / "audit", tmp_path / "reports"
    snap = str(tmp_path / "snap")
    assert main(["audit", "sample", "--snapshot", snap, "--out", str(audit_dir)]) == 0
    assert "1 of 1 locality groups" in capsys.readouterr().out
    assert main(["audit", "rules", "--sample", str(audit_dir / "audit-50.json"),
                 "--index", str(index_path), "--out", str(reports)]) == 0  # fmt: skip
    assert (reports / "audit-50-rules-6.json").is_file()


def test_llm_audit_records_failures_and_continues(index_path: Path) -> None:
    from tests.unit.test_llm_extraction import RELEASE, FakeClient

    from localitylens.evaluation.audit import run_llm

    sample = _sample(2)
    good = json.dumps({"relation": "no_locality"})
    client = FakeClient("{bad", "{bad", good)  # record 1 fails twice; record 2 succeeds
    report = run_llm(sample, index_path, client, RELEASE)
    first, second = report["records"]
    assert first["proposal"] == "failed:malformed_model_output"
    assert first["trace"]["attempts"] == 2
    assert second["relation"] == "no_locality"
    assert report["system"] == "llm"
    assert report["prompt"].startswith(f"{RELEASE.prompt.version} sha256=")
    assert "locality" not in json.dumps(first["trace"])  # traces hold hashes and counts only


def test_an_existing_worksheet_is_never_overwritten(tmp_path: Path) -> None:
    _, worksheet, _ = write_sample(_sample(), tmp_path)
    worksheet.write_text("annotated by hand\n", encoding="utf-8")
    _, _, written = write_sample(_sample(), tmp_path)  # identical sample: allowed
    assert not written
    assert worksheet.read_text(encoding="utf-8") == "annotated by hand\n"


def test_a_different_sample_never_replaces_an_existing_one(tmp_path: Path) -> None:
    from localitylens.evaluation.audit import SampleExistsError

    write_sample(_sample(), tmp_path)
    with pytest.raises(SampleExistsError):
        write_sample(_sample(2), tmp_path)


def test_reports_name_who_annotated_each_sample() -> None:
    assert annotations_by("dev-2") == "Claude's annotations"
    assert annotations_by("dev-3") == "Claude's annotations"
    assert annotations_by("dev-4") == "Claude's annotations"
    for label in ("test-2", "test-2-new", "test-2-repeats"):
        assert annotations_by(label) == "Claude's annotations"
    for label in ("audit-50", "dev-1", "validation", "test"):
        assert annotations_by(label) == "the owner's annotations"
