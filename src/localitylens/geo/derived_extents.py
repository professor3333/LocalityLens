"""Derived extents (``derived-extents-1``): feature extents computed from authoritative geometry.

The reviewed-extent store holds curator measurements for a few features. For everything else a
proposal's radius stays unknown (invariant 6). Where a public, authoritative dataset holds the
feature's own geometry, the same radial can be computed instead of measured by hand:

* **Places** (towns and census-designated places): Census TIGER/Line place polygons. A GNIS
  *Populated Place* takes a polygon when the names match by name key **and** its GNIS point
  lies inside the polygon. GNIS *Civil* and *Census* features match a polygon by ID (the
  polygon's ``PLACENS`` is their GNIS ID), and their point must also lie inside it.
* **Water features** (streams, lakes, reservoirs, glaciers…): USGS NHD geometries that carry the
  feature's GNIS ID, all layers together. The GNIS point must lie within 1 km of that geometry,
  so a point outside the dataset's coverage (Colorado River's, in the delta) is never measured
  against a part of the feature. A feature with any vertex outside the bounding box of the
  state's Census place polygons is left out: it reaches the state line, and the state extract
  may cut it short, which would make the radius too small. (That box lies inside the state, so
  the rule leaves out a few more features than strictly needed, never fewer.)

**The radial** is the geodesic distance (GRS80) from the GNIS representative point to the
farthest vertex of the geometry, rounded **up** to the next metre. It is measured from the point
the proposal uses, as in the reviewed store (BP §3.4.1), so the circle contains every vertex.

**Provenance.** Each row names its method, the source snapshot and the source feature IDs. The
proposal's rationale says "derived", never "measured" or "reviewed". A curator's reviewed
extent always takes precedence (:meth:`localitylens.geo.extents.ExtentStore.get`).
Boundaries are current, not historical: a town's limits in 1900 may have been much smaller.
"""

from __future__ import annotations

import csv
import hashlib
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from pyproj import Geod
from shapely.geometry import Point, Polygon

from localitylens.gazetteer.index import FeatureSummary, Gazetteer
from localitylens.gazetteer.keys import name_key
from localitylens.geo.georeference import ExtentEstimate, ExtentSource

DERIVED_VERSION: Final = "derived-extents-1"
METHOD_PLACE_NAME: Final = "census-place-polygon-by-name"
METHOD_PLACE_ID: Final = "census-place-polygon-by-gnis-id"
METHOD_NHD: Final = "nhd-geometry-by-gnis-id"
METHODS: Final = frozenset({METHOD_PLACE_NAME, METHOD_PLACE_ID, METHOD_NHD})
NHD_MAX_GAP_M: Final = 1000.0
CITE_RADIAL: Final = "BP §3.4.1"
_GEOD: Final = Geod(ellps="GRS80")  # NAD83: GNIS, TIGER and NHD all state it

DERIVED_COLUMNS: Final = (
    "gnis_id", "official_name", "feature_class", "county", "gazetteer_snapshot",
    "latitude", "longitude", "datum", "extent_m", "method", "source_snapshot", "source_ids",
    "vertices",
)  # fmt: skip

Ring = Sequence[tuple[float, float]]  # (longitude, latitude)


class DerivedStoreError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class DerivedExtent:
    feature_id: int
    official_name: str
    feature_class: str
    county: str
    latitude: float
    longitude: float
    extent_m: int
    method: str
    source_snapshot: str
    source_ids: str
    vertices: int

    def estimate(self) -> ExtentEstimate:
        how = {
            METHOD_PLACE_NAME: "Census TIGER/Line place polygon of the same name containing the "
            "GNIS point",
            METHOD_PLACE_ID: "Census TIGER/Line place polygon with this GNIS ID",
            METHOD_NHD: "USGS NHD geometry carrying this GNIS ID",
        }[self.method]
        return ExtentEstimate(
            radius_m=float(self.extent_m),
            source=ExtentSource.DERIVED,
            rationale=(
                f"radial of {self.official_name} from the GNIS representative point "
                f"({CITE_RADIAL}): farthest of {self.vertices:,} vertices of the {how} "
                f"({self.source_snapshot}: {self.source_ids}); current boundaries, not "
                f"curator-reviewed ({DERIVED_VERSION})"
            ),
        )


