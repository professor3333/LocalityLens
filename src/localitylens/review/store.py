"""The curator review store: original records, proposals and decisions, kept apart in SQLite.

* **Originals are immutable.** A record's ``locality`` and admin fields are written once and
  never updated. Proposals and decisions live in their own tables and point back to the record.
* **Every status change goes through** :func:`localitylens.domain.status.transition`.
* **Approval needs a full region.** A curator may approve as proposed, or edit (choose another
  retrieved candidate, supply a reviewed extent) and approve. The edited proposal is recomputed
  by the same deterministic code, and approval is refused unless it is ``computed``. A record
  never becomes ``approved`` with an unknown radius (invariant 5).
* **Decisions are idempotent.** A decision carries a key, by default the hash of what was
  decided. Submitting the same decision again returns the stored one and writes nothing, so a
  retried request never duplicates a decision or an export row.
* **Jobs are kept apart from records.** ``batch`` and ``job`` hold processing state (lease,
  attempts, cancellation) for :mod:`localitylens.jobs`; a record's status says only where the
  record is in its lifecycle (CLAUDE.md §3). Both live in this file so a status change and its
  job update commit together.
* **Each decision records** the reviewer, a UTC timestamp, the rationale and the edits as a diff
  against the proposal (``{"feature_id": [old, new], ...}``). Edits are marked as human edits in
  the export.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from localitylens.domain.status import InvalidTransitionError, RecordStatus, transition
from localitylens.extract.schema import Interpretation
from localitylens.gazetteer.index import Candidate
from localitylens.geo.georeference import (
    ExtentEstimate,
    ExtentSource,
    GeoreferenceProposal,
    ProposalOutcome,
    propose,
)
from localitylens.ingest.specimens import SpecimenRecord

# review-2 adds the batch and job tables (persistent jobs). A review-1 store is upgraded in place:
# the new tables are created empty and nothing else changes.
STORE_SCHEMA_VERSION: Final = "review-2"
_UPGRADABLE: Final = frozenset({"review-1"})

_SCHEMA: Final = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS record (
    record_id      TEXT PRIMARY KEY,
    gbif_id        TEXT NOT NULL,
    occurrence_id  TEXT NOT NULL,
    catalog_number TEXT NOT NULL,
    locality       TEXT NOT NULL,
    state_province TEXT NOT NULL,
    county         TEXT NOT NULL,
    country        TEXT NOT NULL,
    snapshot_id    TEXT NOT NULL,
    status         TEXT NOT NULL,
    imported_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS proposal (
    proposal_id         TEXT PRIMARY KEY,
    record_id           TEXT NOT NULL REFERENCES record(record_id),
    system              TEXT NOT NULL,
    extractor_version   TEXT NOT NULL,
    release             TEXT NOT NULL,
    gazetteer_snapshot  TEXT NOT NULL,
    origin              TEXT NOT NULL,       -- pipeline | curator_edit
    interpretation_json TEXT,                -- null when extraction failed validation
    candidates_json     TEXT NOT NULL,
    proposal_json       TEXT,
    outcome             TEXT NOT NULL,
    created_at          TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision (
    decision_id     TEXT PRIMARY KEY,
    record_id       TEXT NOT NULL REFERENCES record(record_id),
    proposal_id     TEXT NOT NULL REFERENCES proposal(proposal_id),
    action          TEXT NOT NULL,
    reviewer        TEXT NOT NULL,
    rationale       TEXT NOT NULL,
    edits_json      TEXT NOT NULL,
    final_proposal  TEXT REFERENCES proposal(proposal_id),
    decided_at      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS batch (
    batch_id     TEXT PRIMARY KEY,
    system       TEXT NOT NULL,
    release      TEXT NOT NULL,
    snapshot_id  TEXT NOT NULL,              -- specimen snapshot
    gazetteer    TEXT NOT NULL,              -- gazetteer snapshot
    extractor    TEXT NOT NULL,              -- extractor version (for failure rows)
    state        TEXT NOT NULL,              -- active | cancelled
    created_at   TEXT NOT NULL,
    cancelled_at TEXT
);
CREATE TABLE IF NOT EXISTS job (
    job_id        TEXT PRIMARY KEY,          -- hash(batch_id, record_id): enqueueing is idempotent
    batch_id      TEXT NOT NULL REFERENCES batch(batch_id),
    record_id     TEXT NOT NULL REFERENCES record(record_id),
    seq           INTEGER NOT NULL,          -- order within the batch
    state         TEXT NOT NULL,             -- pending | leased | done | failed | cancelled
    attempts      INTEGER NOT NULL,
    lease_owner   TEXT,
    lease_expires REAL,                      -- unix seconds
    last_error    TEXT,                      -- a category, never label text
    updated_at    TEXT NOT NULL,
    UNIQUE (batch_id, record_id)
);
CREATE INDEX IF NOT EXISTS job_state ON job(state, batch_id, seq);
CREATE INDEX IF NOT EXISTS proposal_record ON proposal(record_id);
CREATE INDEX IF NOT EXISTS decision_record ON decision(record_id);
"""


