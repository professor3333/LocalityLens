"""Synthetic GNIS snapshot builders shared by tests."""

import zipfile
from collections.abc import Sequence
from pathlib import Path

from localitylens.data.manifest import SnapshotFile, SnapshotManifest, sha256_file

# --------------------------------------------------------------------------------------------
# Synthetic GNIS snapshot. Names and coordinates are INVENTED for tests; only the file format
# (BOM, CRLF, '|' delimiter, column order, 0.0 for missing source coords) mirrors real GNIS.
# --------------------------------------------------------------------------------------------

DOMESTIC_HEADER = (
    "feature_id|feature_name|feature_class|state_name|state_numeric|county_name|county_numeric|"
    "map_name|date_created|date_edited|bgn_type|bgn_authority|bgn_date|prim_lat_dms|"
    "prim_long_dms|prim_lat_dec|prim_long_dec|source_lat_dms|source_long_dms|source_lat_dec|"
    "source_long_dec"
)
ALL_NAMES_HEADER = (
    "feature_id|feature_name|feature_name_official|sourcecitationabbreviation|sourceoriginator|"
    "sourcereftype|title|edition|sourceurl|publicationdate|seriesname|seriesissue|ending_date|"
    "date_created|citation"
)

# (id, name, class, state, county, prim_lat, prim_lon, src_lat, src_lon)
SYNTH_FEATURES = [
    (1, "Testa Peak", "Summit", "Colorado", "Alpha", "40.1", "-105.1", "0.0", "0.0"),
    (2, "Testa Peak", "Summit", "Colorado", "Beta", "39.1", "-106.1", "0.0", "0.0"),
    (3, "Testa Lake", "Reservoir", "Colorado", "Alpha", "40.2", "-105.2", "0.0", "0.0"),
    (4, "Old Camp (historical)", "Populated Place", "Colorado", "Beta", "39.2", "-106.2", "", ""),
    (5, "Border Wash", "Stream", "Utah", "Zeta", "38.5", "-109.1", "38.7", "-109.3"),
    (6, "Newname Mountain", "Summit", "Colorado", "Gamma", "39.5", "-105.6", "0.0", "0.0"),
    (7, "Oldname Peak", "Summit", "Colorado", "Delta", "39.3", "-106.0", "0.0", "0.0"),
    (8, "Upper Vela Lake", "Lake", "Colorado", "Alpha", "40.3", "-105.3", "0.0", "0.0"),
    (9, "Vela Lake", "Lake", "Colorado", "Alpha", "40.31", "-105.31", "0.0", "0.0"),
]

# (id, name, official/variant, publicationdate, citation)
SYNTH_ALL_NAMES = [
    (6, "Newname Mountain", "Official", "", "Board decision"),
    (6, "Oldname Peak", "Variant", "12/31/1890", "Synthetic survey map 1890"),
    (6, "Newname  Mountain", "Variant", "", "duplicate of official after keying"),
    (99, "Elsewhere Peak", "Variant", "", "feature not in the Colorado file"),
]


def _domestic_row(f: tuple[object, ...]) -> str:
    fid, name, cls, state, county, plat, plon, slat, slon = f
    return (
        f"{fid}|{name}|{cls}|{state}|08|{county}|001|Synthetic Quad|01/01/1980||||||"
        f"|{plat}|{plon}|||{slat}|{slon}"
    )


def _all_names_row(v: tuple[object, ...]) -> str:
    fid, name, official, pubdate, citation = v
    return f"{fid}|{name}|{official}|||Map||||{pubdate}|||||{citation}"


def write_gnis_zips(
    directory: Path,
    features: Sequence[tuple[object, ...]] = SYNTH_FEATURES,
    names: Sequence[tuple[object, ...]] = SYNTH_ALL_NAMES,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    domestic = "﻿" + "\r\n".join([DOMESTIC_HEADER, *map(_domestic_row, features)]) + "\r\n"
    all_names = "﻿" + "\r\n".join([ALL_NAMES_HEADER, *map(_all_names_row, names)]) + "\r\n"
    xml = "<metadata><pubdate>20260101</pubdate></metadata>"
    with zipfile.ZipFile(directory / "DomesticNames_CO_Text.zip", "w") as zf:
        zf.writestr("Text/DomesticNames_CO.txt", domestic.encode())
        zf.writestr("DomesticNames_CO_Text.xml", xml)
    with zipfile.ZipFile(directory / "AllNames_National_Text.zip", "w") as zf:
        zf.writestr("Text/AllNames_National.txt", all_names.encode())
        zf.writestr("AllNames_National_Text.xml", xml)


def synthetic_manifest(directory: Path) -> SnapshotManifest:
    files = tuple(
        SnapshotFile(
            name=name,
            url=f"https://example.invalid/{name}",
            sha256=sha256_file(directory / name),
            size_bytes=(directory / name).stat().st_size,
        )
        for name in ("DomesticNames_CO_Text.zip", "AllNames_National_Text.zip")
    )
    return SnapshotManifest(
        snapshot_id="gnis-synthetic",
        source="synthetic test fixture",
        publisher="tests",
        retrieved_at="2026-01-01T00:00:00+00:00",
        licence="test",
        usage_constraints="test",
        citation="test",
        files=files,
    )