def farthest_vertex_m(feature: FeatureSummary, rings: Iterable[Ring]) -> tuple[int, int]:
    """(radial rounded up to the metre, vertices considered) from the feature's GNIS point."""
    lons: list[float] = []
    lats: list[float] = []
    for ring in rings:
        for lon, lat in ring:
            lons.append(lon)
            lats.append(lat)
    if not lons:
        raise ValueError("no vertices")
    p = feature.primary_point
    _, _, dist = _GEOD.inv([p.longitude] * len(lons), [p.latitude] * len(lats), lons, lats)
    return math.ceil(max(dist)), len(lons)


def inside(feature: FeatureSummary, rings: Iterable[Ring]) -> bool:
    """Even-odd rule over all rings, so holes count as outside."""
    pt = Point(feature.primary_point.longitude, feature.primary_point.latitude)
    crossings = sum(1 for ring in rings if len(ring) >= 4 and Polygon(ring).covers(pt))
    return crossings % 2 == 1


def _row(f: FeatureSummary, extent: int, vertices: int, method: str, snapshot: str,
         ids: str) -> DerivedExtent:  # fmt: skip
    return DerivedExtent(feature_id=f.feature_id, official_name=f.official_name,
                         feature_class=f.feature_class, county=f.county_name,
                         latitude=f.primary_point.latitude, longitude=f.primary_point.longitude,
                         extent_m=extent, method=method, source_snapshot=snapshot,
                         source_ids=ids, vertices=vertices)  # fmt: skip


def derive_places(
    places: Iterable[tuple[dict[str, str], Sequence[Ring]]],
    gazetteer: Gazetteer,
    snapshot: str,
) -> list[DerivedExtent]:
    """Extents for populated places (by name and containment) and civil/census features (by
    ID and containment). A feature that two polygons claim is left out: ambiguous."""
    by_name: dict[str, list[FeatureSummary]] = {}
    for f in gazetteer.features(["Populated Place"]):
        by_name.setdefault(name_key(f.official_name), []).append(f)
    by_id = {f.feature_id: f for f in gazetteer.features(["Civil", "Census"])}
    found: dict[int, list[DerivedExtent]] = {}
    for attrs, rings in places:
        geoid = attrs.get("GEOID", "")
        for f in by_name.get(name_key(attrs.get("NAME", "")), []):
            if inside(f, rings):
                extent, n = farthest_vertex_m(f, rings)
                found.setdefault(f.feature_id, []).append(
                    _row(f, extent, n, METHOD_PLACE_NAME, snapshot, f"GEOID {geoid}")
                )
        ns = attrs.get("PLACENS", "").lstrip("0")
        f2 = by_id.get(int(ns)) if ns.isdigit() else None
        if f2 is not None and inside(f2, rings):
            extent, n = farthest_vertex_m(f2, rings)
            found.setdefault(f2.feature_id, []).append(
                _row(f2, extent, n, METHOD_PLACE_ID, snapshot, f"GEOID {geoid}")
            )
    return [rows[0] for _, rows in sorted(found.items()) if len(rows) == 1]


def ring_bounds(rings: Iterable[Ring]) -> tuple[float, float, float, float]:
    """(west, south, east, north) of every vertex."""
    lons, lats = zip(*(v for ring in rings for v in ring), strict=True)
    return min(lons), min(lats), max(lons), max(lats)


