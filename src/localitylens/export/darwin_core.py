"""Darwin Core export of approved records, plus the unresolved-record report.

Only ``approved`` records are exported. Term names and value conventions follow
https://dwc.tdwg.org/terms/:

* ``geodeticDatum`` is the EPSG code of the point's datum (GNIS points are NAD83:
  ``EPSG:4269``). Coordinates are not transformed.
* ``coordinateUncertaintyInMeters`` is the proposal's radius, rounded **up** to a whole metre,
  so the circle never shrinks. It is never 0.
* ``georeferenceVerificationStatus`` is ``verified by data custodian``: a curator approved the
  record.
* ``georeferenceSources`` and ``georeferenceRemarks`` use `` | `` between list items, as the
  terms recommend.
* ``footprintWKT`` / ``footprintSRS`` are left empty, because footprints are not built yet.
  A point-radius georeference is complete without them.

Curator edits are marked: ``georeferenceRemarks`` says what the curator changed, and the
``localitylens_human_edits`` column holds the diff. The same approved rows go to GeoJSON
(:mod:`localitylens.export.geojson`), converted to WGS 84 as RFC 7946 requires.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from localitylens.domain.status import EXPORTABLE, RecordStatus
from localitylens.geo import uncertainty as policy
from localitylens.geo.geodesy import EPSG_CODE, Coordinate
from localitylens.review.store import Action, ReviewStore

EXPORT_VERSION: Final = "dwc-export-1"

DWC_COLUMNS: Final = (
    "occurrenceID",
    "catalogNumber",
    "locality",
    "decimalLatitude",
    "decimalLongitude",
    "geodeticDatum",
    "coordinateUncertaintyInMeters",
    "footprintWKT",
    "footprintSRS",
    "georeferencedBy",
    "georeferencedDate",
    "georeferenceProtocol",
    "georeferenceSources",
    "georeferenceRemarks",
    "georeferenceVerificationStatus",
    "gbifID",
    "localitylens_release",
    "localitylens_extractor",
    "localitylens_proposal_id",
    "localitylens_decision_id",
    "localitylens_trace_id",
    "localitylens_human_edits",
)
UNRESOLVED_COLUMNS: Final = (
    "occurrenceID", "gbifID", "locality", "status", "blocking", "curator_note",
)  # fmt: skip

PROTOCOL: Final = (
    "Georeferencing Quick Reference Guide (Zermoglio et al. 2020) and Georeferencing Best "
    f"Practices (Chapman & Wieczorek 2020), point-radius method; LocalityLens uncertainty "
    f"policy {policy.POLICY_ID}"
)
VERIFIED: Final = "verified by data custodian"


def _edits_text(edits: dict[str, list[object]]) -> str:
    parts = []
    if "feature_id" in edits:
        old, new = edits["feature_id"]
        parts.append(f"curator chose GNIS feature {new} instead of {old}")
    if "extent_m" in edits:
        old, new = edits["extent_m"]
        parts.append(
            f"curator set the extent to {new} m (was {old if old is not None else 'unknown'})"
        )
    return "; ".join(parts)


@dataclass(frozen=True, slots=True)
class Approved:
    """One approved record: its Darwin Core row plus the unformatted region it came from."""

    row: dict[str, str]
    point: Coordinate
    radius_m: float


def approved_georeferences(store: ReviewStore) -> list[Approved]:
    """Every approved record as a Darwin Core row, in the source datum (shared by all formats)."""
    out: list[Approved] = []
    for rec in store.records(RecordStatus.APPROVED):
        assert RecordStatus(rec["status"]) in EXPORTABLE
        approvals = [d for d in store.decisions(rec["record_id"]) if d.action is Action.APPROVE]
        decision = approvals[-1]
        assert decision.final_proposal is not None
        stored = store.proposal(decision.final_proposal)
        p = stored.proposal
        if p is None or p.point is None or p.radius_m is None or p.feature_id is None:
            raise ValueError(f"approved record {rec['record_id']} has no full region")
        candidate = next(c for c in stored.candidates if c.feature_id == p.feature_id)
        sources = [f"USGS GNIS feature {p.feature_id} ({candidate.official_name}), snapshot "
                   f"{stored.gazetteer_snapshot}"]  # fmt: skip
        extent = next((c for c in p.components if c.name.value == "extent"), None)
        if extent is not None and extent.metres is not None:
            sources.append(f"extent: {extent.rule}")
        remarks = list(p.assumptions)
        if decision.edits:
            remarks.append(_edits_text(decision.edits))
        remarks.append(f"curator rationale: {decision.rationale}")
        row = {
            "occurrenceID": rec["occurrence_id"],
            "catalogNumber": rec["catalog_number"],
            "locality": rec["locality"],  # the original string, unchanged
            "decimalLatitude": f"{p.point.latitude:.6f}",
            "decimalLongitude": f"{p.point.longitude:.6f}",
            "geodeticDatum": EPSG_CODE[p.point.datum],
            "coordinateUncertaintyInMeters": str(math.ceil(p.radius_m)),
            "footprintWKT": "",
            "footprintSRS": "",
            "georeferencedBy": decision.reviewer,
            "georeferencedDate": decision.decided_at,
            "georeferenceProtocol": PROTOCOL,
            "georeferenceSources": " | ".join(sources),
            "georeferenceRemarks": " | ".join(remarks),
            "georeferenceVerificationStatus": VERIFIED,
            "gbifID": rec["gbif_id"],
            "localitylens_release": stored.release,
            "localitylens_extractor": stored.extractor_version,
            "localitylens_proposal_id": stored.proposal_id,
            "localitylens_decision_id": decision.decision_id,
            # the job attempt that produced the pipeline proposal (empty for pre-queue imports)
            "localitylens_trace_id": store.trace_for_proposal(decision.proposal_id) or "",
            "localitylens_human_edits": json.dumps(decision.edits, sort_keys=True)
            if decision.edits
            else "",
        }  # fmt: skip
        out.append(Approved(row, p.point, p.radius_m))
    return out


def export_approved(store: ReviewStore, out: Path) -> int:
    """Write every approved record as one Darwin Core row. Returns the number written."""
    rows = [a.row for a in approved_georeferences(store)]
    _write(out, DWC_COLUMNS, rows)
    return len(rows)


def export_unresolved(store: ReviewStore, out: Path) -> int:
    """Every record that needs information, is unsupported or failed, with what blocks it."""
    rows: list[dict[str, str]] = []
    for status in (RecordStatus.NEEDS_INFORMATION, RecordStatus.UNSUPPORTED, RecordStatus.FAILED):
        for rec in store.records(status):
            stored = store.latest_pipeline_proposal(rec["record_id"])
            p = stored.proposal
            if p is not None:
                blocking = " | ".join([*p.questions, *p.reasons]) or p.outcome.value
            else:
                blocking = stored.outcome  # invalid_extraction or failed:<category>
            notes = [d.rationale for d in store.decisions(rec["record_id"])
                     if d.action is Action.RESEARCH]  # fmt: skip
            rows.append({
                "occurrenceID": rec["occurrence_id"],
                "gbifID": rec["gbif_id"],
                "locality": rec["locality"],
                "status": status.value,
                "blocking": blocking,
                "curator_note": notes[-1] if notes else "",
            })  # fmt: skip
    _write(out, UNRESOLVED_COLUMNS, rows)
    return len(rows)


def _write(out: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
