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


def test_review_commands_apply_the_release_selection_check_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import localitylens.cli as cli

    seen: list[str | None] = []

    def capture(args: object) -> int:
        seen.append(cli._selection(args))  # type: ignore[arg-type]
        return 0

    for name in ("_review_import", "_review_work", "_audit_rules"):
        monkeypatch.setattr(cli, name, capture)
    assert main(["review", "import", "--sample", "s.json"]) == 0
    assert main(["review", "work"]) == 0
    assert main(["review", "work", "--no-selection"]) == 0
    assert main(["review", "import", "--sample", "s.json", "--selection-check"]) == 0
    assert main(["audit", "rules", "--sample", "s.json"]) == 0  # evaluation: only when asked
    assert main(["audit", "rules", "--sample", "s.json", "--selection-2"]) == 0
    assert seen == ["selection-2", "selection-2", None, "selection-1", None, "selection-2"]
    with pytest.raises(SystemExit):
        main(["review", "work", "--no-selection", "--selection-2"])
