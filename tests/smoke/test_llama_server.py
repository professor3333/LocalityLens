"""Smoke test: the real client, prompt, grammar and validation against the pinned llama.cpp server.

The model is a tiny test GGUF (ggml-org/tinygemma3-GGUF at c287502c, ``tinygemma3-Q8_0.gguf``,
SHA-256 7566ae72…, WTFPL), served by the same ``llama.cpp:server-b11960`` image the Compose
``llm`` profile pins. It cannot read labels; the test proves the plumbing, not quality:

* the server applies a chat template, tokenizes, and enforces a JSON schema on completion;
* a real label goes through ``extraction-v2`` and the release grammar, and the extractor ends in
  a valid extraction or a categorized failure, after at most the one bounded retry.

The label is one record of the committed audit sample (University of Colorado Herbarium via
GBIF, CC BY 4.0: GBIF.org (01 November 2026) GBIF Occurrence Download
https://doi.org/10.15468/dl.hqxjjf).

Runs only when ``LOCALITYLENS_SMOKE_URL`` points at the server (CI starts it).
"""

import json
import os
from pathlib import Path

import pytest

from localitylens.extract.llm import LLMExtractor
from localitylens.extract.llm_client import FailureCategory, LlamaServerClient, ModelCallError
from localitylens.extract.schema import ExtractionOutput
from localitylens.release import GenerationSettings, load_release

ROOT = Path(__file__).resolve().parents[2]
URL = os.environ.get("LOCALITYLENS_SMOKE_URL")
pytestmark = [
    pytest.mark.llama_smoke,
    pytest.mark.skipif(not URL, reason="LOCALITYLENS_SMOKE_URL is not set"),
]
RECORD = "2573441754"  # "Northern Gunnison Basin: ca 5 air mi SSW of Paonia."


def _label() -> str:
    sample = json.loads((ROOT / "eval/audit/audit-50.json").read_text(encoding="utf-8"))
    return next(i["record"]["locality"] for i in sample["items"]
                if i["record"]["gbif_id"] == RECORD)  # fmt: skip


def test_the_server_build_and_schema_enforcement() -> None:
    client = LlamaServerClient(URL or "", timeout_s=300)
    assert (
        client.props()["build_info"]
        == load_release(ROOT / "release/manifest.json").server.llama_cpp_build
    )
    prompt = client.render([{"role": "user", "content": "Answer."}], enable_thinking=False)
    assert client.count_tokens(prompt) > 0
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"],
              "additionalProperties": False}  # fmt: skip
    settings = GenerationSettings(temperature=0, top_k=1, seed=1, max_tokens=24,
                                  enable_thinking=False)  # fmt: skip
    out = client.complete(prompt, schema, settings)
    if not out.stopped_by_limit:  # a finished answer must satisfy the schema exactly
        assert set(json.loads(out.text)) == {"ok"}


def test_a_real_label_ends_in_a_valid_extraction_or_a_categorized_failure() -> None:
    release = load_release(ROOT / "release/manifest.json")
    extractor = LLMExtractor(LlamaServerClient(URL or "", timeout_s=300), release)
    label = _label()
    outcome: ExtractionOutput | ModelCallError
    try:
        outcome = extractor.extract(label)
    except ModelCallError as exc:  # a tiny model usually ends here: that is a valid outcome
        outcome = exc
    if isinstance(outcome, ModelCallError):
        assert outcome.category in set(FailureCategory)
        assert outcome.category is not FailureCategory.MODEL_SERVER_UNAVAILABLE
        assert label not in str(outcome)  # errors never carry label text
    else:
        assert isinstance(outcome, ExtractionOutput)
    trace = extractor.last_trace
    assert 1 <= trace.attempts <= 2  # one bounded retry at most
    assert trace.prompt_tokens > 0
    assert trace.completion_tokens > 0
