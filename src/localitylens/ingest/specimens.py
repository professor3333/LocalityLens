"""Specimen records from the GBIF snapshot: screening, model-input allowlist, duplicate groups.

Source file: ``verbatim.txt``, the publisher's values as supplied. For the CU Herbarium the
label text is in ``locality``; ``verbatimLocality`` is empty for every Colorado record in
snapshot ``gbif-cu-2026-11-01``, so ``locality`` is the original text and is never altered.

Answer-bearing columns (coordinates, uncertainty, georeference remarks/sources, footprints)
are not even read here. They are not in :data:`READ_TERMS`, so they cannot leak into a record,
a sample, or a model input.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from localitylens.data.manifest import load_manifest, verify_snapshot
from localitylens.gazetteer.keys import county_key, name_key
from localitylens.ingest.dwca import iter_rows
from localitylens.ingest.normalize import normalize

SCREEN_VERSION: Final = "1"
GROUPING_VERSION: Final = "1"
SOURCE_FILE: Final = "verbatim.txt"

# Fields that may reach a model prompt: the label text and supplied admin geography. This is an
# allowlist; anything not named here never reaches a model.
MODEL_INPUT_FIELDS: Final = ("locality", "state_province", "county", "country")

# Darwin Core terms that carry (part of) an existing answer. Never read, never in model input.
ANSWER_BEARING_TERMS: Final = frozenset(
    {
        "decimalLatitude", "decimalLongitude", "verbatimLatitude", "verbatimLongitude",
        "verbatimCoordinates", "verbatimCoordinateSystem", "coordinateUncertaintyInMeters",
        "coordinatePrecision", "geodeticDatum", "verbatimSRS", "footprintWKT", "footprintSRS",
        "georeferencedBy", "georeferencedDate", "georeferenceProtocol", "georeferenceSources",
        "georeferenceRemarks", "georeferenceVerificationStatus", "pointRadiusSpatialFit",
        "footprintSpatialFit", "locationRemarks", "verbatimElevation", "minimumElevationInMeters",
        "maximumElevationInMeters", "locationID", "higherGeographyID",
    }
)  # fmt: skip

READ_TERMS: Final = (
    "gbifID", "occurrenceID", "catalogNumber", "recordedBy", "recordNumber", "eventDate",
    "country", "countryCode", "stateProvince", "county", "locality", "verbatimLocality",
    "informationWithheld", "dataGeneralizations",
)  # fmt: skip


class ExclusionReason(StrEnum):
    """Why a record is not eligible. Checked in this order; a record gets the first that applies."""

    NO_STATE = "no_state"  # stateProvince empty; not inferred from coordinates (that would leak)
    STATE_UNCERTAIN = "state_uncertain"  # e.g. "Colorado?", "Colorado/Wyoming"
    OUTSIDE_COLORADO = "outside_colorado"
    NOT_UNITED_STATES = "not_united_states"
    SENSITIVE = "sensitive_withheld"  # informationWithheld / dataGeneralizations present
    NO_LOCALITY_TEXT = "no_locality_text"
    NO_LOCALITY_ON_LABEL = "no_locality_on_label"  # "[No locality data provided on the label.]"
    CULTIVATED_NOTE_ONLY = "cultivated_note_only"  # "[Cultivated specimen.]", no place given


_COLORADO: Final = "colorado"
# Whole-string placeholders only: "no locality" followed by placeholder words, or "unknown".
_PLACEHOLDER: Final = re.compile(
    r"\[?\s*(?:no\s+locality(?:\s+(?:data|info|information|given|provided|stated|recorded|on|"
    r"the|label))*|unknown)\s*\.?\s*\]?\s*\.?",
    re.IGNORECASE,
)
_CULTIVATED_ONLY: Final = re.compile(r"\[\s*cultivated(?:\s+specimen)?\s*\.?\s*\]\s*\.?", re.I)


class SpecimenRecord(BaseModel):
    """One eligible record. ``locality`` is the original string, byte for byte."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    gbif_id: str
    occurrence_id: str
    catalog_number: str
    locality: str
    state_province: str
    county: str
    country: str
    recorded_by: str
    record_number: str
    event_date: str
    group_key: str

    def model_input(self) -> ModelInput:
        return ModelInput(**{f: getattr(self, f) for f in MODEL_INPUT_FIELDS})


class ModelInput(BaseModel):
    """Everything a model may see about a record, and nothing else."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    locality: str
    state_province: str
    county: str
    country: str


def screen(row: dict[str, str]) -> ExclusionReason | None:
    state = row["stateProvince"].strip()
    folded = state.casefold()
    if not state:
        return ExclusionReason.NO_STATE
    if folded != _COLORADO:
        if _COLORADO in folded:
            return ExclusionReason.STATE_UNCERTAIN
        return ExclusionReason.OUTSIDE_COLORADO
    country, code = row["country"].strip(), row["countryCode"].strip()
    if not (country == "United States" or code == "US" or (not country and not code)):
        return ExclusionReason.NOT_UNITED_STATES
    if row["informationWithheld"].strip() or row["dataGeneralizations"].strip():
        return ExclusionReason.SENSITIVE
    text = row["locality"].strip()
    if not text:
        return ExclusionReason.NO_LOCALITY_TEXT
    if _PLACEHOLDER.fullmatch(text):
        return ExclusionReason.NO_LOCALITY_ON_LABEL
    if _CULTIVATED_ONLY.fullmatch(text):
        return ExclusionReason.CULTIVATED_NOTE_ONLY
    return None


def group_key(locality: str, county: str) -> str:
    """Duplicate-locality group: the same wording (by name key) in the same supplied county.

    Collecting-event grouping (collector + date) is a separate, later step.
    """
    basis = f"g{GROUPING_VERSION}|{name_key(normalize(locality).text)}|{county_key(county)}"
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def to_record(row: dict[str, str]) -> SpecimenRecord:
    return SpecimenRecord(
        gbif_id=row["gbifID"],
        occurrence_id=row["occurrenceID"],
        catalog_number=row["catalogNumber"],
        locality=row["locality"],
        state_province=row["stateProvince"],
        county=row["county"],
        country=row["country"],
        recorded_by=row["recordedBy"],
        record_number=row["recordNumber"],
        event_date=row["eventDate"],
        group_key=group_key(row["locality"], row["county"]),
    )


@dataclass(slots=True)
class ScreenSummary:
    snapshot_id: str
    total: int = 0
    eligible: int = 0
    excluded: Counter[ExclusionReason] = field(default_factory=Counter)
    groups: set[str] = field(default_factory=set)


def iter_snapshot(
    snapshot_dir: Path, summary: ScreenSummary | None = None, *, verify: bool = True
) -> Iterator[SpecimenRecord]:
    """Eligible records of a verified snapshot, counting every exclusion in ``summary``."""
    manifest = load_manifest(snapshot_dir / "manifest.json")
    if verify:
        verify_snapshot(snapshot_dir, manifest)
    archive = next(snapshot_dir / f.name for f in manifest.files if f.name.endswith(".zip"))
    if summary is not None:
        summary.snapshot_id = manifest.snapshot_id
    for _line, row in iter_rows(archive, SOURCE_FILE, READ_TERMS):
        reason = screen(row)
        if summary is not None:
            summary.total += 1
            if reason is not None:
                summary.excluded[reason] += 1
        if reason is None:
            record = to_record(row)
            if summary is not None:
                summary.eligible += 1
                summary.groups.add(record.group_key)
            yield record
