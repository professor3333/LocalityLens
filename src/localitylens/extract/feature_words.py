"""Words that state a feature type, shared by every extractor and by validation.

An extractor may assert a feature type only together with a quoted word from this table, and
validation re-checks the pair, the same way units and directions are re-parsed by code.
Changing the table changes results, so it is versioned.
"""

from __future__ import annotations

from typing import Final

from localitylens.extract.schema import FeatureType

TYPE_WORDS_VERSION: Final = "1"

# Generic words that state a feature type. Only unambiguous ones: "Springs" and "Park" are
# left out because they are usually town names in Colorado (Colorado Springs, Estes Park).
TYPE_WORDS: Final[dict[str, FeatureType]] = {
    "summit": FeatureType.SUMMIT, "peak": FeatureType.SUMMIT, "pk.": FeatureType.SUMMIT,
    "pk": FeatureType.SUMMIT, "mountain": FeatureType.SUMMIT, "mtn.": FeatureType.SUMMIT,
    "mtn": FeatureType.SUMMIT, "mt.": FeatureType.SUMMIT, "mount": FeatureType.SUMMIT,
    "hill": FeatureType.SUMMIT, "butte": FeatureType.SUMMIT,
    "lake": FeatureType.LAKE, "reservoir": FeatureType.RESERVOIR, "res.": FeatureType.RESERVOIR,
    "creek": FeatureType.STREAM, "cr.": FeatureType.STREAM, "ck.": FeatureType.STREAM,
    "river": FeatureType.STREAM, "fork": FeatureType.STREAM,
    "gulch": FeatureType.VALLEY, "canyon": FeatureType.VALLEY, "cyn.": FeatureType.VALLEY,
    "valley": FeatureType.VALLEY, "draw": FeatureType.VALLEY,
    "spring": FeatureType.SPRING, "pass": FeatureType.GAP, "ridge": FeatureType.RIDGE,
    "basin": FeatureType.BASIN, "flat": FeatureType.FLAT, "flats": FeatureType.FLAT,
}  # fmt: skip


def type_for_word(quote: str) -> FeatureType | None:
    """The type a quoted word states, or None if the word states no unambiguous type."""
    return TYPE_WORDS.get(quote.strip().lower())
