"""Build a ``hybrid-1`` report from a rules report and an LLM report of the same sample.

Both component systems are deterministic (rules; greedy decoding with a pinned model, prompt
and grammar), so the LLM row a live hybrid run would get for a fallback record is the row the
LLM report already holds. Combining reports therefore gives the same choices as
:func:`localitylens.pipeline.hybrid.interpret_hybrid` without calling the model again.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Final

from localitylens.pipeline.hybrid import HYBRID_VERSION, reaches_gazetteer

# Report fields that must agree, or the two reports describe different runs.
_SAME: Final = (
    "audit_version",
    "specimen_snapshot",
    "gazetteer_snapshot",
    "uncertainty_policy",
    "validation_version",
    "core_key_version",
    "seed",
)
_LLM_META: Final = ("model", "gguf", "prompt", "generation", "server")


class ReportMismatchError(ValueError):
    pass


def row_reaches(row: dict[str, Any]) -> bool:
    return reaches_gazetteer(row.get("interpretation") is not None,
                             len(row.get("candidate_ids") or []))  # fmt: skip


def combine_reports(rules: dict[str, Any], llm: dict[str, Any]) -> dict[str, Any]:
    if rules.get("system") != "rules" or llm.get("system") != "llm":
        raise ReportMismatchError("expected one rules report and one LLM report")
    for key in _SAME:
        if rules.get(key) != llm.get(key):
            raise ReportMismatchError(f"reports differ in {key!r}")
    if rules.get("extent_store") != llm.get("extent_store"):
        raise ReportMismatchError("reports differ in 'extent_store'")
    r_rows, l_rows = rules["records"], llm["records"]
    if [r["audit_id"] for r in r_rows] != [r["audit_id"] for r in l_rows]:
        raise ReportMismatchError("reports cover different records")
    rows: list[dict[str, Any]] = []
    for r, lm in zip(r_rows, l_rows, strict=True):
        if row_reaches(r):
            rows.append(r | {"source": "rules", "llm_called": False})
        elif row_reaches(lm):
            rows.append(lm | {"source": "llm", "llm_called": True})
        else:  # the model was asked and did not help: keep the rules, record the call's cost
            kept = r | {"source": "rules", "llm_called": True}
            if "trace" in lm:
                kept["trace"] = lm["trace"]
            rows.append(kept)
    return {
        **{key: rules[key] for key in _SAME},
        "system": "hybrid",
        "extractor_version": HYBRID_VERSION,
        "components": {"rules": rules["extractor_version"], "llm": llm["extractor_version"]},
        **{key: llm[key] for key in _LLM_META if key in llm},
        **({"extent_store": rules["extent_store"]} if "extent_store" in rules else {}),
        "note": "Rules first; the LLM's result is used only where the rules reach no gazetteer "
        "candidate and the LLM does. Built from the two component reports (both deterministic). "
        "The top candidate is the system's ranking, not a reviewed choice, and "
        + (
            "extents come from the reviewed-extent store where it has one."
            if "extent_store" in rules
            else "no extent was supplied."
        ),
        "counts": {
            "source": dict(Counter(r["source"] for r in rows).most_common()),
            "llm_call": {
                "made": sum(r["llm_called"] for r in rows),
                "skipped": sum(not r["llm_called"] for r in rows),
            },
            "relation": dict(Counter(str(r["relation"]) for r in rows).most_common()),
            "retrieval": dict(Counter(str(r["retrieval"]) for r in rows).most_common()),
            "proposal": dict(Counter(str(r["proposal"]) for r in rows).most_common()),
        },
        "records": rows,
    }
