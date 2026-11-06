"""The pinned GNIS snapshot: mirror first, USGS fallback, checksums always; clean refusals when
the gazetteer and the extent store disagree. SYNTHETIC GNIS files; no network (downloads are
replaced by local copies)."""

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from localitylens.data import gnis_fetch
from localitylens.data.manifest import ChecksumMismatchError, SnapshotManifest, write_manifest
from localitylens.review.store import ReviewStore
from localitylens.web.app import ReviewConfig, create_app

SNAPSHOT = "gnis-co-2026-01-15"


@pytest.fixture
def pinned(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path) -> dict[str, Path]:
    """A committed manifest for SNAPSHOT plus the original files, served by a fake download."""
    source, manifest = gnis_snapshot
    manifests = tmp_path / "manifests"
    write_manifest(manifests / f"{SNAPSHOT}.json",
                   manifest.model_copy(update={"snapshot_id": SNAPSHOT}))  # fmt: skip
    return {"source": source, "manifests": manifests, "raw": tmp_path / "out"}  # not the source


def _serve(monkeypatch: pytest.MonkeyPatch, source: Path, *, mirror_bad: bool = False,
           usgs_bad: bool = False, mirror_down: bool = False) -> list[str]:  # fmt: skip
    calls: list[str] = []

    def download(url: str, dest: Path, attempts: int = 4) -> None:
        calls.append(url)
        mirror = url.startswith(gnis_fetch.MIRROR)
        if mirror and mirror_down:
            raise OSError("mirror unreachable")
        if (mirror and mirror_bad) or (not mirror and usgs_bad):
            dest.write_bytes(b"republished, different bytes")
            return
        shutil.copyfile(source / url.rsplit("/", 1)[1], dest)

    monkeypatch.setattr(gnis_fetch, "_download", download)
    return calls


def test_the_pinned_snapshot_comes_from_the_mirror(
    pinned: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _serve(monkeypatch, pinned["source"])
    path, _manifest, sources = gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"],
                                                           pinned["manifests"])  # fmt: skip
    assert path == pinned["raw"] / "2026-01-15"
    assert (path / "manifest.json").is_file()
    assert all(s.startswith(f"{gnis_fetch.MIRROR}/data-{SNAPSHOT}/") for s in sources)
    assert len(calls) == 2
    assert not list(pinned["manifests"].glob("*.json"))[1:]  # no new manifest written
    again = gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    assert again[2] == ["already present", "already present"]
    assert len(calls) == 2  # nothing downloaded twice


def test_a_bad_or_missing_mirror_falls_back_to_usgs(
    pinned: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _serve(monkeypatch, pinned["source"], mirror_bad=True)
    _, _, sources = gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    assert all(s.startswith("https://example.invalid/") for s in sources)  # the manifest's URLs
    shutil.rmtree(pinned["raw"])
    _serve(monkeypatch, pinned["source"], mirror_down=True)
    _, _, sources = gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    assert all(s.startswith("https://example.invalid/") for s in sources)


def test_files_that_match_no_source_are_never_kept(
    pinned: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _serve(monkeypatch, pinned["source"], mirror_bad=True, usgs_bad=True)
    with pytest.raises(ChecksumMismatchError, match="no source matches"):
        gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    assert not (pinned["raw"] / "2026-01-15").exists()
    assert not [p for p in pinned["raw"].iterdir() if p.name.startswith(".incoming")]


def test_an_altered_local_copy_is_refused(
    pinned: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _serve(monkeypatch, pinned["source"])
    path, _, _ = gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    (path / "DomesticNames_CO_Text.zip").write_bytes(b"edited")
    with pytest.raises(ChecksumMismatchError):
        gnis_fetch.fetch_pinned_gnis(SNAPSHOT, pinned["raw"], pinned["manifests"])
    with pytest.raises(FileNotFoundError, match="no committed manifest"):
        gnis_fetch.fetch_pinned_gnis("gnis-co-1999-01-01", pinned["raw"], pinned["manifests"])
    with pytest.raises(ValueError, match="not a GNIS snapshot"):
        gnis_fetch.snapshot_directory(pinned["raw"], "gbif-cu-2026-11-01")


def test_cli_refusals_are_clean(
    tmp_path: Path, gnis_snapshot: tuple[Path, SnapshotManifest],
    capsys: pytest.CaptureFixture[str],
) -> None:  # fmt: skip
    from localitylens.cli import main
    from localitylens.gazetteer.index import build_index

    assert main(["gazetteer", "build", "--snapshot", str(tmp_path / "nowhere")]) == 2
    assert "run `localitylens data fetch-gnis`" in capsys.readouterr().err
    # a gazetteer from another snapshot than the extent store's: processing refuses
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    index = tmp_path / "g.sqlite"
    build_index(directory, manifest, index)
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    code = main(["review", "work", "--db", str(db), "--index", str(index),
                 "--extents", "data/reviewed/extents.csv"])  # fmt: skip
    err = capsys.readouterr().err
    assert code == 2
    assert "refused:" in err
    assert "pinned to a GNIS snapshot" in err


def test_readyz_reports_an_unusable_extent_store(tmp_path: Path) -> None:
    db = tmp_path / "review.sqlite"
    ReviewStore(db).close()
    client = TestClient(create_app(ReviewConfig(db=db, extents_problem="row 1 does not match")))
    r = client.get("/readyz")
    assert r.status_code == 503
    assert "extent store: row 1 does not match" in r.json()["problems"]
    assert client.get("/").status_code == 200  # the screen still serves
