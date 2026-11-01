import sqlite3
import zipfile
from pathlib import Path

import pytest

from localitylens.data.manifest import ChecksumMismatchError, SnapshotManifest
from localitylens.extract.schema import FeatureType
from localitylens.gazetteer.gnis import GnisFormatError, read_domestic, read_variants
from localitylens.gazetteer.index import Gazetteer, MatchKind, build_index
from localitylens.gazetteer.keys import county_key, name_key
from localitylens.geo.geodesy import Datum

Snapshot = tuple[Path, SnapshotManifest]


@pytest.fixture
def gaz(gnis_snapshot: Snapshot, tmp_path: Path) -> Gazetteer:
    directory, manifest = gnis_snapshot
    out = tmp_path / "gazetteer.sqlite"
    build_index(directory, manifest, out)
    return Gazetteer(out)


# ------------------------------------------------------------------------------------- keys


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("Long's Pk.", "Longs Peak"),
        ("Long\u2019s Peak", "Longs Peak"),
        ("Mt. Evans", "Mount Evans"),
        ("Bear Cr", "Bear Creek"),
        ("Café Spgs", "Cafe Springs"),
        ("Old Camp (historical)", "Old Camp"),
        ("  BEAR   LAKE ", "bear lake"),
    ],
)
def test_name_keys_match_label_variants(a: str, b: str) -> None:
    assert name_key(a) == name_key(b)


def test_single_letter_abbreviations_are_not_expanded() -> None:
    assert name_key("L. Granby") == "l granby"


@pytest.mark.parametrize("text", ["Larimer Co.", "Larimer County", "larimer", "LARIMER CO"])
def test_county_key(text: str) -> None:
    assert county_key(text) == "larimer"


# ---------------------------------------------------------------------------------- parsing


def test_domestic_parsing_handles_bom_crlf_and_null_source_coordinates(
    gnis_snapshot: Snapshot,
) -> None:
    directory, _ = gnis_snapshot
    features = {f.feature_id: f for f in read_domestic(directory / "DomesticNames_CO_Text.zip")}
    assert features[1].name == "Testa Peak"  # no BOM leaked into the first field
    assert features[1].source_lat is None  # 0.0 means "missing", never a real position
    assert features[4].source_lat is None  # blank also means missing
    assert features[5].source_lat == pytest.approx(38.7)
    assert features[4].historical is True
    assert features[5].state_name == "Utah"


def test_variant_parsing_keeps_only_variants_of_wanted_features(gnis_snapshot: Snapshot) -> None:
    directory, _ = gnis_snapshot
    variants = list(read_variants(directory / "AllNames_National_Text.zip", {6}))
    assert {v.name for v in variants} == {"Oldname Peak", "Newname  Mountain"}
    oldname = next(v for v in variants if v.name == "Oldname Peak")
    assert oldname.source_date == "12/31/1890"


def test_unexpected_header_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("Text/x.txt", "feature_id|name\r\n1|X\r\n")
    with pytest.raises(GnisFormatError, match="header"):
        list(read_domestic(path))


# ----------------------------------------------------------------------------------- build


def test_build_refuses_tampered_snapshot(gnis_snapshot: Snapshot, tmp_path: Path) -> None:
    directory, manifest = gnis_snapshot
    with (directory / "DomesticNames_CO_Text.zip").open("ab") as fh:
        fh.write(b"tamper")
    with pytest.raises(ChecksumMismatchError):
        build_index(directory, manifest, tmp_path / "g.sqlite")
    assert not (tmp_path / "g.sqlite").exists()


def test_build_is_deterministic_and_records_provenance(
    gnis_snapshot: Snapshot, tmp_path: Path
) -> None:
    directory, manifest = gnis_snapshot
    dumps = []
    for name in ("a.sqlite", "b.sqlite"):
        build_index(directory, manifest, tmp_path / name)
        con = sqlite3.connect(tmp_path / name)
        dumps.append(list(con.iterdump()))
        meta = dict(con.execute("SELECT key, value FROM meta"))
        con.close()
    assert dumps[0] == dumps[1]
    assert meta["snapshot_id"] == "gnis-synthetic"
    assert meta["manifest_sha256"] == manifest.sha256()


def test_variant_identical_to_official_is_not_duplicated(gaz: Gazetteer) -> None:
    rows = gaz._con.execute("SELECT kind FROM name WHERE feature_id = 6").fetchall()
    assert sorted(r[0] for r in rows) == ["official", "variant"]


# ---------------------------------------------------------------------------------- search


def test_exact_match_returns_evidence(gaz: Gazetteer) -> None:
    results = gaz.search("Testa Peak")
    assert [c.feature_id for c in results[:2]] == [1, 2]
    top = results[0]
    assert top.match_kind is MatchKind.EXACT_OFFICIAL
    assert top.primary_point.datum is Datum.NAD83
    assert top.source_point is None
    assert top.feature_type is FeatureType.SUMMIT


def test_county_ranks_but_never_filters(gaz: Gazetteer) -> None:
    results = gaz.search("Testa Peak", county="Beta Co.")
    assert results[0].feature_id == 2
    assert results[0].county_match is True
    other = next(c for c in results if c.feature_id == 1)
    assert other.county_match is False  # still offered as an alternative


def test_type_compatibility_lake_matches_reservoir(gaz: Gazetteer) -> None:
    (top, *_) = gaz.search("Testa Lake", feature_type=FeatureType.LAKE)
    assert top.feature_id == 3
    assert top.type_match is True


def test_abbreviated_label_name_is_found(gaz: Gazetteer) -> None:
    assert gaz.search("Testa Pk.")[0].match_kind is MatchKind.EXACT_OFFICIAL


def test_misspelling_found_by_fuzzy_match(gaz: Gazetteer) -> None:
    results = gaz.search("Tesla Peak")
    assert results
    assert results[0].match_kind is MatchKind.FUZZY_OFFICIAL
    assert results[0].official_name == "Testa Peak"
    assert results[0].name_similarity < 100


def test_unknown_name_is_absent_not_guessed(gaz: Gazetteer) -> None:
    assert gaz.search("Nowhere Gulch") == []
    assert gaz.search("   ") == []


def test_former_name_competes_equally_with_current_official_name(gaz: Gazetteer) -> None:
    # Feature 7 is officially "Oldname Peak"; feature 6 used to be called that (variant).
    no_context = gaz.search("Oldname Peak")
    assert {c.feature_id for c in no_context} >= {6, 7}
    assert no_context[0].feature_id == 7  # official wins only as the final tie-breaker

    with_context = gaz.search("Oldname Peak", county="Gamma")
    assert with_context[0].feature_id == 6
    assert with_context[0].match_kind is MatchKind.EXACT_VARIANT
    assert with_context[0].official_name == "Newname Mountain"
    assert with_context[0].variant_source_date == "12/31/1890"
    assert with_context[0].variant_citation == "Synthetic survey map 1890"


def test_historical_feature_found_without_suffix(gaz: Gazetteer) -> None:
    (top, *_) = gaz.search("Old Camp")
    assert top.feature_id == 4
    assert top.historical is True


def test_out_of_state_feature_is_flagged(gaz: Gazetteer) -> None:
    (top,) = gaz.search("Border Wash")
    assert top.state_match is False
    assert top.source_point is not None


def test_limit_is_respected(gaz: Gazetteer) -> None:
    assert len(gaz.search("Testa Peak", limit=1)) == 1
    assert gaz.search("Testa Peak", limit=0) == []


def test_missing_index_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Gazetteer(tmp_path / "nope.sqlite")
