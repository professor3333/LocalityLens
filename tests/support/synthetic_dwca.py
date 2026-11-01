"""SYNTHETIC Darwin Core Archives shaped like a GBIF download. Records are invented."""

from __future__ import annotations

import zipfile
from pathlib import Path

from localitylens.data.manifest import SnapshotFile, SnapshotManifest, sha256_file, write_manifest
from localitylens.ingest.specimens import READ_TERMS

DWC = "http://rs.tdwg.org/dwc/terms/"
GBIF = "http://rs.gbif.org/terms/1.0/"
# Answer-bearing columns are present in the synthetic file, as in the real one.
COLUMNS = ("gbifID", *[t for t in READ_TERMS if t != "gbifID"], "decimalLatitude")


def meta_xml(location: str = "verbatim.txt", columns: tuple[str, ...] = COLUMNS) -> str:
    fields = "\n".join(
        f'    <field index="{i}" term="{GBIF if c == "gbifID" else DWC}{c}"/>'
        for i, c in enumerate(columns)
    )
    return f"""<archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="metadata.xml">
  <core encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\n" fieldsEnclosedBy=""
        ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/Occurrence">
    <files><location>occurrence.txt</location></files>
    <id index="0"/>
    <field index="0" term="{GBIF}gbifID"/>
  </core>
  <extension encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\n" fieldsEnclosedBy=""
        ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/Occurrence">
    <files><location>{location}</location></files>
    <coreid index="0"/>
{fields}
  </extension>
</archive>
"""


def row(gbif_id: int, locality: str, **values: str) -> dict[str, str]:
    base = {c: "" for c in COLUMNS}
    base |= {
        "gbifID": str(gbif_id),
        "occurrenceID": f"urn:synthetic:{gbif_id}",
        "catalogNumber": f"SYN{gbif_id}",
        "country": "United States",
        "stateProvince": "Colorado",
        "county": "Alpha",
        "locality": locality,
        "decimalLatitude": "40.123456",  # answer-bearing; must never be read
    }
    return base | values


def write_archive(
    path: Path,
    rows: list[dict[str, str]],
    *,
    meta: str | None = None,
    header: list[str] | None = None,
    raw_lines: list[str] | None = None,
) -> None:
    lines = ["\t".join(header or COLUMNS)]
    lines += ["\t".join(r[c] for c in COLUMNS) for r in rows]
    lines += raw_lines or []
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("meta.xml", meta or meta_xml())
        zf.writestr("occurrence.txt", "gbifID\n")
        zf.writestr("verbatim.txt", "\n".join(lines) + "\n")


def write_snapshot(directory: Path, rows: list[dict[str, str]]) -> SnapshotManifest:
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / "0000001-synthetic.zip"
    write_archive(archive, rows)
    manifest = SnapshotManifest(
        snapshot_id="gbif-synthetic",
        source="synthetic",
        publisher="synthetic",
        retrieved_at="2026-01-01T00:00:00+00:00",
        licence="CC BY 4.0",
        usage_constraints="test data",
        citation="synthetic",
        files=(
            SnapshotFile(
                name=archive.name,
                url="https://example.org/synthetic.zip",
                sha256=sha256_file(archive),
                size_bytes=archive.stat().st_size,
            ),
        ),
    )
    write_manifest(directory / "manifest.json", manifest)
    return manifest
