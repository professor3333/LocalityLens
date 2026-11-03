"""Rules first, LLM as fallback (``hybrid-1``).

The locked test of release 1 showed the rules ahead on interpretation and the LLM unable to add
10 points on its own. ``hybrid-1`` keeps the rules' interpretation whenever it reaches the
gazetteer, and asks the LLM only when it does not:

1. Run the rules. If their interpretation is valid **and** retrieval returns at least one
   candidate, use it. No model call is made.
2. Otherwise call the LLM. Use its interpretation only if it is valid and returns at least one
   candidate. Otherwise keep the rules' result (a model failure never makes a record worse).

Whole results are chosen, never mixed field by field, so every interpretation is one system's
reading with its own spans. The LLM's "unsupported" verdicts are deliberately **not** used as a
gate: on the audit (dev data) that gate cost 3 records the rules had right
(``eval/reports/hybrid-1-findings.md``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from localitylens.extract.llm_client import ModelCallError
from localitylens.gazetteer.index import Gazetteer
from localitylens.pipeline.interpret import Extractor, InterpretResult, interpret

HYBRID_VERSION: Final = "hybrid-1"

Source = Literal["rules", "llm"]


def reaches_gazetteer(valid: bool, candidate_count: int) -> bool:
    """The selection rule's single test: a valid interpretation with at least one candidate."""
    return valid and candidate_count > 0


def _reaches(result: InterpretResult) -> bool:
    return reaches_gazetteer(
        result.validation.interpretation is not None,
        len(result.retrieval.candidates) if result.retrieval is not None else 0,
    )


@dataclass(frozen=True, slots=True)
class HybridResult:
    result: InterpretResult  # the chosen system's result, unchanged
    source: Source
    llm_called: bool
    llm_error: str | None  # failure category when the fallback call failed

    @property
    def version(self) -> str:
        return HYBRID_VERSION


def interpret_hybrid(
    original: str,
    rules: Extractor,
    llm: Extractor,
    gazetteer: Gazetteer,
    *,
    supplied_county: str | None = None,
    limit: int = 5,
) -> HybridResult:
    first = interpret(original, rules, gazetteer, supplied_county=supplied_county, limit=limit)
    if _reaches(first):
        return HybridResult(first, "rules", llm_called=False, llm_error=None)
    try:
        second = interpret(original, llm, gazetteer, supplied_county=supplied_county, limit=limit)
    except ModelCallError as exc:
        return HybridResult(first, "rules", llm_called=True, llm_error=exc.category.value)
    if _reaches(second):
        return HybridResult(second, "llm", llm_called=True, llm_error=None)
    return HybridResult(first, "rules", llm_called=True, llm_error=None)
