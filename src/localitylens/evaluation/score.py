"""Score system reports against the owner's annotations (CLAUDE.md §7, §17).

Correctness follows the project definition: a proposal is correct only when the critical
interpretation (relation, distance, unit, direction, qualifiers) matches the annotation **and**
the selected reference feature is one of the acceptable GNIS IDs.

Nearly every proposal in the audit stops at ``needs_information`` because feature extent is
unknown, so the main comparison is the **correct proposal candidate**: an answerable record
whose critical interpretation and top-ranked reference are both right, so that it becomes a
correct proposal as soon as the extent is supplied.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Final

from localitylens.evaluation.annotations import Annotation, annotated_distance

BOOTSTRAP_RESAMPLES: Final = 10_000
BOOTSTRAP_SEED: Final = 20261101


@dataclass(frozen=True, slots=True)
class Judgement:
    audit_id: str
    category: str  # answerable | reference_absent | unsupported | no_reference
    relation_ok: bool
    valid: bool  # the extraction passed validation
    distance_ok: bool
    unit_ok: bool
    direction_ok: bool
    qualifiers_ok: bool
    critical_ok: bool
    top1_ok: bool
    recall5_ok: bool
    correct_candidate: bool
    handled_ok: bool  # unsupported → said unsupported; reference absent → said absent
    false_no_locality: bool
    computed: bool
    corrections: int  # critical fields + reference a curator would have to fix


def _category(a: Annotation) -> str:
    if not a.supported:
        return "unsupported"
    if a.acceptable_ids:
        return "answerable"
    if a.reference_absent:
        return "reference_absent"
    return "no_reference"


def judge(a: Annotation, row: dict[str, Any]) -> Judgement:
    interp = row.get("interpretation")
    valid = interp is not None
    relation_ok = row.get("relation") == a.relation.value
    want_distance = annotated_distance(a.distance) if a.distance else None
    if interp is None:
        distance_ok = unit_ok = direction_ok = qualifiers_ok = False
    else:
        got = interp["distance"]
        if a.distance:
            distance_ok = (
                want_distance is not None and got is not None and math.isclose(got, want_distance)
            )
        else:
            distance_ok = got is None
        unit_ok = interp["unit"] == (a.unit.value if a.unit else None)
        direction_ok = interp["direction"] == (a.direction.value if a.direction else None)
        qualifiers_ok = set(interp["qualifiers"]) == set(a.qualifiers)
    critical_ok = (
        valid and relation_ok and distance_ok and unit_ok and direction_ok and qualifiers_ok
    )
    candidates: list[int] = row.get("candidate_ids") or []
    top1_ok = bool(candidates) and candidates[0] in a.acceptable_ids
    recall5_ok = any(c in a.acceptable_ids for c in candidates[:5])
    category = _category(a)
    if category == "unsupported":
        handled_ok = row.get("proposal") == "unsupported"
    elif category == "reference_absent":
        handled_ok = row.get("retrieval") == "feature_absent_from_index"
    else:
        handled_ok = False
    fields_wrong = sum(not ok for ok in (relation_ok, distance_ok, unit_ok, direction_ok,
                                         qualifiers_ok))  # fmt: skip
    return Judgement(
        audit_id=a.audit_id,
        category=category,
        relation_ok=relation_ok,
        valid=valid,
        distance_ok=distance_ok,
        unit_ok=unit_ok,
        direction_ok=direction_ok,
        qualifiers_ok=qualifiers_ok,
        critical_ok=critical_ok,
        top1_ok=top1_ok,
        recall5_ok=recall5_ok,
        correct_candidate=category == "answerable" and critical_ok and top1_ok,
        handled_ok=handled_ok,
        false_no_locality=row.get("relation") == "no_locality"
        and a.description_type != "no_locality",
        computed=row.get("proposal") == "computed",
        corrections=fields_wrong + (0 if category != "answerable" or top1_ok else 1),
    )


def _rate(hits: int, n: int) -> dict[str, Any]:
    return {"hits": hits, "n": n, "rate": round(hits / n, 3) if n else None}


def summarize(judgements: list[Judgement]) -> dict[str, Any]:
    answerable = [j for j in judgements if j.category == "answerable"]
    unsupported = [j for j in judgements if j.category == "unsupported"]
    absent = [j for j in judgements if j.category == "reference_absent"]
    computed = [j for j in judgements if j.computed]
    return {
        "relation_accuracy": _rate(sum(j.relation_ok for j in judgements), len(judgements)),
        "valid_extraction": _rate(sum(j.valid for j in judgements), len(judgements)),
        "critical_exact_match": _rate(sum(j.critical_ok for j in judgements), len(judgements)),
        "field_accuracy": {
            name: _rate(sum(getattr(j, f"{name}_ok") for j in judgements), len(judgements))
            for name in ("distance", "unit", "direction", "qualifiers")
        },
        "reference_top1": _rate(sum(j.top1_ok for j in answerable), len(answerable)),
        "reference_recall5": _rate(sum(j.recall5_ok for j in answerable), len(answerable)),
        "correct_proposal_candidates": _rate(
            sum(j.correct_candidate for j in answerable), len(answerable)
        ),
        "computed_proposals_correct": _rate(
            sum(j.correct_candidate for j in computed), len(computed)
        ),
        "unsupported_flagged": _rate(sum(j.handled_ok for j in unsupported), len(unsupported)),
        "absent_reported_absent": _rate(sum(j.handled_ok for j in absent), len(absent)),
        "false_no_locality": sum(j.false_no_locality for j in judgements),
        "mean_corrections": round(sum(j.corrections for j in judgements) / len(judgements), 2)
        if judgements
        else None,
    }


def sign_test_p(b: int, c: int) -> float:
    """Exact two-sided sign (McNemar) test on discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (1 << n)
    return min(1.0, 2 * tail)


