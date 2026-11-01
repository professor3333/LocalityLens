"""Parse GNIS pipe-delimited text files straight from their zip archives.

Format facts verified against the 2026-09-29 Colorado snapshot: UTF-8 with BOM, CRLF line
endings, '|' delimiter, a header row; decimal coordinates in NAD83; missing *source*
coordinates written as ``0.0`` (parsed here as None, never as a real position).
"""

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from localitylens.extract.schema import FeatureType
from localitylens.gazetteer.keys import is_historical_name

DOMESTIC_COLUMNS: Final = (
    "feature_id",
    "feature_name",
    "feature_class",
    "state_name",
    "state_numeric",
    "county_name",
    "county_numeric",
    "map_name",
    "date_created",
    "date_edited",
    "bgn_type",
    "bgn_authority",
    "bgn_date",
    "prim_lat_dms",
    "prim_long_dms",
    "prim_lat_dec",
    "prim_long_dec",
    "source_lat_dms",
    "source_long_dms",
    "source_lat_dec",
    "source_long_dec",
)
ALL_NAMES_REQUIRED: Final = (
    "feature_id",
    "feature_name",
    "feature_name_official",
    "publicationdate",
    "citation",
)

# GNIS feature class -> the coarse type an extractor may report. Classes not listed map to None.
CLASS_TO_TYPE: Final[dict[str, FeatureType]] = {
    "Summit": FeatureType.SUMMIT,
    "Ridge": FeatureType.RIDGE,
    "Range": FeatureType.RANGE,
    "Gap": FeatureType.GAP,
    "Lake": FeatureType.LAKE,
    "Reservoir": FeatureType.RESERVOIR,
    "Stream": FeatureType.STREAM,
    "Spring": FeatureType.SPRING,
    "Valley": FeatureType.VALLEY,
    "Basin": FeatureType.BASIN,
    "Flat": FeatureType.FLAT,
    "Park": FeatureType.PARK,
    "Populated Place": FeatureType.POPULATED_PLACE,
    "Locale": FeatureType.LOCALE,
    "Trail": FeatureType.TRAIL,
    "Mine": FeatureType.MINE,
}

# Which GNIS classes count as consistent with a type stated on a label. Lakes and reservoirs
# are interchangeable on old labels; Colorado "parks" are mountain basins/flats.
COMPATIBLE_CLASSES: Final[dict[FeatureType, frozenset[str]]] = {
    FeatureType.SUMMIT: frozenset({"Summit"}),
    FeatureType.RIDGE: frozenset({"Ridge"}),
    FeatureType.RANGE: frozenset({"Range"}),
    FeatureType.GAP: frozenset({"Gap"}),
    FeatureType.LAKE: frozenset({"Lake", "Reservoir"}),
    FeatureType.RESERVOIR: frozenset({"Reservoir", "Lake"}),
    FeatureType.STREAM: frozenset({"Stream"}),
    FeatureType.SPRING: frozenset({"Spring"}),
    FeatureType.VALLEY: frozenset({"Valley"}),
    FeatureType.BASIN: frozenset({"Basin"}),
    FeatureType.FLAT: frozenset({"Flat"}),
    FeatureType.PARK: frozenset({"Park", "Flat", "Basin"}),
    FeatureType.POPULATED_PLACE: frozenset({"Populated Place", "Civil", "Census"}),
    FeatureType.LOCALE: frozenset({"Locale"}),
    FeatureType.TRAIL: frozenset({"Trail"}),
    FeatureType.MINE: frozenset({"Mine"}),
}


class GnisFormatError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class GnisFeature:
    feature_id: int
    name: str
    feature_class: str
    state_name: str
    state_fips: str
    county_name: str
    county_fips: str
    map_name: str
    prim_lat: float
    prim_lon: float
    source_lat: float | None
    source_lon: float | None
    bgn_type: str
    date_edited: str
    historical: bool


@dataclass(frozen=True, slots=True)
class GnisVariant:
    feature_id: int
    name: str
    citation: str
    # Publication date of the source that used this name (MM/DD/YYYY as in GNIS), or "".
    source_date: str


def _optional_coord(lat: str, lon: str) -> tuple[float | None, float | None]:
    if not lat.strip() or not lon.strip():
        return None, None
    flat, flon = float(lat), float(lon)
    if flat == 0.0 and flon == 0.0:
        return None, None  # GNIS encodes "no source coordinate" as 0.0
    return flat, flon


def _open_member(zf: zipfile.ZipFile, suffix: str) -> io.TextIOWrapper:
    members = [n for n in zf.namelist() if n.endswith(suffix)]
    if len(members) != 1:
        raise GnisFormatError(f"expected one member ending in {suffix!r}, found {members}")
    return io.TextIOWrapper(zf.open(members[0]), encoding="utf-8-sig", newline="")


def read_domestic(zip_path: Path) -> Iterator[GnisFeature]:
    with zipfile.ZipFile(zip_path) as zf, _open_member(zf, ".txt") as fh:
        reader = csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE)
        if tuple(reader.fieldnames or ()) != DOMESTIC_COLUMNS:
            raise GnisFormatError(f"unexpected Domestic Names header: {reader.fieldnames}")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise GnisFormatError(f"row {reader.line_num} has the wrong number of fields")
            prim_lat, prim_lon = _optional_coord(row["prim_lat_dec"], row["prim_long_dec"])
            if prim_lat is None or prim_lon is None:
                raise GnisFormatError(f"feature {row['feature_id']} has no primary coordinate")
            src_lat, src_lon = _optional_coord(row["source_lat_dec"], row["source_long_dec"])
            yield GnisFeature(
                feature_id=int(row["feature_id"]),
                name=row["feature_name"],
                feature_class=row["feature_class"],
                state_name=row["state_name"],
                state_fips=row["state_numeric"],
                county_name=row["county_name"],
                county_fips=row["county_numeric"],
                map_name=row["map_name"],
                prim_lat=prim_lat,
                prim_lon=prim_lon,
                source_lat=src_lat,
                source_lon=src_lon,
                bgn_type=row["bgn_type"],
                date_edited=row["date_edited"],
                historical=is_historical_name(row["feature_name"]),
            )


def read_variants(zip_path: Path, feature_ids: set[int]) -> Iterator[GnisVariant]:
    """Variant (non-official) names for the given features, streamed from the national file."""
    wanted = {str(i) for i in feature_ids}
    with zipfile.ZipFile(zip_path) as zf, _open_member(zf, ".txt") as fh:
        header = fh.readline().rstrip("\r\n").split("|")
        missing = [c for c in ALL_NAMES_REQUIRED if c not in header]
        if missing:
            raise GnisFormatError(f"All Names header lacks {missing}")
        i_id, i_name = header.index("feature_id"), header.index("feature_name")
        i_off, i_cit = header.index("feature_name_official"), header.index("citation")
        i_date = header.index("publicationdate")
        for line in fh:
            fid, _, _ = line.partition("|")
            if fid not in wanted:
                continue
            parts = line.rstrip("\r\n").split("|")
            if len(parts) != len(header):
                raise GnisFormatError(f"All Names row for {fid} has {len(parts)} fields")
            if parts[i_off] != "Variant":
                continue
            yield GnisVariant(
                feature_id=int(parts[i_id]),
                name=parts[i_name],
                citation=parts[i_cit].strip(),
                source_date=parts[i_date].strip(),
            )
