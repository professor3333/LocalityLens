"""Name keys: one comparable form for gazetteer names and label text.

Applied identically to index names and queries, so "Long's Pk." and "Longs Peak" meet.
The abbreviation table is versioned because changing it changes retrieval results.
Single-letter forms ("L.", "R.", "M.") are deliberately absent: they are too ambiguous
to expand without context.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final

NAME_KEY_VERSION = "1"

ABBREVIATIONS: Final[dict[str, str]] = {
    "mt": "mount",
    "mtn": "mountain",
    "mtns": "mountains",
    "pk": "peak",
    "cr": "creek",
    "ck": "creek",
    "crk": "creek",
    "res": "reservoir",
    "resv": "reservoir",
    "spg": "spring",
    "spgs": "springs",
    "ft": "fort",
    "cyn": "canyon",
    "jct": "junction",
}

_HISTORICAL: Final = re.compile(r"\(\s*historical\s*\)", re.IGNORECASE)
_APOSTROPHES: Final = re.compile("['\u2019\u2018`]")  # straight, right/left curly, backtick
_NON_ALNUM: Final = re.compile(r"[^0-9a-z]+")
_COUNTY_WORDS: Final = frozenset({"county", "co", "cnty", "cty"})


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold()


def name_key(text: str) -> str:
    s = _HISTORICAL.sub(" ", text)
    s = _APOSTROPHES.sub("", _fold(s))
    tokens = _NON_ALNUM.sub(" ", s).split()
    return " ".join(ABBREVIATIONS.get(t, t) for t in tokens)


def is_historical_name(text: str) -> bool:
    return bool(_HISTORICAL.search(text))


def county_key(text: str) -> str:
    """'Larimer Co.' / 'Larimer County' / 'larimer' -> 'larimer'."""
    s = _APOSTROPHES.sub("", _fold(text))
    tokens = [t for t in _NON_ALNUM.sub(" ", s).split() if t not in _COUNTY_WORDS]
    return " ".join(tokens)
