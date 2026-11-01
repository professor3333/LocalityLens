from pathlib import Path

import pytest

from localitylens.cli import main
from localitylens.data.manifest import SnapshotManifest, write_manifest


def test_build_and_search_commands(
    gnis_snapshot: tuple[Path, SnapshotManifest],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    index = tmp_path / "g.sqlite"

    assert main(["gazetteer", "build", "--snapshot", str(directory), "--out", str(index)]) == 0
    assert "gnis-synthetic" in capsys.readouterr().out

    search = ["gazetteer", "search", "Testa Pk.", "--index", str(index), "--county", "Beta"]
    assert main(search) == 0
    first_line = capsys.readouterr().out.splitlines()[0]
    assert first_line.split()[0] == "2"
    assert "county=y" in first_line

    assert main(["gazetteer", "search", "Nowhere Gulch", "--index", str(index)]) == 0
    assert capsys.readouterr().out.strip() == "feature_absent_from_index"
