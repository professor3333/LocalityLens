"""Explicit datum transformation to WGS 84, for outputs that require it (GeoJSON, RFC 7946 §4).

Geometry and the Darwin Core CSV stay in the source datum (GNIS points are NAD83). Only an
output format that *requires* WGS 84 converts, and it does so here, with one named operation
whose accuracy is carried into the uncertainty:

* **NAD83 → WGS 84: EPSG:1188, "NAD83 to WGS 84 (1)".** A null transformation: the numbers do not
  change. EPSG gives its accuracy as 4 m. For Colorado PROJ prefers a grid-based route
  (``us_noaa_cohpgn.tif``, via NAD83(HARN)), but that grid is not installed and is not fetched at
  runtime, so the accuracy of the operation actually used is the one recorded.
  GNIS does not say which NAD83 realisation its points use, which is another reason not to claim
  a better transformation.
* **WGS 84 → WGS 84:** identity, accuracy 0.

The accuracy is added to ``coordinateUncertaintyInMeters`` by the exporter (GBIF Georeferencing
Best Practices §3.4.4 treats datum as an uncertainty source), so a converted circle never shrinks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from pyproj import Transformer

from localitylens.geo.geodesy import Coordinate, Datum

DATUM_TRANSFORM_VERSION: Final = "datum-1"
NAD83_TO_WGS84: Final = "EPSG:1188"


@dataclass(frozen=True, slots=True)
class Converted:
    coordinate: Coordinate  # in WGS 84
    operation: str  # EPSG code of the operation, or "identity"
    operation_name: str
    accuracy_m: float  # added to the uncertainty radius


def _nad83_transformer() -> Transformer:
    t = Transformer.from_pipeline("urn:ogc:def:coordinateOperation:EPSG::1188")
    # Refuse a PROJ database that describes the operation differently from what is documented.
    if t.name != "noop" or t.accuracy != 4.0:
        raise RuntimeError(f"EPSG:1188 is not the 4 m null transformation here: {t.description}")
    return t


_NAD83: Final = _nad83_transformer()


def to_wgs84(c: Coordinate) -> Converted:
    if c.datum is Datum.WGS84:
        return Converted(c, "identity", "WGS 84 (no transformation)", 0.0)
    if c.datum is Datum.NAD83:
        # EPSG:1188 uses latitude, longitude order on both sides.
        lat, lon = _NAD83.transform(c.latitude, c.longitude)
        out = Coordinate(latitude=float(lat), longitude=float(lon), datum=Datum.WGS84)
        return Converted(out, NAD83_TO_WGS84, _NAD83.description, float(_NAD83.accuracy))
    raise ValueError(f"no transformation to WGS 84 for datum {c.datum}")
