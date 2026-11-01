"""GBIF download flow with the network replaced by a fake transport and a SYNTHETIC archive.

Keys, DOIs and records here are invented test values, not real GBIF identifiers.
"""

import json
import zipfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr

from localitylens.data import gbif_fetch
from localitylens.data.gbif_fetch import (
    CU_HERBARIUM_DATASET_KEY,
    Credentials,
    GbifDownloadError,
    dataset_predicate,
    fetch_gbif,
    read_credentials,
    same_predicate,
)
from localitylens.data.manifest import ChecksumMismatchError, load_manifest, verify_snapshot

KEY = "0000001-990101000000000"
DOI = "10.99999/dl.synthetic"
CREDS = Credentials(user="synthetic-user", password=SecretStr("s3cret-pw"), email="a@example.org")


def write_archive(path: Path, members: tuple[str, ...] = gbif_fetch.REQUIRED_MEMBERS) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name in members:
            zf.writestr(name, f"synthetic {name}\n")


class FakeTransport:
    def __init__(self, archive: Path, states: list[str], **status: Any) -> None:
        self.archive = archive
        self.states = list(states)
        self.posts: list[dict[str, Any]] = []
        self.status_overrides = status

    def post_json(self, url: str, body: dict[str, Any], credentials: Credentials) -> str:
        self.posts.append(body)
        return KEY

    def get_json(self, url: str) -> dict[str, Any]:
        if "/dataset/" in url:
            return {"key": CU_HERBARIUM_DATASET_KEY, "title": "Synthetic Herbarium", "doi": "x"}
        state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        status: dict[str, Any] = {
            "key": KEY,
            "status": state,
            "created": "2026-11-01T10:00:00.000+00:00",
            "request": {
                # GBIF echoes the predicate back with its defaults filled in.
                "predicate": dataset_predicate(CU_HERBARIUM_DATASET_KEY) | {"matchCase": False},
                "format": "DWCA",
                "creator": CREDS.user,
                "notificationAddresses": [CREDS.email],
            },
            "license": "http://creativecommons.org/licenses/by/4.0/legalcode",
            "totalRecords": 3,
        }
        if state == "SUCCEEDED":
            status |= {
                "doi": DOI,
                "downloadLink": f"https://example.org/{KEY}.zip",
                "size": self.archive.stat().st_size,
            }
        return status | self.status_overrides

    def download(self, url: str, dest: Path) -> str | None:
        dest.write_bytes(self.archive.read_bytes())
        return None


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    path = tmp_path / "server.zip"
    write_archive(path)
    return path


def run(tmp_path: Path, transport: FakeTransport, **kwargs: Any) -> Any:
    return fetch_gbif(
        tmp_path / "raw", tmp_path / "manifests", CREDS, transport=transport,
        sleep=lambda _s: None, **kwargs,
    )  # fmt: skip


def test_request_wait_download_and_manifest(tmp_path: Path, archive: Path) -> None:
    transport = FakeTransport(archive, ["PREPARING", "RUNNING", "SUCCEEDED"])
    path, manifest = run(tmp_path, transport)

    assert path == tmp_path / "raw" / "2026-11-01"
    assert manifest.snapshot_id == "gbif-cu-2026-11-01"
    assert manifest.doi == DOI
    assert manifest.record_count == 3
    assert manifest.licence.startswith("CC BY 4.0")
    assert (
        manifest.citation
        == f"GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/{DOI}"
    )
    query = json.loads(manifest.query or "")
    assert same_predicate(query, dataset_predicate(CU_HERBARIUM_DATASET_KEY))
    verify_snapshot(path, manifest)
    assert load_manifest(tmp_path / "manifests" / "gbif-cu-2026-11-01.json") == manifest
    assert transport.posts[0]["predicate"] == dataset_predicate(CU_HERBARIUM_DATASET_KEY)
    assert transport.posts[0]["format"] == "DWCA"
    assert not list((tmp_path / "raw").glob(".incoming-*"))


def test_account_details_never_reach_the_manifest_or_saved_status(
    tmp_path: Path, archive: Path
) -> None:
    path, _ = run(tmp_path, FakeTransport(archive, ["SUCCEEDED"]))
    for written in [*path.glob("*.json"), *(tmp_path / "manifests").glob("*.json")]:
        text = written.read_text()
        for secret in ("s3cret-pw", CREDS.user, "a@example.org"):
            assert secret not in text, (written.name, secret)
    assert "s3cret-pw" not in repr(CREDS)


