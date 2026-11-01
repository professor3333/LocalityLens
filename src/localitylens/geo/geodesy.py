"""Geodesic calculations on the ellipsoid of the source datum.

Every coordinate carries its datum. Calculations use that datum's ellipsoid, and nothing is
silently converted to WGS84. (Datum *transformations*, if ever needed, belong in their own
explicit, tested step.)
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field
from pyproj import Geod


class Datum(StrEnum):
    WGS84 = "WGS84"
    NAD83 = "NAD83"


EPSG_CODE: Final[dict[Datum, str]] = {
    Datum.WGS84: "EPSG:4326",
    Datum.NAD83: "EPSG:4269",
}

_ELLIPSOID: Final[dict[Datum, str]] = {
    Datum.WGS84: "WGS84",
    Datum.NAD83: "GRS80",
}

_GEODS: Final[dict[Datum, Geod]] = {datum: Geod(ellps=ell) for datum, ell in _ELLIPSOID.items()}


class Coordinate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    datum: Datum


def geod_for(datum: Datum) -> Geod:
    return _GEODS[datum]


def forward(origin: Coordinate, bearing_deg: float, distance_m: float) -> Coordinate:
    """Point reached from ``origin`` along a geodesic with the given initial bearing and length."""
    if distance_m < 0:
        raise ValueError(f"distance must be non-negative, got {distance_m}")
    lon, lat, _ = geod_for(origin.datum).fwd(
        origin.longitude, origin.latitude, bearing_deg, distance_m
    )
    return Coordinate(latitude=float(lat), longitude=float(lon), datum=origin.datum)


def inverse(a: Coordinate, b: Coordinate) -> tuple[float, float]:
    """Return ``(initial_bearing_deg in [0, 360), distance_m)`` from ``a`` to ``b``."""
    if a.datum != b.datum:
        raise ValueError(f"coordinates use different datums: {a.datum} vs {b.datum}")
    az12, _, dist = geod_for(a.datum).inv(a.longitude, a.latitude, b.longitude, b.latitude)
    return float(az12) % 360.0, float(dist)


def distance_m(a: Coordinate, b: Coordinate) -> float:
    return inverse(a, b)[1]
