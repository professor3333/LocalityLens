"""Tracked files never name files that are excluded locally in ``.git/info/exclude``.

Those files stay on one machine; naming them in the repository would publish them. The names
are read from the local exclude file, so none of them appears here. In a fresh clone or in CI
the exclude file has no entries and this test passes trivially: it guards local commits.
"""

import subprocess
from pathlib import Path


def _local_only_names() -> list[str]:
    exclude = Path(".git/info/exclude")
    if not exclude.is_file():
        return []
    names = []
    for line in exclude.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not any(c in line for c in "*?[!"):
            names.append(line.strip("/"))
    return names


def test_tracked_files_do_not_name_local_only_files() -> None:
    names = _local_only_names()
    if not names:
        return
    files = subprocess.run(["git", "ls-files"], check=True, capture_output=True,
                           text=True).stdout.splitlines()  # fmt: skip
    hits = []
    for name in files:
        path = Path(name)
        if not path.is_file() or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary
        for number, line in enumerate(text.splitlines(), start=1):
            if any(n in line for n in names):
                hits.append(f"{name}:{number}")
    assert not hits, f"tracked files name local-only files: {hits[:20]}"
