"""Compass directions as written on labels, mapped to nominal bearings.

This module only gives the *nominal* bearing of a compass point (NE -> 45 degrees). How much
angular imprecision a written direction implies is an uncertainty-policy decision, made in a
versioned policy module and shown to the curator, not here.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Final


class CompassPoint(StrEnum):
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"


_ORDER: Final[tuple[CompassPoint, ...]] = tuple(CompassPoint)

NOMINAL_BEARING_DEG: Final[dict[CompassPoint, float]] = {
    point: index * 22.5 for index, point in enumerate(_ORDER)
}

_WORDS: Final[dict[str, str]] = {"north": "N", "south": "S", "east": "E", "west": "W"}
_WORD_RE: Final[re.Pattern[str]] = re.compile(r"north|south|east|west")


def nominal_bearing(point: CompassPoint) -> float:
    """Clockwise bearing from true north in degrees, in [0, 360)."""
    return NOMINAL_BEARING_DEG[point]


def parse_direction(text: str) -> CompassPoint | None:
    """Parse forms such as ``NE``, ``N.E.``, ``n.e``, ``northeast``, ``north-east``, ``N-NE``.

    Returns None for anything that is not one of the 16 compass points; callers must treat that
    as missing information rather than guessing.
    """
    lowered = text.strip().lower()
    if not lowered:
        return None
    lowered = _WORD_RE.sub(lambda m: _WORDS[m.group(0)], lowered)
    letters = re.sub(r"[\s.\-]", "", lowered).upper()
    try:
        return CompassPoint(letters)
    except ValueError:
        return None
