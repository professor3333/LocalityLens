"""View models for the review screen: plain data built from the review store, no HTML.

Everything shown comes from stored originals, interpretations, candidates and proposals. Nothing
here computes a coordinate or a radius: the map draws the stored proposal, and only a
``computed`` proposal gets a circle (invariant 5). Selection evidence and spatial uncertainty
are built separately and shown separately (invariant 7).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from localitylens.domain.status import RecordStatus
from localitylens.extract.schema import Interpretation, Span
from localitylens.geo.georeference import GeoreferenceProposal, ProposalOutcome
from localitylens.review.store import Decision, ReviewStore, StoredProposal

STATUS_ORDER: tuple[RecordStatus, ...] = (
    RecordStatus.READY_FOR_REVIEW,
    RecordStatus.NEEDS_INFORMATION,
    RecordStatus.UNSUPPORTED,
    RecordStatus.FAILED,
    RecordStatus.QUEUED,
    RecordStatus.PROCESSING,
    RecordStatus.APPROVED,
    RecordStatus.REJECTED,
)
DECIDABLE: frozenset[RecordStatus] = frozenset(
    {RecordStatus.READY_FOR_REVIEW, RecordStatus.NEEDS_INFORMATION, RecordStatus.UNSUPPORTED}
)


def summary_line(proposal: StoredProposal) -> str:
    """What the queue shows for a record: the region, or what blocks it."""
    g = proposal.proposal
    if g is not None and g.outcome is ProposalOutcome.COMPUTED and g.radius_m is not None:
        name = next(
            (c.official_name for c in proposal.candidates if c.feature_id == g.feature_id),
            str(g.feature_id),
        )
        return f"{name}, radius {g.radius_m:,.0f} m"
    if g is not None and (g.questions or g.reasons):
        return (g.questions or g.reasons)[0]
    return proposal.outcome.replace("_", " ")


@dataclass(frozen=True, slots=True)
class QueueRow:
    record_id: str
    status: str
    county: str
    locality: str
    summary: str


@dataclass(frozen=True, slots=True)
class QueueView:
    rows: tuple[QueueRow, ...]
    counts: tuple[tuple[str, int], ...]  # (status, count) in display order, zeros left out
    total: int
    status_filter: str | None


def queue_view(store: ReviewStore, status: RecordStatus | None) -> QueueView:
    all_records = store.records()
    counter = Counter(r["status"] for r in all_records)
    shown = all_records if status is None else [r for r in all_records if r["status"] == status]
    rank = {st.value: i for i, st in enumerate(STATUS_ORDER)}
    shown = sorted(shown, key=lambda r: (rank.get(r["status"], len(rank)), r["record_id"]))
    rows = []
    for r in shown:
        try:
            summary = summary_line(store.latest_pipeline_proposal(r["record_id"]))
        except ValueError:
            summary = "not processed yet"
        rows.append(QueueRow(r["record_id"], r["status"], r["county"], r["locality"], summary))
    counts = tuple((s.value, counter[s.value]) for s in STATUS_ORDER if counter[s.value])
    return QueueView(tuple(rows), counts, len(all_records), status.value if status else None)


# --- record page ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Segment:
    text: str
    label: str | None  # None = plain text, else the field this span was extracted for


@dataclass(frozen=True, slots=True)
class FieldRow:
    name: str
    value: str
    state: str  # observed | missing | not stated
    span: str  # "[start:end] text", or ""


def _span_text(span: Span | None) -> str:
    return f"[{span.start}:{span.end}] {span.text}" if span is not None else ""


def label_segments(locality: str, interp: Interpretation | None) -> tuple[Segment, ...]:
    """The original text cut into plain and marked pieces at the extracted spans.

    Spans index the ORIGINAL text, half-open. Overlapping marks keep the first in text order;
    every span is also listed in the field table, so nothing is hidden.
    """
    if interp is None:
        return (Segment(locality, None),)
    marks: list[tuple[int, int, str]] = []
    if interp.reference_feature is not None:
        marks.append(
            (interp.reference_feature.span.start, interp.reference_feature.span.end, "feature")
        )
    if interp.distance is not None:
        marks.append((interp.distance.value_span.start, interp.distance.value_span.end, "distance"))
        if interp.distance.unit_span is not None:
            marks.append((interp.distance.unit_span.start, interp.distance.unit_span.end, "unit"))
    if interp.direction is not None:
        marks.append((interp.direction.span.start, interp.direction.span.end, "direction"))
    marks += [(q.span.start, q.span.end, "qualifier") for q in interp.qualifiers]
    marks += [(a.span.start, a.span.end, "admin") for a in interp.admin_mentions]
    out: list[Segment] = []
    pos = 0
    for start, end, label in sorted(marks):
        if start < pos or end > len(locality) or start >= end:
            continue  # overlaps an earlier mark (still listed in the table)
        if start > pos:
            out.append(Segment(locality[pos:start], None))
        out.append(Segment(locality[start:end], label))
        pos = end
    if pos < len(locality):
        out.append(Segment(locality[pos:], None))
    return tuple(out)


def field_rows(interp: Interpretation | None) -> tuple[FieldRow, ...]:
    if interp is None:
        return ()
    missing = {m.value for m in interp.missing}

    def state(present: bool, key: str) -> str:
        return "observed" if present else ("missing" if key in missing else "not stated")

    f, d, r = interp.reference_feature, interp.distance, interp.direction
    rows = [
        FieldRow(
            "relation",
            interp.relation.value.replace("_", " "),
            "observed",
            _span_text(interp.relation_span),
        ),
        FieldRow(
            "reference feature",
            f.name if f else "",
            state(f is not None, "reference_feature"),
            _span_text(f.span if f else None),
        ),
        FieldRow(
            "feature type",
            f.feature_type.value if f and f.feature_type else "",
            state(bool(f and f.feature_type), "feature_type"),
            _span_text(f.feature_type_span if f else None),
        ),
        FieldRow(
            "distance",
            f"{d.quantity.value:g}" if d else "",
            state(d is not None, "distance"),
            _span_text(d.value_span if d else None),
        ),
        FieldRow(
            "unit",
            d.unit.value if d and d.unit else "",
            state(bool(d and d.unit), "distance_unit"),
            _span_text(d.unit_span if d else None),
        ),
        FieldRow(
            "direction",
            r.point.value if r else "",
            state(r is not None, "direction"),
            _span_text(r.span if r else None),
        ),
    ]
    rows += [
        FieldRow("qualifier", q.kind.value, "observed", _span_text(q.span))
        for q in interp.qualifiers
    ]
    rows += [
        FieldRow("admin (in text)", a.level.value, "observed", _span_text(a.span))
        for a in interp.admin_mentions
    ]
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class CandidateRow:
    rank: int
    feature_id: int
    official_name: str
    matched_name: str
    match_kind: str
    feature_class: str
    county: str
    county_match: bool | None
    type_match: bool | None
    historical: bool
    latitude: float
    longitude: float
    datum: str
    selected: bool


@dataclass(frozen=True, slots=True)
class ComponentRow:
    name: str
    metres: float | None  # None = unknown, shown as unknown and never as 0
    rule: str
    citation: str


@dataclass(frozen=True, slots=True)
class Spatial:
    outcome: str
    policy_id: str
    feature_id: int | None
    point: tuple[float, float, str] | None  # lat, lon, datum
    radius_m: float | None
    radius_lower_bound_m: float | None
    components: tuple[ComponentRow, ...]
    assumptions: tuple[str, ...]
    questions: tuple[str, ...]
    reasons: tuple[str, ...]


def spatial(g: GeoreferenceProposal | None) -> Spatial | None:
    if g is None:
        return None
    point = (g.point.latitude, g.point.longitude, g.point.datum.value) if g.point else None
    return Spatial(
        outcome=g.outcome.value,
        policy_id=g.policy_id,
        feature_id=g.feature_id,
        point=point,
        radius_m=g.radius_m,
        radius_lower_bound_m=g.radius_lower_bound_m,
        components=tuple(
            ComponentRow(c.name.value, c.metres, c.rule, c.citation) for c in g.components
        ),
        assumptions=g.assumptions,
        questions=g.questions,
        reasons=g.reasons,
    )


@dataclass(frozen=True, slots=True)
class RecordView:
    record: dict[str, Any]
    proposal: StoredProposal
    segments: tuple[Segment, ...]
    fields: tuple[FieldRow, ...]
    open_questions: tuple[str, ...]
    candidates: tuple[CandidateRow, ...]
    selection: tuple[str, ...]  # selection evidence, in words
    pipeline_region: Spatial | None
    approved_region: Spatial | None  # the exported proposal, once approved
    decisions: tuple[Decision, ...]
    decidable: bool
    map_data: dict[str, Any] = field(default_factory=dict)


def _selection(p: StoredProposal) -> tuple[str, ...]:
    """Why this reference was chosen, kept apart from how big the region is (invariant 7)."""
    if not p.candidates:
        return ("No gazetteer candidate was retrieved.",)
    chosen_id = p.proposal.feature_id if p.proposal else None
    chosen = next((c for c in p.candidates if c.feature_id == chosen_id), p.candidates[0])
    lines = [
        f"{len(p.candidates)} candidate(s) retrieved; the proposal uses rank "
        f"{p.candidates.index(chosen) + 1}, {chosen.official_name} (GNIS {chosen.feature_id}).",
        f"Name match: {chosen.match_kind.value.replace('_', ' ')} "
        f"(similarity {chosen.name_similarity:.0f}).",
    ]
    checks = {"county": chosen.county_match, "feature type": chosen.type_match}
    stated = [f"{k} {'agrees' if v else 'differs'}" for k, v in checks.items() if v is not None]
    if stated:
        lines.append("Context: " + ", ".join(stated) + ".")
    same_name = [
        c for c in p.candidates if c is not chosen and c.official_name == chosen.official_name
    ]
    if same_name:
        lines.append(f"{len(same_name)} other candidate(s) share the name: the text must decide.")
    if chosen.historical:
        lines.append("The match is a historical name.")
    return tuple(lines)


def record_view(store: ReviewStore, record_id: str) -> RecordView:
    row = dict(store.record(record_id))
    p = store.latest_pipeline_proposal(record_id)
    decisions = tuple(store.decisions(record_id))
    approved = next(
        (store.proposal(d.final_proposal) for d in reversed(decisions) if d.final_proposal), None
    )
    chosen = p.proposal.feature_id if p.proposal else None
    final_fid = approved.proposal.feature_id if approved and approved.proposal else chosen
    candidates = tuple(
        CandidateRow(
            rank=i,
            feature_id=c.feature_id,
            official_name=c.official_name,
            matched_name=c.matched_name,
            match_kind=c.match_kind.value.replace("_", " "),
            feature_class=c.feature_class,
            county=c.county_name,
            county_match=c.county_match,
            type_match=c.type_match,
            historical=c.historical,
            latitude=c.primary_point.latitude,
            longitude=c.primary_point.longitude,
            datum=c.primary_point.datum.value,
            selected=c.feature_id == final_fid,
        )
        for i, c in enumerate(p.candidates, start=1)
    )
    pipeline_region = spatial(p.proposal)
    approved_region = spatial(approved.proposal) if approved else None
    shown = approved_region or pipeline_region
    circle = None
    if shown is not None and shown.outcome == "computed" and shown.point and shown.radius_m:
        circle = {"lat": shown.point[0], "lon": shown.point[1], "radius_m": shown.radius_m}
    map_data = {
        "candidates": [
            {
                "id": c.feature_id,
                "name": c.official_name,
                "lat": c.latitude,
                "lon": c.longitude,
                "selected": c.selected,
                "rank": c.rank,
            }
            for c in candidates
        ],
        "circle": circle,
    }
    interp = p.interpretation
    return RecordView(
        record=row,
        proposal=p,
        segments=label_segments(row["locality"], interp),
        fields=field_rows(interp),
        open_questions=interp.open_questions if interp else (),
        candidates=candidates,
        selection=_selection(p),
        pipeline_region=pipeline_region,
        approved_region=approved_region,
        decisions=decisions,
        decidable=RecordStatus(row["status"]) in DECIDABLE,
        map_data=map_data,
    )
