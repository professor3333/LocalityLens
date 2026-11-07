"""Review store and Darwin Core export. SYNTHETIC gazetteer and records; the extent is
invented test input for a synthetic feature."""

import csv
import json
import math
from datetime import date
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.domain.status import RecordStatus
from localitylens.export.darwin_core import DWC_COLUMNS, export_approved, export_unresolved
from localitylens.export.geojson import GEOJSON_EXPORT_VERSION, export_geojson
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.extents import ExtentStore, ReviewedExtent
from localitylens.ingest.specimens import to_record
from localitylens.review.importer import import_records
from localitylens.review.store import Action, ReviewError, ReviewStore

TEXTS = {
    "lake": "Testa Lake.",  # reviewed extent → computed
    "peak": "2 mi NE of Testa Peak",  # extent unknown → needs information
    "route": "5 mi up the road from Testa Lake",  # unsupported
    "absent": "2 mi N of Nowhere Gulch",  # not in GNIS: which feature?
}
EXTENTS = ExtentStore(
    path=Path("extents.csv"), sha256="0" * 64, pending=0,
    entries={3: ReviewedExtent(feature_id=3, official_name="Testa Lake", extent_m=650.0,
                               method="measured", source="synthetic map", reviewer="tester",
                               reviewed_on=date(2026, 11, 4), note="")},
)  # fmt: skip


