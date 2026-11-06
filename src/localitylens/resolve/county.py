"""Reading the supplied county field (``COUNTY_CONTEXT_VERSION`` 1).

The record's structured ``county`` outranks a county named in the label, but some values are
not one county:

* **Placeholders** such as ``Unknown``, ``Unknown-E`` or ``Unknown-W`` say nothing about where
  the specimen is. They are treated as **missing**, so a county named in the label is used
  instead. Before this rule, ``Unknown`` hid the label's own county and matched no feature.
* **Two-county values** such as ``Gunnison/Pitkin`` or ``Delta or Mesa`` mean the place is in
  either county (often on the line between them). Each county is kept, and a candidate in
  **any** of them counts as a county match.
* **Names the gazetteer doesn't know** (misspellings such as ``Giplin``, or another state's
  county) are dropped. If nothing is left, the value counts as missing.

Measured on ``gbif-cu-2026-11-01``: 2,928 of 105,544 eligible records carry a county that is
not one known Colorado county. 1,305 are placeholders and 218 are empty. Nearly all the rest
are two-county values, and 10 are unknown names.

County context only ranks candidates; it never removes one (current county lines are not
proof for an old label).
"""

from __future__ import annotations

import re
from typing import Final

from localitylens.gazetteer.keys import county_key

COUNTY_CONTEXT_VERSION: Final = "1"

_SEPARATORS: Final = re.compile(r"\s*/\s*|\s+or\s+", re.IGNORECASE)
_PLACEHOLDER_KEYS: Final = frozenset({"", "unknown", "unknown e", "unknown w", "unk", "none"})


def is_placeholder(value: str) -> bool:
    return county_key(value) in _PLACEHOLDER_KEYS


def supplied_counties(
    value: str | None, known_keys: frozenset[str] | None = None
) -> tuple[str, ...]:
    """The counties a supplied value names, in order; empty when it names none.

    With ``known_keys`` (the gazetteer's county keys), parts it doesn't contain are dropped.
    """
    if value is None:
        return ()
    parts = [p.strip() for p in _SEPARATORS.split(value.strip())]
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        key = county_key(part)
        if is_placeholder(part) or key in seen:
            continue
        if known_keys is not None and key not in known_keys:
            continue
        seen.add(key)
        out.append(part)
    return tuple(out)
