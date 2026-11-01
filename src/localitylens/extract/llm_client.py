"""The single interface to the local model server (llama.cpp ``llama-server``).

Every model call in the application goes through :class:`ModelClient`, so tests can use
recorded or fake responses and CI never needs a running model. The server is reached on the
loopback interface only (CLAUDE.md §6).

Requests use ``/apply-template`` (the model's own chat template renders the messages), then
``/tokenize`` (exact token count against the context budget), then ``/completion`` with a JSON
schema, so the rendered prompt can be hashed and nothing is ever truncated silently.
API: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, Protocol
from urllib.parse import urlsplit

from localitylens.release import GenerationSettings

DEFAULT_URL: Final = "http://127.0.0.1:8080"
_LOOPBACK: Final = frozenset({"127.0.0.1", "localhost", "::1"})


class FailureCategory(StrEnum):
    MALFORMED_MODEL_OUTPUT = "malformed_model_output"
    MODEL_SUPPLIED_COORDINATES = "model_supplied_coordinates"
    CONTEXT_BUDGET_EXCEEDED = "context_budget_exceeded"
    INPUT_CONTAINS_DELIMITER = "input_contains_delimiter"
    MODEL_SERVER_UNAVAILABLE = "model_server_unavailable"


class ModelCallError(RuntimeError):
    """A categorized failure. The message never contains label text."""

    def __init__(self, category: FailureCategory, detail: str) -> None:
        super().__init__(f"{category.value}: {detail}")
        self.category = category
        self.detail = detail


@dataclass(frozen=True, slots=True)
class Completion:
    text: str
    prompt_tokens: int
    completion_tokens: int
    truncated: bool
    stopped_by_limit: bool
    seconds: float


class ModelClient(Protocol):
    def render(self, messages: list[dict[str, str]], enable_thinking: bool) -> str: ...
    def count_tokens(self, prompt: str) -> int: ...
    def complete(
        self, prompt: str, schema: dict[str, Any], settings: GenerationSettings
    ) -> Completion: ...


def completion_body(
    prompt: str, schema: dict[str, Any], settings: GenerationSettings
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "json_schema": schema,
        "temperature": settings.temperature,
        "top_k": settings.top_k,
        "seed": settings.seed,
        "n_predict": settings.max_tokens,
        "cache_prompt": True,
        "stream": False,
    }


class LlamaServerClient:
    def __init__(self, base_url: str = DEFAULT_URL, timeout_s: float = 600.0) -> None:
        host = urlsplit(base_url).hostname
        if host not in _LOOPBACK:
            raise ValueError(f"model server must be on the loopback interface, not {host!r}")
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def _call(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as resp:
                data: dict[str, Any] = json.load(resp)
                return data
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            if exc.code == 400 and "context" in detail.lower():
                raise ModelCallError(FailureCategory.CONTEXT_BUDGET_EXCEEDED, detail) from None
            raise ModelCallError(
                FailureCategory.MODEL_SERVER_UNAVAILABLE, f"HTTP {exc.code} on {path}: {detail}"
            ) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise ModelCallError(
                FailureCategory.MODEL_SERVER_UNAVAILABLE, f"{path}: {exc}"
            ) from None

    def props(self) -> dict[str, Any]:
        return self._call("GET", "/props")

    def render(self, messages: list[dict[str, str]], enable_thinking: bool) -> str:
        body = {"messages": messages, "chat_template_kwargs": {"enable_thinking": enable_thinking}}
        return str(self._call("POST", "/apply-template", body)["prompt"])

    def count_tokens(self, prompt: str) -> int:
        tokens = self._call("POST", "/tokenize", {"content": prompt, "add_special": True})
        return len(tokens["tokens"])

    def complete(
        self, prompt: str, schema: dict[str, Any], settings: GenerationSettings
    ) -> Completion:
        started = time.perf_counter()
        data = self._call("POST", "/completion", completion_body(prompt, schema, settings))
        return Completion(
            text=str(data.get("content", "")),
            prompt_tokens=int(data.get("tokens_evaluated", 0)),
            completion_tokens=int(data.get("tokens_predicted", 0)),
            truncated=bool(data.get("truncated", False)),
            stopped_by_limit=data.get("stop_type") == "limit",
            seconds=time.perf_counter() - started,
        )
