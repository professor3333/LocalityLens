"""End to end in a real browser: import → review → approve / edit / reject / defer → export.

SYNTHETIC gazetteer and records; the extent is invented test input for a synthetic feature (as in
test_review_export). The server runs uvicorn on a free loopback port; the browser is Playwright's
headless Chromium. Outside CI the test is skipped when that browser is not installed
(``uv run playwright install chromium-headless-shell``); in CI it must run.
"""

import os
import socket
import threading
import time
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
import uvicorn
from tests.support.synthetic_dwca import row

from localitylens.baseline.rules import Lexicon, RulesExtractor
from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.domain.status import RecordStatus
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.extents import ExtentStore, ReviewedExtent
from localitylens.ingest.specimens import to_record
from localitylens.review.importer import import_records
from localitylens.review.store import ReviewStore
from localitylens.web.app import ReviewConfig, create_app

playwright_sync = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.e2e

TEXTS = {
    "lake": "Testa Lake.",  # reviewed extent → computed
    "peak": "2 mi NE of Testa Peak",  # extent unknown → needs information
    "route": "5 mi up the road from Testa Lake",  # unsupported
    "absent": "2 mi N of Nowhere Gulch",  # not in GNIS
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


@pytest.fixture
def server(db: Path) -> Iterator[str]:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    out = db.parent / "export"
    config = ReviewConfig(db=db, reviewer="Curator E2E", extents=EXTENTS,
                          export_out=out / "occurrences.csv",
                          unresolved_out=out / "unresolved.csv")  # fmt: skip
    srv = uvicorn.Server(uvicorn.Config(create_app(config), host="127.0.0.1", port=port,
                                        log_level="warning"))  # fmt: skip
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not srv.started:
        if time.monotonic() > deadline:
            raise RuntimeError("the review server did not start")
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    srv.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def page(server: str) -> Iterator[object]:
    with playwright_sync.sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as exc:  # the browser binary is missing
            if os.environ.get("CI"):
                raise
            pytest.skip(f"Playwright Chromium not installed: {exc}")
        context = browser.new_context()
        # No basemap tiles in tests: the screen must work without the network.
        context.route("https://basemap.nationalmap.gov/**", lambda route: route.abort())
        pg = context.new_page()
        errors: list[str] = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        yield pg
        browser.close()
        assert not errors, f"JavaScript errors: {errors}"


def _status(db: Path, key: str) -> RecordStatus:
    with ReviewStore(db) as store:
        return store.status(_id(key))


def test_review_flow_in_a_browser(page, server: str, db: Path) -> None:  # type: ignore[no-untyped-def]
    page.goto(server + "/")
    assert page.locator("h1").inner_text() == "Review queue"
    assert page.locator("a.chip", has_text="ready for review").inner_text() == "ready for review 1"

    # A refused approval reports in place (HTMX), without leaving the page.
    page.click(f"text={_id('peak')}")
    assert page.locator(".badge").first.inner_text() == "needs information"
    assert page.locator("input[name=action][value=request_research]").is_checked()
    page.check("input[name=action][value=approve]")
    page.fill("textarea[name=rationale]", "trying without an extent")
    page.click("button:has-text('Record decision')")
    page.wait_for_selector("#decision-error .error")
    assert "no full region" in page.inner_text("#decision-error")
    assert page.url.endswith(f"/records/{_id('peak')}")
    assert _status(db, "peak") is RecordStatus.NEEDS_INFORMATION

    # Edit, then approve: another candidate and a reviewed extent.
    page.select_option("select[name=feature_id]", value="2")
    page.fill("input[name=extent_m]", "900")
    page.fill("input[name=extent_note]", "measured on a map")
    page.fill("textarea[name=rationale]", "the second peak fits the county")
    page.click("button:has-text('Record decision')")
    page.wait_for_selector("text=Approved region (exported)")
    assert "feature_id 1 → 2" in page.inner_text("ol.history")
    assert page.locator("path.leaflet-interactive").count() >= 1  # the circle is drawn
    assert _status(db, "peak") is RecordStatus.APPROVED

    # Approve as proposed, reject, request research.
    for key, action, why in [("lake", "approve", "as proposed"),
                             ("route", "reject", "route description, out of scope"),
                             ("absent", "request_research", "find Nowhere Gulch")]:  # fmt: skip
        page.goto(f"{server}/records/{_id(key)}")
        page.check(f"input[name=action][value={action}]")
        page.fill("textarea[name=rationale]", why)
        page.click("button:has-text('Record decision')")
        page.wait_for_selector("ol.history")
    assert _status(db, "lake") is RecordStatus.APPROVED
    assert _status(db, "route") is RecordStatus.REJECTED
    assert _status(db, "absent") is RecordStatus.NEEDS_INFORMATION

    # Export, then download the approved records.
    page.goto(server + "/")
    page.click("button:has-text('Export Darwin Core')")
    page.wait_for_selector(".done")
    assert "Exported 2 approved record(s)" in page.inner_text(".done")
    with page.expect_download() as download:
        page.click("a[href='/export/occurrences.csv']")
    rows = Path(download.value.path()).read_text(encoding="utf-8").splitlines()
    assert rows[0].startswith("occurrenceID")
    assert len(rows) == 3  # header + peak + lake
    assert "Curator E2E" in rows[1] + rows[2]
