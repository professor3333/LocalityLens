"""User-supplied CSV records: column mapping onto Darwin Core terms, screening, explicit refusals.

* **Mapping.** A column whose header is a supported Darwin Core term (any case, with or
  without a ``dwc:`` prefix) maps to it; ``mapping`` overrides or adds ``column → term``.
  Required: an identifier (``occurrenceID``, ``catalogNumber`` or ``gbifID``), ``locality``
  and/or ``verbatimLocality``, ``stateProvince``, ``county``, and ``country`` or
  ``countryCode``. Optional: ``eventDate``, ``recordedBy``, ``recordNumber``,
  ``informationWithheld``, ``dataGeneralizations``. A missing requirement, a duplicate header
  or an unknown term refuses the whole file before any row is read.
* **Answer-bearing columns are never read.** Coordinates, uncertainty, georeference fields and
  the like are listed as ignored; their values never reach a record, a store or a model.
* **Every row is accepted or refused with a reason, never dropped:** no identifier, a repeated
  identifier, no locality text, text longer than :data:`MAX_LOCALITY_CHARS` (refused, never
  truncated), or a screening exclusion (outside the scope, sensitive: ``informationWithheld`` /
  ``dataGeneralizations`` present, placeholder text).
* **The original text is kept.** ``verbatimLocality`` (the label as written) is used when it is
  present, otherwise ``locality``; the string is stored unchanged.
* **Provenance.** The import's snapshot ID is ``csv-`` plus the first 12 hex digits of the file's
  SHA-256, so every record points back to the exact file it came from.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from localitylens.ingest.specimens import (
    ANSWER_BEARING_TERMS,
    SCREEN_VERSION,
    SpecimenRecord,
    group_key,
    screen,
)

CSV_IMPORT_VERSION: Final = "csv-1"
MAX_LOCALITY_CHARS: Final = 4000  # far above any label; longer text is refused, not truncated
IDENTIFIER_TERMS: Final = ("gbifID", "occurrenceID", "catalogNumber")
SUPPORTED_TERMS: Final = (
    "gbifID", "occurrenceID", "catalogNumber", "locality", "verbatimLocality",
    "stateProvince", "county", "country", "countryCode", "eventDate", "recordedBy",
    "recordNumber", "informationWithheld", "dataGeneralizations",
)  # fmt: skip
_BY_LOWER: Final = {t.lower(): t for t in SUPPORTED_TERMS}
_ANSWER_LOWER: Final = {t.lower() for t in ANSWER_BEARING_TERMS}
_SAFE_ID: Final = re.compile(r"^[A-Za-z0-9._\-]{1,64}$")


class MappingError(ValueError):
    """The file cannot be imported as mapped (nothing is read)."""


@dataclass(frozen=True, slots=True)
class Rejected:
    row: int  # 1-based data row (the header is row 0)
    identifier: str
    reason: str


@dataclass(slots=True)
class CsvImport:
    snapshot_id: str
    sha256: str
    mapping: dict[str, str]  # column → term actually used
    ignored_answer_columns: list[str]
    unmapped_columns: list[str]
    records: list[tuple[str, SpecimenRecord]] = field(default_factory=list)  # (record ID, record)
    rejected: list[Rejected] = field(default_factory=list)
    rows: int = 0
    locality_source: dict[str, int] = field(default_factory=dict)  # term → rows using it


def _term(header: str) -> str:
    h = header.strip()
    return h[4:] if h.lower().startswith("dwc:") else h


def resolve_mapping(headers: list[str], overrides: dict[str, str] | None = None) -> dict[str, str]:
    """``column → term`` for the supported terms; raises :class:`MappingError` when unusable."""
    stripped = [h.strip() for h in headers]
    dupes = sorted({h for h in stripped if stripped.count(h) > 1})
    if dupes:
        raise MappingError(f"duplicate column names: {', '.join(dupes)}")
    mapping: dict[str, str] = {}
    for h in stripped:
        term = _BY_LOWER.get(_term(h).lower())
        if term is not None:
            mapping[h] = term
    for column, term in (overrides or {}).items():
        if column not in stripped:
            raise MappingError(f"--map names a column that is not in the file: {column!r}")
        canonical = _BY_LOWER.get(_term(term).lower())
        if canonical is None:
            if _term(term).lower() in _ANSWER_LOWER:
                raise MappingError(f"{term!r} is answer-bearing and is never imported")
            raise MappingError(
                f"unsupported term {term!r} (supported: {', '.join(SUPPORTED_TERMS)})"
            )
        mapping[column] = canonical
    terms = list(mapping.values())
    twice = sorted({t for t in terms if terms.count(t) > 1})
    if twice:
        raise MappingError(f"several columns map to {', '.join(twice)}")
    have = set(terms)
    missing = []
    if not have & set(IDENTIFIER_TERMS):
        missing.append("an identifier (occurrenceID, catalogNumber or gbifID)")
    if not have & {"locality", "verbatimLocality"}:
        missing.append("locality or verbatimLocality")
    for term in ("stateProvince", "county"):
        if term not in have:
            missing.append(term)
    if not have & {"country", "countryCode"}:
        missing.append("country or countryCode")
    if missing:
        raise MappingError("missing required columns: " + "; ".join(missing))
    return mapping


def record_id(gbif_id: str, identifier: str) -> str:
    """``gbif:<id>`` for a numeric GBIF ID, else ``occ:<identifier>`` (hashed when it holds
    characters unsafe in a URL path)."""
    if gbif_id.strip().isdigit():
        return f"gbif:{gbif_id.strip()}"
    ident = identifier.strip()
    if _SAFE_ID.fullmatch(ident):
        return f"occ:{ident}"
    return "occ:h" + hashlib.sha256(ident.encode("utf-8")).hexdigest()[:16]


class _Row(dict[str, str]):
    """A row's mapped values; an unmapped term reads as empty."""

    def __missing__(self, key: str) -> str:
        return ""


