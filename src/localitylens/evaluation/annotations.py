"""Annotation worksheet: parse and check it mechanically before anything is scored.

Checks only what can be checked without judgement: the source columns are unchanged, every
value is in its inventory, every GNIS ID exists in the pinned snapshot, and the columns agree
with the stated description type. Problems are reported, never fixed silently.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Final

from localitylens.evaluation.audit import WORKSHEET_COLUMNS, AuditSample
from localitylens.extract.quantities import parse_quantity
from localitylens.extract.schema import RelationType
from localitylens.gazetteer.index import Gazetteer
from localitylens.geo.directions import CompassPoint
from localitylens.geo.units import LengthUnit

DESCRIPTION_TYPES: Final = frozenset(
    {"named_feature", "distance_and_direction", "distance_only", "direction_only",
     "route_relative", "itinerary", "between_features", "orthogonal_offsets", "admin_only",
     "habitat_only", "no_locality"}
)  # fmt: skip
# Annotation types that have no RelationType of their own map to OTHER.
TO_RELATION: Final[dict[str, RelationType]] = {
    **{t: RelationType(t) for t in DESCRIPTION_TYPES if t in RelationType._value2member_map_},
    "admin_only": RelationType.OTHER,
    "habitat_only": RelationType.OTHER,
}
MISSING_WORDS: Final = frozenset(
    {"extent", "which_feature", "distance", "unit", "direction", "route_geometry",
     "feature_not_in_gnis", "historical_name"}
)  # fmt: skip
QUALIFIER_WORDS: Final[dict[str, str]] = {
    "about": "approximate", "ca.": "approximate", "ca": "approximate", "approx.": "approximate",
    "approx": "approximate", "approximately": "approximate", "near": "near", "nr.": "near",
    "vicinity": "vicinity", "vicinity of": "vicinity", "vic.": "vicinity", "?": "questioned",
    "+/-": "approximate", "\u00b1": "approximate", "~": "approximate",
}  # fmt: skip
_NEEDS_REFERENCE: Final = frozenset(
    {"named_feature", "distance_and_direction", "distance_only", "direction_only"}
)
_RANGE: Final = re.compile(r"^\s*\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\s*$")


# Spelled-out numbers as annotators copy them from labels ("Nine miles"). Annotation only:
# the extraction parser deliberately does not read words yet (a recorded system limitation).
NUMBER_WORDS: Final[dict[str, float]] = {
    w: float(i)
    for i, w in enumerate(
        (
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
            "twenty",
        )
    )
} | {"half": 0.5}


def annotated_distance(text: str) -> float | None:
    """Value of an annotated distance: a label number, fraction or a spelled-out number."""
    q = parse_quantity(text)
    if q is not None:
        return q.value
    return NUMBER_WORDS.get(text.strip().lower())


class Level(StrEnum):
    ERROR = "error"  # the row cannot be scored as written
    WARNING = "warning"  # scoreable, but worth a second look


@dataclass(frozen=True, slots=True)
class Problem:
    audit_id: str
    column: str
    level: Level
    message: str


@dataclass(frozen=True, slots=True)
class Annotation:
    audit_id: str
    locality: str
    description_type: str
    relation: RelationType
    supported: bool
    reference_features: tuple[str, ...]
    acceptable_ids: frozenset[int]
    reference_absent: bool  # "absent": the reference exists but is not in GNIS
    distance: str
    unit: LengthUnit | None
    direction: CompassPoint | None
    qualifiers: frozenset[str]  # QualifierKind values
    missing: frozenset[str]
    unsure_columns: frozenset[str]  # columns whose value carried a "?" marker
    notes: str


@dataclass(slots=True)
class WorksheetCheck:
    annotations: list[Annotation] = field(default_factory=list)
    problems: list[Problem] = field(default_factory=list)

    @property
    def errors(self) -> list[Problem]:
        return [p for p in self.problems if p.level is Level.ERROR]


def _split(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def _unsure(value: str) -> tuple[str, bool]:
    """Strip a trailing annotator "?" marker (not the qualifier "?" itself)."""
    v = value.strip()
    if len(v) > 1 and v.endswith("?"):
        return v[:-1].strip(), True
    return v, False


def check_worksheet(path: Path, sample: AuditSample, gazetteer: Gazetteer) -> WorksheetCheck:
    result = WorksheetCheck()
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows or tuple(rows[0]) != WORKSHEET_COLUMNS:
        result.problems.append(Problem("-", "header", Level.ERROR, "header differs"))
        return result
    by_id = {i.audit_id: i for i in sample.items}
    seen: set[str] = set()
    all_ids: set[int] = set()
    parsed_rows: list[dict[str, str]] = []
    for raw in rows[1:]:
        if len(raw) != len(WORKSHEET_COLUMNS):
            result.problems.append(Problem(raw[0] if raw else "-", "row", Level.ERROR,
                                           f"{len(raw)} fields"))  # fmt: skip
            continue
        parsed_rows.append(dict(zip(WORKSHEET_COLUMNS, raw, strict=True)))
        for token in _split(parsed_rows[-1]["acceptable_gnis_ids"]):
            token = _unsure(token)[0]
            if token.isdigit():
                all_ids.add(int(token))
    known = gazetteer.describe(all_ids)

    for row in parsed_rows:
        aid = row["audit_id"]

        def problem(column: str, message: str, level: Level = Level.ERROR) -> None:
            result.problems.append(Problem(aid, column, level, message))  # noqa: B023

        item = by_id.get(aid)
        if item is None or aid in seen:
            problem("audit_id", "unknown or duplicate audit id")
            continue
        seen.add(aid)
        r = item.record
        for column, expected in (("gbif_id", r.gbif_id), ("county", r.county),
                                 ("locality", r.locality)):  # fmt: skip
            if row[column] != expected:
                problem(column, "source column was changed")

        unsure: set[str] = set()
        dtype, q = _unsure(row["description_type"])
        if q:
            unsure.add("description_type")
        if dtype not in DESCRIPTION_TYPES:
            problem("description_type", f"{dtype!r} is not in the inventory")
            continue
        supported_raw, q = _unsure(row["supported"])
        if q:
            unsure.add("supported")
        if supported_raw.lower() not in ("yes", "no"):
            problem("supported", f"{supported_raw!r} is not yes/no")

        references = tuple(_split(row["reference_features"]))
        ids: set[int] = set()
        absent = False
        for token in _split(row["acceptable_gnis_ids"]):
            token, q = _unsure(token)
            if q:
                unsure.add("acceptable_gnis_ids")
            if token.lower() == "absent":
                absent = True
            elif token.isdigit():
                if int(token) not in known:
                    problem("acceptable_gnis_ids", f"{token} is not in the GNIS snapshot")
                ids.add(int(token))
            else:
                problem("acceptable_gnis_ids", f"{token!r} is not an ID or 'absent'")
        if absent and ids:
            problem("acceptable_gnis_ids", "both IDs and 'absent'", Level.WARNING)

        distance, q = _unsure(row["distance"])
        if q:
            unsure.add("distance")
        if distance and annotated_distance(distance) is None and not _RANGE.match(distance):
            problem("distance", f"{distance!r} is not a number, fraction or range")
        unit_raw, q = _unsure(row["unit"])
        if q:
            unsure.add("unit")
        unit = None
        if unit_raw:
            try:
                unit = LengthUnit(unit_raw.lower())
            except ValueError:
                problem("unit", f"{unit_raw!r} is not one of {[u.value for u in LengthUnit]}")
        direction_raw, q = _unsure(row["direction"])
        if q:
            unsure.add("direction")
        direction = None
        if direction_raw:
            try:
                direction = CompassPoint(direction_raw.upper())
            except ValueError:
                problem("direction", f"{direction_raw!r} is not a 16-point code")
        qualifiers: set[str] = set()
        for token in _split(row["qualifiers"]):
            kind = QUALIFIER_WORDS.get(token.lower())
            if kind is None:
                problem("qualifiers", f"{token!r} is not a known qualifier", Level.WARNING)
            else:
                qualifiers.add(kind)
        missing: set[str] = set()
        for token in _split(row["missing_information"]):
            word, q = _unsure(token)
            if word.lower().startswith("other"):
                missing.add("other")
            elif word.lower() in MISSING_WORDS:
                missing.add(word.lower())
            else:
                problem("missing_information", f"{token!r} is not in the inventory",
                        Level.WARNING)  # fmt: skip

        # consistency with the stated type
        if dtype in _NEEDS_REFERENCE and not references:
            problem("reference_features", f"{dtype} needs a reference feature")
        if dtype in _NEEDS_REFERENCE and not ids and not absent:
            problem("acceptable_gnis_ids", "no IDs and not 'absent'")
        if (
            dtype in ("distance_and_direction", "distance_only")
            and not distance
            and "distance" not in missing
        ):
            problem("distance", f"{dtype} needs a distance or 'distance' in missing")
        if (
            dtype in ("distance_and_direction", "direction_only")
            and direction is None
            and "direction" not in missing
        ):
            problem("direction", f"{dtype} needs a direction or 'direction' in missing")
        if distance and unit is None and "unit" not in missing:
            problem("unit", "a distance without a unit needs 'unit' in missing", Level.WARNING)
        if dtype == "no_locality" and (references or ids):
            problem("reference_features", "no_locality but a reference is given", Level.WARNING)
        if absent and "feature_not_in_gnis" not in missing:
            problem("missing_information", "'absent' without feature_not_in_gnis", Level.WARNING)

        result.annotations.append(
            Annotation(
                audit_id=aid,
                locality=r.locality,
                description_type=dtype,
                relation=TO_RELATION[dtype],
                supported=supported_raw.lower() == "yes",
                reference_features=references,
                acceptable_ids=frozenset(ids),
                reference_absent=absent,
                distance=distance,
                unit=unit,
                direction=direction,
                qualifiers=frozenset(qualifiers),
                missing=frozenset(missing),
                unsure_columns=frozenset(unsure),
                notes=row["notes"],
            )
        )
    for aid in sorted(set(by_id) - seen):
        result.problems.append(Problem(aid, "row", Level.ERROR, "row missing"))
    return result
