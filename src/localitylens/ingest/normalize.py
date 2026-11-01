"""Text normalization with an exact map back to the original string.

The original locality text is never modified. Normalization produces a second string plus,
for every normalized character, the half-open ``[start, end)`` range of original characters it
came from. Any span found in normalized text can therefore be restored to original-text
coordinates. This single module is used by evaluation and serving alike, so both see identical text.

Rules (version ``NORMALIZATION_VERSION``):
1. Unicode NFC, applied per cluster (a base character plus its combining marks) so every output
   character maps to a definite original range.
2. Every run of whitespace (including CR, LF, tabs) becomes a single space.
3. Leading and trailing whitespace is dropped.

Abbreviation expansion is deliberately *not* done here; it is a separate, versioned rules step
that keeps the same offset discipline.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

NORMALIZATION_VERSION = "1"


@dataclass(frozen=True, slots=True)
class NormalizedText:
    original: str
    text: str
    # starts[i], ends[i]: original [start, end) range for normalized character i.
    starts: tuple[int, ...]
    ends: tuple[int, ...]

    def to_original(self, start: int, end: int) -> tuple[int, int]:
        """Map a half-open normalized span to a half-open span of the original string."""
        if not 0 <= start < end <= len(self.text):
            raise ValueError(
                f"span [{start}, {end}) outside normalized text of length {len(self.text)}"
            )
        return self.starts[start], self.ends[end - 1]

    def original_slice(self, start: int, end: int) -> str:
        o_start, o_end = self.to_original(start, end)
        return self.original[o_start:o_end]


def _clusters(text: str) -> list[tuple[int, int]]:
    """Split into [start, end) ranges of a base character followed by combining marks."""
    ranges: list[tuple[int, int]] = []
    i, n = 0, len(text)
    while i < n:
        j = i + 1
        while j < n and unicodedata.combining(text[j]):
            j += 1
        ranges.append((i, j))
        i = j
    return ranges


def normalize(original: str) -> NormalizedText:
    out: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    pending_space: tuple[int, int] | None = None

    for c_start, c_end in _clusters(original):
        cluster = original[c_start:c_end]
        if cluster.isspace():
            pending_space = (pending_space[0], c_end) if pending_space else (c_start, c_end)
            continue
        if pending_space is not None and out:
            out.append(" ")
            starts.append(pending_space[0])
            ends.append(pending_space[1])
        pending_space = None
        for ch in unicodedata.normalize("NFC", cluster):
            out.append(ch)
            starts.append(c_start)
            ends.append(c_end)

    return NormalizedText(
        original=original, text="".join(out), starts=tuple(starts), ends=tuple(ends)
    )
