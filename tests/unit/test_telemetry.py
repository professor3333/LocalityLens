"""Traces: one per job attempt, linked to its proposal, exported as provenance, emitted as JSON,
and never carrying label text or coordinates. SYNTHETIC gazetteer and records."""

import csv
import json
import logging
import sqlite3
import string
from datetime import date
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError
from tests.support.synthetic_dwca import row

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.export.darwin_core import export_approved
from localitylens.extract.llm import CallTrace
from localitylens.extract.llm_client import FailureCategory, ModelCallError
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.extents import ExtentStore, ReviewedExtent
from localitylens.ingest.specimens import to_record
from localitylens.jobs.queue import JobQueue
from localitylens.jobs.worker import work
from localitylens.review.importer import import_records
from localitylens.review.store import STORE_SCHEMA_VERSION, Action, ReviewStore
from localitylens.telemetry.trace import LOGGER_NAME, RecordTrace, input_sha256

TEXTS = ["Testa Lake.", "2 mi NE of Testa Peak", "5 mi up the road from Testa Lake"]


@pytest.fixture(scope="module")
def index(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from tests.support.synthetic_gnis import synthetic_manifest, write_gnis_zips

    directory = tmp_path_factory.mktemp("gnis")
    write_gnis_zips(directory)
    manifest: SnapshotManifest = synthetic_manifest(directory)
    write_manifest(directory / "manifest.json", manifest)
    path = directory / "g.sqlite"
    build_index(directory, manifest, path)
    return path


EXTENTS = ExtentStore(
    path=Path("extents.csv"), sha256="0" * 64, pending=0,
    entries={3: ReviewedExtent(feature_id=3, official_name="Testa Lake", extent_m=650.0,
                               method="measured", source="synthetic map", reviewer="tester",
                               reviewed_on=date(2026, 11, 4), note="")},
)  # fmt: skip


def _import(db: Path, index: Path, texts: list[str]) -> ReviewStore:
    store = ReviewStore(db)
    records = [to_record(row(i, t, county="Alpha")) for i, t in enumerate(texts, start=1)]
    with Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        import_records(store, records, "gbif-synthetic", gaz, system="rules", rules=rules,
                       llm=None, release="test", extents=EXTENTS)  # fmt: skip
    return store


def _traces(store: ReviewStore) -> list[dict]:  # type: ignore[type-arg]
    return [json.loads(t) for t in store.traces()]


def test_one_trace_per_attempt_linked_to_its_proposal(tmp_path: Path, index: Path) -> None:
    store = _import(tmp_path / "r.sqlite", index, TEXTS)
    traces = _traces(store)
    assert len(traces) == 3
    for t in traces:
        p = store.latest_pipeline_proposal(t["record_id"])
        assert t["proposal_id"] == p.proposal_id
        assert store.trace_for_proposal(p.proposal_id) == t["trace_id"]
        assert t["outcome"] == store.status(t["record_id"]).value
        assert t["attempt"] == 1
        assert t["stages"]["total_ms"] >= 0
        assert t["candidate_count"] >= 0
        assert t["uncertainty_policy"].startswith("gbif-bp-")
        rec = store.record(t["record_id"])
        assert t["input_sha256"] == input_sha256(rec["locality"], rec["county"])


def test_retries_failures_and_expired_leases_leave_traces(tmp_path: Path) -> None:
    store = ReviewStore(tmp_path / "r.sqlite")
    ids = [store.add_record(to_record(row(i, "Testa Lake.")), "gbif-synthetic") for i in (1, 2)]
    clock = [1_000_000.0]
    q = JobQueue(store, clock=lambda: clock[0], lease_s=10, max_attempts=2)
    q.enqueue(ids, system="rules", release="test", snapshot_id="gbif-synthetic",
              gazetteer="gnis-synthetic", extractor="rules-test")  # fmt: skip
    q.claim("dies")  # first record: crash, then the lease expires
    clock[0] += 11
    down = ModelCallError(FailureCategory.MODEL_SERVER_UNAVAILABLE, "down")

    def process(record_id: str):  # type: ignore[no-untyped-def]
        raise down

    work(q, process, owner="w")
    outcomes = sorted(t["outcome"] for t in _traces(store))
    # record 1: crash (lease expires) → retried → outage, attempts used up
    # record 2: outage → retried → outage, attempts used up
    assert outcomes == ["failed:model_server_unavailable", "failed:model_server_unavailable",
                        "retry:lease_expired", "retry:model_server_unavailable"]  # fmt: skip
    failed = [t for t in _traces(store) if t["outcome"].startswith("failed:")]
    assert all(t["proposal_id"] for t in failed)  # the failure proposal is linked


def test_the_export_carries_the_trace_id(tmp_path: Path, index: Path) -> None:
    store = _import(tmp_path / "r.sqlite", index, ["Testa Lake."])
    (rid,) = [r["record_id"] for r in store.records()]
    p = store.latest_pipeline_proposal(rid)
    assert p.outcome == "computed"  # the synthetic lake's reviewed extent
    store.decide(rid, Action.APPROVE, reviewer="r", rationale="ok")
    export_approved(store, tmp_path / "o.csv")
    (exported,) = list(
        csv.DictReader((tmp_path / "o.csv").read_text(encoding="utf-8").splitlines())
    )
    assert exported["localitylens_trace_id"] == store.trace_for_proposal(p.proposal_id)


def test_the_export_links_an_edited_approval_to_its_pipeline_trace(
    tmp_path: Path, index: Path
) -> None:
    store = _import(tmp_path / "r.sqlite", index, ["2 mi NE of Testa Peak"])
    (rid,) = [r["record_id"] for r in store.records()]
    base = store.latest_pipeline_proposal(rid)
    store.decide(rid, Action.APPROVE, reviewer="r", rationale="measured", extent_m=900,
                 extent_note="measured on a map")  # fmt: skip
    export_approved(store, tmp_path / "o.csv")
    (exported,) = list(
        csv.DictReader((tmp_path / "o.csv").read_text(encoding="utf-8").splitlines())
    )
    assert exported["localitylens_trace_id"] == store.trace_for_proposal(base.proposal_id)
    assert len(exported["localitylens_trace_id"]) == 32


def test_traces_are_emitted_as_json_lines(
    tmp_path: Path, index: Path, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        _import(tmp_path / "r.sqlite", index, TEXTS[:2])
    lines = [json.loads(r.message) for r in caplog.records if r.name == LOGGER_NAME]
    assert len(lines) == 2
    assert {line["telemetry_version"] for line in lines} == {"telemetry-1"}


def test_the_schema_has_no_room_for_prose() -> None:
    good = {"trace_id": "0" * 32, "at": "2026-11-06T00:00:00.000+00:00", "job_id": "0" * 16,
            "batch_id": "b-" + "0" * 16, "record_id": "gbif:1", "attempt": 1,
            "input_sha256": "0" * 64, "system": "rules", "extractor_version": "rules-6",
            "release": "test", "gazetteer_snapshot": "gnis-co-2026-09-29",
            "outcome": "needs_information"}  # fmt: skip
    RecordTrace.model_validate(good)
    for field, bad in [("outcome", "2 mi NE of Longs Peak"), ("system", "rules; drop table"),
                       ("record_id", "Longs Peak")]:  # fmt: skip
        with pytest.raises(ValidationError):
            RecordTrace.model_validate({**good, field: bad})
    with pytest.raises(ValidationError):
        RecordTrace.model_validate({**good, "locality": "Testa Lake."})  # unknown field


def test_a_review_2_store_is_upgraded_to_review_3(tmp_path: Path) -> None:
    path = tmp_path / "old.sqlite"
    ReviewStore(path).close()
    con = sqlite3.connect(path)
    con.executescript("DROP TABLE trace; UPDATE meta SET value='review-2' WHERE key='schema';")
    con.close()
    store = ReviewStore(path)
    assert store.connection.execute("SELECT value FROM meta").fetchone()[0] == STORE_SCHEMA_VERSION
    assert store.traces() == []


# Labels with a character no code or ID may contain (uppercase, a space, or ,;'), so a match can
# only mean the text leaked, not that a short label happens to spell part of a hash.
LABELS = st.text(alphabet=string.ascii_letters + string.digits + " .,;:-'", min_size=4,
                 max_size=60).filter(
    lambda s: len(s.strip()) >= 4 and any(c.isupper() or c in " ,;'" for c in s.strip())
)  # fmt: skip


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [x for v in value.values() for x in _strings(v)]
    if isinstance(value, list | tuple):
        return [x for v in value for x in _strings(v)]
    return []


@settings(deadline=None)
@given(label=LABELS)
def test_label_text_never_reaches_a_trace(
    tmp_path_factory: pytest.TempPathFactory, index: Path, label: str
) -> None:
    db = tmp_path_factory.mktemp("t") / "r.sqlite"
    store = _import(db, index, [label, f"{label} Testa Lake."])
    for payload in store.traces():
        data = json.loads(payload)
        data.pop("at")  # the timestamp: digits, dashes, colons and a T
        for value in _strings(data):
            assert label.strip() not in value, (value, label)


def test_coordinates_never_reach_a_trace(tmp_path: Path, index: Path) -> None:
    store = _import(tmp_path / "r.sqlite", index, TEXTS)
    payloads = " ".join(store.traces())
    for r in store.records():
        for c in store.latest_pipeline_proposal(r["record_id"]).candidates:
            assert f"{c.primary_point.latitude:.4f}" not in payloads
            assert f"{c.primary_point.longitude:.4f}" not in payloads


class FakeLLM:
    """Stands in for the LLM extractor: reads like the rules, reports a call trace."""

    version = "fake-llm-1"

    def __init__(self, rules: RulesExtractor, fail: bool = False) -> None:
        self.rules, self.fail = rules, fail
        self.last_trace = CallTrace()

    def extract(self, text: str):  # type: ignore[no-untyped-def]
        self.last_trace = CallTrace(prompt_sha256="a" * 64, prompt_tokens=1500,
                                    completion_tokens=60, attempts=1, seconds=9.5)  # fmt: skip
        if self.fail:
            raise ModelCallError(FailureCategory.MODEL_SERVER_UNAVAILABLE, "down")
        return self.rules.extract(text)


@pytest.mark.parametrize("fail", [False, True])
def test_hybrid_traces_record_the_model_call(tmp_path: Path, index: Path, fail: bool) -> None:
    store = ReviewStore(tmp_path / "r.sqlite")
    texts = ["Testa Lake.", "2 mi N of Nowhere Gulch"]  # the rules reach only the first
    records = [to_record(row(i, t, county="Alpha")) for i, t in enumerate(texts, start=1)]
    with Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        import_records(store, records, "gbif-synthetic", gaz, system="hybrid", rules=rules,
                       llm=FakeLLM(rules, fail), release="test")  # fmt: skip
    by_record = {t["record_id"]: t for t in _traces(store)}
    assert "model" not in by_record["gbif:1"]  # the rules answered: no model call
    model = by_record["gbif:2"]["model"]
    assert model["called"] is True
    assert model["used"] is False  # the LLM reached no candidate either
    assert (model["prompt_tokens"], model["completion_tokens"]) == (1500, 60)
    assert model.get("error") == ("model_server_unavailable" if fail else None)