class Action(StrEnum):
    APPROVE = "approve"  # with or without edits
    REJECT = "reject"
    RESEARCH = "request_research"  # back to needs_information, with a note


class ReviewError(ValueError):
    pass


_APPROVABLE: Final = frozenset({RecordStatus.READY_FOR_REVIEW, RecordStatus.NEEDS_INFORMATION})


_OUTCOME_STATUS: Final = {
    ProposalOutcome.COMPUTED: RecordStatus.READY_FOR_REVIEW,
    ProposalOutcome.NEEDS_INFORMATION: RecordStatus.NEEDS_INFORMATION,
    ProposalOutcome.UNSUPPORTED: RecordStatus.UNSUPPORTED,
}


@dataclass(frozen=True, slots=True)
class StoredProposal:
    proposal_id: str
    record_id: str
    system: str
    extractor_version: str
    release: str
    gazetteer_snapshot: str
    origin: str
    interpretation: Interpretation | None
    candidates: tuple[Candidate, ...]
    proposal: GeoreferenceProposal | None
    outcome: str


@dataclass(frozen=True, slots=True)
class Decision:
    decision_id: str
    record_id: str
    proposal_id: str
    action: Action
    reviewer: str
    rationale: str
    edits: dict[str, Any]
    final_proposal: str | None
    decided_at: str
    created: bool  # False when an identical decision was already stored


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash(*parts: object) -> str:
    material = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class ReviewStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(path, isolation_level=None)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA journal_mode=WAL")
        self._con.execute("PRAGMA foreign_keys=ON")
        self._con.executescript(_SCHEMA)
        row = self._con.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
        if row is None:
            self._con.execute("INSERT INTO meta VALUES ('schema', ?)", (STORE_SCHEMA_VERSION,))
        elif row["value"] in _UPGRADABLE:  # the new tables were just created by _SCHEMA
            self._con.execute("UPDATE meta SET value=? WHERE key='schema'", (STORE_SCHEMA_VERSION,))
        elif row["value"] != STORE_SCHEMA_VERSION:
            raise ReviewError(f"store schema {row['value']}, expected {STORE_SCHEMA_VERSION}")

    def close(self) -> None:
        self._con.close()

    def __enter__(self) -> ReviewStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def connection(self) -> sqlite3.Connection:
        """For :mod:`localitylens.jobs`, which keeps its tables in this file."""
        return self._con

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """One atomic unit (``BEGIN IMMEDIATE``). Inside an open transaction it simply joins it."""
        if self._con.in_transaction:
            yield
            return
        self._con.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self._con.execute("ROLLBACK")
            raise
        self._con.execute("COMMIT")

    def start_processing(self, record_id: str) -> None:
        """``queued`` → ``processing``, when a worker leases the record's job."""
        self._set_status(record_id, RecordStatus.PROCESSING)

    def requeue(self, record_id: str) -> None:
        """``processing`` → ``queued``: an expired lease or a retry after a transient failure."""
        self._set_status(record_id, RecordStatus.QUEUED)

    # --- records ------------------------------------------------------------------------------

    def add_record(self, record: SpecimenRecord, snapshot_id: str) -> str:
        """Store an original record once; importing it again changes nothing."""
        record_id = f"gbif:{record.gbif_id}"
        self._con.execute(
            "INSERT OR IGNORE INTO record VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (record_id, record.gbif_id, record.occurrence_id, record.catalog_number,
             record.locality, record.state_province, record.county, record.country,
             snapshot_id, RecordStatus.QUEUED.value, _now()),
        )  # fmt: skip
        return record_id

    def record(self, record_id: str) -> sqlite3.Row:
        row: sqlite3.Row | None = self._con.execute(
            "SELECT * FROM record WHERE record_id=?", (record_id,)
        ).fetchone()
        if row is None:
            raise ReviewError(f"no record {record_id}")
        return row

    def status(self, record_id: str) -> RecordStatus:
        return RecordStatus(self.record(record_id)["status"])

    def _set_status(self, record_id: str, target: RecordStatus) -> None:
        new = transition(self.status(record_id), target)
        self._con.execute("UPDATE record SET status=? WHERE record_id=?", (new.value, record_id))

    def records(self, status: RecordStatus | None = None) -> list[sqlite3.Row]:
        if status is None:
            return list(self._con.execute("SELECT * FROM record ORDER BY record_id"))
        return list(
            self._con.execute(
                "SELECT * FROM record WHERE status=? ORDER BY record_id", (status.value,)
            )
        )

    # --- proposals ----------------------------------------------------------------------------

    def add_pipeline_result(
        self,
        record_id: str,
        *,
        system: str,
        extractor_version: str,
        release: str,
        gazetteer_snapshot: str,
        interpretation: Interpretation | None,
        candidates: tuple[Candidate, ...],
        proposal: GeoreferenceProposal | None,
        failure: str | None = None,
    ) -> str:
        """Record one pipeline run and move the record to its outcome status.

        The record is ``queued`` (processed directly) or already ``processing`` (leased by a
        worker); both end in the outcome status.
        """
        if failure is not None:
            outcome, target = f"failed:{failure}", RecordStatus.FAILED
        elif proposal is None:
            outcome, target = "invalid_extraction", RecordStatus.NEEDS_INFORMATION
        else:
            outcome, target = proposal.outcome.value, _OUTCOME_STATUS[proposal.outcome]
        if self.status(record_id) is not RecordStatus.PROCESSING:
            self._set_status(record_id, RecordStatus.PROCESSING)
        proposal_id = self._insert_proposal(record_id, system, extractor_version, release,
                                            gazetteer_snapshot, "pipeline", interpretation,
                                            candidates, proposal, outcome)  # fmt: skip
        self._set_status(record_id, target)
        return proposal_id

    def _insert_proposal(
        self,
        record_id: str,
        system: str,
        extractor_version: str,
        release: str,
        gazetteer_snapshot: str,
        origin: str,
        interpretation: Interpretation | None,
        candidates: tuple[Candidate, ...],
        proposal: GeoreferenceProposal | None,
        outcome: str,
    ) -> str:
        interp_json = interpretation.model_dump_json() if interpretation else None
        cand_json = json.dumps([c.model_dump(mode="json") for c in candidates])
        prop_json = proposal.model_dump_json() if proposal else None
        proposal_id = _hash(record_id, system, extractor_version, release, gazetteer_snapshot,
                            origin, interp_json, cand_json, prop_json)  # fmt: skip
        self._con.execute(
            "INSERT OR IGNORE INTO proposal VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (proposal_id, record_id, system, extractor_version, release, gazetteer_snapshot,
             origin, interp_json, cand_json, prop_json, outcome, _now()),
        )  # fmt: skip
        return proposal_id

    def proposal(self, proposal_id: str) -> StoredProposal:
        r = self._con.execute(
            "SELECT * FROM proposal WHERE proposal_id=?", (proposal_id,)
        ).fetchone()
        if r is None:
            raise ReviewError(f"no proposal {proposal_id}")
        return StoredProposal(
            proposal_id=r["proposal_id"],
            record_id=r["record_id"],
            system=r["system"],
            extractor_version=r["extractor_version"],
            release=r["release"],
            gazetteer_snapshot=r["gazetteer_snapshot"],
            origin=r["origin"],
            interpretation=Interpretation.model_validate_json(r["interpretation_json"])
            if r["interpretation_json"]
            else None,
            candidates=tuple(Candidate.model_validate(c) for c in json.loads(r["candidates_json"])),
            proposal=GeoreferenceProposal.model_validate_json(r["proposal_json"])
            if r["proposal_json"]
            else None,
            outcome=r["outcome"],
        )

    def latest_pipeline_proposal(self, record_id: str) -> StoredProposal:
        r = self._con.execute(
            "SELECT proposal_id FROM proposal WHERE record_id=? AND origin='pipeline' "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1",
            (record_id,),
        ).fetchone()
        if r is None:
            raise ReviewError(f"record {record_id} has no proposal")
        return self.proposal(r["proposal_id"])

    # --- decisions ----------------------------------------------------------------------------

    def decide(
        self,
        record_id: str,
        action: Action,
        *,
        reviewer: str,
        rationale: str,
        feature_id: int | None = None,
        extent_m: float | None = None,
        extent_note: str | None = None,
        key: str | None = None,
        extent_lookup: Callable[[int], ExtentEstimate | None] | None = None,
    ) -> Decision:
        """Record a curator decision. ``extent_lookup`` (the reviewed-extent store) supplies the
        extent of a newly chosen feature when the curator gives none."""
        if not reviewer.strip() or not rationale.strip():
            raise ReviewError("a decision needs a reviewer and a rationale")
        base = self.latest_pipeline_proposal(record_id)
        requested = {"feature_id": feature_id, "extent_m": extent_m, "extent_note": extent_note}
        decision_id = key or _hash(record_id, base.proposal_id, action.value, requested,
                                   reviewer.strip(), rationale.strip())  # fmt: skip
        existing = self._decision(decision_id)
        if existing is not None:
            return existing  # a retried submission: nothing new is written

        if action is not Action.APPROVE and (feature_id is not None or extent_m is not None):
            raise ReviewError("edits are only applied when approving")
        current = self.status(record_id)
        if action is Action.APPROVE and current not in _APPROVABLE:
            raise ReviewError(f"cannot approve a record that is {current}")
        extent_m = float(extent_m) if extent_m is not None else None
        final_id: str | None = None
        edits: dict[str, Any] = {}
        if action is Action.APPROVE:
            final_id, edits = self._approved_proposal(
                base, feature_id, extent_m, extent_note, extent_lookup
            )
            target = RecordStatus.APPROVED
        elif action is Action.REJECT:
            target = RecordStatus.REJECTED
        else:
            target = RecordStatus.NEEDS_INFORMATION

        self._con.execute("BEGIN IMMEDIATE")
        try:
            # "Request further research" on a record that already needs information only adds
            # the note; every other decision is a status change.
            if not (action is Action.RESEARCH and current is RecordStatus.NEEDS_INFORMATION):
                try:
                    self._set_status(record_id, target)
                except InvalidTransitionError as exc:
                    raise ReviewError(f"cannot {action.value} a record that is {current}") from exc
            self._con.execute(
                "INSERT INTO decision VALUES (?,?,?,?,?,?,?,?,?)",
                (decision_id, record_id, base.proposal_id, action.value, reviewer.strip(),
                 rationale.strip(), json.dumps(edits, sort_keys=True), final_id, _now()),
            )  # fmt: skip
            self._con.execute("COMMIT")
        except Exception:
            self._con.execute("ROLLBACK")
            raise
        stored = self._decision(decision_id)
        assert stored is not None
        return dataclasses.replace(stored, created=True)

    def _approved_proposal(
        self,
        base: StoredProposal,
        feature_id: int | None,
        extent_m: float | None,
        extent_note: str | None,
        extent_lookup: Callable[[int], ExtentEstimate | None] | None,
    ) -> tuple[str, dict[str, Any]]:
        """The proposal an approval exports: the pipeline's, or a recomputed edited one."""
        if base.interpretation is None:
            raise ReviewError("the extraction failed validation; there is nothing to approve")
        proposed_fid = base.proposal.feature_id if base.proposal else None
        edits: dict[str, Any] = {}
        candidate = next((c for c in base.candidates if c.feature_id == proposed_fid), None)
        if feature_id is not None and feature_id != proposed_fid:
            candidate = next((c for c in base.candidates if c.feature_id == feature_id), None)
            if candidate is None:
                raise ReviewError(f"feature {feature_id} is not among the retrieved candidates")
            edits["feature_id"] = [proposed_fid, feature_id]
        extent: ExtentEstimate | None = None
        if extent_m is not None:
            if not extent_note or not extent_note.strip():
                raise ReviewError("a curator extent needs a note saying how it was determined")
            extent = ExtentEstimate(radius_m=extent_m, source=ExtentSource.REVIEWED,
                                    rationale=f"curator edit: {extent_note.strip()}")  # fmt: skip
            old = base.proposal.components if base.proposal else ()
            old_extent = next((c.metres for c in old if c.name.value == "extent"), None)
            edits["extent_m"] = [old_extent, extent_m]
        if not edits:
            if base.proposal is None or base.proposal.outcome is not ProposalOutcome.COMPUTED:
                raise ReviewError(
                    "the proposal has no full region; edit it (feature, extent) or request "
                    "research instead"
                )
            return base.proposal_id, edits
        if extent is None and not edits.get("feature_id") and base.proposal is not None:
            extent = _carried_extent(base.proposal)  # same feature: keep the extent it had
        if extent is None and candidate is not None and extent_lookup is not None:
            extent = extent_lookup(candidate.feature_id)  # a newly chosen feature's own extent
        recomputed = propose(base.interpretation, candidate, extent)
        if recomputed.outcome is not ProposalOutcome.COMPUTED:
            open_q = "; ".join(recomputed.questions) or "no full region"
            raise ReviewError(f"after the edits the proposal is still incomplete: {open_q}")
        final_id = self._insert_proposal(
            base.record_id, base.system, base.extractor_version, base.release,
            base.gazetteer_snapshot, "curator_edit", base.interpretation, base.candidates,
            recomputed, recomputed.outcome.value,
        )  # fmt: skip
        return final_id, edits

    def _decision(self, decision_id: str) -> Decision | None:
        r = self._con.execute(
            "SELECT * FROM decision WHERE decision_id=?", (decision_id,)
        ).fetchone()
        if r is None:
            return None
        return Decision(
            decision_id=r["decision_id"],
            record_id=r["record_id"],
            proposal_id=r["proposal_id"],
            action=Action(r["action"]),
            reviewer=r["reviewer"],
            rationale=r["rationale"],
            edits=json.loads(r["edits_json"]),
            final_proposal=r["final_proposal"],
            decided_at=r["decided_at"],
            created=False,
        )

    def decisions(self, record_id: str | None = None) -> list[Decision]:
        query = "SELECT decision_id FROM decision"
        args: tuple[str, ...] = ()
        if record_id is not None:
            query, args = query + " WHERE record_id=?", (record_id,)
        ids = [r["decision_id"] for r in self._con.execute(query + " ORDER BY rowid", args)]
        return [d for i in ids if (d := self._decision(i)) is not None]


def _carried_extent(proposal: GeoreferenceProposal) -> ExtentEstimate | None:
    """The extent a pipeline proposal already used, kept when only other fields are edited."""
    for c in proposal.components:
        if c.name.value == "extent" and c.metres is not None:
            source = ExtentSource(c.rule.split(":", 1)[0])
            return ExtentEstimate(radius_m=c.metres, source=source,
                                  rationale=c.rule.split(":", 1)[1].strip() or c.rule)  # fmt: skip
    return None
