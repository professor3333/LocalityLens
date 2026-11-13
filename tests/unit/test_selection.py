"""Selection checks (selection-1, -2, -3). Label texts use invented place names."""

from hypothesis import given, settings
from hypothesis import strategies as st

from localitylens.geo.geodesy import Coordinate, Datum
from localitylens.geo.georeference import GeoreferenceProposal, ProposalOutcome
from localitylens.resolve.selection import (
    QUESTION_PREFIX,
    apply_selection_check,
    competing_features,
    only_selection_questions,
)


def test_a_typed_feature_other_than_the_reference_competes() -> None:
    assert competing_features("Brindle Lake, 4 mi E of Osgood.", "Osgood") == ["Brindle Lake"]
    assert competing_features("Slope of Tamsin Peak, ca. six miles west of Osgood.", "Osgood") == [
        "Tamsin Peak"
    ]
    assert competing_features("Osgood. Fenn River.", "Osgood") == ["Fenn River"]  # across a "."
    curly = "Brindle" + chr(0x2019) + "s Lake"  # a right single quote, as on many labels
    assert competing_features(f"{curly}, 4 mi E of Osgood", "Osgood") == [curly]


def test_broad_areas_untyped_names_and_the_reference_itself_do_not() -> None:
    assert competing_features("Marlow National Forest, 5 mi N of Osgood.", "Osgood") == []
    assert competing_features("Fenn Range: 5 mi N of Osgood.", "Osgood") == []
    assert competing_features("Nine miles north of Osgood on Oak Mesa.", "Osgood") == []  # mesa
    assert competing_features("2 mi NE of Brindle Peak summit.", "Brindle Peak") == []
    assert competing_features("Ranch at the Fenn Fork. Floodplain of the Fenn Fork River.",
                              "Fenn Fork") == []  # contains the reference  # fmt: skip


def _proposal(outcome: ProposalOutcome, questions: tuple[str, ...] = ()) -> GeoreferenceProposal:
    return GeoreferenceProposal(
        outcome=outcome, feature_id=1,
        point=Coordinate(latitude=40.0, longitude=-105.0, datum=Datum.NAD83),
        radius_m=1000.0, radius_lower_bound_m=500.0, components=(), assumptions=(),
        questions=questions, reasons=(),
    )  # fmt: skip


def test_a_held_region_keeps_its_geometry_and_asks() -> None:
    held = apply_selection_check("Brindle Lake, 4 mi E of Osgood.", "Osgood",
                                 _proposal(ProposalOutcome.COMPUTED))  # fmt: skip
    assert held.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert (held.point, held.radius_m) == (_proposal(ProposalOutcome.COMPUTED).point, 1000.0)
    assert held.questions[0].startswith(QUESTION_PREFIX)
    assert "'Brindle Lake'" in held.questions[0]
    assert only_selection_questions(held)
    other = _proposal(ProposalOutcome.NEEDS_INFORMATION, ("Which feature?",))
    assert apply_selection_check("Brindle Lake, 4 mi E of Osgood.", "Osgood", other) is other
    assert not only_selection_questions(other)
    clean = _proposal(ProposalOutcome.COMPUTED)
    assert apply_selection_check("4 mi E of Osgood.", "Osgood", clean) is clean


