"""Few-shot ablation: LLM v2 (11 examples) against the same prompt with no examples.

Scores both LLM reports of each read sample against its annotations, per sample and pooled by
annotator (the owner's: audit, dev-1, validation; Claude's: dev-2, dev-3, dev-4), with the
paired bootstrap and the exact sign test.

    uv run python scripts/ablation_fewshot.py eval/reports/ablation-fewshot.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from localitylens.evaluation.annotations import check_worksheet
from localitylens.evaluation.audit import load_sample
from localitylens.evaluation.score import _category, judge, paired
from localitylens.gazetteer.index import Gazetteer

SAMPLES = {
    "audit-50": ("eval/audit/audit-50.json", "eval/audit/worksheet.csv", "owner"),
    "dev-1": ("eval/dev/dev-1/dev-1.json", "eval/dev/dev-1/worksheet.csv", "owner"),
    "validation": ("eval/benchmark/validation/validation.json",
                   "eval/benchmark/validation/worksheet.csv", "owner"),
    "dev-2": ("eval/dev/dev-2/dev-2.json", "eval/dev/dev-2/worksheet.csv", "Claude"),
    "dev-3": ("eval/dev/dev-3/dev-3.json", "eval/dev/dev-3/worksheet.csv", "Claude"),
    "dev-4": ("eval/dev/dev-4/dev-4.json", "eval/dev/dev-4/worksheet.csv", "Claude"),
}  # fmt: skip
FULL = "llm-x2g2-qwen3.5-4b-q4km"
ZERO = "llm-x2zs-qwen3.5-4b-q4km"


def _records(name: str, system: str) -> dict[str, dict[str, Any]]:
    path = Path(f"eval/reports/{name}-{system}.json")
    return {r["audit_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))["records"]}


def main(out: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"full": FULL, "zero_shot": ZERO, "samples": {}, "pooled": {}}
    pooled: dict[str, tuple[list[bool], list[bool]]] = {}
    with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
        for name, (sample_path, worksheet, annotator) in SAMPLES.items():
            sample = load_sample(Path(sample_path))
            ann = check_worksheet(Path(worksheet), sample, gaz).annotations
            full, zero = _records(name, FULL), _records(name, ZERO)
            answerable = [a for a in ann if _category(a) == "answerable"]
            f = [judge(a, full[a.audit_id]) for a in answerable]
            z = [judge(a, zero[a.audit_id]) for a in answerable]
            fc, zc = [j.correct_candidate for j in f], [j.correct_candidate for j in z]
            invalid = {k: sum(1 for r in recs.values() if r.get("interpretation") is None)
                       for k, recs in (("full", full), ("zero_shot", zero))}  # fmt: skip
            result["samples"][name] = {
                "annotator": annotator, "answerable": len(answerable),
                "correct": {"full": sum(fc), "zero_shot": sum(zc)},
                "critical_exact": {"full": sum(j.critical_ok for j in f),
                                   "zero_shot": sum(j.critical_ok for j in z)},
                "invalid_extractions": invalid,
                "zero_shot_vs_full": paired(fc, zc),
            }  # fmt: skip
            a, b = pooled.setdefault(annotator, ([], []))
            a.extend(fc)
            b.extend(zc)
    for annotator, (fc, zc) in pooled.items():
        result["pooled"][annotator] = {"n": len(fc), "full": sum(fc), "zero_shot": sum(zc),
                                       "zero_shot_vs_full": paired(fc, zc)}  # fmt: skip
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    r = main(Path(sys.argv[1]))
    for name, s in r["samples"].items():
        print(
            f"{name:<10} {s['annotator']:<6} n={s['answerable']:>2}  full {s['correct']['full']:>2}"
            f"  zero-shot {s['correct']['zero_shot']:>2}  invalid {s['invalid_extractions']}"
        )
    for annotator, p in r["pooled"].items():
        d = p["zero_shot_vs_full"]
        print(
            f"pooled {annotator}: n={p['n']} full {p['full']} zero-shot {p['zero_shot']}  "
            f"diff {d['difference']:+.3f} CI {d['ci95']} p {d['sign_test_p']}"
        )
