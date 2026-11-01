"""Fetch logic with the network replaced by local synthetic files."""

from collections.abc import Callable
from pathlib import Path

import pytest
from tests.support.synthetic_gnis import SYNTH_FEATURES, write_gnis_zips

from localitylens.data import gnis_fetch
from localitylens.data.manifest import ChecksumMismatchError, load_manifest, verify_snapshot


def _fake_downloader(source_dir: Path) -> Callable[..., str | None]:
    def fake(url: str, dest: Path, attempts: int = 4) -> str | None:
        dest.write_bytes((source_dir / url.rsplit("/", 1)[1]).read_bytes())
        return "Thu, 01 Jan 2026 00:00:00 GMT"

    return fake


def test_fetch_writes_verified_snapshot_and_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "server"
    write_gnis_zips(source)
    monkeypatch.setattr(gnis_fetch, "_download", _fake_downloader(source))

    path, manifest = gnis_fetch.fetch_gnis(tmp_path / "raw", tmp_path / "manifests")

    assert path == tmp_path / "raw" / "2026-01-01"
    assert manifest.snapshot_id == "gnis-co-2026-01-01"
    verify_snapshot(path, manifest)
    assert load_manifest(tmp_path / "manifests" / "gnis-co-2026-01-01.json") == manifest
    assert not list((tmp_path / "raw").glob(".incoming-*"))


def test_refetch_of_identical_data_reuses_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "server"
    write_gnis_zips(source)
    monkeypatch.setattr(gnis_fetch, "_download", _fake_downloader(source))
    first, _ = gnis_fetch.fetch_gnis(tmp_path / "raw", tmp_path / "m")
    second, _ = gnis_fetch.fetch_gnis(tmp_path / "raw", tmp_path / "m")
    assert first == second


def test_changed_upstream_data_never_overwrites_a_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "server"
    write_gnis_zips(source)
    monkeypatch.setattr(gnis_fetch, "_download", _fake_downloader(source))
    path, original = gnis_fetch.fetch_gnis(tmp_path / "raw", tmp_path / "m")

    write_gnis_zips(source, features=SYNTH_FEATURES[:2])  # same pubdate, different content
    with pytest.raises(ChecksumMismatchError):
        gnis_fetch.fetch_gnis(tmp_path / "raw", tmp_path / "m")
    verify_snapshot(path, original)  # the stored snapshot is untouched
    assert not list((tmp_path / "raw").glob(".incoming-*"))