def test_selection_2_holds_only_for_a_named_place_inside_the_region_or_missing_from_gnis(
    gnis_snapshot, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    """Synthetic GNIS: Testa Lake at 40.2, -105.2 and Vela Lake at 40.31, -105.31 (~15 km)."""
    from localitylens.data.manifest import write_manifest
    from localitylens.gazetteer.index import Gazetteer, build_index
    from localitylens.resolve.selection import apply_selection_2, geographic_competitors

    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    build_index(directory, manifest, tmp_path / "g.sqlite")

    def at_testa(radius: float) -> GeoreferenceProposal:
        return GeoreferenceProposal(
            outcome=ProposalOutcome.COMPUTED, feature_id=3,
            point=Coordinate(latitude=40.2, longitude=-105.2, datum=Datum.NAD83),
            radius_m=radius, radius_lower_bound_m=None, components=(), assumptions=(),
            questions=(), reasons=(),
        )  # fmt: skip

    label = "Below Vela Lake, 1 mi N of Testa Lake"
    with Gazetteer(tmp_path / "g.sqlite") as gaz:
        wide, narrow = at_testa(20_000), at_testa(5_000)
        assert geographic_competitors(label, "Testa Lake", wide, gaz, "Alpha") == [
            ("Vela Lake", "inside")
        ]
        assert geographic_competitors(label, "Testa Lake", narrow, gaz, "Alpha") == []
        held = apply_selection_2(label, "Testa Lake", wide, gaz, "Alpha")
        assert held.outcome is ProposalOutcome.NEEDS_INFORMATION
        assert held.radius_m == 20_000
        assert "in GNIS, inside the proposed region" in held.questions[0]
        assert apply_selection_2(label, "Testa Lake", narrow, gaz, "Alpha") is narrow
        missing = "Near Brindle Lake, 1 mi N of Testa Lake"  # not in the synthetic GNIS
        assert geographic_competitors(missing, "Testa Lake", narrow, gaz, "Alpha") == [
            ("Brindle Lake", "absent")
        ]


# ------------------------------------------------------------------- selection-3 (same-name ties)
# Synthetic candidates with invented names and points; no gazetteer is needed when the label
# names no other place.


def _candidate(fid: int, lat: float, *, county: str = "Marlow", county_match: bool = True,
               kind: str = "exact_official", similarity: float = 100.0):  # type: ignore[no-untyped-def]  # fmt: skip
    from localitylens.extract.schema import FeatureType
    from localitylens.gazetteer.index import Candidate, MatchKind

    return Candidate(
        feature_id=fid, official_name="Brindle Peak", matched_name="Brindle Peak",
        match_kind=MatchKind(kind), name_similarity=similarity, feature_class="Summit",
        feature_type=FeatureType.SUMMIT, state_name="Colorado", county_name=county,
        primary_point=Coordinate(latitude=lat, longitude=-105.0, datum=Datum.NAD83),
        source_point=None, historical=False, variant_citation=None, variant_source_date=None,
        state_match=True, county_match=county_match, type_match=True,
    )  # fmt: skip


def _at(fid: int, radius: float, outcome: ProposalOutcome = ProposalOutcome.COMPUTED):  # type: ignore[no-untyped-def]  # fmt: skip
    return GeoreferenceProposal(
        outcome=outcome, feature_id=fid,
        point=Coordinate(latitude=40.0, longitude=-105.0, datum=Datum.NAD83),
        radius_m=radius, radius_lower_bound_m=None, components=(), assumptions=(),
        questions=(), reasons=(),
    )  # fmt: skip


def test_the_evidence_key_ignores_only_the_stable_order_tie_breakers() -> None:
    from localitylens.gazetteer.index import evidence_key

    official, variant = _candidate(1, 40.0), _candidate(2, 40.5, kind="exact_variant")
    assert evidence_key(official) == evidence_key(variant)  # same tier: "Mt. Evans"
    assert evidence_key(official) != evidence_key(_candidate(3, 40.5, county_match=False))
    assert evidence_key(official) != evidence_key(_candidate(4, 40.5, kind="core_official"))
    fuzzy = _candidate(5, 40.5, kind="fuzzy_official", similarity=90.0)
    assert evidence_key(fuzzy) != evidence_key(_candidate(6, 40.5, kind="fuzzy_official",
                                                          similarity=88.0))  # fmt: skip


def test_a_tie_counts_only_when_it_would_move_the_region_outside_this_one() -> None:
    from localitylens.resolve.selection import same_name_ties

    chosen = _candidate(1, 40.0)
    far = _candidate(2, 40.5)  # ~55 km north
    near = _candidate(3, 40.01)  # ~1.1 km north
    other_county = _candidate(4, 41.0, county="Hale", county_match=False)
    cands = (chosen, far, near, other_county)
    assert [c.feature_id for c in same_name_ties(_at(1, 5_000), cands)] == [2]
    assert same_name_ties(_at(1, 60_000), cands) == []  # both inside a 60 km region
    assert same_name_ties(_at(9, 5_000), cands) == []  # the proposal's feature isn't listed
    no_radius = _at(1, 5_000).model_copy(update={"radius_m": None})
    assert same_name_ties(no_radius, cands) == []


def test_selection_3_holds_a_tied_region_asks_which_and_keeps_its_geometry() -> None:
    from localitylens.resolve.selection import SELECTION_3_VERSION, apply_selection_3

    cands = (_candidate(1, 40.0), _candidate(2, 40.5))
    label = "2 mi N of Brindle Peak"
    held = apply_selection_3(label, "Brindle Peak", _at(1, 5_000), None, "Marlow", cands)
    assert held.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert (held.feature_id, held.point, held.radius_m) == (1, _at(1, 5_000).point, 5_000)
    (question,) = held.questions
    assert question.startswith(QUESTION_PREFIX + "candidates unresolved")
    assert "GNIS 1)" in question
    assert "GNIS 2, 56 km away" in question
    assert SELECTION_3_VERSION in question
    assert only_selection_questions(held)  # a curator's approval confirms the chosen feature

    clean = _at(1, 5_000)
    assert apply_selection_3(label, "Brindle Peak", clean, None, "Marlow", cands[:1]) is clean
    waiting = _at(1, 5_000, ProposalOutcome.NEEDS_INFORMATION)
    assert apply_selection_3(label, "Brindle Peak", waiting, None, "Marlow", cands) is waiting


def test_selection_3_keeps_the_selection_2_question_and_adds_its_own(
    gnis_snapshot, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    from localitylens.data.manifest import write_manifest
    from localitylens.gazetteer.index import Gazetteer, build_index
    from localitylens.resolve.selection import apply_selection_3

    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    build_index(directory, manifest, tmp_path / "g.sqlite")
    label = "Near Brindle Lake, 1 mi N of Brindle Peak"  # Brindle Lake: not in this GNIS
    with Gazetteer(tmp_path / "g.sqlite") as gaz:
        held = apply_selection_3(label, "Brindle Peak", _at(1, 5_000), gaz, "Alpha",
                                 (_candidate(1, 40.0), _candidate(2, 40.5)))  # fmt: skip
    assert held.outcome is ProposalOutcome.NEEDS_INFORMATION
    assert len(held.questions) == 2
    assert "'Brindle Lake' (not in GNIS)" in held.questions[0]
    assert "candidates unresolved" in held.questions[1]


@settings(max_examples=200, deadline=None)
@given(
    lats=st.lists(st.floats(min_value=37.0, max_value=41.0), min_size=1, max_size=5),
    counties=st.lists(st.booleans(), min_size=5, max_size=5),
    radius=st.floats(min_value=1.0, max_value=500_000.0),
)
def test_selection_3_only_ever_holds_and_never_moves_a_region(
    lats: list[float], counties: list[bool], radius: float
) -> None:
    """Whatever the candidates, the check returns the same feature, point and radius, and the
    outcome is unchanged or computed -> needs_information."""
    from localitylens.resolve.selection import apply_selection_3

    cands = tuple(_candidate(i + 1, lat, county_match=counties[i]) for i, lat in enumerate(lats))
    for outcome in ProposalOutcome:
        before = _at(1, radius, outcome)
        after = apply_selection_3("2 mi N of Brindle Peak", "Brindle Peak", before, None,
                                  "Marlow", cands)  # fmt: skip
        assert (after.feature_id, after.point, after.radius_m) == (1, before.point, radius)
        assert after.outcome is outcome or (
            outcome is ProposalOutcome.COMPUTED
            and after.outcome is ProposalOutcome.NEEDS_INFORMATION
        )
