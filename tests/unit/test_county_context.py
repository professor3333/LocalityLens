"""Supplied county values (COUNTY_CONTEXT_VERSION 1)."""

import pytest

from localitylens.resolve.county import is_placeholder, supplied_counties


@pytest.mark.parametrize(("value", "expected"), [
    ("Larimer", ("Larimer",)),
    ("Gunnison/Pitkin", ("Gunnison", "Pitkin")),
    ("Delta or Mesa", ("Delta", "Mesa")),
    ("Boulder OR Weld", ("Boulder", "Weld")),
    ("Lake/Lake Co.", ("Lake",)),  # the same county twice
    ("Unknown", ()),
    ("Unknown-E", ()),
    ("Unknown/Park", ("Park",)),
    ("", ()),
    (None, ()),
])  # fmt: skip
def test_supplied_values_are_split_and_placeholders_dropped(
    value: str | None, expected: tuple[str, ...]
) -> None:
    assert supplied_counties(value) == expected


def test_names_outside_the_gazetteer_are_dropped_when_keys_are_given() -> None:
    known = frozenset({"gilpin", "boulder"})
    assert supplied_counties("Giplin", known) == ()
    assert supplied_counties("Boulder/Giplin", known) == ("Boulder",)
    assert supplied_counties("Giplin") == ("Giplin",)  # without keys, nothing is dropped


def test_placeholders() -> None:
    assert is_placeholder("Unknown-W")
    assert is_placeholder("unknown co.")
    assert not is_placeholder("Unknown Peak")  # not a whole placeholder
