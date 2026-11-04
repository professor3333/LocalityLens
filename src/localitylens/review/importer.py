"""Import records into the review store and run the pipeline on each queued one.

The proposal uses the top-ranked candidate and, when the reviewed-extent store has one, that
feature's extent. Importing the same records again is harmless: originals are stored once, and
only records still ``queued`` are processed. Only the model-input allowlist reaches an
extractor.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from localitylens.extract.llm_client import ModelCallError
from localitylens.gazetteer.index import Gazetteer
from localitylens.geo.extents import ExtentStore
from localitylens.geo.georeference import propose
from localitylens.ingest.specimens import SpecimenRecord
from localitylens.pipeline.hybrid import interpret_hybrid
from localitylens.pipeline.interpret import Extractor, InterpretResult, interpret
from localitylens.review.store import ReviewStore


def import_records(
    store: ReviewStore,
    records: Iterable[SpecimenRecord],
    snapshot_id: str,
    gazetteer: Gazetteer,
    *,
    system: str,
    rules: Extractor,
    llm: Extractor | None,
    release: str,
    extents: ExtentStore | None = None,
) -> Counter[str]:
    """Add the records, then process every queued one. Returns the count per new status."""
    if system not in ("rules", "llm", "hybrid"):
        raise ValueError(f"unknown system {system!r}")
    if system != "rules" and llm is None:
        raise ValueError(f"system {system!r} needs an LLM extractor")
    ids = [store.add_record(r, snapshot_id) for r in records]  # originals first, once each
    outcome: Counter[str] = Counter()
    for record_id in ids:
        if store.status(record_id).value != "queued":
            continue
        row = store.record(record_id)
        locality, county = row["locality"], row["county"] or None
        try:
            result = _run(system, locality, county, rules, llm, gazetteer)
        except ModelCallError as exc:
            store.add_pipeline_result(
                record_id, system=system, extractor_version=_version(system, rules, llm),
                release=release, gazetteer_snapshot=gazetteer.snapshot_id,
                interpretation=None, candidates=(), proposal=None,
                failure=exc.category.value,
            )  # fmt: skip
            outcome["failed"] += 1
            continue
        interp = result.validation.interpretation
        candidates = result.retrieval.candidates if result.retrieval else ()
        top = candidates[0] if candidates else None
        extent = extents.get(top.feature_id) if extents is not None and top else None
        proposal = propose(interp, top, extent) if interp is not None else None
        store.add_pipeline_result(
            record_id, system=system, extractor_version=result.extractor_version,
            release=release, gazetteer_snapshot=gazetteer.snapshot_id,
            interpretation=interp, candidates=tuple(candidates), proposal=proposal,
        )  # fmt: skip
        outcome[store.status(record_id).value] += 1
    return outcome


def _run(
    system: str,
    locality: str,
    county: str | None,
    rules: Extractor,
    llm: Extractor | None,
    gazetteer: Gazetteer,
) -> InterpretResult:
    if system == "hybrid":
        assert llm is not None
        return interpret_hybrid(locality, rules, llm, gazetteer, supplied_county=county).result
    extractor = rules if system == "rules" else llm
    assert extractor is not None
    return interpret(locality, extractor, gazetteer, supplied_county=county)


def _version(system: str, rules: Extractor, llm: Extractor | None) -> str:
    if system == "rules" or llm is None:
        return rules.version
    return llm.version if system == "llm" else f"hybrid-1({rules.version}+{llm.version})"
