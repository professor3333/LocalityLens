"""The release manifest: every version that changes a result, in one committed file.

Model revision and GGUF checksum, llama.cpp build, generation settings, prompt and schema
versions, rules version, uncertainty policy, and source snapshots. Changing any of them is a
version bump (CLAUDE.md §6); tests compare this file with the code's own constants.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_PATH: Final = Path("release/manifest.json")

_STRICT = ConfigDict(extra="forbid", frozen=True)


class ModelPin(BaseModel):
    model_config = _STRICT
    id: str
    upstream_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    licence: str
    gguf_repo: str
    gguf_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    gguf_file: str
    quantization: str
    gguf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    gguf_size_bytes: int = Field(gt=0)

    @property
    def url(self) -> str:
        return (
            f"https://huggingface.co/{self.gguf_repo}/resolve/{self.gguf_revision}/{self.gguf_file}"
        )


class ServerPin(BaseModel):
    model_config = _STRICT
    llama_cpp_version: str
    llama_cpp_build: str  # as reported by /props build_info: "b<build>-<commit>"
    args: tuple[str, ...]


class GenerationSettings(BaseModel):
    model_config = _STRICT
    temperature: float = Field(ge=0)
    top_k: int = Field(ge=0)
    seed: int
    max_tokens: int = Field(gt=0)
    enable_thinking: bool


class PromptPin(BaseModel):
    model_config = _STRICT
    version: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ReleaseManifest(BaseModel):
    model_config = _STRICT
    release: str
    extractor_id: str
    model: ModelPin
    server: ServerPin
    generation: GenerationSettings
    prompt: PromptPin
    schema_version: str
    grammar_version: str  # how the schema is turned into a decoding grammar (extract/llm.py)
    validation_version: str  # extract/validate.py VALIDATION_VERSION
    core_key_version: str  # gazetteer/keys.py CORE_KEY_VERSION (core match tier)
    context_budget_tokens: int = Field(gt=0)
    rules_version: str
    uncertainty_policy: str
    gazetteer_snapshot: str
    specimen_snapshot: str


def load_release(path: Path = DEFAULT_PATH) -> ReleaseManifest:
    return ReleaseManifest.model_validate_json(path.read_text(encoding="utf-8"))
