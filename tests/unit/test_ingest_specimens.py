"""DWCA reading, screening, allowlist and grouping on SYNTHETIC archives."""

from pathlib import Path

import pytest
from tests.support.synthetic_dwca import meta_xml, row, write_archive, write_snapshot

from localitylens.data.manifest import ChecksumMismatchError
from localitylens.ingest.dwca import ArchiveFormatError, iter_rows
from localitylens.ingest.specimens import (
    ANSWER_BEARING_TERMS,
    MODEL_INPUT_FIELDS,
    READ_TERMS,
    ExclusionReason,
    ModelInput,
    ScreenSummary,
    group_key,
    iter_snapshot,
    screen,
    to_record,
)


def test_rows_are_read_by_meta_xml_terms(tmp_path: Path) -> None:
    path = tmp_path / "a.zip"
    write_archive(path, [row(1, "Testa Peak."), row(2, "2 mi N of Testa Lake.")])
    rows = list(iter_rows(path, "verbatim.txt", ("gbifID", "locality")))
    assert rows == [
        (2, {"gbifID": "1", "locality": "Testa Peak."}),
        (3, {"gbifID": "2", "locality": "2 mi N of Testa Lake."}),
    ]


def test_wrong_field_count_raises_with_line_number(tmp_path: Path) -> None:
    path = tmp_path / "a.zip"
    write_archive(path, [row(1, "x")], raw_lines=["3\tonly two fields"])
    with pytest.raises(ArchiveFormatError, match="line 3"):
        list(iter_rows(path, "verbatim.txt", ("locality",)))


def test_header_must_agree_with_meta_xml(tmp_path: Path) -> None:
    path = tmp_path / "a.zip"
    from tests.support.synthetic_dwca import COLUMNS

    swapped = [COLUMNS[0], COLUMNS[2], COLUMNS[1], *COLUMNS[3:]]
    write_archive(path, [row(1, "x")], header=swapped)
    with pytest.raises(ArchiveFormatError, match="header"):
        list(iter_rows(path, "verbatim.txt", ("locality",)))


def test_meta_xml_with_entities_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "a.zip"
    write_archive(path, [], meta='<!DOCTYPE x [<!ENTITY a "b">]>' + meta_xml())
    with pytest.raises(ArchiveFormatError, match="DTD"):
        list(iter_rows(path, "verbatim.txt", ("locality",)))


def test_missing_column_is_named(tmp_path: Path) -> None:
    path = tmp_path / "a.zip"
    write_archive(path, [row(1, "x")])
    with pytest.raises(ArchiveFormatError, match="nonexistentTerm"):
        list(iter_rows(path, "verbatim.txt", ("nonexistentTerm",)))


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"stateProvince": ""}, ExclusionReason.NO_STATE),
        ({"stateProvince": "Colorado?"}, ExclusionReason.STATE_UNCERTAIN),
        ({"stateProvince": "Colorado/Wyoming"}, ExclusionReason.STATE_UNCERTAIN),
        ({"stateProvince": "Wyoming"}, ExclusionReason.OUTSIDE_COLORADO),
        ({"stateProvince": "British Columbia"}, ExclusionReason.OUTSIDE_COLORADO),
        ({"country": "Mexico"}, ExclusionReason.NOT_UNITED_STATES),
        ({"informationWithheld": "field values redacted: eventDate"}, ExclusionReason.SENSITIVE),
        ({"dataGeneralizations": "coordinates generalized"}, ExclusionReason.SENSITIVE),
        ({"locality": "   "}, ExclusionReason.NO_LOCALITY_TEXT),
        ({"locality": "[No locality data provided on the label.]"},
         ExclusionReason.NO_LOCALITY_ON_LABEL),
        ({"locality": "[no locality]"}, ExclusionReason.NO_LOCALITY_ON_LABEL),
        ({"locality": "Unknown."}, ExclusionReason.NO_LOCALITY_ON_LABEL),
        ({"locality": "[Cultivated specimen.]"}, ExclusionReason.CULTIVATED_NOTE_ONLY),
    ],
)  # fmt: skip
def test_each_exclusion_reason(changes: dict[str, str], reason: ExclusionReason) -> None:
    assert screen(row(1, "Testa Peak.") | changes) is reason


