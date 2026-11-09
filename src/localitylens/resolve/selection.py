"""Selection check (``selection-1``): hold a region back when the label names another place.

Selection confidence and spatial uncertainty are separate (invariant 7). A computed region says
how large the area is around the chosen reference; it says nothing about whether the reference
is the right one. On dev data, most wrong regions come from labels that name a specific
collecting place and *also* give an offset from a town ("Burch's Lake, 4 mi E of Lyons"): the
town is chosen, and the region is drawn around the wrong place.

**The rule.** The label is split at sentence and clause breaks (``.``, ``;``, ``:``, ``,``,
parentheses). In each part, a run of capitalised words is a *competing feature* when:

* its last word states a feature type (:data:`localitylens.extract.feature_words.TYPE_WORDS`:
  creek, lake, peak, pass, gulch…), after leading direction words are dropped;
* it is not a broad area (a range, mountains, hills, a wilderness, a national or state park,
  forest or monument: the same words as the rules' broad places);
* its name key is not the chosen reference's, and neither contains the other.

A computed proposal with a competing feature keeps its region but goes to
``needs_information`` with the question "the label also names …". A curator who approves it
answers that question. The check never adds a region and never changes one.

Measured on dev data only (in-sample; ``eval/reports/selection-check-findings.md``).
"""

from __future__ import annotations

import re
from typing import Any, Final

from localitylens.extract.feature_words import TYPE_WORDS
from localitylens.gazetteer.keys import name_key
from localitylens.geo.georeference import GeoreferenceProposal as Proposal
from localitylens.geo.georeference import ProposalOutcome

SELECTION_VERSION: Final = "selection-1"
QUESTION_PREFIX: Final = "Selection check: "
_PARTS: Final = re.compile(r"[.;:,]\s+|\s+\(|\)")
_TOKEN: Final = "[A-Z][A-Za-z'\\u2019\\-]*\\.?"  # a capitalised word; \u2019 = right single quote
_RUN: Final = re.compile(rf"{_TOKEN}(?:\s+(?:of\s+|de\s+|la\s+)?{_TOKEN})*")
_LEADING: Final = frozenset({
    "n", "s", "e", "w", "ne", "nw", "se", "sw", "nne", "nnw", "ene", "ese", "sse", "ssw",
    "wnw", "wsw", "north", "south", "east", "west", "slope", "side", "of",
})  # fmt: skip
_BROAD_LAST: Final = frozenset(
    {"r.", "mountains", "mtns", "mtns.", "mts", "mts.", "range", "hills", "wilderness"}
)
_BROAD_LAST_TWO: Final = frozenset({
    "national park", "state park", "national forest", "state forest", "national monument",
    "nat. forest",
})  # fmt: skip


def competing_features(
    locality: str, reference: str, leading: frozenset[str] = _LEADING
) -> list[str]:
    """Names of typed features in the label other than ``reference``, in label order."""
    ref_key = name_key(reference)
    found: list[str] = []
    for part in _PARTS.split(locality):
        for m in _RUN.finditer(part):
            words = m.group(0).split()
            while words and words[0].lower().rstrip(".") in leading:
                words = words[1:]
            if not words:
                continue
            last = words[-1].lower()
            if last not in TYPE_WORDS:
                last = last.rstrip(".")
                if last not in TYPE_WORDS:
                    continue
                words[-1] = words[-1].rstrip(".")
            lowered = [w.lower() for w in words]
            if lowered[-1] in _BROAD_LAST or " ".join(lowered[-2:]) in _BROAD_LAST_TWO:
                continue
            phrase = " ".join(words)
            key = name_key(phrase)
            if not key or not ref_key or key == ref_key or ref_key in key or key in ref_key:
                continue
            if phrase not in found:
                found.append(phrase)
    return found


