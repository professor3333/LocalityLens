"""Rule question of the dev-3 and dev-4 scoring plans (eval/dev/<sample>/scoring-plan.md).

rules-2 to rules-6 are replayed through the current pipeline and scorer, each version's
``baseline/rules.py`` taken from its git commit. Correct candidates are compared on the
answerable records of the ``place_offset`` stratum, and every record that any two versions read
differently is listed.

    uv run python scripts/replay_rules_versions.py eval/reports/dev-3-rules-question.json
    uv run python scripts/replay_rules_versions.py eval/reports/dev-4-rules-question.json \
        --sample dev-4

``--sample`` names a dev sample under ``eval/dev/``; it defaults to dev-3. The committed rules-6
run of that sample (``eval/reports/<sample>-rules-6.json``) must exist: the replay checks itself
against it.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

from localitylens.baseline import rules as current_rules
from localitylens.evaluation.annotations import check_worksheet
from localitylens.evaluation.audit import load_sample, run_system
from localitylens.evaluation.dev_sample import text_shape
from localitylens.evaluation.score import _category, judge, paired
from localitylens.gazetteer.index import Gazetteer

INDEX = Path("data/derived/gazetteer.sqlite")
COMMITS = {"rules-2": "57b3261", "rules-3": "06cacbc", "rules-4": "4e56bfe", "rules-5": "3b24d4e"}
KEYS = ("relation", "interpretation", "candidate_ids", "proposal")


def load_version(version: str, commit: str, directory: Path) -> ModuleType:
    source = subprocess.run(
        ["git", "show", f"{commit}:src/localitylens/baseline/rules.py"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    path = directory / f"rules_{commit}.py"
    path.write_text(source, encoding="utf-8")
    name = "replay_" + version.replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses need the module registered
    spec.loader.exec_module(module)
    return module


def main(out: Path, name: str = "dev-3") -> dict[str, Any]:
    sample_path = Path(f"eval/dev/{name}/{name}.json")
    worksheet = Path(f"eval/dev/{name}/worksheet.csv")
    committed_path = Path(f"eval/reports/{name}-rules-6.json")
    with tempfile.TemporaryDirectory() as tmp:
        mods = {v: load_version(v, c, Path(tmp)) for v, c in COMMITS.items()}
        mods["rules-6"] = current_rules
        for version, module in mods.items():
            assert version == module.RULES_VERSION, (version, module.RULES_VERSION)
        sample = load_sample(sample_path)
        with Gazetteer(INDEX) as gaz:
            check = check_worksheet(worksheet, sample, gaz)
        ann = {a.audit_id: a for a in check.annotations}
        reports = {}
        for version, module in mods.items():
            report = run_system(
                sample,
                INDEX,
                "rules",
                lambda g, m=module: m.RulesExtractor(m.Lexicon(g.county_names(), g.name_keys())),
                version,
            )
            reports[version] = {r["audit_id"]: r for r in report["records"]}
    committed = {
        r["audit_id"]: r for r in json.loads(committed_path.read_text(encoding="utf-8"))["records"]
    }
    for audit_id, row in committed.items():
        replay = reports["rules-6"][audit_id]
        assert all(replay.get(k) == row.get(k) for k in KEYS), f"rules-6 replay differs: {audit_id}"

    shape = {i.audit_id: text_shape(i.record.locality, "2") for i in sample.items}
    judged = {v: {i: judge(ann[i], rep[i]) for i in rep} for v, rep in reports.items()}
    answerable = [i for i in sorted(ann) if _category(ann[i]) == "answerable"]
    place_offset = [i for i in answerable if shape[i] == "place_offset"]

    def correct(version: str, ids: list[str]) -> list[bool]:
        return [judged[version][i].correct_candidate for i in ids]

    result: dict[str, Any] = {
        "answerable": len(answerable),
        "place_offset_answerable": len(place_offset),
        "correct_by_version_place_offset": {v: sum(correct(v, place_offset)) for v in mods},
        "correct_by_version_all": {v: sum(correct(v, answerable)) for v in mods},
        "rules6_vs_rules2_place_offset": paired(
            correct("rules-2", place_offset), correct("rules-6", place_offset)
        ),
        "rules6_vs_rules2_all": paired(
            correct("rules-2", answerable), correct("rules-6", answerable)
        ),
        "changed_records": [],
    }
    for i in sorted(ann):
        readings = {(reports[v][i]["relation"], reports[v][i].get("reference")) for v in mods}
        interpretations = {
            json.dumps(reports[v][i].get("interpretation"), sort_keys=True) for v in mods
        }
        if len(readings) > 1 or len(interpretations) > 1:
            result["changed_records"].append(
                {
                    "audit_id": i,
                    "stratum": shape[i],
                    "category": _category(ann[i]),
                    "readings": {
                        v: {
                            "relation": reports[v][i]["relation"],
                            "reference": reports[v][i].get("reference"),
                            "correct": judged[v][i].correct_candidate,
                        }
                        for v in mods
                    },
                }
            )
    result["rules5_vs_rules6_differ"] = [
        i
        for i in sorted(ann)
        if any(reports["rules-5"][i].get(k) != reports["rules-6"][i].get(k) for k in KEYS)
    ]
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument("--sample", default="dev-3", help="dev sample name under eval/dev/")
    args = parser.parse_args()
    main(args.out, args.sample)