def derive_nhd(
    groups: Iterable[tuple[int, Any, dict[str, int]]],
    gazetteer: Gazetteer,
    snapshot: str,
    within: tuple[float, float, float, float],
) -> list[DerivedExtent]:
    """Extents for any GNIS feature whose ID NHD geometries carry. ``groups`` yields, per GNIS
    ID, an (n, 2) array of every vertex (longitude, latitude) and the geometry count per layer."""
    west, south, east, north = within
    out: list[DerivedExtent] = []
    for fid, xy, counts in groups:
        lon, lat = xy[:, 0], xy[:, 1]
        if bool(((lon < west) | (lon > east) | (lat < south) | (lat > north)).any()):
            continue  # crosses the covered area's edge: the extract may truncate it
        f = gazetteer.feature(fid)
        if f is None or (f.primary_point.latitude == 0 and f.primary_point.longitude == 0):
            continue
        p = f.primary_point
        n = len(xy)
        _, _, dist = _GEOD.inv([p.longitude] * n, [p.latitude] * n, xy[:, 0], xy[:, 1])
        if float(min(dist)) > NHD_MAX_GAP_M:  # the point is not on this geometry: never measure
            continue
        ids = "; ".join(f"{layer} x{k}" for layer, k in sorted(counts.items()))
        out.append(_row(f, math.ceil(float(max(dist))), n, METHOD_NHD, snapshot, ids))
    return out


def write_derived(path: Path, rows: Iterable[DerivedExtent], snapshot_id: str) -> int:
    """Write the derived store (never over an existing file). Returns the row count."""
    ordered = sorted(rows, key=lambda r: r.feature_id)
    ids = [r.feature_id for r in ordered]
    if len(ids) != len(set(ids)):
        raise DerivedStoreError("a feature appears twice; reviewed precedence would be ambiguous")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(DERIVED_COLUMNS)
        for r in ordered:
            w.writerow([r.feature_id, r.official_name, r.feature_class, r.county, snapshot_id,
                        repr(r.latitude), repr(r.longitude), "NAD83", r.extent_m, r.method,
                        r.source_snapshot, r.source_ids, r.vertices])  # fmt: skip
    return len(ordered)


@dataclass(frozen=True, slots=True)
class DerivedStore:
    path: Path
    sha256: str
    entries: dict[int, DerivedExtent]

    def summary(self) -> dict[str, Any]:
        methods: dict[str, int] = {}
        for e in self.entries.values():
            methods[e.method] = methods.get(e.method, 0) + 1
        return {
            "version": DERIVED_VERSION,
            "sha256": self.sha256,
            "derived": len(self.entries),
            "by_method": dict(sorted(methods.items())),
        }


def load_derived(path: Path, gazetteer: Gazetteer) -> DerivedStore:
    """Load and check every row against the pinned snapshot; refuse the file on any mismatch."""
    snapshot = gazetteer.snapshot_id
    entries: dict[int, DerivedExtent] = {}
    problems: list[str] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != DERIVED_COLUMNS:
            raise DerivedStoreError(f"{path}: columns must be {', '.join(DERIVED_COLUMNS)}")
        for n, row in enumerate(reader, start=1):
            fid = int(row["gnis_id"])
            f = gazetteer.feature(fid)
            expected = None if f is None else {
                "official_name": f.official_name, "feature_class": f.feature_class,
                "county": f.county_name, "gazetteer_snapshot": snapshot, "datum": "NAD83",
            }  # fmt: skip
            if expected is None:
                problems.append(f"row {n}: GNIS {fid} is not in {snapshot}")
                continue
            bad = [c for c, v in expected.items() if row[c] != v]
            p = f.primary_point  # type: ignore[union-attr]
            if (
                abs(float(row["latitude"]) - p.latitude) > 1e-9
                or abs(float(row["longitude"]) - p.longitude) > 1e-9
            ):
                bad.append("point")
            if row["method"] not in METHODS or int(row["extent_m"]) <= 0 or fid in entries:
                bad.append("method/extent/duplicate")
            if bad:
                problems.append(f"row {n}: {', '.join(bad)}")
                continue
            entries[fid] = DerivedExtent(
                feature_id=fid, official_name=row["official_name"],
                feature_class=row["feature_class"], county=row["county"],
                latitude=p.latitude, longitude=p.longitude, extent_m=int(row["extent_m"]),
                method=row["method"], source_snapshot=row["source_snapshot"],
                source_ids=row["source_ids"], vertices=int(row["vertices"]),
            )  # fmt: skip
    if problems:
        raise DerivedStoreError(f"{len(problems)} problem(s) in {path}: {'; '.join(problems[:3])}")
    return DerivedStore(path=path, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        entries=entries)  # fmt: skip
