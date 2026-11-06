"""Per-attempt traces: what ran, on which versions, how long it took and how it ended.

Telemetry never carries label text or coordinates (CLAUDE.md §10). The trace schema has no
free-text field: only IDs, hashes, versions, counts, durations and enum-like codes. The input is
represented by a SHA-256 of the model-input allowlist (normalized locality text and supplied
county), so two runs on the same input can be matched without storing the input.

Each trace is stored in the review store, in the same transaction as the job step it describes,
and is also emitted as one JSON line on the ``localitylens.telemetry`` logger (attach a handler,
e.g. ``review work --log-json PATH``, to keep them).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from localitylens.ingest.normalize import normalize

TELEMETRY_VERSION: Final = "telemetry-1"
LOGGER_NAME: Final = "localitylens.telemetry"
_CODE: Final = r"^[a-z0-9_:\-.+()]{1,80}$"  # identifiers and codes only: no spaces, no prose

log = logging.getLogger(LOGGER_NAME)


def input_sha256(locality: str, county: str | None) -> str:
    """Hash of exactly what may reach an extractor (the allowlist), never the text itself."""
    basis = f"{normalize(locality).text}\x1f{(county or '').strip()}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def new_trace_id() -> str:
    return uuid.uuid4().hex


class StageTimes(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    extract_ms: float | None = None
    validate_ms: float | None = None
    retrieve_ms: float | None = None
    propose_ms: float | None = None
    total_ms: float | None = None


class ModelUse(BaseModel):
    """The LLM call behind this attempt, when one was made (hashes and counts only)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    called: bool
    used: bool  # hybrid: whether the LLM reading was the one kept
    prompt_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    prompt_tokens: int = 0
    completion_tokens: int = 0
    attempts: int = 0
    cache_hits: int = 0
    seconds: float = 0.0
    error: str | None = Field(default=None, pattern=_CODE)


class RecordTrace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    telemetry_version: str = TELEMETRY_VERSION
    trace_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    at: str  # UTC, ISO 8601
    job_id: str = Field(pattern=r"^[0-9a-f]{16}$")
    batch_id: str = Field(pattern=r"^b-[0-9a-f]{16}$")
    record_id: str = Field(pattern=r"^gbif:[0-9]+$")
    attempt: int = Field(ge=1)
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    system: str = Field(pattern=_CODE)
    extractor_version: str = Field(pattern=_CODE)
    release: str = Field(pattern=_CODE)
    gazetteer_snapshot: str = Field(pattern=_CODE)
    uncertainty_policy: str | None = Field(default=None, pattern=r"^[a-z0-9\-/.]{1,40}$")
    validation_version: str | None = Field(default=None, pattern=_CODE)
    outcome: str = Field(pattern=_CODE)  # a record status, or retry:/failed:<category>
    proposal_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16,64}$")
    candidate_count: int | None = Field(default=None, ge=0)
    validation_errors: tuple[str, ...] = ()  # issue codes, not messages
    stages: StageTimes = StageTimes()
    model: ModelUse | None = None


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def emit(trace: RecordTrace) -> None:
    """One JSON line per trace on the telemetry logger, and a span when OpenTelemetry export
    is on (:mod:`localitylens.telemetry.otel`)."""
    log.info(json.dumps(trace.model_dump(mode="json", exclude_none=True), sort_keys=True))
    from localitylens.telemetry import otel  # imported here: otel imports this module

    otel.record(trace)


def json_lines_handler(path: str) -> logging.Handler:
    """A handler that writes each trace as one JSON line (for ``--log-json``)."""
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.setLevel(logging.INFO)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return handler
