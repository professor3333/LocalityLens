import pytest

from localitylens.extract.quantities import parse_quantity


@pytest.mark.parametrize(
    ("text", "value", "decimals", "denominator"),
    [
        ("2", 2.0, 0, None),
        ("2.5", 2.5, 1, None),
        (".5", 0.5, 1, None),
        ("12.25", 12.25, 2, None),
        ("1/2", 0.5, 0, 2),
        ("1 1/2", 1.5, 0, 2),
        ("1-1/2", 1.5, 0, 2),
        ("½", 0.5, 0, 2),
        ("1½", 1.5, 0, 2),
        ("3 ¼", 3.25, 0, 4),
    ],
)
def test_parses_label_numbers(
    text: str, value: float, decimals: int, denominator: int | None
) -> None:
    q = parse_quantity(text)
    assert q is not None
    assert q.value == pytest.approx(value)
    assert q.decimal_places == decimals
    assert q.fraction_denominator == denominator


@pytest.mark.parametrize(
    "text", ["", "twenty-five", "zero", "0", "0.0", "1/0", "0/3", "2.", "-1", "2 mi"]
)
def test_rejects_non_numbers_and_non_positive(text: str) -> None:
    assert parse_quantity(text) is None


@pytest.mark.parametrize(("text", "value", "denominator"), [
    ("Nine", 9.0, None), ("two", 2.0, None), ("TWENTY", 20.0, None), ("half", 0.5, 2),
])  # fmt: skip
def test_spelled_out_numbers_parse_with_the_precision_of_their_digits(
    text: str, value: float, denominator: int | None
) -> None:
    q = parse_quantity(text)
    assert q is not None
    assert (q.value, q.decimal_places, q.fraction_denominator) == (value, 0, denominator)
