"""Typed interpretation of a locality description.

Two layers:

* :class:`ExtractionOutput` is what an extractor (the LLM or the rules baseline) returns. Every
  piece of evidence is an exact *quote* from the normalized locality text. Extractors never
  give character offsets, numbers parsed from text, or coordinates. ``extra="forbid"``
  rejects any field outside the schema, including any attempt to supply latitude/longitude.
* :class:`Interpretation` is produced only by :mod:`localitylens.extract.validate`. Quotes are
  located deterministically, mapped to half-open ``[start, end)`` spans of the *original*
  text, and numbers are parsed by code.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from localitylens.geo.directions import CompassPoint
from localitylens.geo.units import LengthUnit

EXTRACTION_SCHEMA_VERSION = "extraction-1"


class RelationType(StrEnum):
    NAMED_FEATURE = "named_feature"
    DISTANCE_AND_DIRECTION = "distance_and_direction"
    # Recognised so an extractor can name them instead of forcing a supported type.
    # Whether they are supported is decided by policy, not by the extractor.
    DIRECTION_ONLY = "direction_only"
    DISTANCE_ONLY = "distance_only"
    ORTHOGONAL_OFFSETS = "orthogonal_offsets"
    BETWEEN_FEATURES = "between_features"
    ROUTE_RELATIVE = "route_relative"
    ITINERARY = "itinerary"
    NO_LOCALITY = "no_locality"
    OTHER = "other"


class FeatureType(StrEnum):
    SUMMIT = "summit"
    RIDGE = "ridge"
    RANGE = "range"
    GAP = "gap"
    LAKE = "lake"
    RESERVOIR = "reservoir"
    STREAM = "stream"
    SPRING = "spring"
    VALLEY = "valley"
    BASIN = "basin"
    FLAT = "flat"
    PARK = "park"
    POPULATED_PLACE = "populated_place"
    LOCALE = "locale"
    TRAIL = "trail"
    ROAD = "road"
    RAILROAD = "railroad"
    MINE = "mine"
    OTHER = "other"


class AdminLevel(StrEnum):
    COUNTRY = "country"
    STATE = "state"
    COUNTY = "county"


class QualifierKind(StrEnum):
    APPROXIMATE = "approximate"  # "about", "ca.", "approx."
    NEAR = "near"  # "near", "nr."
    VICINITY = "vicinity"  # "vicinity of", "vic."
    QUESTIONED = "questioned"  # "?" attached to a name or distance


class MissingKind(StrEnum):
    REFERENCE_FEATURE = "reference_feature"
    DISTANCE = "distance"
    DISTANCE_UNIT = "distance_unit"
    DIRECTION = "direction"
    ROUTE_GEOMETRY = "route_geometry"
    OTHER = "other"


_STRICT = ConfigDict(extra="forbid", frozen=True)
_QUOTE = Field(min_length=1, max_length=500)


# --------------------------------------------------------------------------- extractor output


class FeatureMentionOut(BaseModel):
    model_config = _STRICT
    name_quote: str = _QUOTE
    feature_type: FeatureType | None = None
    feature_type_quote: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def _type_needs_quote(self) -> FeatureMentionOut:
        if (self.feature_type is None) != (self.feature_type_quote is None):
            raise ValueError("feature_type and feature_type_quote must be given together")
        return self


class DistanceOut(BaseModel):
    model_config = _STRICT
    value_quote: str = _QUOTE
    unit: LengthUnit | None = None
    unit_quote: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def _unit_needs_quote(self) -> DistanceOut:
        if (self.unit is None) != (self.unit_quote is None):
            raise ValueError("unit and unit_quote must be given together")
        return self


class DirectionOut(BaseModel):
    model_config = _STRICT
    point: CompassPoint
    quote: str = _QUOTE


class AdminMentionOut(BaseModel):
    model_config = _STRICT
    level: AdminLevel
    quote: str = _QUOTE


class QualifierOut(BaseModel):
    model_config = _STRICT
    kind: QualifierKind
    quote: str = _QUOTE


class ExtractionOutput(BaseModel):
    model_config = _STRICT
    relation: RelationType
    relation_quote: str | None = Field(default=None, min_length=1, max_length=500)
    reference_feature: FeatureMentionOut | None = None
    distance: DistanceOut | None = None
    direction: DirectionOut | None = None
    admin_mentions: list[AdminMentionOut] = Field(default_factory=list, max_length=6)
    qualifiers: list[QualifierOut] = Field(default_factory=list, max_length=6)
    missing: list[MissingKind] = Field(default_factory=list, max_length=6)
    open_questions: list[str] = Field(default_factory=list, max_length=3)


# --------------------------------------------------------------------- validated interpretation


class Span(BaseModel):
    """Half-open ``[start, end)`` range of the ORIGINAL locality text, plus its surface text."""

    model_config = _STRICT
    start: int = Field(ge=0)
    end: int
    text: str

    @model_validator(mode="after")
    def _ordered(self) -> Span:
        if self.end <= self.start:
            raise ValueError("span end must be greater than start")
        if len(self.text) != self.end - self.start:
            raise ValueError("span text length must equal end - start")
        return self


class ParsedQuantity(BaseModel):
    """A number parsed by code from its quote, keeping how precisely it was written."""

    model_config = _STRICT
    value: float = Field(gt=0)
    decimal_places: int = Field(ge=0)
    fraction_denominator: int | None = Field(default=None, ge=2)


class ResolvedFeature(BaseModel):
    model_config = _STRICT
    name: str
    span: Span
    feature_type: FeatureType | None
    feature_type_span: Span | None


class ResolvedDistance(BaseModel):
    model_config = _STRICT
    quantity: ParsedQuantity
    value_span: Span
    unit: LengthUnit | None
    unit_span: Span | None


class ResolvedDirection(BaseModel):
    model_config = _STRICT
    point: CompassPoint
    span: Span


class ResolvedAdmin(BaseModel):
    model_config = _STRICT
    level: AdminLevel
    span: Span


class ResolvedQualifier(BaseModel):
    model_config = _STRICT
    kind: QualifierKind
    span: Span


class Interpretation(BaseModel):
    model_config = _STRICT
    schema_version: str = EXTRACTION_SCHEMA_VERSION
    normalization_version: str
    relation: RelationType
    relation_span: Span | None
    reference_feature: ResolvedFeature | None
    distance: ResolvedDistance | None
    direction: ResolvedDirection | None
    admin_mentions: tuple[ResolvedAdmin, ...]
    qualifiers: tuple[ResolvedQualifier, ...]
    missing: tuple[MissingKind, ...]
    open_questions: tuple[str, ...]
