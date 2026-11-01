"""Retrieve candidate reference features for an interpretation.

Shared by the rules baseline and the LLM pipeline, so any difference between them comes from
language interpretation, not from retrieval.

Admin context: a county supplied in the record's structured fields takes precedence over one
mentioned in the text. Both only *rank* candidates. The source used is recorded so a reviewer
can see why a candidate moved up.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from localitylens.extract.schema import AdminLevel, Interpretation
from localitylens.gazetteer.index import Candidate, Gazetteer


class RetrievalOutcome(StrEnum):
    CANDIDATES_FOUND = "candidates_found"
    FEATURE_ABSENT_FROM_INDEX = "feature_absent_from_index"
    NO_REFERENCE_FEATURE = "no_reference_feature"


class ContextSource(StrEnum):
    SUPPLIED = "supplied"
    TEXT = "text"


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    outcome: RetrievalOutcome
    query: str | None
    county_context: str | None
    county_source: ContextSource | None
    candidates: tuple[Candidate, ...]


def retrieve(
    interpretation: Interpretation,
    gazetteer: Gazetteer,
    *,
    supplied_county: str | None = None,
    state: str | None = "Colorado",
    limit: int = 5,
) -> RetrievalResult:
    county, source = _county_context(interpretation, supplied_county)
    feature = interpretation.reference_feature
    if feature is None:
        return RetrievalResult(
            RetrievalOutcome.NO_REFERENCE_FEATURE, None, county, source, candidates=()
        )
    candidates = gazetteer.search(
        feature.name,
        state=state,
        county=county,
        feature_type=feature.feature_type,
        limit=limit,
    )
    outcome = (
        RetrievalOutcome.CANDIDATES_FOUND
        if candidates
        else RetrievalOutcome.FEATURE_ABSENT_FROM_INDEX
    )
    return RetrievalResult(outcome, feature.name, county, source, tuple(candidates))


def _county_context(
    interpretation: Interpretation, supplied_county: str | None
) -> tuple[str | None, ContextSource | None]:
    if supplied_county and supplied_county.strip():
        return supplied_county.strip(), ContextSource.SUPPLIED
    for admin in interpretation.admin_mentions:
        if admin.level is AdminLevel.COUNTY:
            return admin.span.text, ContextSource.TEXT
    return None, None
