"""Request, wait for, and store a GBIF occurrence download (Darwin Core Archive) with its DOI.

GBIF downloads are asynchronous: a request returns a key, the key's status moves through
PREPARING and RUNNING to SUCCEEDED, and only then do a DOI and a download link exist.
API: https://techdocs.gbif.org/en/data-use/api-downloads

The whole CU Herbarium dataset is requested. Filtering to Colorado and to meaningful locality
text happens locally, so that every exclusion has a recorded reason; a coordinate-based GBIF
filter would silently drop exactly the records that have no coordinates yet.

Run during ingestion only; the application never contacts GBIF at runtime.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import BaseModel, ConfigDict, SecretStr

from localitylens.data.manifest import (
    ChecksumMismatchError,
    SnapshotFile,
    SnapshotManifest,
    load_manifest,
    sha256_file,
    verify_snapshot,
    write_manifest,
)

API: Final = "https://api.gbif.org/v1"
CU_HERBARIUM_DATASET_KEY: Final = "7c5e863f-3f70-4933-b05d-fc57c66dd3f3"
FORMAT: Final = "DWCA"  # keeps verbatim.txt (original label text) next to the interpreted file
REQUIRED_MEMBERS: Final = ("meta.xml", "occurrence.txt", "verbatim.txt")
STATUS_FILE: Final = "download-status.json"

_PENDING: Final = frozenset({"PREPARING", "RUNNING"})
_LICENCES: Final[dict[str, str]] = {
    "http://creativecommons.org/licenses/by/4.0/legalcode": "CC BY 4.0",
    "http://creativecommons.org/licenses/by-nc/4.0/legalcode": "CC BY-NC 4.0",
    "http://creativecommons.org/publicdomain/zero/1.0/legalcode": "CC0 1.0",
}
_USER_AGENT: Final = "LocalityLens-ingest/0.1 (+https://github.com/professor3333/LocalityLens)"


class GbifDownloadError(RuntimeError):
    pass


class Credentials(BaseModel):
    """GBIF account. ``SecretStr`` keeps the password out of reprs, logs and tracebacks."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    user: str
    password: SecretStr
    email: str | None = None


def _parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values


def read_credentials(env_path: Path | None) -> Credentials:
    """``GBIF_USER``/``GBIF_PWD`` (required) and ``GBIF_EMAIL`` (optional).

    Environment variables win over the ``.env`` file. Error messages name keys, never values.
    """
    file_values = _parse_env(env_path) if env_path is not None and env_path.is_file() else {}

    def get(key: str) -> str | None:
        return os.environ.get(key) or file_values.get(key) or None

    missing = [k for k in ("GBIF_USER", "GBIF_PWD") if not get(k)]
    if missing:
        raise GbifDownloadError(f"missing GBIF credentials: {', '.join(missing)} (set in .env)")
    return Credentials(
        user=_require(get, "GBIF_USER"),
        password=SecretStr(_require(get, "GBIF_PWD")),
        email=get("GBIF_EMAIL"),
    )


def _require(get: Callable[[str], str | None], key: str) -> str:
    value = get(key)
    if value is None:
        raise GbifDownloadError(f"missing GBIF credential {key}")
    return value


def dataset_predicate(dataset_key: str) -> dict[str, str]:
    return {"type": "equals", "key": "DATASET_KEY", "value": dataset_key}


# Fields GBIF adds when it echoes a predicate back, with the default values that leave the
# predicate's meaning unchanged (observed: {"matchCase": false}).
_PREDICATE_DEFAULTS: Final[dict[str, object]] = {"matchCase": False}


def same_predicate(echoed: object, sent: dict[str, str]) -> bool:
    """True when GBIF's echoed predicate means exactly what was sent."""
    if not isinstance(echoed, dict):
        return False
    extra = {k: v for k, v in echoed.items() if k not in sent}
    if any(_PREDICATE_DEFAULTS.get(k, object()) != v for k, v in extra.items()):
        return False
    return all(echoed.get(k) == v for k, v in sent.items())


class Transport(Protocol):
    def post_json(self, url: str, body: dict[str, Any], credentials: Credentials) -> str: ...
    def get_json(self, url: str) -> dict[str, Any]: ...
    def download(self, url: str, dest: Path) -> str | None: ...


