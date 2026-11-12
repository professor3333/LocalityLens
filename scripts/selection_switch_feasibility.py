"""Would switching to the place selection-2 found be right? A feasibility count on read dev data.

selection-2 holds a computed region when the label names another place that GNIS has inside the
region ("inside") or lacks ("absent"). This script asks, for every region it holds on the read
samples, what would happen if the pipeline used the "inside" place instead, read as a named
feature (the offset and its qualifiers dropped):
- is the place one of the annotation's acceptable GNIS IDs (top-1)?
- would the switched proposal be a correct proposal candidate (scorer's own judge())?
- does the place have an extent (reviewed or derived), so that it gets a region?

Read samples only (audit, dev-1, validation: owner-annotated; dev-2 to dev-4: Claude-annotated).
Held-out test sets are refused. Counts only are written; run from the repository root:

    uv run python scripts/selection_switch_feasibility.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from localitylens.evaluation.annotations import check_worksheet
from localitylens.evaluation.audit import annotations_by, load_sample
from localitylens.evaluation.score import judge
from localitylens.gazetteer.index import Gazetteer
from localitylens.geo.directions import CompassPoint, nominal_bearing
from localitylens.geo.extents import load_store
from localitylens.geo.geodesy import distance_m, forward
from localitylens.geo.units import LengthUnit, to_metres
from localitylens.resolve.selection import _STRONG_MATCHES, geographic_competitors

SAMPLES: dict[str, tuple[str, str]] = {
    "audit-50": ("eval/audit/audit-50.json", "eval/audit/worksheet.csv"),
    "dev-1": ("eval/dev/dev-1/dev-1.json", "eval/dev/dev-1/worksheet.csv"),
    "validation": ("eval/benchmark/validation/validation.json",
                   "eval/benchmark/validation/worksheet.csv"),
    "dev-2": ("eval/dev/dev-2/dev-2.json", "eval/dev/dev-2/worksheet.csv"),
    "dev-3": ("eval/dev/dev-3/dev-3.json", "eval/dev/dev-3/worksheet.csv"),
    "dev-4": ("eval/dev/dev-4/dev-4.json", "eval/dev/dev-4/worksheet.csv"),
}  # fmt: skip
REPORTS = Path("eval/reports")
OUT = REPORTS / "selection-switch-feasibility.json"


def _rows(path: Path) -> dict[str, dict[str, Any]]:
    report = json.loads(path.read_text())
    return {r["audit_id"]: r for r in next(v for v in report.values() if isinstance(v, list))}


def _point(row: dict[str, Any], gaz: Gazetteer) -> Any:
    """The proposal's point, recomputed as propose() does: the top candidate's GNIS point,
    moved by the offset for a distance-and-direction reading."""
    top = gaz.feature(row["top_candidate"]["feature_id"])
    assert top is not None
    interp = row["interpretation"]
    if row["relation"] != "distance_and_direction":
        return top.primary_point
    metres = to_metres(interp["distance"], LengthUnit(interp["unit"]))
    return forward(top.primary_point, nominal_bearing(CompassPoint(interp["direction"])), metres)


def main() -> None:
    out: dict[str, Any] = {}
    with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
        store = load_store(
            Path("data/reviewed/extents.csv"), gaz, derived=Path("data/extents/derived.csv")
        )
        for label, (sample_path, worksheet) in SAMPLES.items():
            if "benchmark/test" in sample_path:
                raise SystemExit("held-out test sets are never used here")
            check = check_worksheet(Path(worksheet), load_sample(Path(sample_path)), gaz)
            ann = {a.audit_id: a for a in check.annotations}
            plain = _rows(REPORTS / f"{label}-hybrid-1-extents-derived.json")
            sel2 = _rows(REPORTS / f"{label}-hybrid-1-extents-derived-sel2.json")
            c: Counter[str] = Counter()
            classes: Counter[str] = Counter()
            no_extent_classes: Counter[str] = Counter()
            for aid, row in plain.items():
                if row["proposal"] != "computed":
                    continue
                c["ready_regions"] += 1
                was_correct = judge(ann[aid], row).correct_candidate
                c["ready_correct"] += was_correct
                if sel2[aid]["proposal"] == "computed":
                    continue
                c["held"] += 1
                c["held_correct" if was_correct else "held_wrong"] += 1
                point = _point(row, gaz)
                prop = SimpleNamespace(point=point, radius_m=row["radius_m"])
                found = geographic_competitors(
                    row["locality"], row["reference"], prop, gaz, row["county"]
                )  # type: ignore[arg-type]
                inside = [n for n, why in found if why == "inside"]
                if not inside:
                    c["held_only_absent"] += 1
                    continue
                c["held_with_inside_place"] += 1
                hits = [
                    h for h in gaz.search(inside[0], county=row["county"], limit=3)
                    if h.match_kind.value in _STRONG_MATCHES
                    and distance_m(point, h.primary_point) <= row["radius_m"]
                ]  # fmt: skip
                choice = hits[0].feature_id
                switched = {
                    "relation": "named_feature",
                    "interpretation": {"relation": "named_feature", "distance": None,
                                       "unit": None, "direction": None, "qualifiers": []},
                    "candidate_ids": [h.feature_id for h in hits],
                    "proposal": "computed",
                    "retrieval": "candidates_found",
                }  # fmt: skip
                j = judge(ann[aid], switched)
                has_extent = store.get(choice) is not None
                feature = gaz.feature(choice)
                cls = feature.feature_class if feature is not None else "unknown"
                classes[cls] += 1
                if not has_extent:
                    no_extent_classes[cls] += 1
                c["switch_place_acceptable"] += j.top1_ok
                c["switch_correct_candidate"] += j.correct_candidate
                c["switch_place_has_extent"] += has_extent
                c["switch_correct_region"] += j.correct_candidate and has_extent
                c["switch_place_acceptable_but_reading_differs"] += j.top1_ok and not j.critical_ok
                c[f"held_with_inside_place_was_{'correct' if was_correct else 'wrong'}"] += 1
                c[f"switch_correct_region_was_{'correct' if was_correct else 'wrong'}"] += (
                    j.correct_candidate and has_extent
                )
            out[label] = {
                "annotations": annotations_by(label),
                **dict(sorted(c.items())),
                "switch_place_classes": dict(sorted(classes.items())),
                "switch_place_classes_without_extent": dict(sorted(no_extent_classes.items())),
            }
    result = {
        "note": "Feasibility on read dev data (in-sample, not held out). Counts only. Switched "
        "proposal = the first GNIS strong match of the first 'inside' place, read as a named "
        "feature with no qualifiers; region needs a reviewed or derived extent.",
        "samples": out,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
