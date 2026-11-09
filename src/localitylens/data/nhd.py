"""Read-only access to a USGS NHD state GeoPackage: geometries grouped by GNIS ID.

A GeoPackage is an SQLite database (OGC 12-128r18). It is opened read-only, and each geometry
blob is a GeoPackage header followed by standard WKB (section 2.1.3), which Shapely parses.
Only the three feature layers that carry ``gnis_id`` are read: flowlines, waterbodies and areas.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Final

import numpy as np
import shapely
from numpy.typing import NDArray
from shapely import wkb

LAYERS: Final = ("NHDFlowline", "NHDWaterbody", "NHDArea")
_ENVELOPE_BYTES: Final = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}


class GeoPackageError(ValueError):
    pass


def _coordinates(blob: bytes) -> NDArray[np.float64]:
    if blob[:2] != b"GP":
        raise GeoPackageError("not a GeoPackage geometry blob")
    envelope = (blob[3] >> 1) & 7
    if envelope not in _ENVELOPE_BYTES:
        raise GeoPackageError(f"invalid envelope indicator {envelope}")
    geom = wkb.loads(bytes(blob[8 + _ENVELOPE_BYTES[envelope] :]))
    xy: NDArray[np.float64] = shapely.get_coordinates(geom)  # 2D: longitude, latitude
    return xy


def _check(con: sqlite3.Connection) -> None:
    rows = dict(con.execute(
        "SELECT table_name, srs_id FROM gpkg_contents WHERE table_name IN (?, ?, ?)", LAYERS
    ).fetchall())  # fmt: skip
    for layer in LAYERS:
        if rows.get(layer) != 4269:
            raise GeoPackageError(f"{layer}: expected EPSG:4269 (NAD83), found {rows.get(layer)}")


def gnis_groups(path: Path) -> Iterator[tuple[int, NDArray[np.float64], dict[str, int]]]:
    """Per GNIS ID, in ID order: every vertex of every geometry carrying it, and the number of
    geometries per layer."""
    con = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        _check(con)
        union = " UNION ALL ".join(
            f"SELECT CAST(gnis_id AS INTEGER) AS gid, '{layer}' AS layer, SHAPE FROM {layer} "
            "WHERE gnis_id IS NOT NULL AND gnis_id != ''"
            for layer in LAYERS
        )
        current: int | None = None
        parts: list[NDArray[np.float64]] = []
        counts: dict[str, int] = {}
        for gid, layer, blob in con.execute(
            f"SELECT gid, layer, SHAPE FROM ({union}) ORDER BY gid"
        ):
            if gid != current and current is not None:
                if parts:
                    yield current, np.concatenate(parts), counts
                parts, counts = [], {}
            current = gid
            if blob is not None:
                parts.append(_coordinates(blob))
                counts[layer] = counts.get(layer, 0) + 1
        if current is not None and parts:
            yield current, np.concatenate(parts), counts
    finally:
        con.close()
