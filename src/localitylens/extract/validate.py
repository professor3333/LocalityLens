"""Deterministic validation of extractor output against the locality text.

Validation checks that the output is *mechanically* sound: every quote exists in the text,
every number and unit was parsed by code, quoted forms agree with the enums the extractor
chose, and required components are either present or declared missing. Passing validation
does **not** mean the interpretation is semantically right. That is the curator's job and the
evaluation's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from localitylens.extract.feature_words import type_for_word
from localitylens.extract.quantities import parse_quantity
from localitylens.extract.schema import (
    ExtractionOutput,
    Interpretation,
    MissingKind,
    RelationType,
    ResolvedAdmin,
    ResolvedDirection,
    ResolvedDistance,
    ResolvedFeature,
    ResolvedQualifier,
    Span,
)
from localitylens.geo.directions import parse_direction
from localitylens.geo.units import AMBIGUOUS_UNIT_FORMS, parse_unit
from localitylens.ingest.normalize import NORMALIZATION_VERSION, NormalizedText


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class IssueCode(StrEnum):
    QUOTE_NOT_FOUND = "quote_not_found"
    QUOTE_OUTSIDE_RELATION = "quote_outside_relation"
    UNPARSEABLE_DISTANCE = "unparseable_distance"
    UNIT_MISMATCH = "unit_mismatch"
    AMBIGUOUS_UNIT_ASSERTED = "ambiguous_unit_asserted"
    UNIT_UNDECLARED = "unit_undeclared"
    DIRECTION_MISMATCH = "direction_mismatch"
    DIRECTION_UNPARSED = "direction_unparsed"
    REQUIRED_COMPONENT_UNDECLARED = "required_component_undeclared"
    CONTRADICTORY_MISSING = "contradictory_missing"
    FEATURE_TYPE_UNSUPPORTED = "feature_type_unsupported"


@dataclass(frozen=True, slots=True)
class Issue:
    code: IssueCode
    severity: Severity
    path: str
    detail: str


@dataclass(slots=True)
class ValidationResult:
    interpretation: Interpretation | None
    issues: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.interpretation is not None


# Components each relation needs; each must be present or explicitly declared missing.
REQUIRED_COMPONENTS: dict[RelationType, frozenset[MissingKind]] = {
    RelationType.NAMED_FEATURE: frozenset({MissingKind.REFERENCE_FEATURE}),
    RelationType.DISTANCE_AND_DIRECTION: frozenset(
        {MissingKind.REFERENCE_FEATURE, MissingKind.DISTANCE, MissingKind.DIRECTION}
    ),
    RelationType.DIRECTION_ONLY: frozenset({MissingKind.REFERENCE_FEATURE, MissingKind.DIRECTION}),
    RelationType.DISTANCE_ONLY: frozenset({MissingKind.REFERENCE_FEATURE, MissingKind.DISTANCE}),
}


class _Locator:
    """Finds quotes in normalized text and returns spans of the ORIGINAL text."""

    def __init__(self, text: NormalizedText) -> None:
        self._text = text
        folded = text.text.casefold()
        # Case-insensitive matching only when folding keeps offsets aligned (e.g. not "ß").
        self._folded: str | None = folded if len(folded) == len(text.text) else None
        self.relation_range: tuple[int, int] | None = None

    def _find(self, quote: str) -> tuple[int, int] | None:
        q = " ".join(quote.split())
        if not q:
            return None
        windows = [self.relation_range] if self.relation_range else []
        windows.append((0, len(self._text.text)))
        searches: list[tuple[str, str]] = [(self._text.text, q)]
        folded_q = q.casefold()
        if self._folded is not None and len(folded_q) == len(q):
            searches.append((self._folded, folded_q))
        for haystack, needle in searches:
            for lo, hi in windows:
                idx = haystack.find(needle, lo, hi)
                if idx >= 0:
                    return idx, idx + len(needle)
        return None

    def span(self, quote: str) -> Span | None:
        found = self._find(quote)
        if found is None:
            return None
        o_start, o_end = self._text.to_original(*found)
        return Span(start=o_start, end=o_end, text=self._text.original[o_start:o_end])

    def normalized_range(self, quote: str) -> tuple[int, int] | None:
        return self._find(quote)


def validate_extraction(output: ExtractionOutput, text: NormalizedText) -> ValidationResult:
    issues: list[Issue] = []
    loc = _Locator(text)

    def err(code: IssueCode, path: str, detail: str) -> None:
        issues.append(Issue(code, Severity.ERROR, path, detail))

    def warn(code: IssueCode, path: str, detail: str) -> None:
        issues.append(Issue(code, Severity.WARNING, path, detail))

    def locate(quote: str, path: str) -> Span | None:
        span = loc.span(quote)
        if span is None:
            err(IssueCode.QUOTE_NOT_FOUND, path, f"quote {quote!r} does not occur in the text")
            return None
        is_component = path.startswith(("reference_feature", "distance", "direction"))
        if loc.relation_range is not None and is_component:
            rng = loc.normalized_range(quote)
            lo, hi = loc.relation_range
            if rng is not None and not (lo <= rng[0] and rng[1] <= hi):
                warn(IssueCode.QUOTE_OUTSIDE_RELATION, path, "quote lies outside relation_quote")
        return span

    relation_span: Span | None = None
    if output.relation_quote is not None:
        relation_span = locate(output.relation_quote, "relation_quote")
        if relation_span is not None:
            loc.relation_range = loc.normalized_range(output.relation_quote)

    declared_missing = set(output.missing)

    feature: ResolvedFeature | None = None
    if (f := output.reference_feature) is not None:
        name_span = locate(f.name_quote, "reference_feature.name_quote")
        type_span = (
            locate(f.feature_type_quote, "reference_feature.feature_type_quote")
            if f.feature_type_quote is not None
            else None
        )
        feature_type = f.feature_type
        if feature_type is not None and (
            f.feature_type_quote is None or type_for_word(f.feature_type_quote) is not feature_type
        ):
            warn(
                IssueCode.FEATURE_TYPE_UNSUPPORTED,
                "reference_feature.feature_type",
                f"{feature_type.value!r} is not stated by {f.feature_type_quote!r}; type dropped",
            )
            feature_type, type_span = None, None
        if name_span is not None:
            feature = ResolvedFeature(
                name=name_span.text,
                span=name_span,
                feature_type=feature_type,
                feature_type_span=type_span,
            )

    distance: ResolvedDistance | None = None
    if (d := output.distance) is not None:
        value_span = locate(d.value_quote, "distance.value_quote")
        quantity = parse_quantity(d.value_quote)
        if quantity is None:
            err(
                IssueCode.UNPARSEABLE_DISTANCE,
                "distance.value_quote",
                f"cannot parse a positive number from {d.value_quote!r}",
            )
        unit_span = None
        if d.unit_quote is not None:
            unit_span = locate(d.unit_quote, "distance.unit_quote")
            form = d.unit_quote.strip().lower()
            if form in AMBIGUOUS_UNIT_FORMS:
                err(
                    IssueCode.AMBIGUOUS_UNIT_ASSERTED,
                    "distance.unit",
                    f"{d.unit_quote!r} may mean miles or metres; declare distance_unit missing",
                )
            elif (parsed := parse_unit(d.unit_quote)) is not None and parsed != d.unit:
                err(
                    IssueCode.UNIT_MISMATCH,
                    "distance.unit",
                    f"quote {d.unit_quote!r} reads as {parsed.value}, output says {d.unit}",
                )
        elif MissingKind.DISTANCE_UNIT not in declared_missing:
            err(
                IssueCode.UNIT_UNDECLARED,
                "distance.unit",
                "distance has no unit and distance_unit is not declared missing",
            )
        if value_span is not None and quantity is not None:
            distance = ResolvedDistance(
                quantity=quantity, value_span=value_span, unit=d.unit, unit_span=unit_span
            )

    direction: ResolvedDirection | None = None
    if (r := output.direction) is not None:
        span = locate(r.quote, "direction.quote")
        parsed_point = parse_direction(r.quote)
        if parsed_point is None:
            warn(IssueCode.DIRECTION_UNPARSED, "direction.quote", f"{r.quote!r} not parsed by code")
        elif parsed_point != r.point:
            err(
                IssueCode.DIRECTION_MISMATCH,
                "direction.point",
                f"quote {r.quote!r} reads as {parsed_point.value}, output says {r.point.value}",
            )
        if span is not None:
            direction = ResolvedDirection(point=r.point, span=span)

    admins: list[ResolvedAdmin] = []
    for i, a in enumerate(output.admin_mentions):
        if (span := locate(a.quote, f"admin_mentions[{i}].quote")) is not None:
            admins.append(ResolvedAdmin(level=a.level, span=span))

    qualifiers: list[ResolvedQualifier] = []
    for i, q in enumerate(output.qualifiers):
        if (span := locate(q.quote, f"qualifiers[{i}].quote")) is not None:
            qualifiers.append(ResolvedQualifier(kind=q.kind, span=span))

    present = {
        MissingKind.REFERENCE_FEATURE: output.reference_feature is not None,
        MissingKind.DISTANCE: output.distance is not None,
        MissingKind.DIRECTION: output.direction is not None,
    }
    for kind, is_present in present.items():
        if is_present and kind in declared_missing:
            err(IssueCode.CONTRADICTORY_MISSING, "missing", f"{kind.value} both given and missing")
    unit_given = output.distance is not None and output.distance.unit is not None
    if unit_given and MissingKind.DISTANCE_UNIT in declared_missing:
        err(IssueCode.CONTRADICTORY_MISSING, "missing", "distance_unit both given and missing")
    for kind in REQUIRED_COMPONENTS.get(output.relation, frozenset()):
        if not present[kind] and kind not in declared_missing:
            err(
                IssueCode.REQUIRED_COMPONENT_UNDECLARED,
                kind.value,
                f"{output.relation.value} needs {kind.value} or must declare it missing",
            )

    if any(i.severity is Severity.ERROR for i in issues):
        return ValidationResult(interpretation=None, issues=issues)

    interpretation = Interpretation(
        normalization_version=NORMALIZATION_VERSION,
        relation=output.relation,
        relation_span=relation_span,
        reference_feature=feature,
        distance=distance,
        direction=direction,
        admin_mentions=tuple(admins),
        qualifiers=tuple(qualifiers),
        missing=tuple(output.missing),
        open_questions=tuple(output.open_questions),
    )
    return ValidationResult(interpretation=interpretation, issues=issues)
