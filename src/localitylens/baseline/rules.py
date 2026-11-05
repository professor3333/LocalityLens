"""Regex + gazetteer extractor for locality descriptions.

Design rules:

* Every value is a **quote** cut from the input text (``match.group``), so output always
  satisfies the quote contract. A property test checks that every output validates.
* It abstains rather than guesses. A bare ``m`` gives "unit missing". A number after a road or
  survey word ("Hwy 34 E of Loveland", "R73W") is not a distance. Route descriptions ("2 mi up
  the canyon") are labelled ``route_relative`` instead of being forced into straight-line offsets.
* Admin areas and named places come from a :class:`Lexicon` built from the gazetteer, so
  "Boulder Co." is a county mention and never the town of Boulder.

Detection order: no locality → route-relative → orthogonal offsets → between → distance and
direction → distance only → direction only → named feature.

A named place written right before an offset can win over the offset (rules-3), following the
annotation guide's "most specific clause": see :meth:`RulesExtractor._collecting_place`.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Final

from localitylens.extract.feature_words import TYPE_WORDS
from localitylens.extract.quantities import parse_quantity
from localitylens.extract.schema import (
    AdminLevel,
    ExtractionOutput,
    FeatureType,
    MissingKind,
    QualifierKind,
    RelationType,
)
from localitylens.gazetteer.keys import county_key, name_key
from localitylens.geo.directions import parse_direction
from localitylens.geo.units import AMBIGUOUS_UNIT_FORMS, parse_unit, to_metres

# rules-2: "air mi" / "air miles", spelled-out numbers before a unit, "ca" without a dot.
# rules-3: an abbreviated direction is never cut short ("10 mi. n. w." is not "10 mi. n");
# a named collecting place before an offset wins over the offset (see _collecting_place).
# rules-4: a broad feature (stream, range, park, forest) or the offset's own base never replaces
# a precise offset; a dotless "Mt" no longer crashes (KeyError in _feature since rules-1).
RULES_VERSION: Final = "rules-4"

# ---------------------------------------------------------------------------------- patterns

_VULGAR = "½¼¾⅓⅔⅛⅜⅝⅞"
_NUM = (
    rf"(?<![\w./])(?:\d+\s*[{_VULGAR}]|\d+(?:\s+|-)\d+/\d+|\d+/\d+|\d*\.\d+|\d+|[{_VULGAR}])"
    r"(?![\w/])"
)
_UNIT = (
    r"(?i:miles?\b|mi\b\.?|kilomet(?:er|re)s?\b|km\b\.?|met(?:er|re)s?\b|feet\b|ft\b\.?"
    r"|yards?\b|yds?\b\.?|m\b\.?)"
)
# A spelled-out number counts only directly before a unit ("Nine miles"), never in a name
# ("Two Buttes", "Ten Mile Range").
_NUM_WORD = (
    r"(?i:\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen"
    r"|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|half)\b)"
)
_AIR = r"(?:(?i:air)\s+)?"  # "air mi": a straight-line distance, which is the default reading
_QTY = rf"(?:{_NUM}|{_NUM_WORD}(?=\s*{_AIR}(?:{_UNIT})))"
_DIR_WORD = r"(?:north|south)[\s\-]?(?:east|west)\b|north\b|south\b|east\b|west\b"
_DIR_ABBR = r"[NSEW]\.(?:\s?[NSEW]\.){0,2}|[NSEW]{1,3}\b"
_DIR = rf"(?:(?i:{_DIR_WORD})|(?i:{_DIR_ABBR}))"  # after a number: lower case is fine
_DIR_STRICT = rf"(?:(?i:{_DIR_WORD})|{_DIR_ABBR})"  # standalone: upper-case letters only
_QUAL = r"(?i:(?:about|approx\.?|approximately|ca\.|ca(?=\s)|circa|c\.)\s*)"
_OF = r"(?i:of|from|fr\.)"
_FWORD = r"[A-Z][A-Za-z'\u2019\-]*\.?"
_FEATURE = rf"{_FWORD}(?:\s+(?:(?:of the|of|de|del|la|los|las|el)\s+)?{_FWORD}){{0,5}}"

_RE_NO_LOCALITY = re.compile(
    r"^\s*(?i:no (?:locality|data|locality data)(?: given)?|locality (?:unknown|not given)"
    r"|s\.\s?loc\.?|sine loco|unknown|none)\s*\.?\s*$"
)
_RE_ROUTE = re.compile(
    rf"(?P<num>{_NUM})\s*(?P<unit>{_UNIT})\s+(?:(?:{_DIR})\s+)?"
    r"(?i:along|up|down|via|by|on)\s+[^,;]*"
)
_RE_ROUTE_ANYWHERE = re.compile(r"(?i:\bby (?:road|trail|rail|car|auto)\b|\broad miles?\b)")
_RE_ORTHOGONAL = re.compile(
    rf"(?P<n1>{_NUM})\s*(?:{_UNIT})?\s*(?:{_DIR})\s*(?:,|(?i:and)|&)\s*"
    rf"(?P<n2>{_NUM})\s*(?:{_UNIT})?\s*(?:{_DIR})\s+{_OF}\s+(?:the\s+)?(?P<feat>{_FEATURE})"
)
_RE_BETWEEN = re.compile(rf"(?i:between)\s+(?P<f1>{_FEATURE})\s+(?i:and|&)\s+(?P<f2>{_FEATURE})")
_RE_OFFSET_A = re.compile(
    rf"(?P<qual>{_QUAL})?(?P<num>{_QTY})\s*(?:{_AIR}(?P<unit>{_UNIT}))?\s*(?P<dir>{_DIR})\s+{_OF}\s+"
    rf"(?:the\s+)?(?P<feat>{_FEATURE})"
)
_RE_OFFSET_B = re.compile(
    rf"(?P<feat>{_FEATURE})\s*,?\s+(?P<qual>{_QUAL})?(?P<num>{_QTY})\s*(?:{_AIR}(?P<unit>{_UNIT}))?\s*"
    rf"(?P<dir>{_DIR})(?!\.?\s?(?i:[NSEW])\.)(?=\s*(?:[,.;:)]|$))"
)
_RE_DISTANCE_ONLY = re.compile(
    rf"(?P<qual>{_QUAL})?(?P<num>{_QTY})\s*{_AIR}(?P<unit>{_UNIT})\s+{_OF}\s+(?:the\s+)?"
    rf"(?P<feat>{_FEATURE})"
)
_RE_DIRECTION_ONLY = re.compile(
    rf"(?<![\w.])(?P<dir>{_DIR_STRICT})\s+{_OF}\s+(?:the\s+)?(?P<feat>{_FEATURE})"
)
_RE_STATE = re.compile(r"\b(?:Colorado|COLORADO|Colo\b\.?|COLO\b\.?)(?=\s*(?:[,.;:)]|$))")
_RE_QUALIFIERS: Final[tuple[tuple[re.Pattern[str], QualifierKind], ...]] = (
    (re.compile(r"(?i:\b(?:about|approx\.|approximately|approx|circa|ca\.)(?=\s|$)"
                r"|\bca(?=\s+(?:\d|[½¼¾])))"),
     QualifierKind.APPROXIMATE),
    (re.compile(r"(?i:\bvicinity of\b|\bvic\.)"), QualifierKind.VICINITY),
    (re.compile(r"(?i:\bnear\b|\bnr\.)"), QualifierKind.NEAR),
    (re.compile(r"\?"), QualifierKind.QUESTIONED),
)  # fmt: skip
_RE_ANCHOR = re.compile(r"(?i:\b(?:near|nr\.|vicinity of|vic\.|at)\s+)")
# A lower-case generic type word written right after a name: "Longs Peak summit".
_TRAILING_TYPE = re.compile(
    r"\s+(summit|peak|lake|creek|river|reservoir|spring|pass|ridge|canyon|gulch|valley|basin)\b"
)
_RE_WORD = re.compile(r"[A-Za-z][A-Za-z'\u2019\-]*\.?")
# A word immediately before a number, separated only by spaces (an optional dot allowed).
_RE_WORD_BEFORE = re.compile(r"([A-Za-z\-]+)\.?\s*$")

# Words that make the following number a road/survey designation, not a distance.
_NOT_DISTANCE_PREFIX: Final = frozenset(
    {"hwy", "highway", "route", "rte", "road", "rd", "us", "sec", "section", "t", "r", "i",
     "interstate", "state", "sh", "fs", "fsr", "no", "elev", "alt"}
)  # fmt: skip
_ABBREVIATION_TOKENS: Final = frozenset(
    {"mt.", "pk.", "cr.", "ck.", "ft.", "st.", "res.", "spgs.", "spg.", "mtn.", "mtns.", "jct.",
     "cyn.", "lk."}
)  # fmt: skip
_TRAILING_ADMIN: Final = frozenset({"co.", "co", "county", "colo.", "colo", "colorado"})
# Capitalized words that end a place name when they follow it ("Boulder Elev 5400").
_STOP_INSIDE_NAME: Final = frozenset(
    {"elev", "alt", "coll", "collected", "det", "jan", "feb", "mar", "apr", "jun", "jul", "aug",
     "sep", "sept", "oct", "nov", "dec", "january", "february", "march", "april", "june",
     "july", "august", "september", "october", "november", "december", "usa"}
)  # fmt: skip
_CONNECTORS: Final = frozenset({"of", "the", "de", "del", "la", "los", "las", "el"})
_NOT_PLACE_WORDS: Final = frozenset(
    {"january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december", "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.",
     "sep.", "sept.", "oct.", "nov.", "dec.", "elev.", "elev", "alt.", "alt", "coll.",
     "collected", "det.", "herbarium", "plants", "flora", "usa", "u.s.a.", "colorado",
     "colo.", "colo", "co.", "county", "near", "nr.", "at", "vicinity", "vic.", "about",
     "along", "in", "on", "the", "of", "and", "n", "s", "e", "w", "ne", "nw", "se", "sw"}
)  # fmt: skip

# Each must be in TYPE_WORDS. A dotless "Mt" is not, so it states no type (the shared table also
# checks LLM output, whose frozen runs would change).
_HEAD_INITIAL_TYPES: Final = frozenset({"mt.", "mount", "lake"})

# Collecting place before an offset (rules-3). A position word puts the specimen on the place
# ("S slope of Thunder Mt., 16 miles N of Grand Lake"): the offset only locates it.
_RE_ON_PLACE = re.compile(
    r"(?i:\b(?:slopes?|side|flank|summit|top|foot|base|edge|mouth|head|shore|rim)\s+"
    r"(?:of\s+)?(?:the\s+)?)$"
)
# A name in a route ("toward Independence Pass, 11 mi. E of Aspen") is not a collecting place.
_RE_ROUTE_BEFORE = re.compile(r"(?i:\b(?:toward|towards|to|from|along|via)\s+)$")
_ROUTE_NAME_WORDS: Final = frozenset(
    {"road", "rd", "rd.", "trail", "tr.", "highway", "hwy", "hwy.", "boulevard", "blvd",
     "blvd.", "drive", "dr.", "street", "st.", "avenue", "ave.", "route", "rte."}
)  # fmt: skip
# Below this, an offset region is about as small as most named places, so the offset is the
# more specific clause ("Rollins Pass, 0.3 mi. N. of Needle Eye Tunnel").
_OPENING_PLACE_MIN_OFFSET_M: Final = 1609.344
# Features too broad to replace a precise offset (rules-4). The offset is the more specific
# clause: a stream's region is its whole length ("Arkansas River, 5 mi E of Salida" is not a
# 1,500 km circle). Streams come from TYPE_WORDS. "Park" alone stays out: it is usually a town.
_BROAD_LAST_WORDS: Final = frozenset(
    {"r.", "mountains", "mtns", "mtns.", "mts", "mts.", "range", "hills", "wilderness"}
)
_BROAD_LAST_TWO_WORDS: Final = frozenset(
    {"national park", "state park", "national forest", "state forest", "national monument"}
)


def _is_broad_place(name: str) -> bool:
    """True when the name's last words state a stream, a range, a park or a forest."""
    words = name.lower().split()
    return (
        TYPE_WORDS.get(words[-1]) is FeatureType.STREAM
        or words[-1] in _BROAD_LAST_WORDS
        or " ".join(words[-2:]) in _BROAD_LAST_TWO_WORDS
    )


