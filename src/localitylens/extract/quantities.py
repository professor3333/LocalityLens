"""Parse distance numbers exactly as written on labels: ``2``, ``2.5``, ``.5``, ``1/2``,
``1 1/2``, ``1-1/2``, ``½``, ``1½``.

Spelled-out numbers ("two") are not parsed yet. They come back as None, so the record shows a
validation issue instead of a guessed value.
"""

from __future__ import annotations

import re
from typing import Final

from localitylens.extract.schema import ParsedQuantity

_VULGAR: Final[dict[str, tuple[int, int]]] = {
    "½": (1, 2),
    "⅓": (1, 3),
    "⅔": (2, 3),
    "¼": (1, 4),
    "¾": (3, 4),
    "⅛": (1, 8),
    "⅜": (3, 8),
    "⅝": (5, 8),
    "⅞": (7, 8),
}

_DECIMAL: Final = re.compile(r"(\d+)?(?:\.(\d+))?")
_FRACTION: Final = re.compile(r"(?:(\d+)[\s\-]+)?(\d+)\s*/\s*(\d+)")
_VULGAR_RE: Final = re.compile(r"(\d+)?\s*([" + "".join(_VULGAR) + r"])")


def parse_quantity(text: str) -> ParsedQuantity | None:
    s = text.strip()
    if not s:
        return None

    if m := _FRACTION.fullmatch(s):
        whole = int(m.group(1)) if m.group(1) else 0
        num, den = int(m.group(2)), int(m.group(3))
        if den < 2 or num == 0:
            return None
        value = whole + num / den
        return ParsedQuantity(value=value, decimal_places=0, fraction_denominator=den)

    if m := _VULGAR_RE.fullmatch(s):
        whole = int(m.group(1)) if m.group(1) else 0
        num, den = _VULGAR[m.group(2)]
        return ParsedQuantity(value=whole + num / den, decimal_places=0, fraction_denominator=den)

    m = _DECIMAL.fullmatch(s)
    if m and (m.group(1) or m.group(2)):
        value = float(s)
        if value <= 0:
            return None
        decimals = len(m.group(2)) if m.group(2) else 0
        return ParsedQuantity(value=value, decimal_places=decimals)

    return None
