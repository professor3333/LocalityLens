"""GNIS snapshots: the pinned one (default) or the current USGS files (``--latest``).

USGS serves only its current GNIS files, so the snapshot a release is built on stops being
downloadable when USGS republishes. :func:`fetch_pinned_gnis` therefore downloads the pinned
snapshot from this project's GitHub release ``data-<snapshot id>`` (the original files,
unchanged), falling back to the USGS URLs in the manifest, and verifies every file against the
committed manifest in ``data/manifests``. :func:`fetch_gnis` downloads the current USGS files
and writes a new manifest. Run during ingestion only; the application never contacts USGS or
GitHub at runtime.
"""

from __future__ import annotations

import re
import shutil
import time
import urllib.request
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from localitylens.data.manifest import (
    ChecksumMismatchError,
    SnapshotFile,
    SnapshotManifest,
    load_manifest,
    sha256_file,
    verify_snapshot,
    write_manifest,
)

BASE_URL: Final = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames"
DOMESTIC_CO: Final = "DomesticNames_CO_Text.zip"
ALL_NAMES: Final = "AllNames_National_Text.zip"
FILES: Final[dict[str, str]] = {
    DOMESTIC_CO: f"{BASE_URL}/DomesticNames/{DOMESTIC_CO}",
    ALL_NAMES: f"{BASE_URL}/Topical/{ALL_NAMES}",
}

LICENCE: Final = "U.S. Government work (USGS); public domain in the United States"
USAGE_CONSTRAINTS: Final = (
    "None. Acknowledgment of the U.S. Geological Survey would be appreciated for products "
    "derived from these data. (verbatim from the FGDC metadata <useconst>)"
)
_PUBDATE_RE: Final = re.compile(r"<pubdate>(\d{8})</pubdate>")
_USER_AGENT: Final = "LocalityLens-ingest/0.1 (+https://github.com/professor3333/LocalityLens)"
MIRROR: Final = "https://github.com/professor3333/LocalityLens/releases/download"


def _download(url: str, dest: Path, attempts: int = 4) -> str | None:
    """Stream ``url`` to ``dest``; bounded retries with exponential backoff."""
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as resp, dest.open("wb") as out:
                shutil.copyfileobj(resp, out, length=1 << 20)
                last_modified: str | None = resp.headers.get("Last-Modified")
                return last_modified
        except OSError:
            dest.unlink(missing_ok=True)
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def zip_publication_date(path: Path) -> str | None:
    """First ``<pubdate>`` of the FGDC XML inside a GNIS zip, as YYYY-MM-DD."""
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.filename.endswith(".xml"):
                m = _PUBDATE_RE.search(zf.read(info).decode("utf-8", errors="replace"))
                if m:
                    d = m.group(1)
                    return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return None


def fetch_gnis(raw_root: Path, manifest_dir: Path) -> tuple[Path, SnapshotManifest]:
    """Download into a fresh directory, then move it to ``raw_root/<publication date>``.

    If that snapshot already exists, the new download must match it byte for byte;
    otherwise this raises instead of overwriting immutable data.
    """
    incoming = raw_root / f".incoming-{uuid.uuid4().hex}"
    incoming.mkdir(parents=True)
    try:
        retrieved_at = datetime.now(UTC).replace(microsecond=0).isoformat()
        files: list[SnapshotFile] = []
        for name, url in FILES.items():
            dest = incoming / name
            last_modified = _download(url, dest)
            files.append(
                SnapshotFile(
                    name=name,
                    url=url,
                    sha256=sha256_file(dest),
                    size_bytes=dest.stat().st_size,
                    publication_date=zip_publication_date(dest),
                    server_last_modified=last_modified,
                )
            )
        pubdate = files[0].publication_date
        if pubdate is None:
            raise RuntimeError("could not read publication date from GNIS metadata")
        snapshot_id = f"gnis-co-{pubdate}"
        manifest = SnapshotManifest(
            snapshot_id=snapshot_id,
            source="USGS Geographic Names Information System (GNIS)",
            publisher="U.S. Geological Survey, U.S. Board on Geographic Names",
            retrieved_at=retrieved_at,
            licence=LICENCE,
            usage_constraints=USAGE_CONSTRAINTS,
            citation=(
                "U.S. Geological Survey, Geographic Names Information System (GNIS) Domestic "
                f"Names for CO (published {pubdate}) and All Names (National). "
                "https://www.usgs.gov/us-board-on-geographic-names/download-gnis-data"
            ),
            horizontal_datum="North American Datum of 1983",
            ellipsoid="Geodetic Reference System 80",
            files=tuple(files),
            notes=(
                "DomesticNames_CO lists one row per feature with its primary county only.",
                "Missing source coordinates are encoded as 0.0 and are parsed as null.",
                "Most cultural feature classes (e.g. Locale, Mine) are not in Domestic Names.",
            ),
        )
        final = raw_root / pubdate
        if final.exists():
            existing = final / "manifest.json"
            if existing.is_file():
                verify_snapshot(final, manifest)  # raises if the published files changed
                shutil.rmtree(incoming)
                return final, manifest
            raise ChecksumMismatchError(f"{final} exists without a manifest; refusing to touch it")
        write_manifest(incoming / "manifest.json", manifest)
        incoming.rename(final)
        write_manifest(manifest_dir / f"{snapshot_id}.json", manifest)
        return final, manifest
    finally:
        if incoming.exists():
            shutil.rmtree(incoming)


def snapshot_directory(raw_root: Path, snapshot_id: str) -> Path:
    """``raw_root/<publication date>`` for a ``gnis-co-<date>`` snapshot ID."""
    if not snapshot_id.startswith("gnis-co-"):
        raise ValueError(f"not a GNIS snapshot ID: {snapshot_id!r}")
    return raw_root / snapshot_id.removeprefix("gnis-co-")


def fetch_pinned_gnis(
    snapshot_id: str, raw_root: Path, manifest_dir: Path
) -> tuple[Path, SnapshotManifest, list[str]]:
    """Download the pinned snapshot named by its committed manifest and verify it.

    Returns (directory, manifest, the source of each file). An existing, verified copy is
    reused. A file that matches neither the mirror nor USGS byte for byte is never kept.
    """
    manifest_path = manifest_dir / f"{snapshot_id}.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"no committed manifest {manifest_path}")
    manifest = load_manifest(manifest_path)
    final = snapshot_directory(raw_root, snapshot_id)
    if (final / "manifest.json").is_file():
        verify_snapshot(final, manifest)  # raises if a local copy was altered
        return final, manifest, ["already present"] * len(manifest.files)
    if final.exists():
        raise ChecksumMismatchError(f"{final} exists without a manifest; refusing to touch it")
    incoming = raw_root / f".incoming-{uuid.uuid4().hex}"
    incoming.mkdir(parents=True)
    sources: list[str] = []
    try:
        for f in manifest.files:
            dest = incoming / f.name
            for url in (f"{MIRROR}/data-{snapshot_id}/{f.name}", f.url):
                try:
                    _download(url, dest)
                except OSError:
                    continue
                if dest.stat().st_size == f.size_bytes and sha256_file(dest) == f.sha256:
                    sources.append(url)
                    break
                dest.unlink()  # e.g. USGS has republished: never keep a different file
            else:
                raise ChecksumMismatchError(
                    f"{f.name}: no source matches the manifest's SHA-256 {f.sha256[:12]}…"
                )
        verify_snapshot(incoming, manifest)
        write_manifest(incoming / "manifest.json", manifest)
        incoming.rename(final)
        return final, manifest, sources
    finally:
        if incoming.exists():
            shutil.rmtree(incoming)
