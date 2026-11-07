"""The committed static replay (demo/site) publishes only audit records, each page labelled.

Validation and locked-test records must never reach a public page; the audit sample is committed
development data that already passed the specimen screen.
"""

import json
import re
from pathlib import Path

import pytest

from localitylens.web.replay import record_file

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "demo" / "site"
pytestmark = pytest.mark.skipif(not SITE.is_dir(), reason="no replay built")


def test_only_audit_records_are_published() -> None:
    sample = json.loads((ROOT / "eval/audit/audit-50.json").read_text(encoding="utf-8"))
    allowed = {record_file(f"gbif:{item['record']['gbif_id']}") for item in sample["items"]}
    published = {p.relative_to(SITE).as_posix() for p in (SITE / "records").glob("*.html")}
    assert published
    assert published <= allowed


def test_every_page_says_it_is_a_replay_and_cannot_post() -> None:
    for page in SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        assert "Replay, not live inference." in html, page
        assert "<form" not in html, page
        assert not re.search(r'(?:href|src)="/', html), page
