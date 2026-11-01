"""Read Darwin Core Archive data files straight from the zip, never extracting it.

``meta.xml`` is the source of truth for each file's layout (delimiter, header lines, which
column holds which term). The header line must agree with it, and every row must have exactly
the declared number of fields; a mismatch raises instead of silently shifting columns.
Spec: https://dwc.tdwg.org/text/
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Collection, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

_NS: Final = "{http://rs.tdwg.org/dwc/text/}"
_ESCAPES: Final[dict[str, str]] = {"\\t": "\t", "\\n": "\n", "\\r": "\r", ",": ","}


class ArchiveFormatError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FileLayout:
    location: str
    encoding: str
    delimiter: str
    header_lines: int
    enclosed_by: str
    columns: tuple[str, ...]  # term local name per column index ("gbifID", "locality", ...)


def _local(term: str) -> str:
    return term.rstrip("/").rsplit("/", 1)[-1]


def read_layouts(zf: zipfile.ZipFile) -> dict[str, FileLayout]:
    raw = zf.read("meta.xml")
    if b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
        raise ArchiveFormatError("meta.xml declares a DTD or entities; refusing to parse it")
    root = ET.fromstring(raw)
    layouts: dict[str, FileLayout] = {}
    for element in [*root.iter(f"{_NS}core"), *root.iter(f"{_NS}extension")]:
        location = element.findtext(f"{_NS}files/{_NS}location")
        if not location:
            raise ArchiveFormatError("meta.xml entry without a file location")
        by_index: dict[int, str] = {}
        for field in element.iter(f"{_NS}field"):
            index, term = field.get("index"), field.get("term")
            if index is None or term is None:
                continue  # constant-valued field, not a column
            by_index[int(index)] = _local(term)
        for tag in ("id", "coreid"):
            id_element = element.find(f"{_NS}{tag}")
            if id_element is not None and (idx := id_element.get("index")) is not None:
                by_index.setdefault(int(idx), "id")
        if sorted(by_index) != list(range(len(by_index))):
            raise ArchiveFormatError(f"{location}: column indexes are not contiguous")
        delimiter = element.get("fieldsTerminatedBy", ",")
        layouts[location] = FileLayout(
            location=location,
            encoding=element.get("encoding", "UTF-8"),
            delimiter=_ESCAPES.get(delimiter, delimiter),
            header_lines=int(element.get("ignoreHeaderLines", "0")),
            enclosed_by=element.get("fieldsEnclosedBy", ""),
            columns=tuple(by_index[i] for i in range(len(by_index))),
        )
    return layouts


def iter_rows(
    archive: Path, location: str, terms: Collection[str]
) -> Iterator[tuple[int, dict[str, str]]]:
    """Yield ``(line_number, {term: value})`` for the requested terms of one data file.

    Only unenclosed, delimiter-separated files are supported (what GBIF produces); anything
    else raises rather than being mis-parsed.
    """
    with zipfile.ZipFile(archive) as zf:
        layouts = read_layouts(zf)
        if location not in layouts:
            raise ArchiveFormatError(f"{location} is not described in meta.xml")
        layout = layouts[location]
        if layout.enclosed_by:
            raise ArchiveFormatError(f"{location}: quoted fields are not supported")
        missing = [t for t in terms if t not in layout.columns]
        if missing:
            raise ArchiveFormatError(f"{location} lacks columns {missing}")
        wanted = [(t, layout.columns.index(t)) for t in terms]
        width = len(layout.columns)
        with zf.open(location) as fh:
            text = io.TextIOWrapper(fh, encoding=layout.encoding, newline="")
            for line_no, line in enumerate(text, start=1):
                parts = line.rstrip("\r\n").split(layout.delimiter)
                if line_no <= layout.header_lines:
                    named = [c for c in layout.columns if c != "id"]
                    header = [p for p, c in zip(parts, layout.columns, strict=False) if c != "id"]
                    if len(parts) != width or header != named:
                        raise ArchiveFormatError(f"{location}: header disagrees with meta.xml")
                    continue
                if len(parts) != width:
                    raise ArchiveFormatError(
                        f"{location} line {line_no}: {len(parts)} fields, expected {width}"
                    )
                yield line_no, {t: parts[i] for t, i in wanted}
