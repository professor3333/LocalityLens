"""hybrid-1: rules first, LLM only where the rules reach no gazetteer candidate. SYNTHETIC data."""

import json
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row
from tests.unit.test_llm_extraction import RELEASE, FakeClient

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.evaluation.audit import AuditItem, AuditSample, run_llm, run_rules
from localitylens.evaluation.hybrid import ReportMismatchError, combine_reports
from localitylens.extract.llm import LLMExtractor
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.ingest.specimens import to_record
from localitylens.pipeline.hybrid import HYBRID_VERSION, HybridResult, interpret_hybrid


@pytest.fixture
def index_path(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def named(quote: str) -> str:
    return json.dumps({"relation": "named_feature", "relation_quote": quote,
                       "reference_feature": {"name_quote": quote}})  # fmt: skip


def hybrid(index: Path, text: str, client: FakeClient) -> HybridResult:
    with Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        return interpret_hybrid(text, rules, LLMExtractor(client, RELEASE), gaz)


def test_rules_result_is_used_without_a_model_call(index_path: Path) -> None:
    client = FakeClient()  # no responses: any call would fail the test
    h = hybrid(index_path, "Testa Peak.", client)
    assert (h.source, h.llm_called, client.calls) == ("rules", False, 0)
    assert h.result.extractor_version == "rules-4"
    assert h.version == HYBRID_VERSION


@pytest.mark.parametrize(("text", "quote"), [
    ("Testta Peak.", "Testta Peak"),  # the rules find no place; the LLM's quote matches fuzzily
    ("Cirque of the Testa Lake", "Testa Lake"),  # the rules keep "Cirque of the" in the name
])  # fmt: skip
def test_llm_is_used_where_the_rules_reach_no_candidate(
    index_path: Path, text: str, quote: str
) -> None:
    client = FakeClient(named(quote))
    h = hybrid(index_path, text, client)
    assert (h.source, h.llm_called, client.calls) == ("llm", True, 1)
    assert h.result.retrieval is not None
    assert h.result.retrieval.candidates


def test_rules_are_kept_when_the_llm_does_not_help(index_path: Path) -> None:
    h = hybrid(index_path, "Nowhere Hill.", FakeClient(named("Nowhere Hill")))
    assert (h.source, h.llm_called, h.llm_error) == ("rules", True, None)
    assert h.result.extractor_version == "rules-4"


def test_a_failed_model_call_never_makes_a_record_worse(index_path: Path) -> None:
    h = hybrid(index_path, "Nowhere Hill.", FakeClient("{bad", "{bad"))
    assert (h.source, h.llm_error) == ("rules", "malformed_model_output")


def _sample() -> AuditSample:
    texts = ["Testa Peak.", "Testta Peak.", "Nowhere Hill.", "Cirque of the Testa Lake"]
    items = tuple(AuditItem(audit_id=f"A{i:02d}", group_size=1,
                            record=to_record(row(i, t, county="Alpha")))
                  for i, t in enumerate(texts, start=1))  # fmt: skip
    return AuditSample(snapshot_id="gbif-synthetic", screen_version="1", grouping_version="1",
                       seed="seed", eligible_records=4, eligible_groups=4, items=items)  # fmt: skip


def test_combined_reports_choose_exactly_as_the_live_hybrid(index_path: Path) -> None:
    sample = _sample()
    answers = [
        named("Testa Peak"),
        named("Testta Peak"),
        named("Nowhere Hill"),
        named("Testa Lake"),
    ]
    llm = run_llm(sample, index_path, FakeClient(*answers), RELEASE)
    combined = combine_reports(run_rules(sample, index_path), llm)
    live = [hybrid(index_path, i.record.locality, FakeClient(a))
            for i, a in zip(sample.items, answers, strict=True)]  # fmt: skip
    assert [r["source"] for r in combined["records"]] == [h.source for h in live]
    assert [r["source"] for r in combined["records"]] == ["rules", "llm", "rules", "llm"]
    assert [r["llm_called"] for r in combined["records"]] == [h.llm_called for h in live]
    assert combined["extractor_version"] == HYBRID_VERSION
    assert combined["components"] == {"rules": "rules-4", "llm": RELEASE.extractor_id}
    assert combined["counts"]["llm_call"] == {"made": 3, "skipped": 1}
    assert "trace" in combined["records"][2]  # the unhelpful call's cost is still recorded


def test_reports_of_different_runs_are_refused(index_path: Path) -> None:
    sample = _sample()
    rules = run_rules(sample, index_path)
    llm = run_llm(sample, index_path, FakeClient(*[named("Testa Peak")] * 4), RELEASE)
    with pytest.raises(ReportMismatchError, match="validation_version"):
        combine_reports(rules, llm | {"validation_version": "0"})
    with pytest.raises(ReportMismatchError, match="different records"):
        combine_reports(rules, llm | {"records": llm["records"][:2]})
    with pytest.raises(ReportMismatchError, match="one rules report"):
        combine_reports(llm, rules)