# ----------------------------------------------------------------------------------- lexicon


@dataclass(frozen=True)
class Lexicon:
    """What the rules know about places: county names and indexed gazetteer name keys."""

    county_names: frozenset[str]
    known_name_keys: frozenset[str] = field(default_factory=frozenset)

    def is_known(self, phrase: str) -> bool:
        return name_key(phrase) in self.known_name_keys

    @classmethod
    def from_names(cls, county_names: Iterable[str], place_names: Iterable[str]) -> Lexicon:
        return cls(frozenset(county_names), frozenset(name_key(n) for n in place_names))


# --------------------------------------------------------------------------------- extractor


@dataclass
class _Draft:
    relation: RelationType = RelationType.OTHER
    relation_quote: str | None = None
    feature: dict[str, Any] | None = None
    distance: dict[str, Any] | None = None
    direction: dict[str, Any] | None = None
    missing: list[MissingKind] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    # An offset that was read but not applied (rules-3): its qualifiers are not the place's.
    dropped_span: tuple[int, int] | None = None


class RulesExtractor:
    version: Final = RULES_VERSION

    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        names = sorted(lexicon.county_names, key=len, reverse=True)
        if names:
            alternation = "|".join(re.escape(n) for n in names)
            self._re_county: re.Pattern[str] | None = re.compile(
                rf"(?i:\b(?:{alternation})\s+(?:co\b\.?|county\b|cnty\b\.?))"
            )
        else:
            self._re_county = None

    # ------------------------------------------------------------------------------- public

    def extract(self, text: str) -> ExtractionOutput:
        """Interpret one (normalized) locality string."""
        admin = self._admin_mentions(text)
        admin_spans = [span for span, _ in admin]
        draft = self._relation(text, admin_spans)
        return ExtractionOutput.model_validate(
            {
                "relation": draft.relation,
                "relation_quote": draft.relation_quote,
                "reference_feature": draft.feature,
                "distance": draft.distance,
                "direction": draft.direction,
                "admin_mentions": [
                    {"level": level, "quote": text[s:e]} for (s, e), level in admin[:6]
                ],
                "qualifiers": self._qualifiers(text, draft.dropped_span),
                "missing": list(dict.fromkeys(draft.missing))[:6],
                "open_questions": draft.questions[:3],
            }
        )

    # ------------------------------------------------------------------------------ helpers

    def _admin_mentions(self, text: str) -> list[tuple[tuple[int, int], AdminLevel]]:
        found: list[tuple[tuple[int, int], AdminLevel]] = []
        if self._re_county is not None:
            found += [(m.span(), AdminLevel.COUNTY) for m in self._re_county.finditer(text)]
        found += [(m.span(), AdminLevel.STATE) for m in _RE_STATE.finditer(text)]
        return sorted(found)

    def _qualifiers(
        self, text: str, dropped: tuple[int, int] | None = None
    ) -> list[dict[str, Any]]:
        out: list[tuple[int, dict[str, Any]]] = []
        for pattern, kind in _RE_QUALIFIERS:
            for m in pattern.finditer(text):
                if dropped is not None and dropped[0] <= m.start() < dropped[1]:
                    continue  # "ca. 7 miles W of X" qualifies the offset, not the place
                out.append((m.start(), {"kind": kind, "quote": m.group(0)}))
        return [q for _, q in sorted(out, key=lambda t: t[0])][:6]

    def _relation(self, text: str, admin_spans: list[tuple[int, int]]) -> _Draft:
        if not text.strip() or _RE_NO_LOCALITY.match(text):
            return _Draft(relation=RelationType.NO_LOCALITY)

        if (m := _RE_ROUTE.search(text)) or (m := _RE_ROUTE_ANYWHERE.search(text)):
            quote = m.group(0)[:500].rstrip(" .,")
            return _Draft(
                relation=RelationType.ROUTE_RELATIVE,
                relation_quote=quote,
                missing=[MissingKind.ROUTE_GEOMETRY],
            )

        if hit := self._valid_match(_RE_ORTHOGONAL, text, admin_spans, num_groups=("n1", "n2")):
            m, feature_text = hit
            draft = _Draft(
                relation=RelationType.ORTHOGONAL_OFFSETS, relation_quote=m.group(0).rstrip(" .")
            )
            draft.feature = self._feature(feature_text) if feature_text else None
            return draft

        if m := _RE_BETWEEN.search(text):
            return _Draft(
                relation=RelationType.BETWEEN_FEATURES, relation_quote=m.group(0).rstrip(" .")
            )

        for pattern in (_RE_OFFSET_A, _RE_OFFSET_B):
            if hit := self._valid_match(pattern, text, admin_spans):
                if pattern is _RE_OFFSET_A and (
                    place := self._collecting_place(hit[0], admin_spans)
                ):
                    return self._place_before_offset(text, place, hit[0])
                return self._offset(*hit, RelationType.DISTANCE_AND_DIRECTION)

        if hit := self._valid_match(_RE_DISTANCE_ONLY, text, admin_spans):
            if place := self._collecting_place(hit[0], admin_spans):
                return self._place_before_offset(text, place, hit[0])
            return self._offset(*hit, RelationType.DISTANCE_ONLY)

        if hit := self._valid_match(_RE_DIRECTION_ONLY, text, admin_spans, num_groups=()):
            return self._offset(*hit, RelationType.DIRECTION_ONLY)

        return self._named_feature(text, admin_spans)

    def _valid_match(
        self,
        pattern: re.Pattern[str],
        text: str,
        admin_spans: list[tuple[int, int]],
        num_groups: tuple[str, ...] = ("num",),
    ) -> tuple[re.Match[str], str | None] | None:
        """First usable match plus its feature text (cut short at a following admin mention)."""
        for m in pattern.finditer(text):
            if any(self._is_designation(text, m.start(g)) for g in num_groups):
                continue
            if any(parse_quantity(m.group(g)) is None for g in num_groups):
                continue  # e.g. "0 mi": not a usable distance
            if "feat" not in m.re.groupindex:
                return m, None
            f_start, f_end = m.span("feat")
            if any(s <= f_start < e for s, e in admin_spans):
                continue  # the "feature" is itself a county or state mention
            for s_, _e in admin_spans:
                if f_start < s_ < f_end:
                    f_end = s_
            feature_text = text[f_start:f_end].rstrip(" ,")
            if self._clean_feature(feature_text) is None:
                continue
            return m, feature_text
        return None

    @staticmethod
    def _is_designation(text: str, num_start: int) -> bool:
        """True when the number is part of a road/survey designation, e.g. 'Hwy 34', 'R73W'."""
        if num_start > 0 and text[num_start - 1].isalpha():
            return True  # glued to a letter: 'R73W', 'T5N'
        m = _RE_WORD_BEFORE.search(text[:num_start])
        return m is not None and m.group(1).lower() in _NOT_DISTANCE_PREFIX

    def _offset(self, m: re.Match[str], feature_text: str | None, relation: RelationType) -> _Draft:
        text = m.string
        start, end = m.span()
        draft = _Draft(relation=relation)
        groups = m.re.groupindex
        if feature_text is not None:
            f_end = m.start("feat") + len(feature_text)
            type_word = _TRAILING_TYPE.match(text, f_end)
            if type_word and self.lexicon.is_known(text[m.start("feat") : type_word.end()]):
                # "Bear lake": the type word is part of the name.
                feature_text = text[m.start("feat") : type_word.end()]
                f_end = type_word.end()
            draft.feature = self._feature(feature_text, type_word.group(1) if type_word else None)
            if m.end("feat") == end:  # feature ends the match: end the relation with it
                end = type_word.end() if type_word else f_end
        draft.relation_quote = text[start:end].strip().rstrip(",")
        if draft.feature is None:
            draft.missing.append(MissingKind.REFERENCE_FEATURE)
        if "num" in groups and m.group("num"):
            distance: dict[str, Any] = {"value_quote": m.group("num").strip()}
            unit_text = m.group("unit") if "unit" in groups else None
            if unit_text:
                unit = parse_unit(unit_text)
                if unit is not None and unit_text.strip().lower() not in AMBIGUOUS_UNIT_FORMS:
                    distance |= {"unit": unit, "unit_quote": unit_text.strip()}
                else:
                    draft.missing.append(MissingKind.DISTANCE_UNIT)
                    draft.questions.append(f"Does {unit_text.strip()!r} mean miles or metres?")
            else:
                draft.missing.append(MissingKind.DISTANCE_UNIT)
            draft.distance = distance
        if "dir" in groups and m.group("dir"):
            dir_text = m.group("dir").strip()
            point = parse_direction(dir_text)
            if point is not None:
                draft.direction = {"point": point, "quote": dir_text}
            else:
                draft.missing.append(MissingKind.DIRECTION)
        return draft

    def _collecting_place(
        self, m: re.Match[str], admin_spans: list[tuple[int, int]]
    ) -> tuple[int, int] | None:
        """A known place written right before an "N units DIR of X" offset that names where the
        specimen was collected, so the offset only locates it. The annotation guide takes the
        most specific clause; two label shapes make the place that clause:

        * a position word puts the specimen on the place: "S. slope of Thunder Mt., 16 miles N
          of Grand Lake", "slope of Douglas Mt., 3/5 mi. SW of Greystone";
        * the label opens with the place and the offset is at least a mile: "Vernal Mesa,
          15 mi. east of Montrose". A shorter offset is the more specific clause.

        The place must end right before the offset's comma or semicolon, and it is never a road
        or a name inside a route ("toward Independence Pass, 11 mi. E of Aspen"). It is also
        never a broad feature ("Arkansas River, 5 mi E of Salida") or the offset's own base
        ("Boulder, 2 mi W of Boulder"): the offset is then the more specific clause.
        """
        text = m.string
        before = text[: m.start()].rstrip()
        if not before.endswith((",", ";")):
            return None
        known = [p for p in self._known_phrases(text, admin_spans) if p[1] <= m.start()]
        if not known:
            return None
        start, end = known[-1]
        if text[end : m.start()].strip(" .,;"):
            return None  # something else sits between the place and the offset
        name = text[start:end]
        if name.split()[-1].lower() in _ROUTE_NAME_WORDS or _RE_ROUTE_BEFORE.search(text[:start]):
            return None
        if _is_broad_place(name) or name_key(name) == name_key(m.group("feat")):
            return None
        if _RE_ON_PLACE.search(text[:start]):
            return start, end
        if text[:start].strip():
            return None  # neither a position word nor the label's opening place
        quantity = parse_quantity(m.group("num"))
        unit = parse_unit(m.group("unit")) if m.group("unit") else None
        if (
            quantity is None
            or unit is None
            or m.group("unit").strip().lower() in AMBIGUOUS_UNIT_FORMS
        ):
            return None
        if to_metres(quantity.value, unit) < _OPENING_PLACE_MIN_OFFSET_M:
            return None
        return start, end

    def _place_before_offset(
        self, text: str, place: tuple[int, int], offset: re.Match[str]
    ) -> _Draft:
        start, end = place
        draft = _Draft(relation=RelationType.NAMED_FEATURE, dropped_span=offset.span())
        draft.feature = self._feature(text[start:end])
        offset_quote = offset.group(0).strip().rstrip(".,")[:160]
        draft.questions.append(
            f"The label also gives an offset ({offset_quote!r}); it is read as locating "
            f"{text[start:end]!r}, the collecting place."
        )
        return draft

    def _named_feature(self, text: str, admin_spans: list[tuple[int, int]]) -> _Draft:
        candidates = self._known_phrases(text, admin_spans)
        anchored = [
            c for c in candidates if _RE_ANCHOR.search(text[max(0, c[0] - 14) : c[0]] + " ")
        ]
        pool = anchored or candidates
        chosen: tuple[int, int] | None = pool[0] if pool else None
        if chosen is None:
            fallback = self._anchored_phrase(text, admin_spans)
            if fallback is None:
                return _Draft(relation=RelationType.OTHER, missing=[MissingKind.REFERENCE_FEATURE])
            chosen = fallback
        start, end = chosen
        draft = _Draft(relation=RelationType.NAMED_FEATURE)
        draft.feature = self._feature(text[start:end])
        if draft.feature is None:
            return _Draft(relation=RelationType.OTHER, missing=[MissingKind.REFERENCE_FEATURE])
        others = [text[s:e] for s, e in candidates if (s, e) != chosen]
        if others:
            names = ", ".join(dict.fromkeys([text[start:end], *others]))[:200]
            draft.questions.append(f"Label names several places ({names}); which is the reference?")
        return draft

    def _known_phrases(
        self, text: str, admin_spans: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """Longest gazetteer-known capitalized phrase at each position, in text order."""
        tokens = [m for m in _RE_WORD.finditer(text) if not _overlaps(m.span(), admin_spans)]
        found: list[tuple[int, int]] = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if not tok.group(0)[0].isupper():
                i += 1
                continue
            # The full capitalized run starting here, e.g. "Gold Hill Mine".
            run_end = i
            for j in range(i + 1, min(i + 6, len(tokens))):
                word = tokens[j].group(0)
                if not _adjacent(text, tokens[j - 1], tokens[j]):
                    break
                if word.lower().rstrip(",.") in _STOP_INSIDE_NAME | _TRAILING_ADMIN:
                    break
                if word.lower() in _CONNECTORS:
                    continue
                if not word[0].isupper():
                    break
                run_end = j
            phrase_end = _strip_dot_end(text, tok.start(), tokens[run_end])
            phrase = text[tok.start() : phrase_end]
            single_stop = run_end == i and tok.group(0).lower() in _NOT_PLACE_WORDS
            if not single_stop and self.lexicon.is_known(phrase):
                found.append((tok.start(), phrase_end))
            elif not single_stop and run_end > i and self._has_known_part(tokens, i, run_end):
                # A known name inside a longer one ("Gold Hill" in "Gold Hill Mine"): the longer
                # name is the place. It is kept so retrieval can report it absent.
                found.append((tok.start(), phrase_end))
            i = run_end + 1
        return found

    def _has_known_part(self, tokens: list[re.Match[str]], i: int, j: int) -> bool:
        for a in range(i, j + 1):
            for b in range(a, j + 1):
                if (a, b) != (i, j) and self.lexicon.is_known(
                    " ".join(t.group(0) for t in tokens[a : b + 1])
                ):
                    return True
        return False

    def _anchored_phrase(
        self, text: str, admin_spans: list[tuple[int, int]]
    ) -> tuple[int, int] | None:
        """A capitalized phrase right after 'near', 'at', etc., even if the gazetteer lacks it."""
        for m in _RE_ANCHOR.finditer(text):
            fm = re.compile(_FEATURE).match(text, m.end())
            if fm and not _overlaps(fm.span(), admin_spans):
                cleaned = self._clean_feature(fm.group(0))
                if cleaned is not None:
                    return fm.start(), fm.start() + len(cleaned)
        return None

    def _clean_feature(self, raw: str) -> str | None:
        """Trim a captured name: stop at sentence ends, prefer the longest known prefix, and
        drop trailing admin words. Returns a prefix of ``raw`` (so still a quote), or None."""
        words = list(re.finditer(r"\S+", raw))
        cut = len(words)
        for idx, w in enumerate(words):
            token = w.group(0)
            if token.endswith(".") and token.lower() not in _ABBREVIATION_TOKENS:
                cut = idx + 1
                break
        words = words[:cut]
        for idx, w in enumerate(words):
            if idx > 0 and w.group(0).lower().rstrip(",.") in _STOP_INSIDE_NAME:
                words = words[:idx]
                break
        while words and words[-1].group(0).lower().rstrip(",") in _TRAILING_ADMIN:
            words.pop()
        if not words:
            return None
        candidate = raw[: words[-1].end()]
        last = words[-1].group(0)
        if last.endswith(".") and last.lower() not in _ABBREVIATION_TOKENS:
            candidate = candidate[:-1]
        if not candidate or candidate.lower() in _NOT_PLACE_WORDS:
            return None
        return candidate

    def _feature(self, raw: str, stated_type: str | None = None) -> dict[str, Any] | None:
        """Feature dict from a captured name. ``stated_type`` is a generic word written right
        after the name on the label ("Longs Peak *summit*"); it wins over a word in the name."""
        name = self._clean_feature(raw)
        if name is None:
            return None
        feature: dict[str, Any] = {"name_quote": name}
        type_word = None
        if stated_type is not None and stated_type.lower() in TYPE_WORDS:
            type_word = stated_type
        else:
            # Only the head word states a type: the last word ("Bear Creek") or a leading
            # "Mt."/"Mount"/"Lake" ("Mt. Evans", "Lake Granby"). "Gold Hill Mine" has no type.
            tokens = name.split()
            if tokens[-1].lower() in TYPE_WORDS:
                type_word = tokens[-1]
            elif len(tokens) > 1 and tokens[0].lower() in _HEAD_INITIAL_TYPES:
                type_word = tokens[0]
        if type_word is not None:
            feature |= {
                "feature_type": TYPE_WORDS[type_word.lower()],
                "feature_type_quote": type_word,
            }
        return feature


def _overlaps(span: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    return any(span[0] < e and s < span[1] for s, e in spans)


def _adjacent(text: str, a: re.Match[str], b: re.Match[str]) -> bool:
    return text[a.end() : b.start()].isspace() and not a.group(0).endswith(",")


def _strip_dot_end(text: str, start: int, last: re.Match[str]) -> int:
    token = last.group(0)
    if token.endswith(".") and token.lower() not in _ABBREVIATION_TOKENS:
        return last.end() - 1
    return last.end()


def county_from_mention(quote: str) -> str:
    """'Larimer Co.' -> 'larimer' (for ranking context)."""
    return county_key(quote)
