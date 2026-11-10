"""Property tests for invariants every pipeline stage relies on."""

import unicodedata

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from localitylens.extract.schema import ExtractionOutput
from localitylens.extract.validate import validate_extraction
from localitylens.geo.geodesy import Coordinate, Datum, forward, inverse
from localitylens.ingest.normalize import normalize

texts = st.text(
    alphabet=st.characters(codec="utf-8", exclude_categories=("Cs",)),
    max_size=80,
)


@given(texts)
def test_normalized_chars_map_inside_original(original: str) -> None:
    n = normalize(original)
    assert len(n.starts) == len(n.ends) == len(n.text)
    for start, end in zip(n.starts, n.ends, strict=True):
        assert 0 <= start < end <= len(original)


@given(texts)
def test_normalized_text_has_no_whitespace_runs(original: str) -> None:
    n = normalize(original)
    assert n.text == n.text.strip()
    assert "  " not in n.text
    assert all(not ch.isspace() or ch == " " for ch in n.text)


@pytest.mark.parametrize("original", ["\r\u20e5", "0\r\u20e5", "a \u0301b", "\t\u0301"])
def test_whitespace_before_a_combining_mark_is_still_whitespace(original: str) -> None:
    n = normalize(original)  # found by Hypothesis: "\r" + a mark used to survive as one cluster
    assert n.text == n.text.strip()
    assert all(not ch.isspace() or ch == " " for ch in n.text)


@given(texts)
def test_normalization_is_idempotent(original: str) -> None:
    once = normalize(original).text
    assert normalize(once).text == once


@given(texts)
def test_non_space_chars_come_from_equivalent_original_text(original: str) -> None:
    n = normalize(original)
    for i, ch in enumerate(n.text):
        if ch == " ":
            continue
        source = original[n.starts[i] : n.ends[i]]
        assert ch in unicodedata.normalize("NFC", source)


@given(st.data())
def test_any_located_quote_maps_to_its_original_text(data: st.DataObject) -> None:
    words = data.draw(
        st.lists(st.text(alphabet="abcXYZ.,", min_size=1, max_size=6), min_size=1, max_size=6)
    )
    seps = data.draw(
        st.lists(
            st.sampled_from([" ", "  ", "\n", "\t "]), min_size=len(words), max_size=len(words)
        )
    )
    original = "".join(s + w for s, w in zip(seps, words, strict=True))
    n = normalize(original)
    i = data.draw(st.integers(0, len(words) - 1))
    j = data.draw(st.integers(i, len(words) - 1))
    quote = " ".join(words[i : j + 1])
    out = ExtractionOutput.model_validate(
        {"relation": "named_feature", "reference_feature": {"name_quote": quote}}
    )
    result = validate_extraction(out, n)
    assert result.ok
    assert result.interpretation is not None
    feature = result.interpretation.reference_feature
    assert feature is not None
    span = feature.span
    assert original[span.start : span.end] == span.text
    assert " ".join(span.text.split()).casefold() == quote.casefold()


@given(
    lat=st.floats(-80, 80),
    lon=st.floats(-179, 179),
    bearing=st.floats(0, 359.999),
    dist=st.floats(1.0, 200_000.0),
    datum=st.sampled_from(list(Datum)),
)
def test_geodesic_forward_inverse_round_trip(
    lat: float, lon: float, bearing: float, dist: float, datum: Datum
) -> None:
    origin = Coordinate(latitude=lat, longitude=lon, datum=datum)
    dest = forward(origin, bearing, dist)
    assume(-180 < dest.longitude < 180)
    back_bearing, back_dist = inverse(origin, dest)
    assert back_dist == pytest.approx(dist, rel=1e-9, abs=1e-6)
    diff = abs((back_bearing - bearing + 180) % 360 - 180)
    assert diff < 1e-6
