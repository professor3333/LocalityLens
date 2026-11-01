"""Uncertainty policy: named, cited rules for the point-radius method.

Every value here comes from a primary source, cited next to it:

* **BP**: Chapman & Wieczorek (2020) *Georeferencing Best Practices*, GBIF.
  https://docs.gbif.org/georeferencing-best-practices/1.0/en/
* **QRG**: Zermoglio et al. (2020) *Georeferencing Quick Reference Guide*, GBIF.
  https://docs.gbif.org/georeferencing-quick-reference-guide/1.0/en/
* **Calculator**: Wieczorek & Wieczorek, *Georeferencing Calculator* source code
  (https://github.com/VertNet/georefcalculator, Apache-2.0), files ``support.js`` and
  ``gci_ui.js``. This is the reference implementation that BP §3.4.7 defers to for combining
  uncertainties.

Changing any rule changes results, so it requires bumping :data:`POLICY_VERSION`.
"""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Final

from localitylens.extract.schema import ParsedQuantity
from localitylens.geo.directions import CompassPoint
from localitylens.geo.geodesy import Datum, geod_for

POLICY_VERSION: Final = "1"
POLICY_ID: Final = f"gbif-bp-2020/{POLICY_VERSION}"

# BP §3.4.4: worst case when the datum is unknown and cannot be looked up by location.
UNKNOWN_DATUM_M: Final = 5359.0

# GNIS records coordinates in degrees-minutes-seconds to the nearest second (prim_lat_dms,
# e.g. "370035N"); the decimal columns are conversions of those values.
GNIS_COORDINATE_PRECISION_DEG: Final = 1.0 / 3600.0

# QRG §2.1.2, Table 1: default geographic radials for small features known only by a label or a
# gazetteer point. Only types that map unambiguously to a GNIS feature class are listed; "small
# stream" is excluded because GNIS does not say whether a stream is small.
DEFAULT_RADIAL_BY_GNIS_CLASS_M: Final[dict[str, float]] = {
    "Spring": 3.0,  # "spring, bore, tank, well, or waterhole: 3 m"
}

CITE_HEADING: Final = "BP §3.4.5 Table 4; Calculator getDirectionError"
CITE_DISTANCE_PRECISION: Final = "BP §3.4.6 Table 5; Calculator getDistancePrecisionError"
CITE_COMBINATION: Final = "BP §3.4.7; Calculator calculateMaxErrorDistance"
CITE_COORDINATE_PRECISION: Final = "Calculator getCoordPrecisionError"
CITE_DATUM: Final = "BP §3.4.4"
CITE_EXTENT: Final = "BP §3.4.1; QRG §2.1.2 Table 1"
CITE_COORDINATE_SOURCE: Final = "Calculator getMapScaleError (gazetteer source = 0)"
CITE_ADVERBIAL: Final = "BP §2.2 (adverbial modifiers such as 'about')"
CITE_NEAR: Final = "QRG §2.1.3.8"
CITE_HEADING_ONLY: Final = "QRG §2.2.2"
CITE_TRUE_NORTH: Final = "QRG §1.6.10"


class HeadingClass(StrEnum):
    CARDINAL = "cardinal"  # N, E, S, W
    INTERCARDINAL = "intercardinal"  # NE, SE, SW, NW
    SECONDARY_INTERCARDINAL = "secondary_intercardinal"  # NNE, ENE, ...


_HEADING_DEG: Final[dict[HeadingClass, float]] = {
    HeadingClass.CARDINAL: 45.0,
    HeadingClass.INTERCARDINAL: 22.5,
    HeadingClass.SECONDARY_INTERCARDINAL: 11.25,
}


def heading_class(point: CompassPoint) -> HeadingClass:
    letters = len(point.value)
    if letters == 1:
        return HeadingClass.CARDINAL
    if letters == 2:
        return HeadingClass.INTERCARDINAL
    return HeadingClass.SECONDARY_INTERCARDINAL


def heading_uncertainty_deg(point: CompassPoint) -> float:
    """Half-width of the direction sector (BP Table 4: N 45°, NE 22.5°, NNE 11.25°)."""
    return _HEADING_DEG[heading_class(point)]


def distance_precision(q: ParsedQuantity) -> tuple[float, str]:
    """Precision of a written distance, in the distance's own units, plus the rule applied.

    BP §3.4.6: precision is 1 / the fractional denominator. For integers, BP's rule (powers of
    ten take ten to the next lower power) together with every row of Table 5 is matched by
    ``10 ** max(0, digits - 2)``: 10, 15, 30 and 33 give 1; 100, 140 and 200 give 10; 1000 and
    2000 give 100. Single digits give 1 (QRG §1.6.13: "6 mi" has a precision of 1 mi).
    The uncertainty is half the precision.
    """
    if q.fraction_denominator is not None:
        return 1.0 / q.fraction_denominator, f"fraction 1/{q.fraction_denominator}"
    if q.decimal_places > 0:
        frac = q.value - math.floor(q.value)
        for den in (2, 4, 8):
            numerator = frac * den
            if math.isclose(numerator, round(numerator), abs_tol=1e-9) and round(numerator):
                return 1.0 / den, f"decimal = exact 1/{den}"
        return 10.0**-q.decimal_places, f"{q.decimal_places}-decimal number"
    digits = len(str(round(q.value)))
    precision = 10.0 ** max(0, digits - 2)
    return precision, f"{digits}-digit integer"


def distance_precision_uncertainty(q: ParsedQuantity) -> float:
    """Uncertainty from distance precision, in the distance's units (half the precision)."""
    return distance_precision(q)[0] / 2.0


def heading_distance_error(offset: float, distance_error: float, alpha_deg: float) -> float:
    """Calculator ``getDirectionError``: distance from the offset point to the farthest corner
    of the region bounded by the heading sector ±alpha and distance ``offset + distance_error``.

    Units are whatever ``offset`` and ``distance_error`` use.
    """
    a = math.radians(alpha_deg)
    x = offset * math.cos(a)
    y = offset * math.sin(a)
    xp = offset + distance_error
    return math.hypot(xp - x, y)


def metres_per_degree(latitude: float, datum: Datum) -> tuple[float, float]:
    """(lat, lon) metres per degree at a latitude, from the ellipsoid's radii of curvature.

    Same construction as the Calculator's ``calculateLatLongMetersPerDegree``:
    M = a(1-e²)/(1-e²sin²φ)^1.5 (meridian), N = a/(1-e²sin²φ)^0.5 (prime vertical).
    """
    geod = geod_for(datum)
    a, f = geod.a, geod.f
    e2 = 2.0 * f - f * f
    s2 = math.sin(math.radians(latitude)) ** 2
    m = a * (1.0 - e2) / (1.0 - e2 * s2) ** 1.5
    n = a / math.sqrt(1.0 - e2 * s2)
    k = math.pi / 180.0
    return k * m, k * n * math.cos(math.radians(latitude))


def coordinate_precision_error_m(latitude: float, datum: Datum, precision_deg: float) -> float:
    """Calculator ``getCoordPrecisionError``: precision * hypot(lat m/deg, lon m/deg)."""
    lat_m, lon_m = metres_per_degree(latitude, datum)
    return precision_deg * math.hypot(lat_m, lon_m)
