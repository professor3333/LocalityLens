import json
from pathlib import Path

import pytest

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.cli import main
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.pipeline.interpret import interpret
from localitylens.resolve.retrieve import ContextSource, RetrievalOutcome

Snapshot = tuple[Path, SnapshotManifest]


@pytest.fixture
def index_path(gnis_snapshot: Snapshot, tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


@pytest.fixture
def gaz(index_path: Path) -> Gazetteer:
    return Gazetteer(index_path)


@pytest.fixture
def rules(gaz: Gazetteer) -> RulesExtractor:
    return RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))


def test_text_county_ranks_candidates(gaz: Gazetteer, rules: RulesExtractor) -> None:
    result = interpret("Beta Co., 2 mi NE of Testa Peak summit", rules, gaz)
    assert result.retrieval is not None
    assert result.retrieval.outcome is RetrievalOutcome.CANDIDATES_FOUND
    assert result.retrieval.county_source is ContextSource.TEXT
    top = result.retrieval.candidates[0]
    assert (top.feature_id, top.county_match, top.type_match) == (2, True, True)


def test_supplied_county_takes_precedence(gaz: Gazetteer, rules: RulesExtractor) -> None:
    result = interpret("Beta Co., 2 mi NE of Testa Peak", rules, gaz, supplied_county="Alpha")
    assert result.retrieval is not None
    assert result.retrieval.county_source is ContextSource.SUPPLIED
    assert result.retrieval.candidates[0].feature_id == 1


def test_absent_and_missing_reference_are_distinct(gaz: Gazetteer, rules: RulesExtractor) -> None:
    absent = interpret("2 mi N of Nowhere Gulch", rules, gaz).retrieval
    assert absent is not None
    assert absent.outcome is RetrievalOutcome.FEATURE_ABSENT_FROM_INDEX
    none = interpret("2 mi along the trail from Testa Lake", rules, gaz).retrieval
    assert none is not None
    assert none.outcome is RetrievalOutcome.NO_REFERENCE_FEATURE


def test_baseline_cli(index_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["baseline", "run", "2 mi NE of Testa Peak", "--index", str(index_path)]) == 0
    out = capsys.readouterr().out
    assert "distance_and_direction" in out
    assert "Testa Peak" in out

    assert (
        main(["baseline", "run", "3 m E of Testa Lake", "--index", str(index_path), "--json"]) == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["extractor"] == "rules-2"
    assert "distance_unit" in payload["interpretation"]["missing"]
    assert payload["retrieval"]["outcome"] == "candidates_found"


def test_baseline_cli_proposal(index_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = ["baseline", "run", "2 mi NE of Testa Peak", "--index", str(index_path), "--propose"]
    assert main(base) == 0
    out = capsys.readouterr().out
    assert "proposal    needs_information" in out
    assert "extent of Testa Peak" in out

    assert main([*base, "--extent-m", "500", "--extent-note", "test", "--json"]) == 0
    proposal = json.loads(capsys.readouterr().out)["proposal"]
    assert proposal["outcome"] == "computed"
    assert proposal["radius_m"] > proposal["radius_lower_bound_m"] > 0
    assert proposal["policy_id"].startswith("gbif-bp-2020/")

    assert main([*base, "--feature-id", "999"]) == 2


@pytest.mark.parametrize("placeholder", ["Unknown", "Unknown-E", "unknown-w", "", "  "])
def test_a_placeholder_county_gives_way_to_the_labels_county(
    gaz: Gazetteer, rules: RulesExtractor, placeholder: str
) -> None:
    result = interpret("Beta Co., 2 mi NE of Testa Peak", rules, gaz, supplied_county=placeholder)
    assert result.retrieval is not None
    assert result.retrieval.county_source is ContextSource.TEXT
    assert result.retrieval.candidates[0].feature_id == 2  # Beta, from the label


@pytest.mark.parametrize("value", ["Beta/Gamma", "Gamma / Beta", "Gamma or Beta"])
def test_a_two_county_value_matches_either_county(
    gaz: Gazetteer, rules: RulesExtractor, value: str
) -> None:
    result = interpret("2 mi NE of Testa Peak", rules, gaz, supplied_county=value)
    assert result.retrieval is not None
    assert result.retrieval.county_source is ContextSource.SUPPLIED
    top, other = result.retrieval.candidates[:2]
    assert (top.feature_id, top.county_match) == (2, True)
    assert (other.feature_id, other.county_match) == (1, False)  # ranked lower, never removed


def test_an_unknown_county_name_counts_as_missing(gaz: Gazetteer, rules: RulesExtractor) -> None:
    result = interpret("Beta Co., Testa Peak", rules, gaz, supplied_county="Giplin")
    assert result.retrieval is not None
    assert result.retrieval.county_source is ContextSource.TEXT
    assert result.retrieval.county_context == "Beta Co."
