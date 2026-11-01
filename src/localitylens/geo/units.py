"""Exact length-unit conversion.

Conversion factors are exact by definition (international yard and pound agreement, 1959):
1 ft = 0.3048 m, 1 yd = 0.9144 m, 1 statute mile = 1609.344 m.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class LengthUnit(StrEnum):
    MILE = "mile"
    KILOMETRE = "kilometre"
    METRE = "metre"
    FOOT = "foot"
    YARD = "yard"


METRES_PER_UNIT: Final[dict[LengthUnit, float]] = {
    LengthUnit.MILE: 1609.344,
    LengthUnit.KILOMETRE: 1000.0,
    LengthUnit.METRE: 1.0,
    LengthUnit.FOOT: 0.3048,
    LengthUnit.YARD: 0.9144,
}

# Surface forms seen on labels. Deliberately excludes bare "m": on historical US labels it can
# mean miles or metres, so it must be resolved by context or a curator, not by this table.
_UNIT_ALIASES: Final[dict[str, LengthUnit]] = {
    "mi": LengthUnit.MILE,
    "mi.": LengthUnit.MILE,
    "mile": LengthUnit.MILE,
    "miles": LengthUnit.MILE,
    "km": LengthUnit.KILOMETRE,
    "km.": LengthUnit.KILOMETRE,
    "kilometer": LengthUnit.KILOMETRE,
    "kilometers": LengthUnit.KILOMETRE,
    "kilometre": LengthUnit.KILOMETRE,
    "kilometres": LengthUnit.KILOMETRE,
    "meter": LengthUnit.METRE,
    "meters": LengthUnit.METRE,
    "metre": LengthUnit.METRE,
    "metres": LengthUnit.METRE,
    "ft": LengthUnit.FOOT,
    "ft.": LengthUnit.FOOT,
    "foot": LengthUnit.FOOT,
    "feet": LengthUnit.FOOT,
    "yd": LengthUnit.YARD,
    "yd.": LengthUnit.YARD,
    "yds": LengthUnit.YARD,
    "yard": LengthUnit.YARD,
    "yards": LengthUnit.YARD,
}

AMBIGUOUS_UNIT_FORMS: Final[frozenset[str]] = frozenset({"m", "m."})


def to_metres(value: float, unit: LengthUnit) -> float:
    if value < 0:
        raise ValueError(f"distance must be non-negative, got {value}")
    return value * METRES_PER_UNIT[unit]


def parse_unit(text: str) -> LengthUnit | None:
    """Map a label's unit token to a unit. Returns None for unknown or ambiguous forms."""
    return _UNIT_ALIASES.get(text.strip().lower())
