"""Snapshots of the two geometry sources behind derived extents: USGS NHD and Census TIGER places.

Same rules as the GNIS and GBIF snapshots: one immutable directory per snapshot under
``data/raw/<source>/``, a committed manifest with URL, SHA-256, size and dates, and a pinned
fetch that keeps a file only if it matches the manifest byte for byte. Licence and use
constraints are quoted from each product's own metadata.
"""

from __future__ import annotations

import shutil
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from localitylens.data import gnis_fetch
from localitylens.data.manifest import (
    ChecksumMismatchError,
    SnapshotFile,
    SnapshotManifest,
    sha256_file,
    write_manifest,
)


@dataclass(frozen=True, slots=True)
class GeometrySource:
    snapshot_id: str
    directory: str  # under the source's raw root
    url: str
    file: str
    publication_date: str
    source: str
    publisher: str
    licence: str
    usage_constraints: str
    citation: str


NHD: Final = GeometrySource(
    snapshot_id="nhd-co-2023-12-27",
    directory="2023-12-27",
    url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHD/State/GPKG/"
    "NHD_H_Colorado_State_GPKG.zip",
    file="NHD_H_Colorado_State_GPKG.zip",
    publication_date="2023-12-27",
    source="USGS National Hydrography Dataset Best Resolution (NHD) - Colorado (published "
    "20231227) GeoPackage",
    publisher="U.S. Geological Survey, National Geospatial Program",
    licence="U.S. Government work (USGS); public domain in the United States",
    usage_constraints=(
        "None. However, users should be aware that temporal changes may have occurred since "
        "this data set was collected and that some parts of this data may no longer represent "
        "actual surface conditions. (from the FGDC metadata <useconst>, first sentences)"
    ),
    citation="U.S. Geological Survey, National Hydrography Dataset Best Resolution (NHD) for "
    "Colorado, GeoPackage, published 2023-12-27",
)

TIGER_PLACE: Final = GeometrySource(
    snapshot_id="tiger-place-co-2025",
    directory="2025",
    url="https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_08_place.zip",
    file="tl_2025_08_place.zip",
    publication_date="2025-09-18",
    source="TIGER/Line Shapefile, Current, State, Colorado, Place (tl_2025_08_place)",
    publisher="U.S. Department of Commerce, U.S. Census Bureau, Geography Division",
    licence="Not copyrighted (U.S. Census Bureau); acknowledgement of the source is required",
    usage_constraints=(
        "The TIGER/Line Shapefile products are not copyrighted however TIGER/Line and Census "
        "TIGER are registered trademarks of the U.S. Census Bureau. These products are free to "
        "use in a product or publication, however acknowledgement must be given to the U.S. "
        "Census Bureau as the source. The boundary information in the TIGER/Line Shapefiles are "
        "for statistical data collection and tabulation purposes only; their depiction and "
        "designation for statistical purposes does not constitute a determination of "
        "jurisdictional authority or rights of ownership or entitlement and they are not legal "
        "land descriptions. (verbatim from the ISO metadata)"
    ),
    citation="U.S. Census Bureau, 2025 TIGER/Line Shapefiles: Places, Colorado",
)

SOURCES: Final = {s.snapshot_id: s for s in (NHD, TIGER_PLACE)}


def _manifest(spec: GeometrySource, path: Path, retrieved: datetime) -> SnapshotManifest:
    return SnapshotManifest(
        snapshot_id=spec.snapshot_id,
        source=spec.source,
        publisher=spec.publisher,
        retrieved_at=retrieved.isoformat(timespec="seconds"),
        licence=spec.licence,
        usage_constraints=spec.usage_constraints,
        citation=spec.citation,
        horizontal_datum="North American Datum of 1983",
        ellipsoid="Geodetic Reference System 80",
        files=(
            SnapshotFile(
                name=spec.file,
                url=spec.url,
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
                publication_date=spec.publication_date,
                server_last_modified=None,
            ),
        ),
        notes=(
            "Used only to derive feature extents (localitylens.geo.derived_extents); never "
            "shown to a model.",
        ),
    )


def adopt(spec: GeometrySource, downloaded: Path, raw_root: Path, manifest_dir: Path,
          retrieved: datetime | None = None) -> tuple[Path, SnapshotManifest]:  # fmt: skip
    """Move a freshly downloaded file into its snapshot directory and write a new manifest.
    Refuses if the snapshot or its manifest already exists (snapshots are write-once)."""
    final = raw_root / spec.directory
    manifest_path = manifest_dir / f"{spec.snapshot_id}.json"
    if final.exists() or manifest_path.exists():
        raise ChecksumMismatchError(f"{final} or {manifest_path} exists; snapshots are write-once")
    manifest = _manifest(spec, downloaded, retrieved or datetime.now(UTC))
    final.mkdir(parents=True)
    shutil.move(str(downloaded), final / spec.file)
    write_manifest(final / "manifest.json", manifest)
    write_manifest(manifest_path, manifest)
    return final, manifest


def fetch_geometry(
    snapshot_id: str, raw_root: Path, manifest_dir: Path
) -> tuple[Path, SnapshotManifest, list[str]]:
    """The pinned snapshot if its manifest is committed (checksums decide); otherwise a fresh
    download that writes the manifest."""
    spec = SOURCES[snapshot_id]
    if (manifest_dir / f"{snapshot_id}.json").is_file():
        return gnis_fetch.fetch_pinned_snapshot(
            snapshot_id, raw_root / spec.directory, raw_root, manifest_dir
        )
    incoming = raw_root / f".incoming-{uuid.uuid4().hex}"
    incoming.mkdir(parents=True)
    try:
        gnis_fetch._download(spec.url, incoming / spec.file)
        final, manifest = adopt(spec, incoming / spec.file, raw_root, manifest_dir)
        return final, manifest, [spec.url]
    finally:
        shutil.rmtree(incoming, ignore_errors=True)
