"""Point-radius proposals: interpretation + chosen candidate + uncertainty policy → region.

Nothing here is guessed:

* The point comes from the candidate's GNIS coordinate plus, for offsets, a geodesic forward
  calculation on that coordinate's own datum.
* Each uncertainty component is listed with its rule and citation. An unknown component is
  ``None``, never 0.
* A GNIS representative point is not a feature's extent. Unless a reviewed extent is supplied
  (or the feature class has a published default), the radius stays unknown. The proposal then
  reports a lower bound that excludes extent and asks the curator for the extent.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from localitylens.extract.schema import Interpretation, QualifierKind, RelationType
from localitylens.gazetteer.index import Candidate
from localitylens.geo import uncertainty as policy
from localitylens.geo.directions import nominal_bearing
from localitylens.geo.geodesy import Coordinate, forward
from localitylens.geo.units import METRES_PER_UNIT


class ProposalOutcome(StrEnum):
    COMPUTED = "computed"  # point and full radius known
    NEEDS_INFORMATION = "needs_information"  # a stated question blocks a defensible radius
    UNSUPPORTED = "unsupported"  # locality type outside the supported set


class ComponentName(StrEnum):
    EXTENT = "extent"
    COORDINATE_PRECISION = "coordinate_precision"
    DATUM = "datum"
    COORDINATE_SOURCE = "coordinate_source"
    DISTANCE_PRECISION = "distance_precision"
    OFFSET = "offset"
    HEADING = "heading"


class ExtentSource(StrEnum):
    REVIEWED = "reviewed"  # supplied by a curator, with a rationale
    CLASS_DEFAULT = "class_default"  # QRG Table 1 default for the feature class
    DERIVED = "derived"  # computed from an authoritative polygon or line; not curator-reviewed


class ExtentEstimate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    radius_m: float = Field(gt=0)
    source: ExtentSource
    rationale: str = Field(min_length=1)


class UncertaintyComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: ComponentName
    metres: float | None  # None = unknown, which is never treated as 0
    rule: str
    citation: str


class GeoreferenceProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    policy_id: str = policy.POLICY_ID
    method: str = "point-radius"
    outcome: ProposalOutcome
    feature_id: int | None
    point: Coordinate | None
    radius_m: float | None
    radius_lower_bound_m: float | None  # every known component, extent excluded
    components: tuple[UncertaintyComponent, ...]
    assumptions: tuple[str, ...]
    questions: tuple[str, ...]
    reasons: tuple[str, ...]


_SUPPORTED: frozenset[RelationType] = frozenset(
    {RelationType.NAMED_FEATURE, RelationType.DISTANCE_AND_DIRECTION, RelationType.DISTANCE_ONLY}
)


def default_extent(candidate: Candidate) -> ExtentEstimate | None:
    radius = policy.DEFAULT_RADIAL_BY_GNIS_CLASS_M.get(candidate.feature_class)
    if radius is None:
        return None
    return ExtentEstimate(
        radius_m=radius,
        source=ExtentSource.CLASS_DEFAULT,
        rationale=f"QRG Table 1 default for a {candidate.feature_class.lower()}",
    )


def propose(
    interpretation: Interpretation,
    candidate: Candidate | None,
    extent: ExtentEstimate | None = None,
) -> GeoreferenceProposal:
    """Build a point-radius proposal for one interpretation and one chosen candidate."""
    relation = interpretation.relation
    if relation not in _SUPPORTED:
        reason = {
            RelationType.DIRECTION_ONLY: (
                f"Heading without a distance has no defensible bound ({policy.CITE_HEADING_ONLY})."
            ),
            RelationType.ROUTE_RELATIVE: "Distance along a route needs the route geometry.",
            RelationType.ORTHOGONAL_OFFSETS: "Orthogonal offsets are not supported yet.",
            RelationType.BETWEEN_FEATURES: "'Between two features' is not supported yet.",
            RelationType.NO_LOCALITY: "The label gives no locality.",
        }.get(relation, f"Locality type '{relation.value}' is not supported.")
        outcome = (
            ProposalOutcome.NEEDS_INFORMATION
            if relation is RelationType.DIRECTION_ONLY
            else ProposalOutcome.UNSUPPORTED
        )
        return _empty(outcome, candidate, reasons=(reason,))
    if candidate is None:
        return _empty(
            ProposalOutcome.NEEDS_INFORMATION,
            None,
            questions=("Which gazetteer feature is the reference?",),
        )

    questions: list[str] = []
    assumptions: list[str] = [
        f"Reference point: GNIS feature {candidate.feature_id} ({candidate.official_name}), "
        f"representative point in {candidate.primary_point.datum.value}."
    ]
    origin = candidate.primary_point
    datum = origin.datum

    # --- qualifiers -----------------------------------------------------------------------
    kinds = {q.kind for q in interpretation.qualifiers}
    if QualifierKind.APPROXIMATE in kinds:
        assumptions.append(
            f"'about'/'ca.' does not change coordinates or uncertainty ({policy.CITE_ADVERBIAL})."
        )
    if kinds & {QualifierKind.NEAR, QualifierKind.VICINITY}:
        questions.append(
            f"'near'/'vicinity' has no defensible default buffer ({policy.CITE_NEAR}); "
            f"how far around {candidate.official_name} should the region extend?"
        )
    if QualifierKind.QUESTIONED in kinds:
        questions.append("The label marks part of the locality as uncertain ('?'); confirm it.")

    # --- components shared by every supported type ---------------------------------------
    extent = extent or default_extent(candidate)
    extent_m = extent.radius_m if extent else None
    if extent is None:
        questions.append(
            f"What is the extent of {candidate.official_name} ({candidate.feature_class})? GNIS "
            "gives only a representative point, which is not the feature's extent."
        )
    if candidate.feature_class == "Stream":
        assumptions.append("GNIS places a stream's representative point at its mouth.")
    components: list[UncertaintyComponent] = [
        UncertaintyComponent(
            name=ComponentName.EXTENT,
            metres=extent_m,
            rule=f"{extent.source.value}: {extent.rationale}" if extent else "unknown",
            citation=policy.CITE_EXTENT,
        ),
        UncertaintyComponent(
            name=ComponentName.DATUM,
            metres=0.0,
            rule=f"recorded ({datum.value}), not transformed",
            citation=policy.CITE_DATUM,
        ),
        UncertaintyComponent(
            name=ComponentName.COORDINATE_SOURCE,
            metres=0.0,
            rule="gazetteer coordinate, no map measurement",
            citation=policy.CITE_COORDINATE_SOURCE,
        ),
    ]

    # --- geometry per locality type -------------------------------------------------------
    point = origin
    coordinate_latitude = origin.latitude
    dp_known = 0.0  # Calculator "dp": datum + extent + measurement + distance precision + scale
    offset_m = 0.0
    alpha: float | None = None

    distance = interpretation.distance
    if relation in (RelationType.DISTANCE_AND_DIRECTION, RelationType.DISTANCE_ONLY):
        if distance is None or distance.unit is None:
            questions.append("The distance or its unit is missing.")
            return _finish(
                ProposalOutcome.NEEDS_INFORMATION,
                candidate,
                None,
                components,
                assumptions,
                questions,
            )
        per_unit = METRES_PER_UNIT[distance.unit]
        offset_m = distance.quantity.value * per_unit
        precision, rule = policy.distance_precision(distance.quantity)
        dp_m = precision / 2.0 * per_unit
        dp_known += dp_m
        components.append(
            UncertaintyComponent(
                name=ComponentName.DISTANCE_PRECISION,
                metres=dp_m,
                rule=f"{rule}: precision {precision:g} {distance.unit.value}, half of it",
                citation=policy.CITE_DISTANCE_PRECISION,
            )
        )

    if relation is RelationType.DISTANCE_AND_DIRECTION:
        direction = interpretation.direction
        if direction is None:
            questions.append("The direction is missing.")
            return _finish(
                ProposalOutcome.NEEDS_INFORMATION,
                candidate,
                None,
                components,
                assumptions,
                questions,
            )
        bearing = nominal_bearing(direction.point)
        alpha = policy.heading_uncertainty_deg(direction.point)
        point = forward(origin, bearing, offset_m)
        coordinate_latitude = point.latitude
        assumptions.append(
            f"'{direction.span.text}' read as bearing {bearing:g}° ± {alpha:g}° from true north "
            f"({policy.CITE_HEADING}; {policy.CITE_TRUE_NORTH})."
        )
        assumptions.append(f"Offset measured as a straight line: {offset_m:,.1f} m.")
    elif relation is RelationType.DISTANCE_ONLY:
        components.append(
            UncertaintyComponent(
                name=ComponentName.OFFSET,
                metres=offset_m,
                rule="distance without heading: the whole circle of that radius is possible",
                citation=policy.CITE_COMBINATION,
            )
        )

    coord_m = policy.coordinate_precision_error_m(
        coordinate_latitude, datum, policy.GNIS_COORDINATE_PRECISION_DEG
    )
    components.append(
        UncertaintyComponent(
            name=ComponentName.COORDINATE_PRECISION,
            metres=coord_m,
            rule="GNIS coordinates to the nearest second",
            citation=policy.CITE_COORDINATE_PRECISION,
        )
    )

    def radius(extent_value: float) -> float:
        dp = dp_known + extent_value  # datum, coordinate source and measurement are 0 here
        if relation is RelationType.DISTANCE_AND_DIRECTION and alpha is not None:
            heading_err = policy.heading_distance_error(offset_m, dp, alpha)
            return heading_err + coord_m
        return dp + offset_m + coord_m  # named feature (offset 0) and distance only

    if alpha is not None:
        components.append(
            UncertaintyComponent(
                name=ComponentName.HEADING,
                metres=policy.heading_distance_error(offset_m, 0.0, alpha),
                rule=f"±{alpha:g}° at {offset_m:,.0f} m (alone; combined geometrically)",
                citation=policy.CITE_HEADING,
            )
        )

    lower = radius(0.0)
    full = radius(extent_m) if extent_m is not None else None
    outcome = ProposalOutcome.COMPUTED if not questions else ProposalOutcome.NEEDS_INFORMATION
    return GeoreferenceProposal(
        outcome=outcome,
        feature_id=candidate.feature_id,
        point=point,
        radius_m=full,
        radius_lower_bound_m=lower,
        components=tuple(components),
        assumptions=tuple(assumptions),
        questions=tuple(questions),
        reasons=(),
    )


def _empty(
    outcome: ProposalOutcome,
    candidate: Candidate | None,
    *,
    questions: tuple[str, ...] = (),
    reasons: tuple[str, ...] = (),
) -> GeoreferenceProposal:
    return GeoreferenceProposal(
        outcome=outcome,
        feature_id=candidate.feature_id if candidate else None,
        point=None,
        radius_m=None,
        radius_lower_bound_m=None,
        components=(),
        assumptions=(),
        questions=questions,
        reasons=reasons,
    )


def _finish(
    outcome: ProposalOutcome,
    candidate: Candidate,
    point: Coordinate | None,
    components: list[UncertaintyComponent],
    assumptions: list[str],
    questions: list[str],
) -> GeoreferenceProposal:
    return GeoreferenceProposal(
        outcome=outcome,
        feature_id=candidate.feature_id,
        point=point,
        radius_m=None,
        radius_lower_bound_m=None,
        components=tuple(components),
        assumptions=tuple(assumptions),
        questions=tuple(questions),
        reasons=(),
    )
