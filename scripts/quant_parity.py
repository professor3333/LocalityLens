"""Paired Q4_K_M vs Q8_0 comparison from a release-workflow run's artifacts.

    gh run download <run id> -D runs -p 'eval-*'
    uv run python scripts/quant_parity.py runs

For each sample it also builds hybrid-1 with the Q8_0 LLM report (the same rules report) and
scores it, then prints pooled counts and record-by-record discordant pairs with an exact sign
test. Counts only.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

SAMPLES = {
    "audit-50": ("eval/audit/audit-50.json", "eval/audit/worksheet.csv"),
    "dev-1": ("eval/dev/dev-1/dev-1.json", "eval/dev/dev-1/worksheet.csv"),
    "validation": ("eval/benchmark/validation/validation.json",
                   "eval/benchmark/validation/worksheet.csv"),
    "dev-2": ("eval/dev/dev-2/dev-2.json", "eval/dev/dev-2/worksheet.csv"),
    "dev-3": ("eval/dev/dev-3/dev-3.json", "eval/dev/dev-3/worksheet.csv"),
    "dev-4": ("eval/dev/dev-4/dev-4.json", "eval/dev/dev-4/worksheet.csv"),
}  # fmt: skip
Q8 = "release/manifest-q8.json"


def _cli(*args: str) -> None:
    subprocess.run(["uv", "run", "localitylens", *args], check=True, capture_output=True)


def _sign_p(b: int, c: int) -> float:
    n, k = b + c, min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n) if n else 1.0


def main(runs: Path) -> dict[str, Any]:
    pooled: dict[str, list[int]] = {}
    pairs = {"llm critical_ok": [0, 0], "llm correct_candidate": [0, 0],
             "hybrid correct_candidate": [0, 0]}  # fmt: skip
    for s, (sample, worksheet) in SAMPLES.items():
        q4dir, q8dir, h8 = runs / f"eval-q4-{s}", runs / f"eval-q8-{s}", runs / f"hybrid-q8-{s}"
        h8.mkdir(exist_ok=True)
        for src in (q4dir / f"{s}-rules-6-extents-derived.json",
                    q8dir / f"{s}-llm-x2g2-qwen3.5-4b-q8_0-extents-derived.json"):  # fmt: skip
            (h8 / src.name).write_bytes(src.read_bytes())
        _cli("audit", "hybrid", "--sample", sample, "--out", str(h8), "--with-derived",
             "--release", Q8)  # fmt: skip
        _cli("audit", "score", "--sample", sample, "--out", str(h8), "--worksheet", worksheet,
             "--with-derived", "--release", Q8,
             "--hybrid", str(h8 / f"{s}-hybrid-1-extents-derived.json"))  # fmt: skip
        scores = {
            "q4": json.loads((q4dir / f"{s}-score-hybrid-1-extents-derived.json").read_text()),
            "q8": json.loads((h8 / f"{s}-score-hybrid-1-extents-derived.json").read_text()),
        }
        for quant, sc in scores.items():
            for system in ("llm", "hybrid"):
                for m in ("valid_extraction", "critical_exact_match",
                          "correct_proposal_candidates"):  # fmt: skip
                    cell = sc["all"]["systems"][system][m]
                    key = f"{quant} {system} {m}"
                    pooled[key] = [pooled.get(key, [0, 0])[0] + cell["hits"],
                                   pooled.get(key, [0, 0])[1] + cell["n"]]  # fmt: skip
            p = sc["all"]["proposals"]["hybrid"]
            key = f"{quant} hybrid ready regions (correct, ready)"
            pooled[key] = [pooled.get(key, [0, 0])[0] + p["precision"]["hits"],
                           pooled.get(key, [0, 0])[1] + p["computed"]["hits"]]  # fmt: skip
        j = {q: {sys_: {r["audit_id"]: r for r in sc["all"]["judgements"][sys_]}
                    for sys_ in ("llm", "hybrid")} for q, sc in scores.items()}  # fmt: skip
        for name in pairs:
            system, field = name.split()
            for aid, r4 in j["q4"][system].items():
                a, b = r4[field], j["q8"][system][aid][field]
                if a != b:
                    pairs[name][0 if b else 1] += 1
    out = {
        "pooled": pooled,
        "discordant_pairs": {
            k: {"q8_only": v[0], "q4_only": v[1], "sign_test_p": round(_sign_p(*v), 3)}
            for k, v in pairs.items()
        },
    }
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main(Path(sys.argv[1]))
