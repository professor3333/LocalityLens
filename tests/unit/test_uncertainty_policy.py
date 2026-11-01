"""Uncertainty policy against the published GBIF examples (exact values from the sources)."""

import math

import pytest

from localitylens.extract.quantities import parse_quantity
from localitylens.geo import uncertainty as policy
from localitylens.geo.directions import CompassPoint
from localitylens.geo.geodesy import Datum


def _unc(text: str) -> float:
    q = parse_quantity(text)
    assert q is not None
    return policy.distance_precision_uncertainty(q)


# BP §3.4.6 Table 5, "Recommended Uncertainty" column (same units as the distance).
TABLE_5 = [
    ("10.1", 0.05), ("10.25", 0.125), ("10.5", 0.25), ("10.6", 0.05), ("10.75", 0.125),
    ("10", 0.5), ("15", 0.5), ("30", 0.5), ("33", 0.5), ("100", 5), ("140", 5), ("200", 5),
    ("1000", 50), ("2000", 50),
]  # fmt: skip


@pytest.mark.parametrize(("distance", "expected"), TABLE_5)
def test_distance_precision_matches_every_row_of_bp_table_5(distance: str, expected: float) -> None:
    assert _unc(distance) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("distance", "precision"),
    [("6", 1.0), ("3.75", 0.25)],  # QRG §1.6.13 examples: "6 mi" -> 1 mi, "3.75 km" -> 1/4 km
)
def test_distance_precision_matches_qrg_examples(distance: str, precision: float) -> None:
    q = parse_quantity(distance)
    assert q is not None
    assert policy.distance_precision(q)[0] == pytest.approx(precision)


@pytest.mark.parametrize(
    ("written", "expected"),
    [("1/2", 0.25), ("1 1/2", 0.25), ("½", 0.25), ("2¼", 0.125), ("1/3", 1 / 6), ("3/8", 1 / 16)],
)
def test_written_fractions_use_their_denominator(written: str, expected: float) -> None:
    # Calculator getDistancePrecisionError: 1/2 -> 0.25, 1/3 -> 0.1666667, 1/4 -> 0.125 ...
    assert _unc(written) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("point", "alpha"),
    [(CompassPoint.N, 45.0), (CompassPoint.E, 45.0), (CompassPoint.NE, 22.5),
     (CompassPoint.SW, 22.5), (CompassPoint.NNE, 11.25), (CompassPoint.WSW, 11.25)],
)  # fmt: skip
def test_heading_uncertainty_matches_bp_table_4(point: CompassPoint, alpha: float) -> None:
    assert policy.heading_uncertainty_deg(point) == alpha


def test_every_compass_point_has_a_heading_class() -> None:
    counts = {cls: 0 for cls in policy.HeadingClass}
    for point in CompassPoint:
        counts[policy.heading_class(point)] += 1
    assert list(counts.values()) == [4, 4, 8]


def test_heading_error_reproduces_bp_worked_example() -> None:
    # BP §3.4.5: "10 km NE of Lambert Centre" ignoring distance imprecision -> 3.90 km.
    assert policy.heading_distance_error(10.0, 0.0, 22.5) == pytest.approx(3.90, abs=0.005)


def test_coordinate_precision_reproduces_qrg_quarter_degree_grid() -> None:
    # QRG Table 1: "Grid, 1/4 degree precision (at equator): 39226 m".
    error = policy.coordinate_precision_error_m(0.0, Datum.WGS84, 0.25)
    assert error == pytest.approx(39226, rel=5e-4)


def test_nearest_second_in_colorado_is_tens_of_metres() -> None:
    error = policy.coordinate_precision_error_m(40.0, Datum.NAD83, 1 / 3600)
    lat_m, lon_m = policy.metres_per_degree(40.0, Datum.NAD83)
    assert error == pytest.approx(math.hypot(lat_m, lon_m) / 3600)
    assert 35 < error < 45


def test_metres_per_degree_matches_known_values() -> None:
    lat_m, lon_m = policy.metres_per_degree(0.0, Datum.WGS84)
    assert lat_m == pytest.approx(110_574, rel=1e-4)  # meridian degree at the equator
    assert lon_m == pytest.approx(111_320, rel=1e-4)  # equatorial degree


def test_policy_id_is_versioned() -> None:
    assert policy.POLICY_ID.endswith(f"/{policy.POLICY_VERSION}")
    assert policy.UNKNOWN_DATUM_M == 5359.0  # BP §3.4.4 worst case
