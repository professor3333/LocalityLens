"""The completion cache (llm-cache-1): same request + same model and server → same completion."""

import json
from pathlib import Path

import pytest
from tests.support.synthetic_dwca import row
from tests.unit.test_llm_extraction import RELEASE, FakeClient

from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.evaluation.audit import AuditItem, AuditSample, run_llm
from localitylens.extract.cache import CachingClient, cache_key, is_deterministic
from localitylens.extract.llm import LLMExtractor, extraction_schema
from localitylens.gazetteer.index import build_index
from localitylens.ingest.specimens import to_record

IDENTITY = {"gguf_sha256": RELEASE.model.gguf_sha256, "server_build": "b1-abc",
            "model_file": "m.gguf", "n_ctx": 4096}  # fmt: skip
SERVER = {"build_info": "b1-abc", "model_file": "m.gguf", "n_ctx": 4096}


def named(quote: str) -> str:
    return json.dumps({"relation": "named_feature", "relation_quote": quote,
                       "reference_feature": {"name_quote": quote}})  # fmt: skip


def test_a_repeated_request_is_answered_from_disk(tmp_path: Path) -> None:
    first = FakeClient(named("Testa Peak"))
    out1 = LLMExtractor(CachingClient(first, tmp_path, IDENTITY), RELEASE).extract("Testa Peak.")

    second = FakeClient()  # no responses: a model call would fail the test
    caching = CachingClient(second, tmp_path, IDENTITY)
    extractor = LLMExtractor(caching, RELEASE)
    out2 = extractor.extract("Testa Peak.")

    assert out2 == out1
    assert (first.calls, second.calls) == (1, 0)
    assert (caching.hits, caching.misses) == (1, 0)
    assert extractor.last_trace.cache_hits == 1
    assert extractor.last_trace.seconds == 0.0  # a hit is never reported as measured latency


@pytest.mark.parametrize("change", [
    {"gguf_sha256": "0" * 64},  # another model file or quantization
    {"server_build": "b2-def"},  # another llama.cpp build
    {"n_ctx": 8192},
])  # fmt: skip
def test_a_different_model_or_server_misses(tmp_path: Path, change: dict[str, object]) -> None:
    LLMExtractor(CachingClient(FakeClient(named("Testa Peak")), tmp_path, IDENTITY),
                 RELEASE).extract("Testa Peak.")  # fmt: skip
    other = FakeClient(named("Testa Peak"))
    LLMExtractor(CachingClient(other, tmp_path, IDENTITY | change), RELEASE).extract("Testa Peak.")
    assert other.calls == 1


def test_the_key_covers_prompt_schema_and_settings() -> None:
    schema = extraction_schema()
    s = RELEASE.generation
    base = cache_key("p", schema, s, IDENTITY)
    assert cache_key("p ", schema, s, IDENTITY) != base
    assert cache_key("p", schema | {"x": 1}, s, IDENTITY) != base
    assert cache_key("p", schema, s.model_copy(update={"seed": s.seed + 1}), IDENTITY) != base
    assert cache_key("p", schema, s.model_copy(update={"max_tokens": 64}), IDENTITY) != base
    assert cache_key("p", schema, s, dict(IDENTITY)) == base  # stable


def test_stochastic_settings_are_never_cached(tmp_path: Path) -> None:
    stochastic = RELEASE.generation.model_copy(update={"temperature": 0.7, "top_k": 40})
    assert not is_deterministic(stochastic)
    client = FakeClient(named("A"), named("A"))
    caching = CachingClient(client, tmp_path, IDENTITY)
    for _ in range(2):
        caching.complete("p", {}, stochastic)
    assert client.calls == 2
    assert not any(tmp_path.rglob("*.json"))


def test_an_incomplete_identity_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="server_build"):
        CachingClient(FakeClient(), tmp_path, IDENTITY | {"server_build": None})


@pytest.fixture
def index_path(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def _sample() -> AuditSample:
    items = tuple(AuditItem(audit_id=f"A{i:02d}", group_size=1,
                            record=to_record(row(i, t, county="Alpha")))
                  for i, t in enumerate(["Testa Peak.", "Testa Lake."], start=1))  # fmt: skip
    return AuditSample(snapshot_id="gbif-synthetic", screen_version="1", grouping_version="1",
                       seed="seed", eligible_records=2, eligible_groups=2, items=items)  # fmt: skip


def test_a_cached_rerun_gives_the_same_report_rows(index_path: Path, tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    answers = [named("Testa Peak"), named("Testa Lake")]
    plain = run_llm(_sample(), index_path, FakeClient(*answers), RELEASE, server=SERVER)
    first = run_llm(_sample(), index_path, FakeClient(*answers), RELEASE, server=SERVER,
                    cache_dir=cache)  # fmt: skip
    again = run_llm(_sample(), index_path, FakeClient(), RELEASE, server=SERVER, cache_dir=cache)

    assert "cache" not in plain
    assert first["cache"]["misses"] == 2
    assert (again["cache"]["hits"], again["cache"]["misses"]) == (2, 0)

    def strip(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        return [{k: v for k, v in r.items() if k != "trace"} for r in rows]

    assert strip(again["records"]) == strip(plain["records"])
    assert all(r["trace"]["cache_hits"] == 1 for r in again["records"])
    assert all("cache_hits" not in r["trace"] for r in plain["records"])


def test_the_locked_test_split_is_recognised() -> None:
    from localitylens.cli import _is_locked  # audit llm turns the cache off for these paths

    assert _is_locked(Path("eval/benchmark/test/test.json"))
    assert _is_locked(Path("eval/benchmark/test/../test/worksheet.csv"))
    assert not _is_locked(Path("eval/benchmark/validation/validation.json"))