class UrllibTransport:
    """Standard-library HTTP. GETs retry with exponential backoff; the POST does not, because a
    retried request could create a second download on the account."""

    def __init__(self, attempts: int = 5, timeout_s: float = 120.0) -> None:
        self.attempts = attempts
        self.timeout_s = timeout_s

    def post_json(self, url: str, body: dict[str, Any], credentials: Credentials) -> str:
        token = base64.b64encode(
            f"{credentials.user}:{credentials.password.get_secret_value()}".encode()
        ).decode()
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {token}",
                "User-Agent": _USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as resp:
                return str(resp.read().decode().strip())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise GbifDownloadError(
                f"download request rejected: HTTP {exc.code} {detail}"
            ) from None

    def _retry[T](self, action: Callable[[], T]) -> T:
        for attempt in range(self.attempts):
            try:
                return action()
            except urllib.error.HTTPError as exc:
                if exc.code < 500 or attempt == self.attempts - 1:
                    raise
            except OSError:
                if attempt == self.attempts - 1:
                    raise
            time.sleep(2**attempt)
        raise AssertionError("unreachable")

    def get_json(self, url: str) -> dict[str, Any]:
        def action() -> dict[str, Any]:
            request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(request, timeout=self.timeout_s) as resp:
                data: dict[str, Any] = json.load(resp)
                return data

        return self._retry(action)

    def download(self, url: str, dest: Path) -> str | None:
        def action() -> str | None:
            request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as resp:
                    with dest.open("wb") as out:
                        shutil.copyfileobj(resp, out, length=1 << 20)
                    last_modified: str | None = resp.headers.get("Last-Modified")
                    return last_modified
            except BaseException:
                dest.unlink(missing_ok=True)
                raise

        return self._retry(action)


def request_download(
    transport: Transport, credentials: Credentials, dataset_key: str = CU_HERBARIUM_DATASET_KEY
) -> str:
    body: dict[str, Any] = {
        "creator": credentials.user,
        "format": FORMAT,
        "predicate": dataset_predicate(dataset_key),
        "sendNotification": credentials.email is not None,
        "notificationAddresses": [credentials.email] if credentials.email else [],
    }
    key = transport.post_json(f"{API}/occurrence/download/request", body, credentials)
    if not key or any(c.isspace() for c in key):
        raise GbifDownloadError(f"unexpected download key {key[:80]!r}")
    return key


def wait_for_download(
    transport: Transport,
    key: str,
    *,
    poll_s: float = 60.0,
    max_wait_s: float = 6 * 3600.0,
    sleep: Callable[[float], None] = time.sleep,
    on_status: Callable[[str], None] = lambda _status: None,
) -> dict[str, Any]:
    """Poll until SUCCEEDED. Any other final status (FAILED, KILLED, CANCELLED, ...) raises."""
    waited = 0.0
    while True:
        status = transport.get_json(f"{API}/occurrence/download/{key}")
        state = str(status.get("status"))
        on_status(state)
        if state == "SUCCEEDED":
            return status
        if state not in _PENDING:
            raise GbifDownloadError(f"download {key} ended with status {state}")
        if waited >= max_wait_s:
            raise GbifDownloadError(
                f"download {key} still {state} after {waited:.0f} s; resume with --key {key}"
            )
        sleep(poll_s)
        waited += poll_s


def _redacted(status: dict[str, Any]) -> dict[str, Any]:
    """The status response without account details (creator, notification addresses)."""
    out = json.loads(json.dumps(status))
    request = out.get("request")
    if isinstance(request, dict):
        request.pop("creator", None)
        request.pop("notificationAddresses", None)
    return dict(out)


