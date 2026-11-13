"""Clause-choice spike: can one model call pick the collecting place in "place, offset" labels?

Feasibility on read dev data only (in-sample; no held-out set). For every "place, offset" label
(text shape 2) in the read samples, the options are hybrid-1's current reading plus each other
clause of the label that GNIS matches exactly or by core name. The model sees the label, the
supplied county and, for each option, the GNIS name, class, county and distance from the offset
point. It must answer with one option letter (schema-constrained). Prompt:
scripts/clause_choice_prompt-v1.txt, written once and run once, no tuning.

Compared, with the scorer's own judge(): hybrid-1 as it is, a plain rule (switch to a place GNIS
puts inside the offset region), the model's choice, and the best option available (oracle).
Counts only are written. Needs llama-server with the release model:

    uv run python scripts/clause_choice_spike.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from localitylens.evaluation.annotations import check_worksheet
from localitylens.evaluation.audit import annotations_by, load_sample
from localitylens.evaluation.dev_sample import text_shape
from localitylens.evaluation.score import judge
from localitylens.extract.llm_client import LlamaServerClient
from localitylens.gazetteer.index import Gazetteer
from localitylens.gazetteer.keys import name_key
from localitylens.geo.directions import CompassPoint, nominal_bearing
from localitylens.geo.geodesy import distance_m, forward
from localitylens.geo.units import LengthUnit, to_metres
from localitylens.release import load_release
from localitylens.resolve.selection import _LEADING_2, _STRONG_MATCHES

SAMPLES: dict[str, tuple[str, str]] = {
    "audit-50": ("eval/audit/audit-50.json", "eval/audit/worksheet.csv"),
    "dev-1": ("eval/dev/dev-1/dev-1.json", "eval/dev/dev-1/worksheet.csv"),
    "validation": ("eval/benchmark/validation/validation.json",
                   "eval/benchmark/validation/worksheet.csv"),
    "dev-2": ("eval/dev/dev-2/dev-2.json", "eval/dev/dev-2/worksheet.csv"),
    "dev-3": ("eval/dev/dev-3/dev-3.json", "eval/dev/dev-3/worksheet.csv"),
    "dev-4": ("eval/dev/dev-4/dev-4.json", "eval/dev/dev-4/worksheet.csv"),
}  # fmt: skip
PROMPT = Path("scripts/clause_choice_prompt-v1.txt")
OUT = Path("eval/reports/clause-choice-spike.json")
_SECTION = re.compile(r"^=== (system|user|assistant) ===$", re.M)
_NUMBER = re.compile(r"\d")


def _messages(locality: str, county: str, options: str) -> list[dict[str, str]]:
    text = PROMPT.read_text(encoding="utf-8")
    parts = _SECTION.split(text)[1:]
    msgs = [{"role": r, "content": c.strip()} for r, c in zip(parts[::2], parts[1::2], strict=True)]
    last = msgs[-1]["content"]
    msgs[-1]["content"] = (last.replace("{locality}", locality).replace("{county}", county)
                           .replace("{options}", options))  # fmt: skip
    return msgs


def _rows(path: Path) -> dict[str, dict[str, Any]]:
    report = json.loads(path.read_text())
    return {r["audit_id"]: r for r in next(v for v in report.values() if isinstance(v, list))}


def _offset_point(row: dict[str, Any], gaz: Gazetteer) -> Any:
    top = gaz.feature(row["top_candidate"]["feature_id"])
    assert top is not None
    interp = row["interpretation"]
    if row["relation"] != "distance_and_direction" or not interp.get("direction"):
        return top.primary_point
    metres = to_metres(interp["distance"], LengthUnit(interp["unit"]))
    return forward(top.primary_point, nominal_bearing(CompassPoint(interp["direction"])), metres)


def _clause_places(locality: str, reference: str, county: str | None, gaz: Gazetteer) -> list[Any]:
    """GNIS strong matches for each clause of the label other than the current reference's;
    clauses with digits (offsets, elevations) are skipped."""
    ref = name_key(reference)
    out, seen = [], set()
    for part in re.split(r"[,;:()]", locality):
        words = part.strip().rstrip(".").split()
        while words and words[0].lower().rstrip(".") in _LEADING_2:
            words = words[1:]
        phrase = " ".join(words)
        if not phrase or _NUMBER.search(phrase) or not name_key(phrase) or name_key(phrase) == ref:
            continue
        hits = [h for h in gaz.search(phrase, county=county, limit=3)
                if h.match_kind.value in _STRONG_MATCHES]  # fmt: skip
        if hits and hits[0].feature_id not in seen:
            seen.add(hits[0].feature_id)
            out.append((phrase, hits))
    return out


def main() -> None:
    release = load_release(Path("release/manifest.json"))
    client = LlamaServerClient()
    schema_for = lambda letters: {  # noqa: E731
        "type": "object", "properties": {"choice": {"enum": letters}},
        "required": ["choice"], "additionalProperties": False,
    }  # fmt: skip
    result: dict[str, Any] = {}
    with Gazetteer(Path("data/derived/gazetteer.sqlite")) as gaz:
        for label, (sample_path, worksheet) in SAMPLES.items():
            sample = load_sample(Path(sample_path))
            ann = {a.audit_id: a for a in check_worksheet(Path(worksheet), sample, gaz).annotations}
            rows = _rows(Path(f"eval/reports/{label}-hybrid-1-extents-derived.json"))
            c: Counter[str] = Counter()
            for item in sample.items:
                aid, text = item.audit_id, item.record.locality
                row = rows[aid]
                if text_shape(text, "2") != "place_offset":
                    continue
                c["place_offset_labels"] += 1
                if judge(ann[aid], row).category != "answerable":
                    c["not_answerable"] += 1
                    continue
                if not row.get("top_candidate") or not row.get("reference"):
                    c["hybrid_no_reference"] += 1
                    continue
                county = row.get("county")
                places = _clause_places(text, row["reference"], county, gaz)
                if not places:
                    c["no_other_place_in_gnis"] += 1
                    continue
                c["with_choice"] += 1
                point = _offset_point(row, gaz)
                top = row["top_candidate"]
                kind = ("Offset: " + f"{row['interpretation']['distance']:g} "
                        f"{row['interpretation']['unit']} {row['interpretation']['direction']} of "
                        if row["relation"] == "distance_and_direction" else "Current reading: ")  # fmt: skip
                lines = [f"A. {kind}{top['name']} ({top['class']}, {top['county']} Co.)"]
                judged = [judge(ann[aid], row)]
                inside_letter = None
                for i, (_phrase, hits) in enumerate(places):
                    letter = chr(ord("B") + i)
                    d_km = distance_m(point, hits[0].primary_point) / 1000
                    lines.append(f"{letter}. {hits[0].official_name} ({hits[0].feature_class}, "
                                 f"{hits[0].county_name} Co.), {d_km:.1f} km from the offset point")  # fmt: skip
                    switched = {"relation": "named_feature", "proposal": "computed",
                                "interpretation": {"relation": "named_feature", "distance": None,
                                                   "unit": None, "direction": None,
                                                   "qualifiers": []},
                                "candidate_ids": [h.feature_id for h in hits]}  # fmt: skip
                    judged.append(judge(ann[aid], switched))
                    if (inside_letter is None and row.get("radius_m")
                            and d_km * 1000 <= row["radius_m"]):  # fmt: skip
                        inside_letter = letter
                letters = [chr(ord("A") + i) for i in range(len(judged))]
                prompt = client.render(_messages(text, county or "none", "\n".join(lines)), False)
                done = client.complete(prompt, schema_for(letters), release.generation)
                pick = json.loads(done.text)["choice"]
                rule = inside_letter or "A"
                for name, letter in (("hybrid", "A"), ("inside_rule", rule), ("model", pick)):
                    j = judged[letters.index(letter)]
                    c[f"{name}_reference_ok"] += j.top1_ok
                    c[f"{name}_correct_candidate"] += j.correct_candidate
                c["oracle_reference_ok"] += any(j.top1_ok for j in judged)
                c["oracle_correct_candidate"] += any(j.correct_candidate for j in judged)
                c["model_picked_offset"] += pick == "A"
                c["model_changed_a_right_choice"] += judged[0].top1_ok and pick != "A"
                c["model_fixed_a_wrong_choice"] += (not judged[0].top1_ok
                                                    and judged[letters.index(pick)].top1_ok)  # fmt: skip
            result[label] = {"annotations": annotations_by(label), **dict(sorted(c.items()))}
            print(label, dict(sorted(c.items())), flush=True)
    OUT.write_text(json.dumps({
        "note": "Read dev data (in-sample), counts only. Prompt scripts/clause_choice_prompt-v1.txt, "
                "run once, no tuning. Options: hybrid-1's reading (A) and each other label clause "
                "GNIS matches exactly or by core name.",
        "model": release.extractor_id, "samples": result}, indent=2) + "\n")  # fmt: skip


if __name__ == "__main__":
    main()
