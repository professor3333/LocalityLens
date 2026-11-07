"""JSON API contracts: every route, its errors, idempotent decisions and streamed batch progress.
SYNTHETIC gazetteer and records; the extent is invented test input for a synthetic feature."""

import json
import threading
import time
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tests.support.synthetic_dwca import row

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.domain.status import RecordStatus
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.extents import ExtentStore, ReviewedExtent
from localitylens.ingest.specimens import to_record
from localitylens.jobs.queue import JobQueue
from localitylens.review.importer import import_records, work_batch
from localitylens.review.store import ReviewStore
from localitylens.web.app import ReviewConfig, create_app

TEXTS = {
    "lake": "Testa Lake.",  # reviewed extent → computed
    "peak": "2 mi NE of Testa Peak",  # extent unknown → needs information
    "route": "5 mi up the road from Testa Lake",  # unsupported
}
EXTENTS = ExtentStore(
    path=Path("extents.csv"), sha256="0" * 64, pending=0,
    entries={3: ReviewedExtent(feature_id=3, official_name="Testa Lake", extent_m=650.0,
                               method="measured", source="synthetic map", reviewer="tester",
                               reviewed_on=date(2026, 11, 4), note="")},
)  # fmt: skip
JSON = {"Content-Type": "application/json"}


def _id(key: str) -> str:
    return f"gbif:{list(TEXTS).index(key) + 1}"


