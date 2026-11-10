"""Counts-only stage breakdown of hybrid ready regions; prints no labels, names or IDs.

Usage (repo root): uv run python scripts/diagnose_regions.py <sample> <worksheet>
<hybrid report> <score report> [<dispute-candidates.txt>]. With the last argument, the
dispute-candidate and clause-choice row IDs (IDs only) are written next to it.
Used for eval/reports/test-3-diagnosis.md.
"""

import json
import sys
from collections import Counter
from pathlib import Path

from localitylens.evaluation.annotations import check_worksheet
from localitylens.evaluation.audit import load_sample
from localitylens.gazetteer.index import Gazetteer
from localitylens.gazetteer.keys import core_key, name_key

sample, ws, hyb, sc = map(Path, sys.argv[1:5])
with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
    ann = {a.audit_id: a for a in check_worksheet(ws, load_sample(sample), gaz).annotations}
rows = {
    r["audit_id"]: r
    for r in next(v for v in json.loads(hyb.read_text()).values() if isinstance(v, list))
}
judg = {j["audit_id"]: j for j in json.loads(sc.read_text())["all"]["judgements"]["hybrid"]}


def keys(n: str) -> set[str]:
    k = name_key(n)
    return {k, core_key(k)} - {None, ""}


stage, disputes, clause = Counter(), [], []
for aid, r in rows.items():
    if r["proposal"] != "computed":
        continue
    j, a = judg[aid], ann[aid]
    same_name = bool(r.get("reference")) and any(
        keys(r["reference"]) & keys(n) for n in a.reference_features
    )
    unsure = bool(a.unsure_columns)
    if j["correct_candidate"]:
        s = "correct"
    elif j["category"] == "unsupported":
        s = "annotated unsupported (relation)"
    elif j["category"] in ("reference_absent", "no_reference"):
        s = (
            "annotated absent, system found a same-named GNIS feature"
            if same_name
            else "clause choice (annotated place absent from GNIS; system used another place)"
        )
    elif not j["top1_ok"]:
        s = (
            "GNIS identity (same name, other feature)"
            if same_name
            else "clause choice (other place chosen)"
        )
    else:
        bad = [
            f
            for f in ("relation", "distance", "unit", "direction", "qualifiers")
            if not j[f + "_ok"]
        ]
        s = "reading: " + "+".join(bad or ["invalid"])
    stage[s] += 1
    if s.startswith("clause"):
        clause.append(aid)
    if s != "correct" and (same_name or unsure):
        disputes.append(aid)
    if s == "correct" and unsure:
        disputes.append(aid)
print("ready regions", sum(stage.values()))
for k, v in stage.most_common():
    print(f"  {v:3d}  {k}")
print("dispute candidates (same name or unsure marker)", len(disputes))
if len(sys.argv) > 5:
    Path(sys.argv[5]).write_text("\n".join(sorted(disputes)) + "\n")
    Path(sys.argv[5].replace("dispute-candidates", "clause-choice")).write_text(
        "\n".join(sorted(clause)) + "\n"
    )
