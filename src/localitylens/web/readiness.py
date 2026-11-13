"""Readiness and version report for ``/readyz`` and ``/api/version`` (deploy verification).

Ready means: the review store opens at the current schema, the release manifest loads, and the
manifest's pinned versions match the running code (the same checks as the release-manifest
contract test, run at deploy time). The report lists every pinned version: model and upstream
revision, GGUF SHA-256, llama.cpp build, prompt and schema versions, gazetteer and specimen
snapshots, uncertainty policy, and the store, jobs, telemetry and API versions. It contains no
record data.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Any

from localitylens.baseline.rules import RULES_VERSION
from localitylens.extract.prompt import PROMPT_VERSION, load_prompt
from localitylens.extract.schema import EXTRACTION_SCHEMA_VERSION
from localitylens.extract.validate import VALIDATION_VERSION
from localitylens.gazetteer.keys import CORE_KEY_VERSION
from localitylens.geo.uncertainty import POLICY_ID
from localitylens.jobs.queue import JOBS_VERSION
from localitylens.release import ReleaseManifest, load_release
from localitylens.resolve.county import COUNTY_CONTEXT_VERSION
from localitylens.resolve.selection import (
    SELECTION_2_VERSION,
    SELECTION_3_VERSION,
    SELECTION_VERSION,
)
from localitylens.review.store import STORE_SCHEMA_VERSION, ReviewError, ReviewStore
from localitylens.telemetry.trace import TELEMETRY_VERSION
from localitylens.web.api import API_VERSION


def _package_version() -> str:
    try:
        return metadata.version("localitylens")
    except metadata.PackageNotFoundError:  # running from a source tree without install
        return "unknown"


def _mismatches(release: ReleaseManifest) -> list[str]:
    """Pinned versions that differ from the running code."""
    checks = {
        "schema_version": (release.schema_version, EXTRACTION_SCHEMA_VERSION),
        "rules_version": (release.rules_version, RULES_VERSION),
        "uncertainty_policy": (release.uncertainty_policy, POLICY_ID),
        "prompt.version": (release.prompt.version, PROMPT_VERSION),
        "prompt.sha256": (release.prompt.sha256, load_prompt().sha256),
        "validation_version": (release.validation_version, VALIDATION_VERSION),
        "core_key_version": (release.core_key_version, CORE_KEY_VERSION),
        "county_context_version": (release.county_context_version, COUNTY_CONTEXT_VERSION),
    }
    out = [f"{k}: manifest {a!r}, code {b!r}" for k, (a, b) in checks.items() if a != b]
    if release.selection_version not in (
        None, SELECTION_VERSION, SELECTION_2_VERSION, SELECTION_3_VERSION
    ):  # fmt: skip
        out.append(f"selection_version: manifest {release.selection_version!r}, not in the code")
    return out


def report(
    db: Path, release_path: Path, extra_problems: list[str] | None = None
) -> tuple[bool, dict[str, Any]]:
    """(ready, report). Never raises for a missing or broken input: it says what is wrong."""
    problems: list[str] = list(extra_problems or [])
    out: dict[str, Any] = {
        "package": _package_version(),
        "store_schema": STORE_SCHEMA_VERSION,
        "jobs": JOBS_VERSION,
        "telemetry": TELEMETRY_VERSION,
        "api": API_VERSION,
        "code": {
            "rules": RULES_VERSION,
            "validation": VALIDATION_VERSION,
            "uncertainty_policy": POLICY_ID,
            "prompt": PROMPT_VERSION,
            "schema": EXTRACTION_SCHEMA_VERSION,
            "selection": [SELECTION_VERSION, SELECTION_2_VERSION, SELECTION_3_VERSION],
        },
    }
    if not db.is_file():
        problems.append(f"review store: {db} does not exist (run `review import` first)")
    else:
        try:
            with ReviewStore(db):
                out["store"] = "ok"
        except (ReviewError, OSError) as exc:  # e.g. an unknown schema version
            problems.append(f"review store: {exc}")
    try:
        release = load_release(release_path)
    except (OSError, ValueError) as exc:
        problems.append(f"release manifest {release_path}: {exc}")
    else:
        out["release"] = {
            "release": release.release,
            "extractor_id": release.extractor_id,
            "model": {"id": release.model.id, "upstream_revision": release.model.upstream_revision,
                      "gguf_file": release.model.gguf_file,
                      "quantization": release.model.quantization,
                      "gguf_sha256": release.model.gguf_sha256},
            "llama_cpp": {"version": release.server.llama_cpp_version,
                          "build": release.server.llama_cpp_build},
            "prompt": {"version": release.prompt.version, "sha256": release.prompt.sha256},
            "schema_version": release.schema_version,
            "grammar_version": release.grammar_version,
            "validation_version": release.validation_version,
            "rules_version": release.rules_version,
            "selection_version": release.selection_version,
            "uncertainty_policy": release.uncertainty_policy,
            "gazetteer_snapshot": release.gazetteer_snapshot,
            "specimen_snapshot": release.specimen_snapshot,
            "generation": release.generation.model_dump(),
        }  # fmt: skip
        problems += [f"version mismatch: {m}" for m in _mismatches(release)]
    out["ready"] = not problems
    out["problems"] = problems
    return not problems, out
