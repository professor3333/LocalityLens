"""normalize → extract → validate → retrieve, for any extractor (rules now, LLM later)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol

from localitylens.extract.schema import ExtractionOutput
from localitylens.extract.validate import ValidationResult, validate_extraction
from localitylens.gazetteer.index import Gazetteer
from localitylens.ingest.normalize import NormalizedText, normalize
from localitylens.resolve.retrieve import RetrievalResult, retrieve


class Extractor(Protocol):
    @property
    def version(self) -> str: ...

    def extract(self, text: str) -> ExtractionOutput: ...


@dataclass(frozen=True, slots=True)
class InterpretResult:
    extractor_version: str
    text: NormalizedText
    extraction: ExtractionOutput
    validation: ValidationResult
    retrieval: RetrievalResult | None  # None when validation failed
    stage_ms: dict[str, float] = field(default_factory=dict)  # extract, validate, retrieve


def interpret(
    original: str,
    extractor: Extractor,
    gazetteer: Gazetteer,
    *,
    supplied_county: str | None = None,
    limit: int = 5,
) -> InterpretResult:
    text = normalize(original)
    t0 = time.perf_counter()
    extraction = extractor.extract(text.text)
    t1 = time.perf_counter()
    validation = validate_extraction(extraction, text)
    t2 = time.perf_counter()
    retrieval = (
        retrieve(validation.interpretation, gazetteer, supplied_county=supplied_county, limit=limit)
        if validation.interpretation is not None
        else None
    )
    t3 = time.perf_counter()
    stage_ms = {"extract_ms": (t1 - t0) * 1000, "validate_ms": (t2 - t1) * 1000,
                "retrieve_ms": (t3 - t2) * 1000}  # fmt: skip
    return InterpretResult(extractor.version, text, extraction, validation, retrieval, stage_ms)
