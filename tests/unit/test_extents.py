"""The reviewed-extent store (extents-1). SYNTHETIC gazetteer; every extent here is invented
test input for a synthetic feature, not a geographic fact."""

import csv
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row
from tests.unit.test_llm_extraction import RELEASE, FakeClient

from localitylens.cli import main
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.evaluation.audit import AuditItem, AuditSample, run_llm, run_rules, write_report
from localitylens.evaluation.hybrid import ReportMismatchError, combine_reports
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.extents import (
    EXTENT_COLUMNS,
    STORE_VERSION,
    ExtentStoreError,
    check_store,
    load_store,
    write_extent_worksheet,
)
from localitylens.geo.georeference import ExtentSource, ProposalOutcome
from localitylens.ingest.specimens import to_record

REVIEW = {"method": "measured on a map", "source": "synthetic map", "reviewer": "tester",
          "reviewed_on": "2026-11-03"}  # fmt: skip


@pytest.fixture
def index_path(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, EXTENT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _store(index: Path, tmp_path: Path, **filled: dict[str, str]) -> Path:
    """A worksheet for features 1 and 3, with the given rows (by GNIS ID) filled in."""
    path = tmp_path / "extents.csv"
    with Gazetteer(index) as gaz:
        write_extent_worksheet(path, [3, 1], gaz)
    rows = [r | filled.get(f"f{r['gnis_id']}", {}) for r in _rows(path)]
    _write(path, rows)
    return path


def test_worksheet_rows_copy_the_snapshot_and_start_pending(
    index_path: Path, tmp_path: Path
) -> None:
    path = _store(index_path, tmp_path)
    rows = _rows(path)
    assert [r["gnis_id"] for r in rows] == ["1", "3"]
    assert rows[1]["official_name"] == "Testa Lake"
    assert (rows[1]["feature_class"], rows[1]["county"], rows[1]["datum"]) == (
        "Reservoir", "Alpha", "NAD83")  # fmt: skip
    assert float(rows[1]["latitude"]) == 40.2
    assert all(r["extent_m"] == "" for r in rows)
    with Gazetteer(index_path) as gaz:
        check = check_store(path, gaz)
        assert (check.pending, check.entries, check.problems) == (2, {}, [])
        with pytest.raises(FileExistsError):
            write_extent_worksheet(path, [1], gaz)  # never overwrites
        with pytest.raises(ExtentStoreError, match="not in the GNIS snapshot"):
            write_extent_worksheet(tmp_path / "other.csv", [12345], gaz)


def test_a_reviewed_row_becomes_a_reviewed_extent(index_path: Path, tmp_path: Path) -> None:
    path = _store(index_path, tmp_path, f3=REVIEW | {"extent_m": "650", "note": "dam to inlet"})
    with Gazetteer(index_path) as gaz:
        store = load_store(path, gaz)
    assert (len(store.entries), store.pending) == (1, 1)
    estimate = store.get(3)
    assert estimate is not None
    assert (estimate.radius_m, estimate.source) == (650.0, ExtentSource.REVIEWED)
    assert "tester" in estimate.rationale
    assert "2026-11-03" in estimate.rationale
    assert "representative point" in estimate.rationale
    assert "dam to inlet" in estimate.rationale
    assert store.get(1) is None  # pending: no extent
    assert store.summary()["version"] == STORE_VERSION
    assert len(store.summary()["sha256"]) == 64


@pytest.mark.parametrize(("change", "column"), [
    ({"extent_m": "0"}, "extent_m"),
    ({"extent_m": "-5"}, "extent_m"),
    ({"extent_m": "nan"}, "extent_m"),
    ({"extent_m": "2 km"}, "extent_m"),
    ({"method": ""}, "method"),
    ({"reviewer": ""}, "reviewer"),
    ({"reviewed_on": "3/11/2026"}, "reviewed_on"),
    ({"official_name": "Testa Pond"}, "official_name"),
    ({"latitude": "40.25"}, "latitude"),
    ({"gazetteer_snapshot": "gnis-older"}, "gazetteer_snapshot"),
    ({"extent_m": ""}, "extent_m"),  # review fields without an extent
])  # fmt: skip
def test_a_bad_row_is_an_error_and_never_used(
    index_path: Path, tmp_path: Path, change: dict[str, str], column: str
) -> None:
    path = _store(index_path, tmp_path, f3=REVIEW | {"extent_m": "650"} | change)
    with Gazetteer(index_path) as gaz:
        check = check_store(path, gaz)
        assert 3 not in check.entries
        assert [p.column for p in check.problems] == [column]
        with pytest.raises(ExtentStoreError):
            load_store(path, gaz)


def test_unknown_duplicate_ids_and_a_wrong_header_are_errors(
    index_path: Path, tmp_path: Path
) -> None:
    path = _store(index_path, tmp_path)
    rows = _rows(path)
    _write(path, [*rows, rows[0], rows[0] | {"gnis_id": "12345"}])
    with Gazetteer(index_path) as gaz:
        messages = [p.message for p in check_store(path, gaz).problems]
        assert any("twice" in m for m in messages)
        assert any("not in the GNIS snapshot" in m for m in messages)
        path.write_text("gnis_id,extent\n3,650\n", encoding="utf-8")
        assert check_store(path, gaz).problems[0].column == "header"


def _sample() -> AuditSample:
    texts = ["Testa Lake.", "Testa Peak.", "Nowhere Hill."]
    items = tuple(AuditItem(audit_id=f"A{i:02d}", group_size=1,
                            record=to_record(row(i, t, county="Alpha")))
                  for i, t in enumerate(texts, start=1))  # fmt: skip
    return AuditSample(snapshot_id="gbif-synthetic", screen_version="1", grouping_version="1",
                       seed="seed", eligible_records=3, eligible_groups=3, items=items)  # fmt: skip


def test_runs_with_the_store_compute_proposals_and_say_where_extents_came_from(
    index_path: Path, tmp_path: Path
) -> None:
    path = _store(index_path, tmp_path, f3=REVIEW | {"extent_m": "650"})
    with Gazetteer(index_path) as gaz:
        store = load_store(path, gaz)
    plain = run_rules(_sample(), index_path)
    with_store = run_rules(_sample(), index_path, extents=store)

    assert "extent_store" not in plain
    assert "extent" not in plain["records"][0]
    assert with_store["extent_store"] == store.summary()
    lake, peak, nowhere = with_store["records"]
    assert (lake["proposal"], lake["extent"]) == (ProposalOutcome.COMPUTED.value, "reviewed")
    assert lake["radius_m"] is not None
    assert lake["radius_m"] >= 650
    assert lake["radius_lower_bound_m"] < 650  # the bound without extent is still reported
    assert (peak["proposal"], peak["extent"]) == ("needs_information", None)  # still pending
    assert nowhere["extent"] is None
    assert "reviewed-extent store" in with_store["note"]

    json_path, _ = write_report(with_store, tmp_path / "reports", "s")
    assert json_path.name == "s-rules-3-extents.json"  # never overwrites the plain run
    plain_path, _ = write_report(plain, tmp_path / "reports", "s")
    assert plain_path.name == "s-rules-3.json"


def test_hybrid_refuses_components_run_with_different_stores(
    index_path: Path, tmp_path: Path
) -> None:
    path = _store(index_path, tmp_path, f3=REVIEW | {"extent_m": "650"})
    with Gazetteer(index_path) as gaz:
        store = load_store(path, gaz)
    answers = ['{"relation": "named_feature", "relation_quote": "Testa Lake", '
               '"reference_feature": {"name_quote": "Testa Lake"}}'] * 3  # fmt: skip
    rules = run_rules(_sample(), index_path, extents=store)
    llm = run_llm(_sample(), index_path, FakeClient(*answers), RELEASE, extents=store)
    combined = combine_reports(rules, llm)
    assert combined["extent_store"] == store.summary()
    with pytest.raises(ReportMismatchError, match="extent_store"):
        combine_reports(rules, run_llm(_sample(), index_path, FakeClient(*answers), RELEASE))


def test_cli_check_and_propose_use_the_store(
    index_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(index_path, tmp_path, f3=REVIEW | {"extent_m": "650"})
    assert main(["extents", "check", "--store", str(path), "--index", str(index_path)]) == 0
    assert "1 reviewed, 1 pending, 0 problems" in capsys.readouterr().out

    run = ["baseline", "run", "Testa Lake.", "--index", str(index_path), "--propose", "--json"]
    assert main([*run, "--extents", str(path)]) == 0
    out = capsys.readouterr().out
    assert '"outcome": "computed"' in out
    assert "measured by tester" in out
    assert main(run) == 0
    assert '"outcome": "needs_information"' in capsys.readouterr().out

    rows = _rows(path)
    _write(path, [rows[0], rows[1] | {"latitude": "41.0"}])
    assert main(["extents", "check", "--store", str(path), "--index", str(index_path)]) == 2


def test_the_worksheet_command_never_reads_the_locked_test(
    index_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    locked = "eval/benchmark/test/test.json"
    cmd = ["extents", "worksheet", "--sample", locked, "--worksheet",
           "eval/benchmark/test/worksheet.csv", "--index", str(index_path),
           "--out", str(tmp_path / "x.csv")]  # fmt: skip
    assert main(cmd) == 2
    assert "locked test" in capsys.readouterr().err
    assert not (tmp_path / "x.csv").exists()
