"""Point-radius proposals. Candidates use SYNTHETIC coordinates, not real feature positions."""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from localitylens.extract.schema import ExtractionOutput, Interpretation
from localitylens.extract.validate import validate_extraction
from localitylens.gazetteer.index import Candidate, MatchKind
from localitylens.geo import uncertainty as policy
from localitylens.geo.geodesy import Coordinate, Datum, inverse
from localitylens.geo.georeference import (
    ComponentName,
    ExtentEstimate,
    ExtentSource,
    ProposalOutcome,
    propose,
)
from localitylens.ingest.normalize import normalize

ORIGIN = Coordinate(latitude=40.0, longitude=-105.5, datum=Datum.NAD83)  # synthetic


def candidate(feature_class: str = "Summit", name: str = "Testa Peak") -> Candidate:
    return Candidate(
        feature_id=1,
        official_name=name,
        matched_name=name,
        match_kind=MatchKind.EXACT_OFFICIAL,
        name_similarity=100.0,
        feature_class=feature_class,
        feature_type=None,
        state_name="Colorado",
        county_name="Alpha",
        primary_point=ORIGIN,
        source_point=None,
        historical=False,
        variant_citation=None,
        variant_source_date=None,
        state_match=True,
        county_match=None,
        type_match=None,
    )


def interp(text: str, **extraction: Any) -> Interpretation:
    result = validate_extraction(ExtractionOutput.model_validate(extraction), normalize(text))
    assert result.interpretation is not None, result.issues
    return result.interpretation


def offset(text: str = "2 mi NE of Testa Peak", value: str = "2", unit: str = "mile",
           unit_quote: str = "mi", point: str = "NE", **extra: Any) -> Interpretation:  # fmt: skip
    return interp(
        text,
        relation="distance_and_direction",
        reference_feature={"name_quote": "Testa Peak"},
        distance={"value_quote": value, "unit": unit, "unit_quote": unit_quote},
        direction={"point": point, "quote": point},
        **extra,
    )


NAMED = interp(
    "Testa Peak", relation="named_feature", reference_feature={"name_quote": "Testa Peak"}
)
REVIEWED = ExtentEstimate(radius_m=500.0, source=ExtentSource.REVIEWED, rationale="test extent")


def component(p: Any, name: ComponentName) -> float | None:
    return next(c.metres for c in p.components if c.name is name)


def test_unknown_extent_is_never_zero_and_blocks_the_radius() -> None:
    p = propose(NAMED, candidate())
    assert p.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert p.radius_m is None
    assert component(p, ComponentName.EXTENT) is None
    assert p.radius_lower_bound_m == pytest.approx(component(p, ComponentName.COORDINATE_PRECISION))
    assert any("extent of Testa Peak" in q for q in p.questions)


def test_reviewed_extent_completes_a_named_feature() -> None:
    p = propose(NAMED, candidate(), REVIEWED)
    assert p.outcome is ProposalOutcome.COMPUTED
    coord = component(p, ComponentName.COORDINATE_PRECISION)
    assert coord is not None
    assert p.radius_m == pytest.approx(500.0 + coord)
    assert p.point == ORIGIN


def test_spring_uses_the_qrg_default_radial() -> None:
    p = propose(NAMED, candidate("Spring", "Testa Spring"))
    assert p.outcome is ProposalOutcome.COMPUTED
    assert component(p, ComponentName.EXTENT) == 3.0


def test_offset_point_and_radius_follow_the_calculator() -> None:
    p = propose(offset(), candidate(), REVIEWED)
    assert p.outcome is ProposalOutcome.COMPUTED
    assert p.point is not None
    bearing, dist = inverse(ORIGIN, p.point)
    assert dist == pytest.approx(3218.688, abs=1e-3)
    assert bearing == pytest.approx(45.0, abs=1e-6)
    dp = 0.5 * 1609.344 + 500.0  # distance precision (half of 1 mi) + extent
    coord = component(p, ComponentName.COORDINATE_PRECISION)
    assert coord is not None
    expected = policy.heading_distance_error(3218.688, dp, 22.5) + coord
    assert p.radius_m == pytest.approx(expected)
    assert any("45° ± 22.5°" in a for a in p.assumptions)


