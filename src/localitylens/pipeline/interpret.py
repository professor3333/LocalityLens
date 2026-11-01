"""normalize → extract → validate → retrieve, for any extractor (rules now, LLM later)."""

from __future__ import annotations

from dataclasses import dataclass
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


def interpret(
    original: str,
    extractor: Extractor,
    gazetteer: Gazetteer,
    *,
    supplied_county: str | None = None,
    limit: int = 5,
) -> InterpretResult:
    text = normalize(original)
    extraction = extractor.extract(text.text)
    validation = validate_extraction(extraction, text)
    retrieval = (
        retrieve(validation.interpretation, gazetteer, supplied_county=supplied_county, limit=limit)
        if validation.interpretation is not None
        else None
    )
    return InterpretResult(extractor.version, text, extraction, validation, retrieval)
