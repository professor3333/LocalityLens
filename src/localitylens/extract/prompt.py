"""Versioned extraction prompts, loaded from files under ``extract/prompts/``.

A prompt file holds a system message, few-shot turns and a final user turn with one
``{locality}`` placeholder, separated by ``=== role ===`` lines. Prompt files are immutable:
a change means a new version file, and the release manifest pins each file's SHA-256.
The label text is fenced between delimiters and is substituted verbatim, never escaped or
rewritten, because the model must quote it exactly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from importlib import resources
from typing import Final

PROMPT_VERSION: Final = "extraction-v2"
DELIMITERS: Final = ("<<<LOCALITY", "LOCALITY>>>")
PLACEHOLDER: Final = "{locality}"
_ROLE_LINE: Final = re.compile(r"^=== (system|user|assistant) ===$", re.MULTILINE)


class PromptFormatError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    version: str
    sha256: str
    turns: tuple[tuple[str, str], ...]  # (role, content); the last user turn has the placeholder

    def render(self, locality: str) -> list[dict[str, str]]:
        if any(d in locality for d in DELIMITERS):
            raise PromptFormatError("locality text contains the prompt delimiter")
        messages = [{"role": r, "content": c} for r, c in self.turns]
        messages[-1]["content"] = messages[-1]["content"].replace(PLACEHOLDER, locality)
        return messages

    def examples(self) -> list[tuple[str, str]]:
        """Few-shot (locality, assistant JSON) pairs, for tests that validate them."""
        pairs: list[tuple[str, str]] = []
        for (r1, c1), (r2, c2) in zip(self.turns[1:-1:2], self.turns[2:-1:2], strict=True):
            if (r1, r2) != ("user", "assistant"):
                raise PromptFormatError("few-shot turns must alternate user/assistant")
            start, end = c1.index(DELIMITERS[0]), c1.index(DELIMITERS[1])
            pairs.append((c1[start + len(DELIMITERS[0]) : end].strip("\n"), c2))
        return pairs


def load_prompt(version: str = PROMPT_VERSION) -> PromptTemplate:
    raw = resources.files("localitylens.extract").joinpath(f"prompts/{version}.txt").read_bytes()
    text = raw.decode("utf-8")
    parts = _ROLE_LINE.split(text)
    if parts[0].strip():
        raise PromptFormatError("text before the first role line")
    turns = tuple(
        (role, content.strip("\n")) for role, content in zip(parts[1::2], parts[2::2], strict=True)
    )
    if not turns or turns[0][0] != "system" or turns[-1][0] != "user":
        raise PromptFormatError("a prompt starts with system and ends with a user turn")
    if sum(c.count(PLACEHOLDER) for _, c in turns) != 1 or PLACEHOLDER not in turns[-1][1]:
        raise PromptFormatError("exactly one placeholder, in the last user turn")
    return PromptTemplate(version, hashlib.sha256(raw).hexdigest(), turns)
