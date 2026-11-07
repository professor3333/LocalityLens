"""The one datum transformation (NAD83 → WGS 84 for GeoJSON). Coordinates are synthetic."""

from hypothesis import given
from hypothesis import strategies as st

from localitylens.geo.datum import NAD83_TO_WGS84, to_wgs84
from localitylens.geo.geodesy import Coordinate, Datum


def test_nad83_uses_the_named_null_transformation() -> None:
    c = to_wgs84(Coordinate(latitude=40.0, longitude=-105.5, datum=Datum.NAD83))
    assert c.operation == NAD83_TO_WGS84 == "EPSG:1188"
    assert c.accuracy_m == 4.0  # EPSG's stated accuracy, added to the uncertainty radius
    assert c.coordinate == Coordinate(latitude=40.0, longitude=-105.5, datum=Datum.WGS84)


def test_wgs84_is_left_alone() -> None:
    src = Coordinate(latitude=39.1, longitude=-104.2, datum=Datum.WGS84)
    c = to_wgs84(src)
    assert (c.coordinate, c.operation, c.accuracy_m) == (src, "identity", 0.0)


@given(lat=st.floats(36.9, 41.1), lon=st.floats(-109.1, -102.0))
def test_conversion_moves_no_number_and_never_swaps_axes(lat: float, lon: float) -> None:
    c = to_wgs84(Coordinate(latitude=lat, longitude=lon, datum=Datum.NAD83)).coordinate
    assert (c.latitude, c.longitude, c.datum) == (lat, lon, Datum.WGS84)
