"""Freeze the review screen into a static replay for GitHub Pages.

The real app renders every page (the queue, each status filter, each record) from a review store
that the real pipeline filled. Each page is saved as HTML with the static files beside it. Links
are rewritten to relative paths so the site works under any URL prefix (a project site lives
under ``/<repo>/``). In replay mode the banner says the pages are precomputed, and decisions and
export are not rendered, so nothing on the site posts anywhere. Only the map tiles come from
the network.
"""

from __future__ import annotations

import dataclasses
import re
import shutil
from pathlib import Path
from typing import Final

from fastapi.testclient import TestClient

from localitylens.domain.status import RecordStatus
from localitylens.review.store import ReviewStore
from localitylens.web.app import HERE, Replay, ReviewConfig, create_app

REPLAY_VERSION: Final = "replay-1"
_BASE: Final = "http://testserver"
# href/src/action attributes holding a site-absolute path (or the test client's absolute URL)
_ATTR: Final = re.compile(
    r'(?P<attr>\b(?:href|src|action))="(?P<url>(?:http://testserver)?/[^"]*)"'
)


def record_file(record_id: str) -> str:
    """``gbif:123`` → ``records/gbif-123.html`` (no colon: not every checkout allows one)."""
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", record_id)
    return f"records/{safe}.html"


def _target(url: str, records: dict[str, str]) -> str:
    """Where a site-absolute URL lives in the frozen site, relative to the site root."""
    path = url.removeprefix(_BASE)
    if path == "/":
        return "index.html"
    if path.startswith("/?status="):
        return f"status-{path.removeprefix('/?status=')}.html"
    if path.startswith("/static/"):
        return path.removeprefix("/")
    if path.startswith("/records/"):
        rid = path.removeprefix("/records/")
        if rid in records:
            return records[rid]
    raise ValueError(f"the replay has no page for {url!r}")


def _relink(html: str, depth: int, records: dict[str, str]) -> str:
    prefix = "../" * depth

    def swap(m: re.Match[str]) -> str:
        return f'{m["attr"]}="{prefix}{_target(m["url"], records)}"'

    return _ATTR.sub(swap, html)


def freeze(config: ReviewConfig, replay: Replay, out: Path) -> dict[str, int]:
    """Write the static replay into ``out`` (which must not exist yet). Returns page counts."""
    if out.exists():
        raise FileExistsError(f"{out} exists: the replay is always written into a new folder")
    with ReviewStore(config.db) as s:
        ids = [r["record_id"] for r in s.records()]
        statuses = sorted({RecordStatus(r["status"]).value for r in s.records()})
    records = {rid: record_file(rid) for rid in ids}
    app = create_app(dataclasses.replace(config, replay=replay))
    pages: dict[str, tuple[str, int]] = {"index.html": ("/", 0)}
    pages |= {f"status-{st}.html": (f"/?status={st}", 0) for st in statuses}
    pages |= {path: (f"/records/{rid}", 1) for rid, path in records.items()}
    out.mkdir(parents=True)
    with TestClient(app) as client:
        for path, (url, depth) in pages.items():
            r = client.get(url)
            if r.status_code != 200:
                raise RuntimeError(f"{url} returned {r.status_code}")
            dest = out / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(_relink(r.text, depth, records), encoding="utf-8")
    shutil.copytree(HERE / "static", out / "static")
    (out / ".nojekyll").write_text("", encoding="utf-8")  # serve the files as they are
    return {"records": len(records), "pages": len(pages)}