@pytest.fixture
def index(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    path = tmp_path / "g.sqlite"
    build_index(directory, manifest, path)
    return path


def _import(db: Path, index: Path, *, process: bool) -> str:
    records = [to_record(row(i, t, county="Alpha")) for i, t in enumerate(TEXTS.values(), 1)]
    with ReviewStore(db) as store, Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        import_records(store, records, "gbif-synthetic", gaz, system="rules", rules=rules,
                       llm=None, release="test", extents=EXTENTS, process_now=process)  # fmt: skip
        return JobQueue(store, clock=time.time).batches()[0].batch_id


def _client(db: Path, reviewer: str | None = "Curator API") -> TestClient:
    out = db.parent / "export"
    config = ReviewConfig(
        db=db, reviewer=reviewer, extents=EXTENTS,
        export_out=out / "occurrences.csv", unresolved_out=out / "unresolved.csv",
    )  # fmt: skip
    return TestClient(create_app(config))


@pytest.fixture
def processed(tmp_path: Path, index: Path) -> tuple[TestClient, Path, str]:
    db = tmp_path / "review.sqlite"
    batch = _import(db, index, process=True)
    return _client(db), db, batch


def _events(text: str) -> list[tuple[str, dict]]:  # type: ignore[type-arg]
    out = []
    for block in text.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        out.append((lines["event"], json.loads(lines["data"])))
    return out


# --- health, batches -------------------------------------------------------------------------


def test_health(processed: tuple[TestClient, Path, str]) -> None:
    client, _, _ = processed
    assert client.get("/api/health").json() == {"status": "ok", "api": "api-1"}


def test_batches_list_and_detail(processed: tuple[TestClient, Path, str]) -> None:
    client, _, batch = processed
    (b,) = client.get("/api/batches").json()
    assert b["batch_id"] == batch
    assert (b["state"], b["total"], b["finished"], b["open"]) == ("active", 3, 3, 0)
    assert client.get(f"/api/batches/{batch}").json()["jobs"] == {"done": 3}
    assert client.get("/api/batches/b-0000000000000000").status_code == 404


def test_a_finished_batch_streams_progress_then_end(
    processed: tuple[TestClient, Path, str],
) -> None:
    client, _, batch = processed
    r = client.get(f"/api/batches/{batch}/events")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    events = _events(r.text)
    assert [e for e, _ in events] == ["progress", "end"]
    assert events[-1][1]["open"] == 0


def test_a_running_batch_streams_until_the_worker_finishes(tmp_path: Path, index: Path) -> None:
    db = tmp_path / "review.sqlite"
    batch = _import(db, index, process=False)
    client = _client(db)

    def worker() -> None:  # the separate worker process, here a thread
        time.sleep(0.3)
        with ReviewStore(db) as store, Gazetteer(index) as gaz:
            rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
            q = JobQueue(store, clock=time.time)
            for _ in range(3):
                work_batch(store, q, batch, gaz, rules=rules, llm=None, extents=EXTENTS,
                           max_jobs=1)  # fmt: skip
                time.sleep(0.15)

    t = threading.Thread(target=worker)
    t.start()
    r = client.get(f"/api/batches/{batch}/events?interval=0.05&timeout=20")
    t.join()
    events = _events(r.text)
    assert events[0][1]["open"] == 3
    assert events[-1][0] == "end"
    assert events[-1][1]["jobs"] == {"done": 3}
    assert len(events) >= 3  # at least one intermediate progress event


def test_a_stalled_stream_times_out(tmp_path: Path, index: Path) -> None:
    db = tmp_path / "review.sqlite"
    batch = _import(db, index, process=False)
    r = _client(db).get(f"/api/batches/{batch}/events?interval=0.05&timeout=0.1")
    assert [e for e, _ in _events(r.text)][-1] == "timeout"


def test_unknown_batch_stream_is_404(processed: tuple[TestClient, Path, str]) -> None:
    client, _, _ = processed
    assert client.get("/api/batches/b-0000000000000000/events").status_code == 404


def test_cancel_and_resume(tmp_path: Path, index: Path) -> None:
    db = tmp_path / "review.sqlite"
    batch = _import(db, index, process=False)
    client = _client(db)
    r = client.post(f"/api/batches/{batch}/cancel", json={})
    assert r.status_code == 200
    assert r.json()["cancelled_jobs"] == 3
    assert r.json()["batch"]["state"] == "cancelled"
    end = _events(client.get(f"/api/batches/{batch}/events").text)[-1]
    assert end[0] == "end"  # a cancelled, idle batch ends its stream
    r = client.post(f"/api/batches/{batch}/resume", json={})
    assert r.json()["resumed_jobs"] == 3
    assert r.json()["batch"]["open"] == 3
    assert client.post("/api/batches/b-0000000000000000/cancel", json={}).status_code == 404


# --- records ---------------------------------------------------------------------------------


def test_records_list_filter_and_detail(processed: tuple[TestClient, Path, str]) -> None:
    client, _, _ = processed
    assert {r["record_id"] for r in client.get("/api/records").json()} == {_id(k) for k in TEXTS}
    ready = client.get("/api/records?status=ready_for_review").json()
    assert [r["record_id"] for r in ready] == [_id("lake")]
    assert client.get("/api/records?status=nonsense").status_code == 400
    detail = client.get(f"/api/records/{_id('lake')}").json()
    assert detail["record"]["locality"] == TEXTS["lake"]  # the original text, unchanged
    p = detail["proposal"]
    assert p["outcome"] == "computed"
    assert p["region"]["radius_m"] >= 650
    assert p["candidates"][0]["feature_id"] == 3
    assert len(p["trace_id"]) == 32
    assert detail["decisions"] == []
    assert client.get("/api/records/gbif:999").status_code == 404


# --- decisions -------------------------------------------------------------------------------


def test_a_decision_is_created_once_and_a_retry_returns_it(
    processed: tuple[TestClient, Path, str],
) -> None:
    client, db, _ = processed
    body = {"action": "approve", "rationale": "as proposed"}
    first = client.post(f"/api/records/{_id('lake')}/decisions", json=body)
    assert first.status_code == 201
    assert first.json()["created"] is True
    assert first.json()["status"] == "approved"
    again = client.post(f"/api/records/{_id('lake')}/decisions", json=body)
    assert again.status_code == 200
    assert again.json()["created"] is False
    assert again.json()["decision_id"] == first.json()["decision_id"]
    with ReviewStore(db) as store:
        assert len(store.decisions(_id("lake"))) == 1
        assert store.decisions(_id("lake"))[0].reviewer == "Curator API"


def test_an_explicit_key_makes_a_decision_idempotent(
    processed: tuple[TestClient, Path, str],
) -> None:
    client, db, _ = processed
    body = {"action": "reject", "rationale": "route", "key": "client-req-1"}
    assert client.post(f"/api/records/{_id('route')}/decisions", json=body).status_code == 201
    assert client.post(f"/api/records/{_id('route')}/decisions", json=body).status_code == 200
    with ReviewStore(db) as store:
        assert store.status(_id("route")) is RecordStatus.REJECTED


def test_edit_then_approve_through_the_api(processed: tuple[TestClient, Path, str]) -> None:
    client, _, _ = processed
    body = {"action": "approve", "rationale": "summit measured", "feature_id": 2,
            "extent_m": 900, "extent_note": "measured on a map"}  # fmt: skip
    r = client.post(f"/api/records/{_id('peak')}/decisions", json=body)
    assert r.status_code == 201
    assert r.json()["edits"] == {"feature_id": [1, 2], "extent_m": [None, 900.0]}
    assert r.json()["final_proposal"]


@pytest.mark.parametrize(
    ("key", "body", "code", "detail"),
    [("peak", {"action": "approve", "rationale": "x"}, 400, "no full region"),
     ("peak", {"action": "approve", "rationale": "x", "feature_id": 99, "extent_m": 5,
               "extent_note": "n"}, 400, "not among the retrieved candidates"),
     ("lake", {"action": "approve", "rationale": " "}, 400, "needs a reviewer and a rationale"),
     ("route", {"action": "approve", "rationale": "x"}, 400, "cannot approve"),
     ("lake", {"action": "explode", "rationale": "x"}, 422, None),
     ("lake", {"action": "approve", "rationale": "x", "latitude": 40.0}, 422, None),
     ("lake", {"action": "approve", "rationale": "x", "extent_m": -5}, 422, None)],
)  # fmt: skip
def test_refused_decisions_are_explicit(
    processed: tuple[TestClient, Path, str],
    key: str,
    body: dict,
    code: int,
    detail: str | None,  # type: ignore[type-arg]
) -> None:
    client, db, _ = processed
    before = None
    with ReviewStore(db) as store:
        before = store.status(_id(key))
    r = client.post(f"/api/records/{_id(key)}/decisions", json=body)
    assert r.status_code == code
    if detail:
        assert detail in r.json()["detail"]
    with ReviewStore(db) as store:
        assert store.status(_id(key)) is before  # nothing changed


def test_unknown_record_decision_is_404(processed: tuple[TestClient, Path, str]) -> None:
    client, _, _ = processed
    r = client.post("/api/records/gbif:999/decisions", json={"action": "reject", "rationale": "x"})
    assert r.status_code == 404


def test_a_reviewer_is_required_when_none_is_configured(tmp_path: Path, index: Path) -> None:
    db = tmp_path / "review.sqlite"
    _import(db, index, process=True)
    client = _client(db, reviewer=None)
    body = {"action": "approve", "rationale": "ok"}
    assert client.post(f"/api/records/{_id('lake')}/decisions", json=body).status_code == 400
    named = client.post(f"/api/records/{_id('lake')}/decisions", json={**body, "reviewer": "B"})
    assert named.status_code == 201


def test_posts_need_json_and_the_same_origin(processed: tuple[TestClient, Path, str]) -> None:
    client, db, batch = processed
    form = client.post(f"/api/records/{_id('lake')}/decisions",
                       data={"action": "approve", "rationale": "x"})  # fmt: skip
    assert form.status_code == 415
    cross = client.post(f"/api/batches/{batch}/cancel", json={},
                        headers={"Origin": "https://evil.example"})  # fmt: skip
    assert cross.status_code == 403
    assert client.post("/api/exports", content="{}").status_code == 415  # no content type
    cross_form = client.post(f"/api/records/{_id('lake')}/decisions",
                             data={"action": "approve", "rationale": "x"},
                             headers={"Origin": "https://evil.example"})  # fmt: skip
    assert cross_form.status_code == 403  # refused before the body is even parsed
    with ReviewStore(db) as store:
        assert store.status(_id("lake")) is RecordStatus.READY_FOR_REVIEW


# --- export ----------------------------------------------------------------------------------


def test_export_through_the_api(processed: tuple[TestClient, Path, str]) -> None:
    client, db, _ = processed
    client.post(f"/api/records/{_id('lake')}/decisions",
                json={"action": "approve", "rationale": "ok"})  # fmt: skip
    r = client.post("/api/exports", json={})
    assert r.status_code == 200
    assert (r.json()["approved"], r.json()["unresolved"]) == (1, 2)
    assert Path(r.json()["files"]["occurrences.csv"]).is_file()
    assert Path(r.json()["files"]["occurrences.geojson"]).is_file()
    again = client.post("/api/exports", json={})  # a retry rewrites the same rows
    assert again.json()["approved"] == 1
    lines = (db.parent / "export" / "occurrences.csv").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2  # header + the one approved record, no duplicate
