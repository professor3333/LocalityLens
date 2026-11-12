"""Release gates: compare a fresh evaluation of a release candidate with the committed reports.

The release workflow (`.github/workflows/release.yml`) re-runs every system on the dev and
validation samples, one job per sample and quantization, and collects the output folders under
one directory:

    <runs>/eval-q4-<sample>/   rules, LLM (shipped quant), hybrid-1, scores, with and without
                               selection-2; memory.txt
    <runs>/eval-q8-<sample>/   rules and LLM (reference quant) and their score; memory.txt

This module applies the gates declared in ``release/regression.json`` and writes the evidence
(JSON) and a Markdown summary. It reads aggregate scores and per-record model timings only.

    uv run python -m localitylens.evaluation.release_check --runs runs --out evidence.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

RELEASE_CHECK_VERSION = "release-check-1"
SCORE = "{label}-score-hybrid-1-extents-derived{suffix}.json"
_UNITS = {"B": 1, "KiB": 2**10, "MiB": 2**20, "GiB": 2**30, "TiB": 2**40,
          "kB": 1e3, "MB": 1e6, "GB": 1e9}  # fmt: skip


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing report: {path}")
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _hits(score: dict[str, Any], system: str, metric: str) -> tuple[int, int]:
    cell = score["all"]["systems"][system][metric]
    return int(cell["hits"]), int(cell["n"])


def _regions(score: dict[str, Any]) -> tuple[int, int]:
    """(ready regions, correct ready regions) of hybrid-1."""
    p = score["all"]["proposals"]["hybrid"]
    return int(p["computed"]["hits"]), int(p["precision"]["hits"])


def _nearest_rank(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[max(0, math.ceil(len(ordered) * q) - 1)], 1)


def parse_memory(text: str) -> int | None:
    """Peak bytes from `docker stats --format '{{.MemUsage}}'` lines ("3.1GiB / 15.6GiB")."""
    peak: float | None = None
    for line in text.splitlines():
        m = re.match(r"\s*([\d.]+)\s*([KMGT]?i?B|[kMG]B)\b", line)
        if m and m.group(2) in _UNITS:
            value = float(m.group(1)) * _UNITS[m.group(2)]
            peak = value if peak is None else max(peak, value)
    return None if peak is None else int(peak)


def _model_seconds(report: dict[str, Any]) -> list[float]:
    rows = next(v for v in report.values() if isinstance(v, list))
    return [
        float(r["trace"]["model_seconds"])
        for r in rows
        if r.get("trace") and not r["trace"].get("cache_hits")
    ]


def check(
    runs: Path, baseline: Path, regression: dict[str, Any], llm_ids: dict[str, str]
) -> dict[str, Any]:
    """Apply the declared gates. ``llm_ids`` maps "q4"/"q8" to the LLM extractor IDs."""
    samples: list[str] = regression["samples"]
    gates = regression["gates"]
    results: list[dict[str, Any]] = []

    fresh = {s: _load(runs / f"eval-q4-{s}" / SCORE.format(label=s, suffix="")) for s in samples}
    fresh2 = {s: _load(runs / f"eval-q4-{s}" / SCORE.format(label=s, suffix="-sel2"))
              for s in samples}  # fmt: skip
    base = {s: _load(baseline / SCORE.format(label=s, suffix="")) for s in samples}
    base2 = {s: _load(baseline / SCORE.format(label=s, suffix="-sel2")) for s in samples}

    g = gates["rules_exact"]
    diffs = []
    for s in samples:
        for m in g["metrics"]:
            got, want = _hits(fresh[s], "rules", m)[0], _hits(base[s], "rules", m)[0]
            if got != want:
                diffs.append(f"{s} {m}: {got} vs {want}")
    results.append({"gate": "rules_exact", "passed": not diffs, "differences": diffs})

    for name in ("model_systems", "abstention"):
        g = gates[name]
        rows = []
        for system in g["systems"]:
            for m in g["metrics"]:
                got = sum(_hits(fresh[s], system, m)[0] for s in samples)
                want = sum(_hits(base[s], system, m)[0] for s in samples)
                n = sum(_hits(fresh[s], system, m)[1] for s in samples)
                rows.append({"system": system, "metric": m, "fresh": got, "baseline": want,
                             "n": n, "passed": want - got <= g["max_pooled_drop"]})  # fmt: skip
        results.append({"gate": name, "passed": all(r["passed"] for r in rows), "rows": rows})

    ready = sum(_regions(fresh[s])[0] for s in samples)
    correct = sum(_regions(fresh[s])[1] for s in samples)
    ready2 = sum(_regions(fresh2[s])[0] for s in samples)
    correct2 = sum(_regions(fresh2[s])[1] for s in samples)
    held_correct = correct - correct2
    held_wrong = (ready - correct) - (ready2 - correct2)
    p1 = correct / ready if ready else 0.0
    p2 = correct2 / ready2 if ready2 else 0.0
    base_held = sum(_regions(base[s])[0] - _regions(base2[s])[0] for s in samples)
    results.append({
        "gate": "selection_2",
        "passed": held_wrong >= 2 * held_correct and p2 >= p1,
        "held_back_wrong": held_wrong, "held_back_correct": held_correct,
        "baseline_held_back": base_held,
        "precision_without": round(p1, 3), "precision_with": round(p2, 3),
    })  # fmt: skip

    g = gates["quantization_parity"]
    q4 = [_hits(fresh[s], "llm", "critical_exact_match") for s in samples]
    q8 = [_hits(_load(runs / f"eval-q8-{s}" / f"{s}-score-extents-derived.json"), "llm",
                "critical_exact_match") for s in samples]  # fmt: skip
    r4 = sum(h for h, _ in q4) / sum(n for _, n in q4)
    r8 = sum(h for h, _ in q8) / sum(n for _, n in q8)
    loss = round(100 * (r8 - r4), 1)
    results.append({
        "gate": "quantization_parity", "passed": loss <= g["max_loss_points"],
        "shipped_rate": round(r4, 3), "reference_rate": round(r8, 3), "loss_points": loss,
    })  # fmt: skip

    resources: dict[str, Any] = {}
    for quant in ("q4", "q8"):
        seconds: list[float] = []
        peak: int | None = None
        for s in samples:
            d = runs / f"eval-{quant}-{s}"
            seconds += _model_seconds(_load(d / f"{s}-{llm_ids[quant]}-extents-derived.json"))
            mem = d / "memory.txt"
            if mem.is_file():
                m = parse_memory(mem.read_text(encoding="utf-8"))
                peak = m if peak is None or (m is not None and m > peak) else peak
        resources[quant] = {
            "model_calls": len(seconds),
            "model_seconds_p50": _nearest_rank(seconds, 0.5),
            "model_seconds_p95": _nearest_rank(seconds, 0.95),
            "llama_server_peak_memory_bytes": peak,
        }
    return {
        "version": RELEASE_CHECK_VERSION,
        "regression": regression["version"],
        "passed": all(r["passed"] for r in results),
        "gates": results,
        "resources_reported_not_gated": resources,
    }


def summary_markdown(evidence: dict[str, Any]) -> str:
    lines = [f"## Release check: {'PASSED' if evidence['passed'] else 'FAILED'}", ""]
    for r in evidence["gates"]:
        mark = "pass" if r["passed"] else "**FAIL**"
        detail = ""
        if r["gate"] == "rules_exact":
            detail = "identical" if r["passed"] else "; ".join(r["differences"])
        elif "rows" in r:
            detail = ", ".join(f"{x['system']} {x['metric']} {x['fresh']} vs {x['baseline']}"
                               for x in r["rows"])  # fmt: skip
        elif r["gate"] == "selection_2":
            detail = (f"held back {r['held_back_wrong']} wrong / {r['held_back_correct']} correct; "
                      f"precision {r['precision_without']} -> {r['precision_with']}")  # fmt: skip
        elif r["gate"] == "quantization_parity":
            detail = (f"critical exact match Q4_K_M {r['shipped_rate']} vs Q8_0 "
                      f"{r['reference_rate']} (loss {r['loss_points']} points)")  # fmt: skip
        lines.append(f"- {mark} `{r['gate']}`: {detail}")
    lines += ["", "Reported, not gated (the runner is not the reference machine):", ""]
    for quant, res in evidence["resources_reported_not_gated"].items():
        peak = res["llama_server_peak_memory_bytes"]
        mem = f"{peak / 2**30:.2f} GiB" if peak else "not measured"
        lines.append(f"- {quant}: {res['model_calls']} model calls, p50 "
                     f"{res['model_seconds_p50']} s, p95 {res['model_seconds_p95']} s, "
                     f"llama-server peak memory {mem}")  # fmt: skip
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    from localitylens.release import load_release

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", required=True)
    ap.add_argument("--baseline", default="eval/reports")
    ap.add_argument("--regression", default="release/regression.json")
    ap.add_argument("--release", default="release/manifest.json")
    ap.add_argument("--reference", default="release/manifest-q8.json")
    ap.add_argument("--out", required=True, help="evidence JSON")
    ap.add_argument("--summary", help="append the Markdown summary here")
    args = ap.parse_args(argv)
    regression = json.loads(Path(args.regression).read_text(encoding="utf-8"))
    llm_ids = {"q4": load_release(Path(args.release)).extractor_id,
               "q8": load_release(Path(args.reference)).extractor_id}  # fmt: skip
    evidence = check(Path(args.runs), Path(args.baseline), regression, llm_ids)
    Path(args.out).write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    text = summary_markdown(evidence)
    print(text)
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as f:
            f.write(text)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
