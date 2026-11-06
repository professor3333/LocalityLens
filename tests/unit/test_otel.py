"""OpenTelemetry export: off by default, one span per stored trace with stage children, error
status for failed attempts, and no label text or coordinates. SYNTHETIC gazetteer and records."""

import json
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode
from tests.support.synthetic_dwca import row

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.extract.llm_client import FailureCategory, ModelCallError
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.ingest.specimens import to_record
from localitylens.jobs.queue import JobQueue
from localitylens.jobs.worker import work
from localitylens.review.importer import import_records
from localitylens.review.store import ReviewStore
from localitylens.telemetry import otel

TEXTS = ["Testa Lake.", "2 mi NE of Testa Peak", "5 mi up the road from Testa Lake"]


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    otel.uninstall()
    yield
    otel.uninstall()


@pytest.fixture
def spans() -> InMemorySpanExporter:
    exporter = InMemorySpanExporter()
    otel.install(exporter)
    return exporter


@pytest.fixture
def index(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def _import(db: Path, index: Path) -> ReviewStore:
    store = ReviewStore(db)
    records = [to_record(row(i, t, county="Alpha")) for i, t in enumerate(TEXTS, start=1)]
    with Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        import_records(store, records, "gbif-synthetic", gaz, system="rules", rules=rules,
                       llm=None, release="test")  # fmt: skip
    return store


def test_off_by_default(tmp_path: Path, index: Path) -> None:
    assert not otel.enabled()
    _import(tmp_path / "r.sqlite", index)  # runs without any exporter


def test_one_span_per_trace_with_stage_children(
    tmp_path: Path, index: Path, spans: InMemorySpanExporter
) -> None:
    store = _import(tmp_path / "r.sqlite", index)
    finished = spans.get_finished_spans()
    parents = [s for s in finished if s.name == otel.SPAN_NAME]
    traces = {json.loads(t)["trace_id"]: json.loads(t) for t in store.traces()}
    assert len(parents) == len(traces) == 3
    for span in parents:
        attrs = dict(span.attributes or {})
        t = traces[attrs["localitylens.trace_id"]]
        assert attrs["localitylens.record_id"] == t["record_id"]
        assert attrs["localitylens.outcome"] == t["outcome"]
        assert attrs["localitylens.input_sha256"] == t["input_sha256"]
        children = [c for c in finished if c.parent and c.parent.span_id == span.context.span_id]
        stages = ["extract", "validate", "retrieve", "propose"]
        assert [c.name for c in children] == [f"localitylens.{x}" for x in stages]
        assert span.start_time <= children[0].start_time
        assert children[-1].end_time <= span.end_time
        assert span.status.status_code is not StatusCode.ERROR


def test_failed_attempts_are_error_spans(tmp_path: Path, spans: InMemorySpanExporter) -> None:
    store = ReviewStore(tmp_path / "r.sqlite")
    ids = [store.add_record(to_record(row(1, "Testa Lake.")), "gbif-synthetic")]
    q = JobQueue(store, clock=time.time, max_attempts=2)
    q.enqueue(ids, system="rules", release="test", snapshot_id="gbif-synthetic",
              gazetteer="gnis-synthetic", extractor="rules-test")  # fmt: skip

    def process(record_id: str):  # type: ignore[no-untyped-def]
        raise ModelCallError(FailureCategory.MODEL_SERVER_UNAVAILABLE, "down")

    work(q, process, owner="w")
    statuses = [(s.attributes or {}).get("localitylens.outcome") for s in
                spans.get_finished_spans() if s.name == otel.SPAN_NAME]  # fmt: skip
    assert statuses == ["retry:model_server_unavailable", "failed:model_server_unavailable"]
    assert all(s.status.status_code is StatusCode.ERROR for s in spans.get_finished_spans()
               if s.name == otel.SPAN_NAME)  # fmt: skip


def test_no_label_text_or_coordinates_in_spans(
    tmp_path: Path, index: Path, spans: InMemorySpanExporter
) -> None:
    store = _import(tmp_path / "r.sqlite", index)
    values = " ".join(str(v) for s in spans.get_finished_spans()
                      for v in (s.attributes or {}).values())  # fmt: skip
    for r in store.records():
        assert r["locality"] not in values
        for c in store.latest_pipeline_proposal(r["record_id"]).candidates:
            assert f"{c.primary_point.latitude:.4f}" not in values
            assert c.official_name not in values


def test_configuration_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(otel.OTEL_ENV, raising=False)
    assert otel.configure_from_env() is None
    monkeypatch.setenv(otel.OTEL_ENV, "off")
    assert otel.configure_from_env() is None
    monkeypatch.setenv(otel.OTEL_ENV, "console")
    provider = otel.configure_from_env()
    assert provider is not None
    assert otel.enabled()
    assert isinstance(provider._active_span_processor._span_processors[0].span_exporter,  # type: ignore[attr-defined]
                      ConsoleSpanExporter)  # fmt: skip
    otel.uninstall()
    monkeypatch.setenv(otel.OTEL_ENV, "jaeger")
    with pytest.raises(ValueError, match="expected console, otlp or off"):
        otel.configure_from_env()


def test_otlp_without_the_extra_says_how_to_install_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "opentelemetry.exporter.otlp.proto.http.trace_exporter", None)
    monkeypatch.setenv(otel.OTEL_ENV, "otlp")
    with pytest.raises(RuntimeError, match="uv sync --extra otel"):
        otel.configure_from_env()