def _check_archive(path: Path) -> None:
    """Integrity check of the untrusted zip without extracting it."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            unsafe = [n for n in names if n.startswith("/") or ".." in Path(n).parts]
            if unsafe:
                raise GbifDownloadError(f"archive has unsafe member paths: {unsafe[:3]}")
            missing = [m for m in REQUIRED_MEMBERS if m not in names]
            if missing:
                raise GbifDownloadError(f"archive lacks {', '.join(missing)}")
            if (bad := zf.testzip()) is not None:
                raise GbifDownloadError(f"archive member {bad} fails its CRC check")
    except zipfile.BadZipFile as exc:
        raise GbifDownloadError(f"not a zip archive: {exc}") from None


def build_manifest(
    status: dict[str, Any],
    dataset: dict[str, Any],
    archive: SnapshotFile,
    status_file: SnapshotFile,
    retrieved_at: str,
) -> SnapshotManifest:
    key = str(status["key"])
    doi = str(status["doi"])
    created = str(status["created"])[:10]
    licence_url = str(status.get("license", ""))
    licence = _LICENCES.get(licence_url, licence_url or "unknown")
    title = str(dataset.get("title", "unknown dataset"))
    day = datetime.fromisoformat(created).strftime("%d %B %Y")
    request = status.get("request") or {}
    return SnapshotManifest(
        snapshot_id=f"gbif-cu-{created}",
        source=f"GBIF occurrence download {key} ({request.get('format', FORMAT)})",
        publisher=title,
        retrieved_at=retrieved_at,
        licence=f"{licence} ({licence_url})" if licence != licence_url else licence,
        usage_constraints=(
            "Attribute the publisher and cite the download DOI. Annotations derived from these "
            "records are modifications and are marked as such."
        ),
        citation=f"GBIF.org ({day}) GBIF Occurrence Download https://doi.org/{doi}",
        doi=doi,
        record_count=int(status["totalRecords"]) if "totalRecords" in status else None,
        query=json.dumps(request.get("predicate"), sort_keys=True),
        files=(archive, status_file),
        notes=(
            f"Dataset {dataset.get('key', '')} (dataset DOI {dataset.get('doi', 'unknown')}), "
            "requested whole; Colorado and locality filtering are done locally with reasons.",
            f"{STATUS_FILE} is the GBIF status response with account details removed.",
            f"GBIF may erase the archive file after {str(status.get('eraseAfter', '?'))[:10]}; "
            "the DOI stays resolvable and the query above can be reissued.",
            "Coordinates and georeference fields in the archive are answer-bearing and never "
            "reach a model prompt.",
        ),
    )


def fetch_gbif(
    raw_root: Path,
    manifest_dir: Path,
    credentials: Credentials | None,
    *,
    key: str | None = None,
    dataset_key: str = CU_HERBARIUM_DATASET_KEY,
    transport: Transport | None = None,
    poll_s: float = 60.0,
    max_wait_s: float = 6 * 3600.0,
    sleep: Callable[[float], None] = time.sleep,
    on_status: Callable[[str], None] = lambda _status: None,
) -> tuple[Path, SnapshotManifest]:
    """Request (or resume ``key``), wait, download into a fresh directory, verify, and move it to
    ``raw_root/<creation date>``. An existing snapshot is reused only if it is the same download;
    otherwise this raises instead of overwriting immutable data."""
    transport = transport or UrllibTransport()
    if key is None:
        if credentials is None:
            raise GbifDownloadError("credentials are required to request a new download")
        key = request_download(transport, credentials, dataset_key)
        on_status(f"requested {key}")
    status = wait_for_download(
        transport, key, poll_s=poll_s, max_wait_s=max_wait_s, sleep=sleep, on_status=on_status
    )
    request = status.get("request") or {}
    if not same_predicate(request.get("predicate"), dataset_predicate(dataset_key)):
        raise GbifDownloadError(f"download {key} is not a whole-dataset request for {dataset_key}")
    if request.get("format") != FORMAT:
        raise GbifDownloadError(f"download {key} has format {request.get('format')}, not {FORMAT}")
    for field in ("doi", "downloadLink", "created"):
        if not status.get(field):
            raise GbifDownloadError(f"download {key} status lacks '{field}'")

    created = str(status["created"])[:10]
    final = raw_root / created
    if (final / "manifest.json").is_file():
        existing = load_manifest(final / "manifest.json")
        if existing.doi != status["doi"]:
            raise ChecksumMismatchError(
                f"{final} holds download {existing.doi}, not {status['doi']}; refusing to touch it"
            )
        verify_snapshot(final, existing)
        return final, existing
    if final.exists():
        raise ChecksumMismatchError(f"{final} exists without a manifest; refusing to touch it")

    dataset = transport.get_json(f"{API}/dataset/{dataset_key}")
    incoming = raw_root / f".incoming-{uuid.uuid4().hex}"
    incoming.mkdir(parents=True)
    try:
        retrieved_at = datetime.now(UTC).replace(microsecond=0).isoformat()
        archive_path = incoming / f"{key}.zip"
        on_status("downloading")
        last_modified = transport.download(str(status["downloadLink"]), archive_path)
        size = archive_path.stat().st_size
        if "size" in status and int(status["size"]) != size:
            raise GbifDownloadError(f"downloaded {size} bytes, GBIF reports {status['size']}")
        _check_archive(archive_path)
        status_path = incoming / STATUS_FILE
        status_path.write_text(json.dumps(_redacted(status), indent=2) + "\n", encoding="utf-8")
        archive = SnapshotFile(
            name=archive_path.name,
            url=str(status["downloadLink"]),
            sha256=sha256_file(archive_path),
            size_bytes=size,
            publication_date=created,
            server_last_modified=last_modified,
        )
        status_file = SnapshotFile(
            name=STATUS_FILE,
            url=f"{API}/occurrence/download/{key}",
            sha256=sha256_file(status_path),
            size_bytes=status_path.stat().st_size,
            publication_date=created,
        )
        manifest = build_manifest(status, dataset, archive, status_file, retrieved_at)
        write_manifest(incoming / "manifest.json", manifest)
        incoming.rename(final)
        write_manifest(manifest_dir / f"{manifest.snapshot_id}.json", manifest)
        return final, manifest
    finally:
        if incoming.exists():
            shutil.rmtree(incoming)


def fetch_pinned_gbif(
    snapshot_id: str, raw_root: Path, manifest_dir: Path
) -> tuple[Path, SnapshotManifest, list[str]]:
    """The pinned specimen snapshot, without a GBIF account: the archive in the project's data
    release ``data-<snapshot_id>`` (CC BY 4.0, the download DOI in its manifest), else GBIF's own
    download URL while GBIF keeps it. Checksums from the committed manifest decide.

    The archived ``download-status.json`` is GBIF's status response with account details removed,
    so only the release copy matches; GBIF's live status page never does.
    """
    from localitylens.data import gnis_fetch

    if not snapshot_id.startswith("gbif-cu-"):
        raise ValueError(f"not a GBIF snapshot ID: {snapshot_id!r}")
    final = raw_root / snapshot_id.removeprefix("gbif-cu-")
    return gnis_fetch.fetch_pinned_snapshot(snapshot_id, final, raw_root, manifest_dir)
