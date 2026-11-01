"""Core-key matching: generic words, positional prefixes, descriptors (SYNTHETIC gazetteer)."""

from pathlib import Path

import pytest

from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.extract.schema import FeatureType
from localitylens.gazetteer.index import Gazetteer, MatchKind, build_index
from localitylens.gazetteer.keys import core_compatible, core_key, name_key


@pytest.mark.parametrize(
    ("name", "core"),
    [("Mt. Zenobia", "zenobia"), ("Zenobia Peak", "zenobia"), ("Longs Peak summit", "longs"),
     ("Lower Piney Lake", "piney lake"), ("Gunnison Canon", "gunnison canyon"),
     ("Rainbow Lakes", "rainbow lake"), ("North Cheyenne Canon", "north cheyenne canyon"),
     ("Lower Lake", None), ("Mount", None), ("Peak", None), ("Upper Creek", None)],
)  # fmt: skip
def test_core_key(name: str, core: str | None) -> None:
    assert core_key(name_key(name)) == core


def test_contradictory_positions_are_not_compatible() -> None:
    assert not core_compatible(name_key("Lower Piney Lake"), name_key("Upper Piney Lake"))
    assert core_compatible(name_key("Lower Piney Lake"), name_key("Piney Lake"))
    assert core_compatible(name_key("Piney Lake"), name_key("Upper Piney Lake"))


@pytest.fixture
def gaz(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Gazetteer:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    build_index(directory, manifest, tmp_path / "g.sqlite")
    return Gazetteer(tmp_path / "g.sqlite")


def test_generic_word_swap_is_found_as_a_core_match(gaz: Gazetteer) -> None:
    top = gaz.search("Mt. Testa", county="Alpha", feature_type=FeatureType.SUMMIT)[0]
    assert top.official_name == "Testa Peak"
    assert top.county_name == "Alpha"
    assert top.match_kind is MatchKind.CORE_OFFICIAL


def test_trailing_descriptor_is_set_aside(gaz: Gazetteer) -> None:
    assert gaz.search("Testa Peak summit", county="Beta")[0].feature_id == 2


def test_exact_matches_always_outrank_core_matches(gaz: Gazetteer) -> None:
    results = gaz.search("Vela Lake")
    assert results[0].official_name == "Vela Lake"
    assert results[0].match_kind is MatchKind.EXACT_OFFICIAL
    upper = next(c for c in results if c.official_name == "Upper Vela Lake")
    assert upper.match_kind is MatchKind.CORE_OFFICIAL  # a compatible, lower-ranked candidate


def test_a_contradictory_position_is_never_offered(gaz: Gazetteer) -> None:
    names = [c.official_name for c in gaz.search("Lower Vela Lake")]
    assert names[0] == "Vela Lake"
    assert "Upper Vela Lake" not in names


def test_a_name_absent_in_every_form_stays_absent(gaz: Gazetteer) -> None:
    assert gaz.search("Quorn Butte") == []
