"""A minimal, read-only ESRI shapefile reader for polygon layers, straight from the zip.

Enough for the Census TIGER/Line place layer (shape type 5, polygons) and its attribute table,
without a GIS dependency. It reads members of the archive in memory and never extracts files.
Format: ESRI Shapefile Technical Description (1998); dBASE III attribute table.
"""

from __future__ import annotations

import struct
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

POLYGON: Final = 5
_NULL: Final = 0


class ShapefileError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PolygonRecord:
    attributes: dict[str, str]
    rings: tuple[tuple[tuple[float, float], ...], ...]  # (x, y) = (longitude, latitude)


def _member(zf: zipfile.ZipFile, suffix: str) -> bytes:
    names = [n for n in zf.namelist() if n.lower().endswith(suffix) and "/" not in n]
    if len(names) != 1:
        raise ShapefileError(f"expected one *{suffix} at the archive root, found {names}")
    return zf.read(names[0])


def _dbf(data: bytes, encoding: str) -> list[dict[str, str]]:
    if len(data) < 32:
        raise ShapefileError("attribute table too short")
    count, header_len, record_len = struct.unpack("<IHH", data[4:12])
    fields: list[tuple[str, int]] = []
    pos = 32
    while True:
        if pos >= min(header_len, len(data)):
            raise ShapefileError("attribute table header has no terminator")
        if data[pos] == 0x0D:
            break
        if pos + 32 > len(data):
            raise ShapefileError("attribute table header is truncated")
        name = data[pos : pos + 11].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        fields.append((name, data[pos + 16]))
        pos += 32
    if sum(length for _, length in fields) + 1 != record_len:
        raise ShapefileError("attribute record length does not match its fields")
    rows: list[dict[str, str]] = []
    for i in range(count):
        start = header_len + i * record_len
        record = data[start : start + record_len]
        if len(record) != record_len:
            raise ShapefileError("attribute table is truncated")
        if record[:1] == b"*":
            rows.append({})  # deleted record: keeps positions aligned with the shapes
            continue
        values: dict[str, str] = {}
        offset = 1
        for name, length in fields:
            values[name] = record[offset : offset + length].decode(encoding).strip()
            offset += length
        rows.append(values)
    return rows


def _shapes(data: bytes) -> Iterator[tuple[tuple[tuple[float, float], ...], ...] | None]:
    if len(data) < 100 or struct.unpack(">I", data[:4])[0] != 9994:
        raise ShapefileError("not a shapefile (bad file code)")
    if struct.unpack("<I", data[32:36])[0] != POLYGON:
        raise ShapefileError("only polygon shapefiles are supported")
    pos = 100
    while pos < len(data):
        _number, words = struct.unpack(">II", data[pos : pos + 8])
        content = data[pos + 8 : pos + 8 + 2 * words]
        if len(content) != 2 * words:
            raise ShapefileError("shape record is truncated")
        pos += 8 + 2 * words
        kind = struct.unpack("<I", content[:4])[0]
        if kind == _NULL:
            yield None
            continue
        if kind != POLYGON:
            raise ShapefileError(f"unexpected shape type {kind}")
        n_parts, n_points = struct.unpack("<II", content[36:44])
        parts = struct.unpack(f"<{n_parts}I", content[44 : 44 + 4 * n_parts])
        start = 44 + 4 * n_parts
        flat = struct.unpack(f"<{2 * n_points}d", content[start : start + 16 * n_points])
        points = list(zip(flat[0::2], flat[1::2], strict=True))
        bounds = [*parts, n_points]
        yield tuple(tuple(points[bounds[i] : bounds[i + 1]]) for i in range(n_parts))


def read_polygons(archive: Path, encoding: str | None = None) -> Iterator[PolygonRecord]:
    """Each polygon of the shapefile inside ``archive`` with its attributes, in file order."""
    with zipfile.ZipFile(archive) as zf:
        shp, dbf = _member(zf, ".shp"), _member(zf, ".dbf")
        if encoding is None:
            try:
                encoding = _member(zf, ".cpg").decode("ascii").strip() or "utf-8"
            except ShapefileError:
                encoding = "latin-1"
    rows = _dbf(dbf, encoding)
    shapes = list(_shapes(shp))
    if len(shapes) != len(rows):
        raise ShapefileError(f"{len(shapes)} shapes but {len(rows)} attribute records")
    for rings, attrs in zip(shapes, rows, strict=True):
        if rings is not None and attrs:
            yield PolygonRecord(attributes=attrs, rings=rings)