def test_distance_only_is_a_full_circle() -> None:
    i = interp(
        "2 mi from Testa Peak",
        relation="distance_only",
        reference_feature={"name_quote": "Testa Peak"},
        distance={"value_quote": "2", "unit": "mile", "unit_quote": "mi"},
    )
    p = propose(i, candidate(), REVIEWED)
    coord = component(p, ComponentName.COORDINATE_PRECISION)
    assert coord is not None
    assert p.point == ORIGIN
    assert p.radius_m == pytest.approx(3218.688 + 0.5 * 1609.344 + 500.0 + coord)


def test_about_does_not_change_the_result() -> None:
    plain = propose(offset(), candidate(), REVIEWED)
    about = propose(
        offset(
            "about 2 mi NE of Testa Peak", qualifiers=[{"kind": "approximate", "quote": "about"}]
        ),
        candidate(),
        REVIEWED,
    )
    assert about.radius_m == pytest.approx(plain.radius_m)
    assert about.outcome is ProposalOutcome.COMPUTED
    assert any("about" in a for a in about.assumptions)


def test_near_needs_a_curator_decision() -> None:
    i = interp(
        "near Testa Peak",
        relation="named_feature",
        reference_feature={"name_quote": "Testa Peak"},
        qualifiers=[{"kind": "near", "quote": "near"}],
    )
    p = propose(i, candidate(), REVIEWED)
    assert p.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert any("near" in q for q in p.questions)


def test_missing_unit_cannot_be_computed() -> None:
    i = interp(
        "2 NE of Testa Peak",
        relation="distance_and_direction",
        reference_feature={"name_quote": "Testa Peak"},
        distance={"value_quote": "2"},
        direction={"point": "NE", "quote": "NE"},
        missing=["distance_unit"],
    )
    p = propose(i, candidate(), REVIEWED)
    assert p.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert p.radius_m is None
    assert p.point is None


@pytest.mark.parametrize(
    ("relation", "outcome"),
    [("direction_only", ProposalOutcome.NEEDS_INFORMATION),
     ("route_relative", ProposalOutcome.UNSUPPORTED),
     ("between_features", ProposalOutcome.UNSUPPORTED),
     ("no_locality", ProposalOutcome.UNSUPPORTED)],
)  # fmt: skip
def test_unsupported_and_unbounded_types(relation: str, outcome: ProposalOutcome) -> None:
    extraction: dict[str, Any] = {"relation": relation}
    if relation == "direction_only":
        extraction |= {
            "reference_feature": {"name_quote": "Testa Peak"},
            "direction": {"point": "NE", "quote": "NE"},
        }
    p = propose(interp("NE of Testa Peak", **extraction), candidate(), REVIEWED)
    assert p.outcome is outcome
    assert p.point is None
    assert p.reasons


def test_no_candidate_asks_which_feature() -> None:
    p = propose(NAMED, None)
    assert p.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert p.questions == ("Which gazetteer feature is the reference?",)


def test_stream_point_is_flagged_as_the_mouth() -> None:
    p = propose(NAMED, candidate("Stream", "Testa Peak"))
    assert any("mouth" in a for a in p.assumptions)
    assert p.radius_m is None


@given(
    extent=st.floats(1.0, 20_000.0),
    more=st.floats(0.1, 5_000.0),
    point=st.sampled_from(["N", "NE", "NNE", "W", "SSW"]),
    value=st.sampled_from(["1", "2.5", "10", "1/2", "140"]),
)
def test_radius_invariants(extent: float, more: float, point: str, value: str) -> None:
    i = offset(f"{value} mi {point} of Testa Peak", value=value, point=point)

    def reviewed(radius: float) -> ExtentEstimate:
        return ExtentEstimate(radius_m=radius, source=ExtentSource.REVIEWED, rationale="t")

    small = propose(i, candidate(), reviewed(extent))
    large = propose(i, candidate(), reviewed(extent + more))
    assert small.radius_m is not None
    assert large.radius_m is not None
    assert small.radius_lower_bound_m is not None
    assert small.radius_m >= small.radius_lower_bound_m  # extent never shrinks the region
    assert large.radius_m > small.radius_m  # more extent, larger region
    heading = component(small, ComponentName.HEADING)
    assert heading is not None
    assert small.radius_m >= heading  # the combined radius covers the heading arc