@pytest.mark.parametrize(
    "locality",
    [
        "No locality, but collected near Testa Peak.",  # placeholder words only, then a place
        "Colorado (exact station unknown).",
        "[Cultivated] garden 2 mi N of Testa Lake.",
        "Testa Peak [summit].",
    ],
)
def test_text_with_a_place_is_not_a_placeholder(locality: str) -> None:
    assert screen(row(1, locality)) is None


@pytest.mark.parametrize("state", ["Colorado", "COLORADO", "COlorado", " colorado "])
def test_colorado_spellings_are_eligible(state: str) -> None:
    assert screen(row(1, "Testa Peak.", stateProvince=state)) is None


def test_answer_bearing_terms_are_never_read() -> None:
    assert not set(READ_TERMS) & ANSWER_BEARING_TERMS
    required = {"decimalLatitude", "coordinateUncertaintyInMeters", "georeferenceRemarks",
                "georeferenceSources", "footprintWKT", "verbatimCoordinates"}  # fmt: skip
    assert required <= ANSWER_BEARING_TERMS


def test_model_input_is_exactly_the_allowlist() -> None:
    assert tuple(ModelInput.model_fields) == MODEL_INPUT_FIELDS
    record = to_record(row(7, "2 mi N of Testa Lake."))
    model_input = record.model_input()
    assert model_input.model_dump() == {
        "locality": "2 mi N of Testa Lake.",
        "state_province": "Colorado",
        "county": "Alpha",
        "country": "United States",
    }
    assert "7" not in model_input.model_dump_json()  # no ids, catalogue numbers or dates


def test_original_text_is_kept_byte_for_byte() -> None:
    text = "  Testa\u00a0Peak,  N  slope.\u2019 "
    assert to_record(row(1, text)).locality == text


def test_groups_merge_wording_variants_within_a_county() -> None:
    assert group_key("Testa Peak.", "Alpha") == group_key("TESTA  PEAK", "Alpha County")
    assert group_key("Testa Pk.", "Alpha") == group_key("Testa Peak", "Alpha")
    assert group_key("Testa Peak.", "Alpha") != group_key("Testa Peak.", "Beta")
    assert group_key("2 mi N of Testa Peak", "Alpha") != group_key("2 mi S of Testa Peak", "Alpha")


def test_snapshot_scan_counts_every_record(tmp_path: Path) -> None:
    rows = [
        row(1, "Testa Peak."),
        row(2, "TESTA PEAK"),
        row(3, "2 mi N of Testa Lake."),
        row(4, "Elsewhere.", stateProvince="Utah"),
        row(5, "[No locality.]"),
    ]
    write_snapshot(tmp_path / "snap", rows)
    summary = ScreenSummary(snapshot_id="")
    records = list(iter_snapshot(tmp_path / "snap", summary))
    assert [r.gbif_id for r in records] == ["1", "2", "3"]
    assert summary.total == 5
    assert summary.eligible == 3
    assert summary.eligible + sum(summary.excluded.values()) == summary.total
    assert len(summary.groups) == 2
    assert summary.snapshot_id == "gbif-synthetic"


def test_a_tampered_snapshot_is_not_read(tmp_path: Path) -> None:
    write_snapshot(tmp_path / "snap", [row(1, "Testa Peak.")])
    archive = next((tmp_path / "snap").glob("*.zip"))
    archive.write_bytes(archive.read_bytes() + b"x")
    with pytest.raises(ChecksumMismatchError):
        list(iter_snapshot(tmp_path / "snap"))