def paired(rules: list[bool], llm: list[bool]) -> dict[str, Any]:
    """LLM minus rules on the same records, with a percentile bootstrap interval."""
    n = len(rules)
    b = sum(lm and not r for r, lm in zip(rules, llm, strict=True))
    c = sum(r and not lm for r, lm in zip(rules, llm, strict=True))
    rng = random.Random(BOOTSTRAP_SEED)
    diffs = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(llm[i] - rules[i] for i in idx) / n)
    diffs.sort()
    lo = diffs[int(0.025 * BOOTSTRAP_RESAMPLES)]
    hi = diffs[int(0.975 * BOOTSTRAP_RESAMPLES) - 1]
    return {
        "n": n,
        "rules": sum(rules),
        "llm": sum(llm),
        "difference": round((sum(llm) - sum(rules)) / n, 3) if n else None,
        "ci95": [round(lo, 3), round(hi, 3)],
        "llm_only": b,
        "rules_only": c,
        "sign_test_p": round(sign_test_p(b, c), 4),
    }


def score(
    annotations: list[Annotation],
    reports: dict[str, dict[str, Any]],
    exclude_unsure: bool = False,
) -> dict[str, Any]:
    used = [a for a in annotations if not (exclude_unsure and a.unsure_columns)]
    rows = {name: {r["audit_id"]: r for r in rep["records"]} for name, rep in reports.items()}
    judged = {name: [judge(a, rows[name][a.audit_id]) for a in used] for name in reports}
    out: dict[str, Any] = {
        "records": len(used),
        "excluded_unsure": len(annotations) - len(used),
        "annotated_types": dict(Counter(a.description_type for a in used).most_common()),
        "categories": dict(Counter(_category(a) for a in used).most_common()),
        "systems": {name: summarize(js) for name, js in judged.items()},
        "by_type": {
            name: {
                t: _rate(
                    sum(
                        j.correct_candidate
                        for j, a in zip(js, used, strict=True)
                        if a.description_type == t
                    ),
                    sum(
                        1 for a in used if a.description_type == t and _category(a) == "answerable"
                    ),
                )
                for t in sorted({a.description_type for a in used})
            }
            for name, js in judged.items()
        },
        "judgements": {name: [asdict(j) for j in js] for name, js in judged.items()},
    }
    if {"rules", "llm"} <= set(judged):
        ans = [i for i, a in enumerate(used) if _category(a) == "answerable"]
        out["paired_correct_proposal_candidates"] = paired(
            [judged["rules"][i].correct_candidate for i in ans],
            [judged["llm"][i].correct_candidate for i in ans],
        )
        out["paired_critical_exact_match"] = paired(
            [j.critical_ok for j in judged["rules"]], [j.critical_ok for j in judged["llm"]]
        )
    return out


_HEADLINE: Final = (
    ("relation_accuracy", "Relation read correctly"),
    ("valid_extraction", "Extraction passed validation"),
    ("critical_exact_match", "Critical interpretation exact"),
    ("reference_top1", "Reference top-1 acceptable (answerable)"),
    ("reference_recall5", "Reference in top 5 (answerable)"),
    ("correct_proposal_candidates", "**Correct proposal candidates** (answerable)"),
    ("computed_proposals_correct", "Computed proposals that are correct"),
    ("unsupported_flagged", "Unsupported records flagged unsupported"),
    ("absent_reported_absent", "References absent from GNIS reported absent"),
)


