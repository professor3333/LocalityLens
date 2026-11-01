"""Snapshot manifests: what was downloaded, from where, when, under which terms, and its hash.

Raw files under ``data/raw/`` are write-once. Everything derived from them checks the
manifest's checksums first, so an altered or partial file can never feed the pipeline silently.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

MANIFEST_VERSION = "2"  # 2: optional doi, record_count, query (GBIF downloads)
_CHUNK = 1 << 20


class SnapshotFile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    url: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(ge=0)
    publication_date: str | None = None
    server_last_modified: str | None = None


class SnapshotManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    manifest_version: str = MANIFEST_VERSION
    snapshot_id: str
    source: str
    publisher: str
    retrieved_at: str
    licence: str
    usage_constraints: str
    citation: str
    horizontal_datum: str | None = None
    ellipsoid: str | None = None
    doi: str | None = None  # GBIF download DOI, the citable identifier of the exact records
    record_count: int | None = None
    query: str | None = None  # the download filter as JSON, so the request can be reissued
    files: tuple[SnapshotFile, ...]
    notes: tuple[str, ...] = ()

    def file(self, name: str) -> SnapshotFile:
        for f in self.files:
            if f.name == name:
                return f
        raise KeyError(name)

    def sha256(self) -> str:
        """Hash of the manifest itself. Used as provenance for anything built from it."""
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


class ChecksumMismatchError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def verify_snapshot(directory: Path, manifest: SnapshotManifest) -> None:
    """Raise unless every manifest file exists in ``directory`` with the recorded hash and size."""
    for f in manifest.files:
        path = directory / f.name
        if not path.is_file():
            raise ChecksumMismatchError(f"{path} is missing")
        if path.stat().st_size != f.size_bytes:
            raise ChecksumMismatchError(f"{path} size differs from manifest")
        if (actual := sha256_file(path)) != f.sha256:
            raise ChecksumMismatchError(f"{path} sha256 {actual} != manifest {f.sha256}")


def load_manifest(path: Path) -> SnapshotManifest:
    return SnapshotManifest.model_validate_json(path.read_text(encoding="utf-8"))


def write_manifest(path: Path, manifest: SnapshotManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
