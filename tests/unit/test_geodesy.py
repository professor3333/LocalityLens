import pytest

from localitylens.geo.geodesy import Coordinate, Datum, distance_m, forward, inverse

# Synthetic origin for tests only. It is not a real feature's coordinate.
ORIGIN = Coordinate(latitude=40.0, longitude=-105.5, datum=Datum.NAD83)


def test_forward_then_inverse_recovers_bearing_and_distance() -> None:
    dest = forward(ORIGIN, 45.0, 3218.688)
    bearing, dist = inverse(ORIGIN, dest)
    assert dist == pytest.approx(3218.688, abs=1e-6)
    assert bearing == pytest.approx(45.0, abs=1e-9)
    assert dest.datum is Datum.NAD83
    assert dest.latitude > ORIGIN.latitude
    assert dest.longitude > ORIGIN.longitude


def test_zero_distance_is_identity() -> None:
    dest = forward(ORIGIN, 123.0, 0.0)
    assert distance_m(ORIGIN, dest) == pytest.approx(0.0, abs=1e-9)


def test_negative_distance_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        forward(ORIGIN, 0.0, -1.0)


def test_mixed_datums_are_refused() -> None:
    other = Coordinate(latitude=40.0, longitude=-105.4, datum=Datum.WGS84)
    with pytest.raises(ValueError, match="different datums"):
        inverse(ORIGIN, other)


def test_coordinate_rejects_out_of_range_and_extra_fields() -> None:
    with pytest.raises(ValueError, match="less than or equal"):
        Coordinate(latitude=91, longitude=0, datum=Datum.WGS84)
    with pytest.raises(ValueError, match="Extra inputs"):
        Coordinate.model_validate({"latitude": 0, "longitude": 0, "datum": "WGS84", "elev": 1})