def read_csv(
    path: Path, mapping: dict[str, str] | None = None, *, encoding: str = "utf-8-sig"
) -> CsvImport:
    """Map, screen and validate a CSV file. Raises :class:`MappingError` for an unusable file."""
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError as exc:
        raise MappingError(
            f"not valid {encoding} at byte {exc.start}; re-save as UTF-8 or pass --encoding"
        ) from exc
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        headers = next(reader)
    except StopIteration as exc:
        raise MappingError("the file is empty") from exc
    used = resolve_mapping(headers, mapping)
    stripped = [h.strip() for h in headers]
    ignored = [h for h in stripped if h not in used and _term(h).lower() in _ANSWER_LOWER]
    unmapped = [h for h in stripped if h not in used and h not in ignored]
    out = CsvImport(snapshot_id=f"csv-{sha[:12]}", sha256=sha, mapping=used,
                    ignored_answer_columns=ignored, unmapped_columns=unmapped)  # fmt: skip
    index = {term: stripped.index(col) for col, term in used.items()}
    seen: set[str] = set()
    for number, cells in enumerate(reader, start=1):
        if not any(c.strip() for c in cells):
            continue  # a blank line is not a record
        out.rows += 1
        if len(cells) != len(headers):
            reason = f"has {len(cells)} fields, expected {len(headers)}"
            out.rejected.append(Rejected(number, "", reason))
            continue
        row = _Row({t: cells[i] for t, i in index.items()})
        identifier = next((row[t].strip() for t in IDENTIFIER_TERMS if row[t].strip()), "")
        if not identifier:
            out.rejected.append(Rejected(number, "", "no identifier"))
            continue
        rid = record_id(row["gbifID"], row["occurrenceID"].strip()
                        or row["catalogNumber"].strip() or identifier)  # fmt: skip
        if rid in seen:
            out.rejected.append(Rejected(number, identifier, "repeated identifier in this file"))
            continue
        source = "verbatimLocality" if row["verbatimLocality"].strip() else "locality"
        locality = row[source]
        if len(locality) > MAX_LOCALITY_CHARS:
            reason = f"locality longer than {MAX_LOCALITY_CHARS} characters"
            out.rejected.append(Rejected(number, identifier, reason))
            continue
        excluded = screen({
            "stateProvince": row["stateProvince"], "country": row["country"],
            "countryCode": row["countryCode"], "informationWithheld": row["informationWithheld"],
            "dataGeneralizations": row["dataGeneralizations"], "locality": locality,
        })  # fmt: skip
        if excluded is not None:
            out.rejected.append(Rejected(number, identifier, f"screened out: {excluded.value}"))
            continue
        seen.add(rid)
        out.locality_source[source] = out.locality_source.get(source, 0) + 1
        record = SpecimenRecord(
            gbif_id=row["gbifID"].strip(), occurrence_id=row["occurrenceID"].strip(),
            catalog_number=row["catalogNumber"].strip(), locality=locality,
            state_province=row["stateProvince"].strip(), county=row["county"].strip(),
            country=row["country"].strip() or row["countryCode"].strip(),
            recorded_by=row["recordedBy"].strip(), record_number=row["recordNumber"].strip(),
            event_date=row["eventDate"].strip(), group_key=group_key(locality, row["county"]),
        )  # fmt: skip
        out.records.append((rid, record))
    return out


def write_rejects(result: CsvImport, path: Path) -> None:
    """The refusal report: one row per refused record, with its reason."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["row", "identifier", "reason", "source_sha256", "screen_version"])
        for r in result.rejected:
            writer.writerow([r.row, r.identifier, r.reason, result.sha256, SCREEN_VERSION])
