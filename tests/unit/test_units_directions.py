import pytest

from localitylens.geo.directions import CompassPoint, nominal_bearing, parse_direction
from localitylens.geo.units import LengthUnit, parse_unit, to_metres


def test_two_miles_is_exact() -> None:
    assert to_metres(2, LengthUnit.MILE) == pytest.approx(3218.688, abs=1e-9)


@pytest.mark.parametrize(
    ("unit", "metres"),
    [
        (LengthUnit.KILOMETRE, 1000.0),
        (LengthUnit.METRE, 1.0),
        (LengthUnit.FOOT, 0.3048),
        (LengthUnit.YARD, 0.9144),
    ],
)
def test_unit_factors(unit: LengthUnit, metres: float) -> None:
    assert to_metres(1, unit) == pytest.approx(metres)


def test_negative_distance_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        to_metres(-1, LengthUnit.MILE)


@pytest.mark.parametrize(
    ("text", "unit"),
    [
        ("mi", LengthUnit.MILE),
        ("Mi.", LengthUnit.MILE),
        ("miles", LengthUnit.MILE),
        ("km", LengthUnit.KILOMETRE),
        ("ft.", LengthUnit.FOOT),
        ("feet", LengthUnit.FOOT),
    ],
)
def test_parse_unit(text: str, unit: LengthUnit) -> None:
    assert parse_unit(text) is unit


@pytest.mark.parametrize("text", ["m", "m.", "furlongs", ""])
def test_ambiguous_or_unknown_units_are_not_guessed(text: str) -> None:
    assert parse_unit(text) is None


@pytest.mark.parametrize(
    ("text", "point"),
    [
        ("NE", CompassPoint.NE),
        ("N.E.", CompassPoint.NE),
        ("n.e", CompassPoint.NE),
        ("northeast", CompassPoint.NE),
        ("North-East", CompassPoint.NE),
        ("NNW", CompassPoint.NNW),
        ("N-NW", CompassPoint.NNW),
        ("W", CompassPoint.W),
        ("west", CompassPoint.W),
    ],
)
def test_parse_direction(text: str, point: CompassPoint) -> None:
    assert parse_direction(text) is point


@pytest.mark.parametrize("text", ["", "up", "NEN", "northerly", "NE of"])
def test_unparseable_directions(text: str) -> None:
    assert parse_direction(text) is None


def test_nominal_bearings() -> None:
    assert nominal_bearing(CompassPoint.N) == 0.0
    assert nominal_bearing(CompassPoint.NE) == 45.0
    assert nominal_bearing(CompassPoint.SSW) == 202.5
    bearings = [nominal_bearing(p) for p in CompassPoint]
    assert bearings == sorted(bearings)
    assert len(set(bearings)) == 16
