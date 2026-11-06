"""A local cache of model completions, keyed by everything that determines them.

Under the pinned greedy settings (temperature 0, top-k 1, fixed seed), llama-server returns the
same completion for the same request on the same model file and build. Rerunning the LLM on a
sample, for example to add reviewed extents downstream, then needs no new model calls.

**What is cached.** Only the model's raw completion. Validation, retrieval and the uncertainty
policy run again on every record, so a change to any of them takes effect at once. This is why
the key leaves out the gazetteer snapshot and the uncertainty policy: neither reaches the model.

**The key** is the SHA-256 of a canonical JSON object holding:

* the cache format version
* the exact request body: rendered prompt (label text included), JSON schema, temperature,
  top-k, seed, token limit
* the GGUF file's SHA-256 from the release manifest
* the running server's ``build_info``, model file name and context size, read from ``/props``

A different prompt, schema, model, quantization, server build or setting gives a different key.

**What is never cached.** Stochastic settings (temperature above 0 with top-k other than 1),
which must be run several times instead (§6). A cache hit's trace reports 0 model seconds and
counts as a hit, so cached rows are never mistaken for measured latency.

Entries live in a gitignored directory (``eval/.cache/llm`` by default), one JSON file per key.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Final

from localitylens.extract.llm_client import Completion, ModelClient, completion_body
from localitylens.release import GenerationSettings

CACHE_VERSION: Final = "llm-cache-1"
DEFAULT_CACHE_DIR: Final = Path("eval/.cache/llm")


def is_deterministic(settings: GenerationSettings) -> bool:
    """Greedy decoding: the only settings whose completions may be cached."""
    return settings.temperature == 0 or settings.top_k == 1


def cache_key(
    prompt: str,
    schema: dict[str, Any],
    settings: GenerationSettings,
    identity: dict[str, Any],
) -> str:
    material = {
        "version": CACHE_VERSION,
        "body": completion_body(prompt, schema, settings),
        "identity": identity,
    }
    canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class CachingClient:
    """A :class:`ModelClient` that answers repeated greedy requests from disk.

    ``identity`` must name the model file and the running server (see the module docstring);
    an incomplete identity is refused, so two different models can never share an entry.
    """

    REQUIRED_IDENTITY: Final = ("gguf_sha256", "server_build", "model_file", "n_ctx")

    def __init__(self, inner: ModelClient, directory: Path, identity: dict[str, Any]) -> None:
        missing = [k for k in self.REQUIRED_IDENTITY if not identity.get(k)]
        if missing:
            raise ValueError(f"cache identity is missing {missing}")
        self.inner = inner
        self.directory = directory
        self.identity = dict(identity)
        self.hits = 0
        self.misses = 0
        self.last_hit = False

    def render(self, messages: list[dict[str, str]], enable_thinking: bool) -> str:
        return self.inner.render(messages, enable_thinking)

    def count_tokens(self, prompt: str) -> int:
        return self.inner.count_tokens(prompt)

    def complete(
        self, prompt: str, schema: dict[str, Any], settings: GenerationSettings
    ) -> Completion:
        self.last_hit = False
        if not is_deterministic(settings):
            return self.inner.complete(prompt, schema, settings)
        key = cache_key(prompt, schema, settings, self.identity)
        path = self.directory / key[:2] / f"{key}.json"
        if path.is_file():
            stored = json.loads(path.read_text(encoding="utf-8"))
            if stored.get("key") == key:
                self.hits += 1
                self.last_hit = True
                return Completion(
                    text=stored["text"],
                    prompt_tokens=stored["prompt_tokens"],
                    completion_tokens=stored["completion_tokens"],
                    truncated=stored["truncated"],
                    stopped_by_limit=stored["stopped_by_limit"],
                    seconds=0.0,  # not a measurement
                )
        completion = self.inner.complete(prompt, schema, settings)
        self.misses += 1
        self._store(path, key, completion)
        return completion

    @staticmethod
    def _store(path: Path, key: str, c: Completion) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "key": key,
            "version": CACHE_VERSION,
            "text": c.text,
            "prompt_tokens": c.prompt_tokens,
            "completion_tokens": c.completion_tokens,
            "truncated": c.truncated,
            "stopped_by_limit": c.stopped_by_limit,
            "measured_seconds": round(c.seconds, 3),
        }
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)  # atomic: a crash never leaves a half-written entry
