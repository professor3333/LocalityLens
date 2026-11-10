"""Compute the test-3 review comparison planned in eval/calibration/test-3-review/README.md.

Counts only: no label text, names or per-record values are printed or written. Run once from
the repository root: uv run python scripts/score_test3_review.py
"""

import json
import math
from pathlib import Path
from typing import Any

from localitylens.evaluation.agreement import agreement
from localitylens.evaluation.annotations import Annotation, check_worksheet
from localitylens.evaluation.audit import load_sample
from localitylens.evaluation.score import judge
from localitylens.gazetteer.index import Gazetteer

REVIEW = Path("eval/calibration/test-3-review")
TEST3 = Path("eval/benchmark/test-3")
HYBRID = TEST3 / "reports/test-3-hybrid-1-extents-derived.json"
SCORE = TEST3 / "reports/test-3-score-hybrid-1-extents-derived.json"
STRATA = TEST3 / "diagnosis/review-strata.json"
OUT = Path("eval/reports/test-3-review.json")
SIZES = {"clause_choice_absent": 21, "clause_choice_in_gnis": 20}
READY = 53


def _annotations(worksheet: Path, sample: Path, gaz: Gazetteer) -> dict[str, Annotation]:
    check = check_worksheet(worksheet, load_sample(sample), gaz)
    if check.errors:
        raise SystemExit(f"{worksheet}: {len(check.errors)} checker errors")
    return {a.audit_id: a for a in check.annotations}


def _found_absent(a: Annotation) -> bool:
    return "absent-specific" in a.notes or a.reference_absent


def main() -> None:
    pairs: dict[str, str] = json.loads((REVIEW / "pairs.json").read_text())["pairs"]
    to_r = {p: r for r, p in pairs.items()}
    strata: dict[str, Any] = json.loads(STRATA.read_text())
    with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
        rev = _annotations(REVIEW / "worksheet.csv", REVIEW / "test-3-review.json", gaz)
        cdx = _annotations(TEST3 / "worksheet.csv", TEST3 / "test-3.json", gaz)
    report = json.loads(HYBRID.read_text())
    rows = {r["audit_id"]: r for r in next(v for v in report.values() if isinstance(v, list))}
    codex_judged = {j["audit_id"]: j for j in json.loads(SCORE.read_text())["all"]["judgements"]["hybrid"]}  # fmt: skip
    ready = {p for p, r in rows.items() if r["proposal"] == "computed"}
    if len(ready) != READY:
        raise SystemExit(f"expected {READY} ready regions, found {len(ready)}")

    def correct_under_review(p: str) -> bool:
        return judge(rev[to_r[p]], rows[p]).correct_candidate

    def correct_under_codex(p: str) -> bool:
        return bool(codex_judged[p]["correct_candidate"])

    out: dict[str, Any] = {}
    shares = {}
    for name in ("clause_choice_absent", "clause_choice_in_gnis"):
        ids = strata[name]
        entry = {
            "rows": len(ids),
            "of": SIZES[name],
            "correct_under_codex": sum(correct_under_codex(p) for p in ids),
            "correct_under_reviewer": sum(correct_under_review(p) for p in ids),
            "same_acceptable_ids_as_codex": sum(
                rev[to_r[p]].acceptable_ids == cdx[p].acceptable_ids
                and rev[to_r[p]].reference_absent == cdx[p].reference_absent
                for p in ids
            ),
            "reviewer_finds_specific_place_absent": sum(_found_absent(rev[to_r[p]]) for p in ids),
            "reviewer_category": dict(
                sorted(
                    {
                        c: sum(judge(rev[to_r[p]], rows[p]).category == c for p in ids)
                        for c in ("answerable", "reference_absent", "unsupported", "no_reference")
                    }.items()
                )
            ),
        }
        out[name] = entry
        shares[name] = entry["correct_under_reviewer"] / entry["rows"]

    unsure = strata["unsure_marker"]
    in_gnis_all = set(Path(TEST3 / "diagnosis/clause-choice-in-gnis.txt").read_text().split())
    unsure_pairs = {to_r[p]: p for p in unsure}
    ua = agreement(list(rev.values()), list(cdx.values()), unsure_pairs)
    out["unsure_rows"] = {
        "rows": len(unsure),
        "every_field_agrees": ua.every_field,
        "by_field": ua.by_field,
        "correct_under_codex": sum(correct_under_codex(p) for p in unsure),
        "correct_under_reviewer": sum(correct_under_review(p) for p in unsure),
    }

    allp = agreement(list(rev.values()), list(cdx.values()), pairs)
    out["all_23"] = {
        "agreement": allp.as_dict(),
        "ready_regions_correct_under_codex": sum(correct_under_codex(p) for p in pairs.values()),
        "ready_regions_correct_under_reviewer": sum(
            correct_under_review(p) for p in pairs.values()
        ),
    }

    # Estimate: strata scaled from their 10 seeded rows; of the 12 other ready regions, the 2
    # reviewed (unsure) rows take the reviewer's judgement and the other 10 keep Codex's.
    clause_all = in_gnis_all | set(Path(TEST3 / "diagnosis/clause-choice-absent.txt").read_text().split())  # fmt: skip
    rest = ready - clause_all
    reviewed_rest = {p for p in unsure if p in rest}
    rest_correct = sum(correct_under_review(p) for p in reviewed_rest) + sum(
        correct_under_codex(p) for p in rest - reviewed_rest
    )
    est = sum(SIZES[n] * shares[n] for n in SIZES) + rest_correct
    var = sum(
        SIZES[n] ** 2 * shares[n] * (1 - shares[n]) / out[n]["rows"] * (1 - out[n]["rows"] / SIZES[n])
        for n in SIZES
    )  # fmt: skip
    half = 1.96 * math.sqrt(var)
    out["estimate"] = {
        "label": "estimate, not a measurement",
        "ready_regions": READY,
        "correct_estimated": round(est, 1),
        "precision_estimated": round(est / READY, 3),
        "precision_95_interval_approx": [
            round(max(0.0, est - half) / READY, 3),
            round(min(READY, est + half) / READY, 3),
        ],
        "precision_under_codex": round(sum(correct_under_codex(p) for p in ready) / READY, 3),
        "other_ready_regions": {
            "rows": len(rest),
            "reviewed": len(reviewed_rest),
            "correct_used": rest_correct,
        },
        "method": "stratified: 21 x (absent-stratum share) + 20 x (in-GNIS share) + the other 12 "
        "ready regions; normal approximation with finite-population correction",
    }
    result = {
        "plan": "eval/calibration/test-3-review/README.md",
        "annotator": "Claude (at the owner's request; not a human check, and Claude wrote the "
        "systems). Compared against Codex's test-3 annotations.",
        "note": "Diagnosis of a used set; counts only. test-3's declared result stands.",
        "review_worksheet_sha256_prefix": "d4dd4b1f",
        **out,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
