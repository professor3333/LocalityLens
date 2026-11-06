"""LLM extraction (model call 1): label text → :class:`ExtractionOutput`, quotes only.

The model sees only the label text inside a fenced prompt and returns JSON constrained by the
extraction schema. Code then checks it:

* parsing and Pydantic validation with ``extra="forbid"`` (no extra fields, so no coordinates);
* free-text fields scanned for anything that looks like a coordinate;
* one bounded retry on malformed output, then ``malformed_model_output``;
* the exact token count checked against the context budget before the call, so an oversized
  input fails explicitly instead of being truncated.

Quote location and span validation happen afterwards in ``extract.validate``, the same as for
the rules baseline.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Final

from pydantic import ValidationError

from localitylens.extract.llm_client import FailureCategory, ModelCallError, ModelClient
from localitylens.extract.prompt import PromptFormatError, PromptTemplate, load_prompt
from localitylens.extract.schema import ExtractionOutput
from localitylens.release import ReleaseManifest

MAX_ATTEMPTS: Final = 2  # one bounded retry on malformed output

# Coordinate-like text: 3+ decimals ("40.255"), a degree sign, or a latitude/longitude pair with
# any decimals ("40.0, -105.0"; found by the adversarial suite: it passed the first two).
_COORDINATE: Final = re.compile(
    r"-?\b\d{1,3}\.\d{3,}\b|\d\s*°"
    r"|(?<![\d.])-?\d{1,2}\.\d+\s*[,;]\s*-?\d{2,3}\.\d+(?![\d.])"
    r"|(?<![\d.])-?\d{1,2}\.\d+\s+-\d{2,3}\.\d+(?![\d.])"
)


# Version of the grammar schema derived from ExtractionOutput. 1: the plain Pydantic schema.
# 2: both-or-neither pairs encoded as alternatives, so the grammar admits only what validation
# accepts (with greedy decoding, a rejected output would otherwise repeat on retry).
GRAMMAR_VERSION: Final = "2"

# Fields that Pydantic validators require to be given together or not at all.
_PAIRED: Final[dict[str, tuple[str, str]]] = {
    "FeatureMentionOut": ("feature_type", "feature_type_quote"),
    "DistanceOut": ("unit", "unit_quote"),
}


def _non_null(prop: dict[str, Any]) -> dict[str, Any]:
    options = [o for o in prop.get("anyOf", [prop]) if o.get("type") != "null"]
    if len(options) != 1:
        raise ValueError(f"expected one non-null option in {prop}")
    return dict(options[0])


def _both_or_neither(definition: dict[str, Any], a: str, b: str) -> dict[str, Any]:
    props = definition["properties"]
    required = list(definition.get("required", []))
    rest = {k: v for k, v in props.items() if k not in (a, b)}
    both = {**rest, a: _non_null(props[a]), b: _non_null(props[b])}

    def variant(properties: dict[str, Any], req: list[str]) -> dict[str, Any]:
        return {"type": "object", "properties": properties, "required": req,
                "additionalProperties": False}  # fmt: skip

    return {
        "title": definition.get("title"),
        "anyOf": [variant(both, [*required, a, b]), variant(rest, required)],
    }


def extraction_schema() -> dict[str, Any]:
    """The JSON schema given to the grammar: ExtractionOutput's schema with every
    both-or-neither pair expressed structurally. Pydantic stays the final check."""
    schema = ExtractionOutput.model_json_schema()
    for name, (a, b) in _PAIRED.items():
        schema["$defs"][name] = _both_or_neither(schema["$defs"][name], a, b)
    return schema


@dataclass(slots=True)
class CallTrace:
    """What happened on the last call. Hashes and counts only, never label text."""

    prompt_sha256: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    attempts: int = 0
    seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    cache_hits: int = 0  # attempts answered from the completion cache (0 model seconds each)


class LLMExtractor:
    def __init__(
        self,
        client: ModelClient,
        release: ReleaseManifest,
        prompt: PromptTemplate | None = None,
    ) -> None:
        self.client = client
        self.release = release
        self.prompt = prompt or load_prompt(release.prompt.version)
        if self.prompt.sha256 != release.prompt.sha256:
            raise ValueError(
                f"prompt {self.prompt.version} sha256 {self.prompt.sha256} does not match the "
                "release manifest; prompt files are immutable, add a new version instead"
            )
        self.schema = extraction_schema()
        self.last_trace = CallTrace()

    @property
    def version(self) -> str:
        return self.release.extractor_id

    def extract(self, text: str) -> ExtractionOutput:
        trace = CallTrace()
        self.last_trace = trace
        settings = self.release.generation
        try:
            messages = self.prompt.render(text)
        except PromptFormatError as exc:
            raise ModelCallError(FailureCategory.INPUT_CONTAINS_DELIMITER, str(exc)) from None
        rendered = self.client.render(messages, settings.enable_thinking)
        trace.prompt_sha256 = hashlib.sha256(rendered.encode()).hexdigest()
        needed = self.client.count_tokens(rendered) + settings.max_tokens
        if needed > self.release.context_budget_tokens:
            raise ModelCallError(
                FailureCategory.CONTEXT_BUDGET_EXCEEDED,
                f"{needed} tokens needed, budget {self.release.context_budget_tokens}",
            )
        last = ModelCallError(FailureCategory.MALFORMED_MODEL_OUTPUT, "no attempt made")
        for _ in range(MAX_ATTEMPTS):
            trace.attempts += 1
            completion = self.client.complete(rendered, self.schema, settings)
            trace.prompt_tokens = completion.prompt_tokens
            trace.completion_tokens += completion.completion_tokens
            trace.seconds += completion.seconds
            trace.cache_hits += bool(getattr(self.client, "last_hit", False))
            try:
                return self._check(
                    completion.text, completion.truncated, completion.stopped_by_limit
                )
            except ModelCallError as exc:
                trace.errors.append(exc.category.value)
                last = exc
        raise last

    @staticmethod
    def _check(text: str, truncated: bool, stopped_by_limit: bool) -> ExtractionOutput:
        if truncated or stopped_by_limit:
            raise ModelCallError(
                FailureCategory.MALFORMED_MODEL_OUTPUT, "output hit the token limit"
            )
        try:
            output = ExtractionOutput.model_validate_json(text)
        except ValidationError as exc:
            kinds = sorted({str(e["type"]) for e in exc.errors()})
            if "extra_forbidden" in kinds:
                fields = sorted({".".join(map(str, e["loc"])) for e in exc.errors()})
                raise ModelCallError(
                    FailureCategory.MODEL_SUPPLIED_COORDINATES
                    if any(_looks_like_coordinate_field(f) for f in fields)
                    else FailureCategory.MALFORMED_MODEL_OUTPUT,
                    f"fields outside the schema: {fields}",
                ) from None
            raise ModelCallError(
                FailureCategory.MALFORMED_MODEL_OUTPUT, f"schema validation: {kinds}"
            ) from None
        if any(_COORDINATE.search(q) for q in output.open_questions):
            raise ModelCallError(
                FailureCategory.MODEL_SUPPLIED_COORDINATES, "coordinate-like text in a question"
            )
        return output


def _looks_like_coordinate_field(name: str) -> bool:
    lowered = name.lower()
    return any(w in lowered for w in ("lat", "lon", "lng", "coord", "radius", "wkt", "geometry"))
