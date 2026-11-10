"""Build the static replay (demo/site) from the 50 audit records.

    uv run python scripts/build_replay.py            # needs llama-server on 127.0.0.1:8080

Steps:
1. Import eval/audit/audit-50.json into a new, temporary review store with the release system
   (hybrid-1: rules first, the LLM only where the rules reach no gazetteer candidate), the
   reviewed-extent store, the derived extents and the release's selection check. These are the real pipeline and the real
   model, run once here.
2. Freeze the review screen into static pages (localitylens.web.replay).
3. Replace demo/site.

Why these records: the audit sample is committed (CC BY 4.0), its records passed the specimen
screen (no informationWithheld / dataGeneralizations), and they are development data, already
read. No validation or locked-test record is ever published here; a test checks it. No curator
decisions are added: the replay shows proposals as the pipeline left them.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from localitylens.cli import main as cli
from localitylens.web.app import Replay, ReviewConfig
from localitylens.web.replay import freeze

ROOT = Path(__file__).resolve().parent.parent
MARKER = ".nojekyll"  # every frozen site has it; refuse to delete a folder without it


def _sh(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sample", default="eval/audit/audit-50.json")
    ap.add_argument("--extents", default="data/reviewed/extents.csv")
    ap.add_argument("--derived-extents", default="data/extents/derived.csv")
    ap.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ap.add_argument("--release", default="release/manifest.json")
    ap.add_argument("--out", default="demo/site")
    args = ap.parse_args()
    if _sh("git", "status", "--porcelain", "--untracked-files=no"):
        print("refused: commit or stash tracked changes first (the banner names the commit)")
        return 2
    out = ROOT / args.out
    if out.exists() and not (out / MARKER).is_file():
        print(f"refused: {out} exists and is not a frozen replay")
        return 2
    manifest = json.loads((ROOT / args.release).read_text(encoding="utf-8"))
    commit = _sh("git", "rev-parse", "--short", "HEAD")
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "replay.sqlite"
        argv = ["review", "import", "--sample", args.sample, "--system", "hybrid",
                "--extents", args.extents, "--derived-extents", args.derived_extents,
                "--index", args.index, "--release", args.release, "--db", str(db)]  # fmt: skip
        if cli(argv) != 0:
            return 1
        replay = Replay(
            system=f"hybrid-1: {manifest['rules_version']} first, then "
            f"{manifest['extractor_id']} only where the rules reach no gazetteer candidate; "
            "extents measured by hand where they exist, otherwise derived from Census place "
            "polygons and USGS NHD geometry (marked 'derived, not curator-reviewed'); "
            f"{manifest['selection_version']} holds a region for review when the label names "
            "another place that GNIS has inside it, or one GNIS lacks",
            records="the 50 audit records, University of Colorado Herbarium (development data, "
            "not held-out results)",
            built=f"commit {commit}, {datetime.now(UTC).date().isoformat()}",
            attribution="Specimen data: GBIF.org (01 November 2026) GBIF Occurrence Download "
            "https://doi.org/10.15468/dl.hqxjjf, CC BY 4.0. Place names: USGS GNIS "
            f"({manifest['gazetteer_snapshot']}), public domain. Map tiles: USGS The National Map",
        )
        staged = Path(tmp) / "site"
        counts = freeze(ReviewConfig(db=db), replay, staged)
        if out.exists():
            shutil.rmtree(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged, out)
    print(f"replay: {counts['records']} records, {counts['pages']} pages -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