def test_resuming_a_key_makes_no_new_request(tmp_path: Path, archive: Path) -> None:
    transport = FakeTransport(archive, ["SUCCEEDED"])
    fetch_gbif(tmp_path / "raw", tmp_path / "m", None, key=KEY, transport=transport)
    assert transport.posts == []


def test_a_download_of_another_query_is_rejected(tmp_path: Path, archive: Path) -> None:
    other = {"predicate": dataset_predicate("other-dataset"), "format": "DWCA"}
    with pytest.raises(GbifDownloadError, match="not a whole-dataset request"):
        run(tmp_path, FakeTransport(archive, ["SUCCEEDED"], request=other))


@pytest.mark.parametrize(
    "echoed",
    [{"matchCase": True}, {"value": "other"}, {"key": "COUNTRY"}, {"extra": 1}],
)
def test_predicate_changes_that_alter_meaning_are_detected(echoed: dict[str, object]) -> None:
    sent = dataset_predicate(CU_HERBARIUM_DATASET_KEY)
    assert same_predicate(sent | {"matchCase": False}, sent)
    assert not same_predicate(sent | echoed, sent)


@pytest.mark.parametrize("state", ["FAILED", "KILLED", "CANCELLED", "FILE_ERASED"])
def test_terminal_failure_raises(tmp_path: Path, archive: Path, state: str) -> None:
    with pytest.raises(GbifDownloadError, match=state):
        run(tmp_path, FakeTransport(archive, ["RUNNING", state]))
    assert not (tmp_path / "raw").exists() or not any((tmp_path / "raw").iterdir())


def test_waiting_too_long_says_how_to_resume(tmp_path: Path, archive: Path) -> None:
    with pytest.raises(GbifDownloadError, match=f"--key {KEY}"):
        run(tmp_path, FakeTransport(archive, ["RUNNING"]), poll_s=10, max_wait_s=30)


def test_size_mismatch_is_rejected_and_cleaned_up(tmp_path: Path, archive: Path) -> None:
    with pytest.raises(GbifDownloadError, match="bytes"):
        run(tmp_path, FakeTransport(archive, ["SUCCEEDED"], size=1))
    assert not list((tmp_path / "raw").glob("*"))


def test_archive_without_verbatim_file_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "bad.zip"
    write_archive(bad, ("meta.xml", "occurrence.txt"))
    with pytest.raises(GbifDownloadError, match=r"verbatim\.txt"):
        run(tmp_path, FakeTransport(bad, ["SUCCEEDED"]))


def test_archive_with_traversal_paths_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "bad.zip"
    write_archive(bad, (*gbif_fetch.REQUIRED_MEMBERS, "../escape.txt"))
    with pytest.raises(GbifDownloadError, match="unsafe"):
        run(tmp_path, FakeTransport(bad, ["SUCCEEDED"]))


def test_same_download_is_reused_and_a_different_one_refused(tmp_path: Path, archive: Path) -> None:
    first, _ = run(tmp_path, FakeTransport(archive, ["SUCCEEDED"]))
    again, _ = run(tmp_path, FakeTransport(archive, ["SUCCEEDED"]))
    assert again == first
    with pytest.raises(ChecksumMismatchError, match="refusing"):
        run(tmp_path, FakeTransport(archive, ["SUCCEEDED"], doi="10.99999/other"))


def test_credentials_from_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for k in ("GBIF_USER", "GBIF_PWD", "GBIF_EMAIL"):
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text('# comment\nGBIF_USER = alice\nexport GBIF_PWD="p w=1"\nGBIF_EMAIL=\n')
    creds = read_credentials(env)
    assert creds.user == "alice"
    assert creds.password.get_secret_value() == "p w=1"
    assert creds.email is None


def test_missing_credentials_name_the_key_not_the_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for k in ("GBIF_USER", "GBIF_PWD"):
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text("GBIF_USER=alice\n")
    with pytest.raises(GbifDownloadError, match="GBIF_PWD") as err:
        read_credentials(env)
    assert "alice" not in str(err.value)