def _cell(r: dict[str, Any]) -> str:
    return f"{r['hits']}/{r['n']}" + (f" ({r['rate']:.0%})" if r["rate"] is not None else "")


def write_score_report(
    full: dict[str, Any], sure: dict[str, Any], meta: dict[str, str], directory: Any
) -> tuple[Any, Any]:
    import json
    from pathlib import Path

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = "audit-50-score"
    json_path = directory / f"{stem}.json"
    json_path.write_text(
        json.dumps({"meta": meta, "all": full, "excluding_unsure": sure}, indent=2) + "\n",
        "utf-8",
    )
    systems = list(full["systems"])
    md = [
        "# 50-record audit: scores against the owner's annotations",
        "",
        " · ".join(f"{k} `{v}`" for k, v in meta.items()),
        "",
        f"Annotated records: {full['records']}. Categories: "
        + " · ".join(f"{k} {v}" for k, v in full["categories"].items())
        + ". Annotated types: "
        + " · ".join(f"{k} {v}" for k, v in full["annotated_types"].items())
        + ".",
        "",
        "> A **correct proposal candidate** is an answerable record whose critical "
        "interpretation (relation, distance, unit, direction, qualifiers) matches the annotation "
        "and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal "
        "once the feature extent is supplied. One annotator; 50 records; wide intervals.",
        "",
        "| Metric | " + " | ".join(systems) + " |",
        "|---|" + "---|" * len(systems),
    ]
    for key, label in _HEADLINE:
        md.append(f"| {label} | " + " | ".join(_cell(full["systems"][s][key]) for s in systems)
                  + " |")  # fmt: skip
    for key, label in (("false_no_locality", "Place names read as no locality"),
                       ("mean_corrections", "Mean fields to correct per record")):  # fmt: skip
        md.append(f"| {label} | " + " | ".join(str(full["systems"][s][key]) for s in systems)
                  + " |")  # fmt: skip
    for key, label in (("paired_correct_proposal_candidates", "correct proposal candidates"),
                       ("paired_critical_exact_match", "critical exact match")):  # fmt: skip
        if key in full:
            p = full[key]
            md += ["", f"**Paired, {label} (LLM \u2212 rules):** {p['difference']:+.0%} "
                   f"(95% bootstrap CI {p['ci95'][0]:+.0%} to {p['ci95'][1]:+.0%}); "
                   f"LLM-only {p['llm_only']}, rules-only {p['rules_only']}, "
                   f"exact sign test p = {p['sign_test_p']}."]  # fmt: skip
    md += ["", f"<details><summary><b>Sensitivity: excluding {sure['excluded_unsure']} rows "
           "with an unsure (?) annotation</b></summary>", "",
           "| Metric | " + " | ".join(systems) + " |", "|---|" + "---|" * len(systems)]  # fmt: skip
    for key, label in _HEADLINE:
        md.append(f"| {label} | " + " | ".join(_cell(sure["systems"][s][key]) for s in systems)
                  + " |")  # fmt: skip
    if "paired_correct_proposal_candidates" in sure:
        p = sure["paired_correct_proposal_candidates"]
        ci = f"{p['ci95'][0]:+.0%} to {p['ci95'][1]:+.0%}"
        md += ["", f"Paired correct proposal candidates: {p['difference']:+.0%} "
               f"(CI {ci}), p = {p['sign_test_p']}."]  # fmt: skip
    md += ["", "</details>", "", "<details><summary><b>Correct proposal candidates by annotated "
           "type</b></summary>", "", "| Type | " + " | ".join(systems) + " |",
           "|---|" + "---|" * len(systems)]  # fmt: skip
    for t in full["by_type"][systems[0]]:
        md.append(f"| {t} | " + " | ".join(_cell(full["by_type"][s][t]) for s in systems) + " |")
    md += ["", "</details>", "", "<details><summary><b>Per record</b> (C = critical "
           "interpretation, R = top-1 reference, ✓ correct candidate)</summary>", "",
           "| id | category | " + " | ".join(systems) + " |",
           "|---|---|" + "---|" * len(systems)]  # fmt: skip
    rows = {s: full["judgements"][s] for s in systems}
    for i, j0 in enumerate(rows[systems[0]]):
        cells = []
        for s in systems:
            j = rows[s][i]
            mark = "✓" if j["correct_candidate"] else ""
            c = "+" if j["critical_ok"] else "\u2212"
            r = "+" if j["top1_ok"] else "\u2212"
            cells.append(f"C{c} R{r} {mark}")
        md.append(f"| {j0['audit_id']} | {j0['category']} | " + " | ".join(cells) + " |")
    md += ["", "</details>", ""]
    md_path = directory / f"{stem}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    return json_path, md_path
