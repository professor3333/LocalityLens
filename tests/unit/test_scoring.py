"""Worksheet checks and scoring, on SYNTHETIC records, annotations and gazetteer."""

import csv
from pathlib import Path
from typing import Any

import pytest
from tests.support.synthetic_dwca import row

from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.evaluation.annotations import Annotation, Level, check_worksheet
from localitylens.evaluation.audit import WORKSHEET_COLUMNS, AuditSample, sample_groups
from localitylens.evaluation.score import judge, paired, score, sign_test_p
from localitylens.extract.schema import RelationType
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.directions import CompassPoint
from localitylens.geo.units import LengthUnit
from localitylens.ingest.specimens import to_record


@pytest.fixture
def gaz(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> Gazetteer:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    build_index(directory, manifest, tmp_path / "g.sqlite")
    return Gazetteer(tmp_path / "g.sqlite")


@pytest.fixture
def sample() -> AuditSample:
    records = [
        to_record(row(i, t))
        for i, t in [
            (1, "Nine miles N of Testa Peak."),
            (2, "Testa Lake."),
            (3, "4 mi up Testa Rd."),
        ]
    ]
    items, total, groups = sample_groups(records, 10, "s")
    return AuditSample(
        snapshot_id="x",
        screen_version="1",
        grouping_version="1",
        seed="s",
        eligible_records=total,
        eligible_groups=groups,
        items=tuple(items),
    )


def write_sheet(path: Path, sample: AuditSample, fills: dict[str, dict[str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(WORKSHEET_COLUMNS)
        for item in sample.items:
            r = item.record
            base = {"audit_id": item.audit_id, "gbif_id": r.gbif_id, "county": r.county,
                    "locality": r.locality} | fills.get(r.locality, {})  # fmt: skip
            w.writerow([base.get(c, "") for c in WORKSHEET_COLUMNS])
    return path


GOOD = {
    "Nine miles N of Testa Peak.": {"description_type": "distance_and_direction",
        "supported": "yes", "reference_features": "Testa Peak", "acceptable_gnis_ids": "1?",
        "distance": "Nine", "unit": "mile", "direction": "N", "missing_information": "extent"},
    "Testa Lake.": {"description_type": "named_feature", "supported": "yes",
        "reference_features": "Testa Lake", "acceptable_gnis_ids": "3"},
    "4 mi up Testa Rd.": {"description_type": "route_relative", "supported": "no",
        "missing_information": "route_geometry"},
}  # fmt: skip


def test_a_clean_worksheet_parses(tmp_path: Path, sample: AuditSample, gaz: Gazetteer) -> None:
    result = check_worksheet(write_sheet(tmp_path / "w.csv", sample, GOOD), sample, gaz)
    assert result.errors == []
    by_text = {a.locality: a for a in result.annotations}
    first = by_text["Nine miles N of Testa Peak."]
    assert first.acceptable_ids == {1}  # an ID with a "?" marker is still looked up
    assert "acceptable_gnis_ids" in first.unsure_columns
    assert first.direction is CompassPoint.N
    assert by_text["4 mi up Testa Rd."].supported is False


@pytest.mark.parametrize(
    ("change", "column"),
    [({"locality": "edited text"}, "locality"),
     ({"description_type": "summit"}, "description_type"),
     ({"acceptable_gnis_ids": "424242"}, "acceptable_gnis_ids"),
     ({"unit": "furlong"}, "unit"),
     ({"direction": "NNNE"}, "direction"),
     ({"distance": "lots"}, "distance"),
     ({"reference_features": ""}, "reference_features")],
)  # fmt: skip
def test_errors_name_the_column(
    tmp_path: Path, sample: AuditSample, gaz: Gazetteer, change: dict[str, str], column: str
) -> None:
    key = "Nine miles N of Testa Peak."
    fills = GOOD | {key: GOOD[key] | change}
    result = check_worksheet(write_sheet(tmp_path / "w.csv", sample, fills), sample, gaz)
    assert any(p.column == column and p.level is Level.ERROR for p in result.problems)


def annotation(**over: Any) -> Annotation:
    base: dict[str, Any] = dict(
        audit_id="A01",
        locality="2 mi NE of Testa Peak",
        description_type="distance_and_direction",
        relation=RelationType.DISTANCE_AND_DIRECTION,
        supported=True,
        reference_features=("Testa Peak",),
        acceptable_ids=frozenset({1}),
        reference_absent=False,
        distance="2",
        unit=LengthUnit.MILE,
        direction=CompassPoint.NE,
        qualifiers=frozenset(),
        missing=frozenset({"extent"}),
        unsure_columns=frozenset(),
        notes="",
    )
    return Annotation(**(base | over))


def report_row(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "audit_id": "A01", "relation": "distance_and_direction", "retrieval": "candidates_found",
        "proposal": "needs_information", "candidate_ids": [1, 2],
        "interpretation": {"relation": "distance_and_direction", "distance": 2.0, "unit": "mile",
                           "direction": "NE", "qualifiers": []},
    }  # fmt: skip
    return base | over


def test_a_fully_correct_record_is_a_correct_candidate() -> None:
    j = judge(annotation(), report_row())
    assert j.critical_ok
    assert j.top1_ok
    assert j.correct_candidate
    assert j.corrections == 0


@pytest.mark.parametrize(
    ("interp_change", "field"),
    [({"distance": 3.0}, "distance_ok"), ({"unit": "kilometre"}, "unit_ok"),
     ({"direction": "NNE"}, "direction_ok"), ({"qualifiers": ["approximate"]}, "qualifiers_ok")],
)  # fmt: skip
def test_one_wrong_field_breaks_the_critical_match(
    interp_change: dict[str, Any], field: str
) -> None:
    r = report_row()
    r["interpretation"] = r["interpretation"] | interp_change
    j = judge(annotation(), r)
    assert not getattr(j, field)
    assert not j.critical_ok
    assert not j.correct_candidate
    assert j.corrections == 1


def test_reference_second_place_counts_for_recall_not_top1() -> None:
    j = judge(annotation(), report_row(candidate_ids=[2, 1]))
    assert not j.top1_ok
    assert j.recall5_ok
    assert not j.correct_candidate


def test_invalid_extraction_is_never_correct() -> None:
    j = judge(annotation(), report_row(interpretation=None, proposal="invalid_extraction"))
    assert not j.valid
    assert not j.critical_ok


def test_spelled_out_annotated_distance_compares_by_value() -> None:
    assert judge(annotation(distance="two"), report_row()).distance_ok


def test_half_and_tilde_as_annotators_copy_them() -> None:
    from localitylens.evaluation.annotations import QUALIFIER_WORDS, annotated_distance

    assert annotated_distance("Half") == 0.5
    assert QUALIFIER_WORDS["~"] == "approximate"


def test_unsupported_and_absent_handling() -> None:
    unsupported = annotation(
        supported=False,
        relation=RelationType.ROUTE_RELATIVE,
        description_type="route_relative",
        acceptable_ids=frozenset(),
    )
    assert judge(unsupported, report_row(proposal="unsupported")).handled_ok
    assert not judge(unsupported, report_row(proposal="needs_information")).handled_ok
    absent = annotation(acceptable_ids=frozenset(), reference_absent=True)
    assert judge(absent, report_row(retrieval="feature_absent_from_index")).handled_ok
    assert not judge(absent, report_row()).handled_ok


def test_place_named_as_no_locality_is_flagged() -> None:
    named = annotation(description_type="named_feature", relation=RelationType.NAMED_FEATURE)
    assert judge(named, report_row(relation="no_locality", interpretation=None)).false_no_locality


def test_sign_test_matches_hand_computed_values() -> None:
    assert sign_test_p(5, 0) == pytest.approx(2 / 32)
    assert sign_test_p(3, 3) == 1.0
    assert sign_test_p(0, 0) == 1.0


def test_paired_comparison_is_deterministic_and_signed() -> None:
    rules = [True, False, False, False, True, False]
    llm = [True, True, True, False, False, False]
    first, again = paired(rules, llm), paired(rules, llm)
    assert first == again
    assert first["llm_only"] == 2
    assert first["rules_only"] == 1
    assert first["difference"] == pytest.approx(1 / 6, abs=1e-3)
    lo, hi = first["ci95"]
    assert lo <= first["difference"] <= hi


def test_score_excludes_unsure_rows_on_request() -> None:
    sure, unsure = annotation(), annotation(audit_id="A02", unsure_columns=frozenset({"unit"}))
    reports = {name: {"records": [report_row(), report_row(audit_id="A02")]}
               for name in ("rules", "llm")}  # fmt: skip
    assert score([sure, unsure], reports)["records"] == 2
    trimmed = score([sure, unsure], reports, exclude_unsure=True)
    assert trimmed["records"] == 1
    assert trimmed["excluded_unsure"] == 1
