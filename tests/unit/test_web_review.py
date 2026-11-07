"""Review screen routes. SYNTHETIC gazetteer and records; the extent is invented test input for
a synthetic feature (as in test_review_export)."""

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
from localitylens.review.importer import import_records
from localitylens.review.store import ReviewStore
from localitylens.web.app import ReviewConfig, config_from_env, create_app, serve
from localitylens.web.views import label_segments

TEXTS = {
    "lake": "Testa Lake.",  # reviewed extent → computed
    "peak": "2 mi NE of Testa Peak",  # extent unknown → needs information
    "route": "5 mi up the road from Testa Lake",  # unsupported
    "absent": "2 mi N of Nowhere Gulch",  # not in GNIS
    "inject": "<script>alert(1)</script> Testa Lake.",  # label text is untrusted
}
EXTENTS = ExtentStore(
    path=Path("extents.csv"), sha256="0" * 64, pending=0,
    entries={3: ReviewedExtent(feature_id=3, official_name="Testa Lake", extent_m=650.0,
                               method="measured", source="synthetic map", reviewer="tester",
                               reviewed_on=date(2026, 11, 4), note="")},
)  # fmt: skip


def _id(key: str) -> str:
    return f"gbif:{list(TEXTS).index(key) + 1}"


@pytest.fixture
def db(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Path:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    index = tmp_path / "g.sqlite"
    build_index(directory, manifest, index)
    path = tmp_path / "review.sqlite"
    records = [to_record(row(i, t, county="Alpha")) for i, t in enumerate(TEXTS.values(), 1)]
    with ReviewStore(path) as store, Gazetteer(index) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        import_records(store, records, "gbif-synthetic", gaz, system="rules", rules=rules,
                       llm=None, release="test", extents=EXTENTS)  # fmt: skip
    return path


def _config(db: Path, **kw: object) -> ReviewConfig:
    out = db.parent / "export"
    return ReviewConfig(
        db=db, export_out=out / "occurrences.csv", unresolved_out=out / "unresolved.csv", **kw
    )  # type: ignore[arg-type]


@pytest.fixture
def client(db: Path) -> TestClient:
    return TestClient(create_app(_config(db, reviewer="Curator A")))


def _status(db: Path, key: str) -> RecordStatus:
    with ReviewStore(db) as store:
        return store.status(_id(key))


def _decide(client: TestClient, key: str, **form: str) -> object:
    data = {"rationale": "checked against the map", **form}
    return client.post(f"/records/{_id(key)}/decision", data=data, follow_redirects=False)


# --- pages ----------------------------------------------------------------------------------


def test_queue_lists_records_with_counts_and_filters(client: TestClient) -> None:
    page = client.get("/")
    assert page.status_code == 200
    assert "ready for review <b>2</b>" in page.text  # lake and inject
    assert all(_id(k) in page.text for k in TEXTS)
    ready = client.get("/?status=ready_for_review").text
    assert _id("lake") in ready
    assert _id("peak") not in ready
    assert client.get("/?status=nonsense").status_code == 400


def test_record_page_marks_spans_and_shows_the_region(client: TestClient) -> None:
    page = client.get(f"/records/{_id('lake')}").text
    assert '<mark class="m-feature" title="feature">Testa Lake</mark>' in page
    assert "GNIS 3" in page
    assert '"circle": {' in page  # a computed region gets a circle
    assert "Record decision" in page


def test_an_unknown_extent_is_unknown_and_draws_no_circle(client: TestClient) -> None:
    page = client.get(f"/records/{_id('peak')}").text
    assert '<span class="unknown">unknown</span>' in page
    assert '"circle": null' in page
    assert "selection evidence" in page
    assert "spatial uncertainty" in page


def test_label_text_is_escaped(client: TestClient) -> None:
    page = client.get(f"/records/{_id('inject')}").text
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_unknown_record_is_404(client: TestClient) -> None:
    assert client.get("/records/gbif:999").status_code == 404
    r = client.post("/records/gbif:999/decision", data={"action": "reject", "rationale": "x"})
    assert r.status_code == 404


def test_overlapping_spans_never_lose_text() -> None:
    assert "".join(s.text for s in label_segments("abc", None)) == "abc"


# --- decisions ------------------------------------------------------------------------------


def test_approve_as_proposed_redirects_and_a_retry_is_stored_once(
    client: TestClient, db: Path
) -> None:
    first = _decide(client, "lake", action="approve", feature_id="3")
    assert first.status_code == 303  # type: ignore[attr-defined]
    assert _status(db, "lake") is RecordStatus.APPROVED
    again = _decide(client, "lake", action="approve", feature_id="3")
    assert again.status_code == 303  # type: ignore[attr-defined]
    with ReviewStore(db) as store:
        assert len(store.decisions(_id("lake"))) == 1
        assert store.decisions(_id("lake"))[0].reviewer == "Curator A"
    page = client.get(f"/records/{_id('lake')}").text
    assert "Approved region (exported)" in page
    assert "no decision is possible" in page


def test_approval_without_a_full_region_is_refused(client: TestClient, db: Path) -> None:
    r = _decide(client, "peak", action="approve", feature_id="1")
    assert r.status_code == 400  # type: ignore[attr-defined]
    assert "no full region" in r.text  # type: ignore[attr-defined]
    assert _status(db, "peak") is RecordStatus.NEEDS_INFORMATION
    hx = client.post(f"/records/{_id('peak')}/decision", headers={"HX-Request": "true"},
                     data={"action": "approve", "rationale": "x"})  # fmt: skip
    assert hx.status_code == 400
    assert hx.text.startswith('<p class="error"')  # only the message, swapped in place


def test_edit_then_approve_records_the_diff(client: TestClient, db: Path) -> None:
    r = _decide(client, "peak", action="approve", feature_id="2", extent_m="900",
                extent_note="measured on a map")  # fmt: skip
    assert r.status_code == 303  # type: ignore[attr-defined]
    with ReviewStore(db) as store:
        (d,) = store.decisions(_id("peak"))
    assert d.edits == {"feature_id": [1, 2], "extent_m": [None, 900.0]}
    assert "feature_id 1 → 2" in client.get(f"/records/{_id('peak')}").text


def test_htmx_success_redirects_the_page(client: TestClient) -> None:
    r = client.post(f"/records/{_id('lake')}/decision", headers={"HX-Request": "true"},
                    data={"action": "approve", "feature_id": "3", "rationale": "ok"})  # fmt: skip
    assert r.status_code == 200
    assert r.headers["HX-Redirect"] == f"/records/{_id('lake')}"


@pytest.mark.parametrize(
    ("key", "form", "message"),
    [("peak", {"action": "approve", "feature_id": "99", "extent_m": "5", "extent_note": "n"},
      "not among the retrieved candidates"),
     ("lake", {"action": "approve", "rationale": ""}, "needs a reviewer and a rationale"),
     ("peak", {"action": "approve", "extent_m": "lots", "extent_note": "n"}, "must be a number"),
     ("peak", {"action": "approve", "extent_m": "900"}, "needs a note"),
     ("route", {"action": "approve"}, "cannot approve"),
     ("lake", {"action": "explode"}, "invalid input")],
)  # fmt: skip
def test_refused_decisions_explain_why(
    client: TestClient, key: str, form: dict[str, str], message: str
) -> None:
    r = _decide(client, key, **form)
    assert r.status_code == 400  # type: ignore[attr-defined]
    assert message in r.text  # type: ignore[attr-defined]


def test_reject_and_request_research(client: TestClient, db: Path) -> None:
    assert _decide(client, "route", action="reject").status_code == 303  # type: ignore[attr-defined]
    assert _status(db, "route") is RecordStatus.REJECTED
    assert _decide(client, "absent", action="request_research").status_code == 303  # type: ignore[attr-defined]
    assert _status(db, "absent") is RecordStatus.NEEDS_INFORMATION


def test_cross_site_posts_are_refused(client: TestClient, db: Path) -> None:
    r = client.post(f"/records/{_id('lake')}/decision", headers={"Origin": "https://evil.example"},
                    data={"action": "approve", "rationale": "x"})  # fmt: skip
    assert r.status_code == 403
    assert _status(db, "lake") is RecordStatus.READY_FOR_REVIEW


def test_reviewer_comes_from_the_form_when_not_configured(db: Path) -> None:
    client = TestClient(create_app(_config(db)))
    assert 'name="reviewer"' in client.get(f"/records/{_id('lake')}").text
    assert _decide(client, "lake", action="approve").status_code == 400  # type: ignore[attr-defined]
    ok = _decide(client, "lake", action="approve", reviewer="Curator B")
    assert ok.status_code == 303  # type: ignore[attr-defined]


def test_config_reads_the_reviewer_setting(monkeypatch: pytest.MonkeyPatch, db: Path) -> None:
    monkeypatch.setenv("LOCALITYLENS_REVIEWER", "  Curator C ")
    assert config_from_env(db).reviewer == "Curator C"
    monkeypatch.setenv("LOCALITYLENS_REVIEWER", " ")
    assert config_from_env(db).reviewer is None


def test_only_loopback(db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOCALITYLENS_CONTAINER", raising=False)
    with pytest.raises(ValueError, match="local only"):
        serve(ReviewConfig(db=db), host="0.0.0.0")


def test_approve_is_offered_only_when_it_can_succeed(client: TestClient) -> None:
    absent = client.get(f"/records/{_id('absent')}").text  # no candidate: approval impossible
    assert 'value="approve"' not in absent
    assert "No candidate to show." in absent
    peak = client.get(f"/records/{_id('peak')}").text  # candidates, no full region yet
    assert 'value="approve" >' in peak  # offered, for an edit, but not preselected
    assert 'value="request_research" checked' in peak
    lake = client.get(f"/records/{_id('lake')}").text
    assert 'value="approve" checked' in lake


# --- export ---------------------------------------------------------------------------------


def test_export_writes_approved_and_unresolved_and_serves_only_those(
    client: TestClient, db: Path
) -> None:
    assert client.get("/export/occurrences.csv").status_code == 404  # nothing exported yet
    _decide(client, "lake", action="approve", feature_id="3")
    page = client.post("/export")
    assert page.status_code == 200
    assert "Exported 1 approved record(s)" in page.text
    assert "3 unresolved record(s)" in page.text  # peak, route, absent (inject is still ready)
    csv_text = client.get("/export/occurrences.csv")
    assert csv_text.status_code == 200
    assert csv_text.headers["content-type"].startswith("text/csv")
    assert csv_text.text.splitlines()[0].startswith("occurrenceID")
    assert len(csv_text.text.splitlines()) == 2  # header + the approved lake
    assert client.get("/export/unresolved.csv").status_code == 200
    geo = client.get("/export/occurrences.geojson")
    assert geo.status_code == 200
    assert geo.headers["content-type"].startswith("application/geo+json")
    assert len(geo.json()["features"]) == 1
    assert 'href="/export/occurrences.geojson"' in client.get("/").text
    assert client.get("/export/..%2Freview.sqlite").status_code == 404
    assert client.get("/export/review.sqlite").status_code == 404
    assert (db.parent / "export" / "occurrences.csv").is_file()


def test_cross_site_export_is_refused(client: TestClient, db: Path) -> None:
    r = client.post("/export", headers={"Origin": "https://evil.example"})
    assert r.status_code == 403
    assert not (db.parent / "export").exists()