@pytest.fixture
def index_path(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


@pytest.fixture
def store(index_path: Path, tmp_path: Path) -> ReviewStore:
    s = ReviewStore(tmp_path / "review.sqlite")
    _import(s, index_path)
    return s


def _records() -> list:  # type: ignore[type-arg]
    return [to_record(row(i, t, county="Alpha")) for i, t in enumerate(TEXTS.values(), start=1)]


def _import(s: ReviewStore, index: Path) -> dict[str, int]:
    with Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        counts = import_records(s, _records(), "gbif-synthetic", gaz, system="rules",
                                rules=rules, llm=None, release="test", extents=EXTENTS)  # fmt: skip
        return dict(counts)


def _id(key: str) -> str:
    return f"gbif:{list(TEXTS).index(key) + 1}"


def test_import_sets_each_status_from_its_proposal(store: ReviewStore) -> None:
    assert store.status(_id("lake")) is RecordStatus.READY_FOR_REVIEW
    assert store.status(_id("peak")) is RecordStatus.NEEDS_INFORMATION
    assert store.status(_id("route")) is RecordStatus.UNSUPPORTED
    assert store.status(_id("absent")) is RecordStatus.NEEDS_INFORMATION


def test_reimport_changes_nothing(store: ReviewStore, index_path: Path) -> None:
    assert _import(store, index_path) == {}  # nothing queued any more
    assert store.record(_id("lake"))["locality"] == TEXTS["lake"]  # the original, unchanged


def test_approval_needs_a_full_region(store: ReviewStore) -> None:
    with pytest.raises(ReviewError, match="no full region"):
        store.decide(_id("peak"), Action.APPROVE, reviewer="r", rationale="looks right")
    with pytest.raises(ReviewError, match="needs a note"):
        store.decide(_id("peak"), Action.APPROVE, reviewer="r", rationale="x", extent_m=900)
    assert store.status(_id("peak")) is RecordStatus.NEEDS_INFORMATION


def test_a_retried_decision_is_stored_once(store: ReviewStore) -> None:
    first = store.decide(_id("lake"), Action.APPROVE, reviewer="r", rationale="as proposed")
    again = store.decide(_id("lake"), Action.APPROVE, reviewer="r", rationale="as proposed")
    assert (first.created, again.created) == (True, False)
    assert first.decision_id == again.decision_id
    assert len(store.decisions(_id("lake"))) == 1
    assert store.status(_id("lake")) is RecordStatus.APPROVED


def test_edit_then_approve_recomputes_and_records_the_diff(store: ReviewStore) -> None:
    d = store.decide(_id("peak"), Action.APPROVE, reviewer="r", rationale="summit is small",
                     feature_id=2, extent_m=900, extent_note="measured on a map")  # fmt: skip
    assert d.edits == {"feature_id": [1, 2], "extent_m": [None, 900]}
    final = store.proposal(d.final_proposal or "")
    assert final.origin == "curator_edit"
    assert final.proposal is not None
    assert final.proposal.feature_id == 2
    assert final.proposal.radius_m is not None
    assert final.proposal.radius_m > 900
    with pytest.raises(ReviewError, match="not among the retrieved candidates"):
        store.decide(_id("absent"), Action.APPROVE, reviewer="r", rationale="x", feature_id=3,
                     extent_m=5, extent_note="n")  # fmt: skip


def test_reject_research_and_illegal_moves(store: ReviewStore) -> None:
    with pytest.raises(ReviewError, match="cannot approve"):
        store.decide(_id("route"), Action.APPROVE, reviewer="r", rationale="x", extent_m=5,
                     extent_note="n")  # fmt: skip
    store.decide(_id("route"), Action.REJECT, reviewer="r", rationale="route, out of scope")
    assert store.status(_id("route")) is RecordStatus.REJECTED
    store.decide(_id("absent"), Action.RESEARCH, reviewer="r", rationale="find the hill")
    assert store.status(_id("absent")) is RecordStatus.NEEDS_INFORMATION


def test_decisions_survive_a_restart(store: ReviewStore, tmp_path: Path) -> None:
    store.decide(_id("lake"), Action.APPROVE, reviewer="r", rationale="ok")
    store.close()
    with ReviewStore(tmp_path / "review.sqlite") as reopened:
        assert reopened.status(_id("lake")) is RecordStatus.APPROVED
        assert [d.rationale for d in reopened.decisions(_id("lake"))] == ["ok"]


def test_export_writes_approved_records_only(store: ReviewStore, tmp_path: Path) -> None:
    store.decide(_id("lake"), Action.APPROVE, reviewer="Curator A", rationale="as proposed")
    store.decide(_id("lake"), Action.APPROVE, reviewer="Curator A", rationale="as proposed")
    store.decide(_id("peak"), Action.APPROVE, reviewer="Curator B", rationale="edited",
                 extent_m=900, extent_note="measured")  # fmt: skip
    store.decide(_id("absent"), Action.RESEARCH, reviewer="Curator A", rationale="find the hill")
    out = tmp_path / "dwc.csv"
    assert export_approved(store, out) == 2  # the retried approval adds no row
    with out.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        assert tuple(reader.fieldnames or ()) == DWC_COLUMNS
        rows = {r["gbifID"]: r for r in reader}
    lake, peak = rows["1"], rows["2"]
    assert lake["locality"] == TEXTS["lake"]
    assert lake["geodeticDatum"] == "EPSG:4269"
    assert lake["georeferenceVerificationStatus"] == "verified by data custodian"
    assert lake["georeferencedBy"] == "Curator A"
    radius = int(lake["coordinateUncertaintyInMeters"])
    assert radius >= 650  # the reviewed extent plus coordinate precision, rounded up
    assert radius == math.ceil(radius)
    assert "USGS GNIS feature 3" in lake["georeferenceSources"]
    assert lake["localitylens_human_edits"] == ""
    assert "curator set the extent to 900" in peak["georeferenceRemarks"]
    assert peak["localitylens_human_edits"] == '{"extent_m": [null, 900.0]}'

    unresolved = tmp_path / "unresolved.csv"
    assert export_unresolved(store, unresolved) == 2  # route (unsupported) and the absent hill
    with unresolved.open(encoding="utf-8", newline="") as fh:
        by_id = {r["gbifID"]: r for r in csv.DictReader(fh)}
    assert by_id["4"]["curator_note"] == "find the hill"
    assert by_id["3"]["status"] == "unsupported"
    assert by_id["3"]["blocking"]


def _no_nan(name: str) -> object:
    raise AssertionError(f"GeoJSON must not contain {name}")


def test_geojson_holds_the_same_approved_records_in_wgs84(
    store: ReviewStore, tmp_path: Path
) -> None:
    store.decide(_id("lake"), Action.APPROVE, reviewer="Curator A", rationale="as proposed")
    store.decide(_id("peak"), Action.APPROVE, reviewer="Curator B", rationale="edited",
                 extent_m=900, extent_note="measured")  # fmt: skip
    store.decide(_id("route"), Action.REJECT, reviewer="Curator A", rationale="route")
    out_csv, out_geo = tmp_path / "dwc.csv", tmp_path / "dwc.geojson"
    assert export_approved(store, out_csv) == 2
    assert export_geojson(store, out_geo) == 2
    with out_csv.open(encoding="utf-8", newline="") as fh:
        rows = {r["localitylens_decision_id"]: r for r in csv.DictReader(fh)}
    fc = json.loads(out_geo.read_text(encoding="utf-8"), parse_constant=_no_nan)

    assert fc["type"] == "FeatureCollection"
    assert "crs" not in fc  # RFC 7946 section 4: WGS 84 only, no crs member
    assert fc["localitylens"]["export_version"] == GEOJSON_EXPORT_VERSION
    assert {f["id"] for f in fc["features"]} == set(rows)  # approved records only, once each
    for f in fc["features"]:
        row, props = rows[f["id"]], f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Point"
        # EPSG:1188 is a null transformation: the numbers stay, the datum label changes
        assert (lat, lon) == (float(row["decimalLatitude"]), float(row["decimalLongitude"]))
        assert (props["decimalLatitude"], props["decimalLongitude"]) == (lat, lon)
        assert props["geodeticDatum"] == "EPSG:4326"
        assert props["localitylens_source_datum"] == row["geodeticDatum"] == "EPSG:4269"
        assert props["localitylens_datum_transform"] == "EPSG:1188"
        # the transformation's 4 m accuracy is added, so the circle never shrinks
        assert (
            props["coordinateUncertaintyInMeters"] == int(row["coordinateUncertaintyInMeters"]) + 4
        )
        assert props["georeferenceRemarks"].startswith(row["georeferenceRemarks"])
        assert "EPSG:1188" in props["georeferenceRemarks"]
        assert props["locality"] == row["locality"]  # the original string, unchanged
        assert props["footprintWKT"] is None
    peak = next(f["properties"] for f in fc["features"] if f["properties"]["gbifID"] == "2")
    assert peak["localitylens_human_edits"] == {"extent_m": [None, 900.0]}


def test_geojson_of_an_empty_store_is_an_empty_collection(
    store: ReviewStore, tmp_path: Path
) -> None:
    out = tmp_path / "none.geojson"
    assert export_geojson(store, out) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["features"] == []


def test_review_cli_end_to_end(
    index_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from localitylens.cli import main
    from localitylens.evaluation.audit import AuditItem, AuditSample

    items = tuple(AuditItem(audit_id=f"A{i:02d}", group_size=1, record=r)
                  for i, r in enumerate(_records(), start=1))  # fmt: skip
    sample = AuditSample(snapshot_id="gbif-synthetic", screen_version="1", grouping_version="1",
                         seed="s", eligible_records=4, eligible_groups=4, items=items)  # fmt: skip
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(sample.model_dump_json(), encoding="utf-8")
    db = str(tmp_path / "r.sqlite")
    common = ["--db", db]
    assert main(["review", "import", "--sample", str(sample_path), "--system", "rules",
                 "--index", str(index_path), *common]) == 0  # fmt: skip
    assert "needs_information  3" in capsys.readouterr().out
    assert main(["review", "decide", "gbif:2", "approve", "--reviewer", "r", "--rationale", "x",
                 *common]) == 2  # fmt: skip
    assert "no full region" in capsys.readouterr().err
    assert main(["review", "decide", "gbif:2", "approve", "--reviewer", "r", "--rationale", "x",
                 "--extent-m", "900", "--extent-note", "map", *common]) == 0  # fmt: skip
    out_csv, unres = tmp_path / "o.csv", tmp_path / "u.csv"
    assert main(["review", "export", "--out", str(out_csv), "--unresolved", str(unres),
                 *common]) == 0  # fmt: skip
    printed = capsys.readouterr().out
    assert "approved       1" in printed
    assert "geojson        1" in printed
    assert (tmp_path / "o.geojson").is_file()  # next to --out by default