def apply_selection_check(locality: str, reference: str, proposal: Proposal) -> Proposal:
    """A computed proposal whose label names a competing feature goes to needs_information,
    with its region kept. Anything else is returned unchanged."""
    if proposal.outcome is not ProposalOutcome.COMPUTED:
        return proposal
    others = competing_features(locality, reference)
    if not others:
        return proposal
    names = ", ".join(f"'{o}'" for o in others)
    question = (
        f"{QUESTION_PREFIX}the label also names {names}, which this proposal does not use. "
        f"Is '{reference}' the reference for the collecting place? ({SELECTION_VERSION})"
    )
    return proposal.model_copy(update={
        "outcome": ProposalOutcome.NEEDS_INFORMATION,
        "questions": (*proposal.questions, question),
    })  # fmt: skip


def only_selection_questions(proposal: Proposal) -> bool:
    """True when a region is full and the selection check is all that holds it back: a
    curator's approval answers it."""
    return (
        proposal.outcome is ProposalOutcome.NEEDS_INFORMATION
        and proposal.point is not None
        and proposal.radius_m is not None
        and bool(proposal.questions)
        and all(q.startswith(QUESTION_PREFIX) for q in proposal.questions)
    )


# ------------------------------------------------------------------------------- selection-2

SELECTION_2_VERSION: Final = "selection-2"
# selection-2 also drops a capitalised preposition or position word that opens a sentence
# ("Below Vela Lake", "Head of Fenn Creek"); the position words are the rules' (rules-3).
_LEADING_2: Final = _LEADING | frozenset({
    "below", "above", "near", "at", "in", "on", "along", "from", "to", "toward", "towards",
    "by", "beside", "across", "around", "behind", "beyond", "off", "over", "under", "up", "down",
    "approx", "approximately", "about", "ca", "just", "head", "foot", "top", "base", "mouth",
    "edge", "shore", "rim", "summit", "flank", "the",
})  # fmt: skip
_STRONG_MATCHES: Final = frozenset({"exact_official", "exact_variant", "core_official",
                                    "core_variant"})  # fmt: skip


def geographic_competitors(
    locality: str,
    reference: str,
    proposal: Proposal,
    gazetteer: Any,
    county: str | None,
) -> list[tuple[str, str]]:
    """``selection-2``: the competing features of :func:`competing_features` that still cast
    doubt once GNIS is asked. Each is ``(name, why)``, where ``why`` is ``"inside"`` (GNIS has
    the feature, by an exact or core name match, and its point lies inside the proposed region:
    the label's offset points at a more specific named place) or ``"absent"`` (GNIS has no such
    feature, so the label names a place this gazetteer cannot place). A competing feature that
    GNIS places outside the region is a separate landmark ("along the Arikaree River") and does
    not count."""
    from localitylens.geo.geodesy import distance_m

    if proposal.point is None or proposal.radius_m is None:
        return []
    out: list[tuple[str, str]] = []
    for name in competing_features(locality, reference, _LEADING_2):
        hits = [h for h in gazetteer.search(name, county=county, limit=3)
                if h.match_kind.value in _STRONG_MATCHES]  # fmt: skip
        if not hits:
            out.append((name, "absent"))
        elif distance_m(proposal.point, hits[0].primary_point) <= proposal.radius_m:
            out.append((name, "inside"))
    return out


def apply_selection_2(
    locality: str, reference: str, proposal: Proposal, gazetteer: Any, county: str | None
) -> Proposal:
    """Hold a computed region in needs_information when :func:`geographic_competitors` finds
    any; keep the region. Anything else is returned unchanged."""
    if proposal.outcome is not ProposalOutcome.COMPUTED:
        return proposal
    found = geographic_competitors(locality, reference, proposal, gazetteer, county)
    if not found:
        return proposal
    parts = [
        f"'{n}' (in GNIS, inside the proposed region)" if why == "inside"
        else f"'{n}' (not in GNIS)"
        for n, why in found
    ]  # fmt: skip
    question = (
        f"{QUESTION_PREFIX}the label also names {', '.join(parts)}, which this proposal does "
        f"not use. Is '{reference}' the reference for the collecting place? "
        f"({SELECTION_2_VERSION})"
    )
    return proposal.model_copy(update={
        "outcome": ProposalOutcome.NEEDS_INFORMATION,
        "questions": (*proposal.questions, question),
    })  # fmt: skip
