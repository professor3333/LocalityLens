"""GeoJSON export of approved records (RFC 7946), next to the Darwin Core CSV.

The same approved records and Darwin Core terms as :mod:`localitylens.export.darwin_core`, as
one ``FeatureCollection``. Where RFC 7946 forces a difference, it is explicit:

* **WGS 84.** RFC 7946 §4 allows only WGS 84 longitude/latitude, so the point is converted with
  :func:`localitylens.geo.datum.to_wgs84` (NAD83 → WGS 84 by EPSG:1188, a 4 m null
  transformation). ``geodeticDatum`` is ``EPSG:4326``, and the source point and datum stay in
  ``localitylens_source_latitude`` / ``_longitude`` / ``_datum``.
* **The circle grows by the transformation's accuracy.** ``coordinateUncertaintyInMeters`` is
  the proposal's radius plus that accuracy, rounded **up**, so it is never smaller than the CSV's.
  ``georeferenceRemarks`` says so.
* **A point-radius region is a Point.** GeoJSON has no circle; the radius stays in
  ``coordinateUncertaintyInMeters``. No footprint polygon is built yet, so ``footprintWKT`` is null.
* **Positions have 6 decimals** (RFC 7946 §11.2: about 10 cm), as in the CSV. ``Feature.id`` is the
  decision ID, which is unique per exported row. No ``crs`` member (RFC 7946 §4 removed it).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Final

from localitylens.export.darwin_core import DWC_COLUMNS, approved_georeferences
from localitylens.geo.datum import DATUM_TRANSFORM_VERSION, to_wgs84
from localitylens.geo.geodesy import EPSG_CODE
from localitylens.review.store import ReviewStore

GEOJSON_EXPORT_VERSION: Final = "geojson-export-1"
MEDIA_TYPE: Final = "application/geo+json"  # RFC 7946 §12


def _remark(operation: str, name: str, accuracy_m: float, source: str) -> str:
    if operation == "identity":
        return "coordinates are WGS 84 as computed (no datum transformation)"
    return (
        f"coordinates converted from {source} to WGS 84 (EPSG:4326) for GeoJSON with {operation} "
        f"({name}, accuracy {accuracy_m:g} m); coordinateUncertaintyInMeters includes those "
        f"{accuracy_m:g} m"
    )


def feature_collection(store: ReviewStore) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for a in approved_georeferences(store):
        conv = to_wgs84(a.point)
        lat = round(conv.coordinate.latitude, 6)
        lon = round(conv.coordinate.longitude, 6)
        props: dict[str, Any] = {}
        for col in DWC_COLUMNS:
            value = a.row[col]
            props[col] = value if value != "" else None
        props["decimalLatitude"] = lat
        props["decimalLongitude"] = lon
        props["geodeticDatum"] = EPSG_CODE[conv.coordinate.datum]
        props["coordinateUncertaintyInMeters"] = math.ceil(a.radius_m + conv.accuracy_m)
        remark = _remark(conv.operation, conv.operation_name, conv.accuracy_m,
                         EPSG_CODE[a.point.datum])  # fmt: skip
        props["georeferenceRemarks"] = " | ".join(
            [r for r in (a.row["georeferenceRemarks"], remark) if r]
        )
        if a.row["localitylens_human_edits"]:
            props["localitylens_human_edits"] = json.loads(a.row["localitylens_human_edits"])
        props["localitylens_source_latitude"] = float(a.row["decimalLatitude"])
        props["localitylens_source_longitude"] = float(a.row["decimalLongitude"])
        props["localitylens_source_datum"] = a.row["geodeticDatum"]
        props["localitylens_datum_transform"] = conv.operation
        features.append({
            "type": "Feature",
            "id": a.row["localitylens_decision_id"],
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": props,
        })  # fmt: skip
    return {
        "type": "FeatureCollection",
        "localitylens": {
            "export_version": GEOJSON_EXPORT_VERSION,
            "datum_transform_version": DATUM_TRANSFORM_VERSION,
        },
        "features": features,
    }


def export_geojson(store: ReviewStore, out: Path) -> int:
    """Write every approved record as one GeoJSON Feature. Returns the number written."""
    fc = feature_collection(store)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(fc, ensure_ascii=False, indent=1, sort_keys=False, allow_nan=False)
    out.write_text(text + "\n", encoding="utf-8")
    return len(fc["features"])
