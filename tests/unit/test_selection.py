"""Selection check (selection-1). Label texts use invented place names."""

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
