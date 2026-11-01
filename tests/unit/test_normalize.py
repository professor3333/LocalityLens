import pytest

from localitylens.ingest.normalize import normalize


def test_collapses_whitespace_and_maps_back() -> None:
    original = "  Larimer Co.,\r\n  Colo.,\t2 mi  NE "
    n = normalize(original)
    assert n.text == "Larimer Co., Colo., 2 mi NE"
    start = n.text.index("2 mi")
    assert n.original_slice(start, start + 4) == "2 mi"
    # The single space between "Co.," and "Colo." stands for the whole original run.
    space = n.text.index(" Colo")
    o_start, o_end = n.to_original(space, space + 1)
    assert original[o_start:o_end] == "\r\n  "


def test_nfc_composes_decomposed_accents() -> None:
    original = "Café Creek"  # e + combining acute
    n = normalize(original)
    assert n.text == "Café Creek"
    start = n.text.index("é")
    assert n.original_slice(start, start + 1) == "é"


def test_empty_and_blank() -> None:
    assert normalize("").text == ""
    assert normalize(" \n\t ").text == ""


def test_out_of_range_span_rejected() -> None:
    n = normalize("abc")
    with pytest.raises(ValueError, match="outside"):
        n.to_original(1, 4)
    with pytest.raises(ValueError, match="outside"):
        n.to_original(2, 2)
