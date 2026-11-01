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


# --- core keys: a looser key for a match tier between exact and fuzzy -----------------------
#
# Labels and GNIS often name the same feature with a different generic word ("Mt. Zenobia" vs
# "Zenobia Peak"), a positional prefix ("Lower Piney Lake" vs "Piney Lake"), a trailing
# descriptor ("Longs Peak summit"), an older spelling ("Canon" for Canyon) or a plural. The
# core key removes or folds exactly those differences. It is applied identically to index names
# and queries, and only ever adds candidates below every exact match.
CORE_KEY_VERSION = "1"

_SUMMIT_GENERICS: Final = frozenset({"mount", "mountain", "peak", "summit"})
_POSITIONAL_PREFIXES: Final = frozenset({"upper", "lower", "middle"})
_CORE_FOLDS: Final[dict[str, str]] = {"canon": "canyon", "lakes": "lake", "peaks": "peak"}
# Words that name a kind of feature. A core made only of these says nothing specific.
_GENERIC_ONLY: Final = frozenset(
    {"lake", "creek", "river", "canyon", "gulch", "spring", "springs", "basin", "ridge", "pass",
     "park", "valley", "draw", "hill", "butte", "reservoir", "fork", "flat", "flats", "mesa"}
)  # fmt: skip


def positional_prefix(key: str) -> str | None:
    """The leading positional word of a name key ("upper", "lower", "middle"), if any."""
    first = key.split(" ", 1)[0]
    return first if first in _POSITIONAL_PREFIXES else None


def core_compatible(query_key: str, name_key_: str) -> bool:
    """Two names with the same core still differ if they carry different positional prefixes:
    "Lower Piney Lake" is evidence against "Upper Piney Lake", not for it."""
    a, b = positional_prefix(query_key), positional_prefix(name_key_)
    return a is None or b is None or a == b


def core_key(key: str) -> str | None:
    """Core of a name key, or None when nothing specific would remain."""
    tokens = [_CORE_FOLDS.get(t, t) for t in key.split()]
    while tokens and tokens[0] in _POSITIONAL_PREFIXES:
        tokens = tokens[1:]
    tokens = [t for t in tokens if t not in _SUMMIT_GENERICS]
    if not tokens or all(t in _GENERIC_ONLY for t in tokens):
        return None
    return " ".join(tokens)
