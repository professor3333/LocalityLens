"""The 50-record feasibility audit: sample, annotation worksheet, and a rules-baseline run.

Sampling is per duplicate-locality group, not per specimen: a curator georeferences each
distinct locality once, so a frequent label ("Boulder.") counts once. Groups are ordered by
``sha256(seed | group_key)``, which is reproducible from the snapshot and the seed alone.

Order of work: the owner annotates ``worksheet.csv`` first, then opens the rules report.
Audited records (and their groups) must be assigned to the dev split, never to test.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from localitylens.ingest.specimens import SpecimenRecord

AUDIT_VERSION: Final = "1"
WORKSHEET_COLUMNS: Final = (
    "audit_id", "gbif_id", "county", "locality",
    # filled in by the annotator, before looking at any system output:
    "description_type", "supported", "reference_features", "acceptable_gnis_ids",
    "distance", "unit", "direction", "qualifiers", "missing_information", "notes",
)  # fmt: skip


class AuditItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    audit_id: str
    group_size: int  # specimens in the snapshot sharing this locality group
    record: SpecimenRecord


class AuditSample(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    audit_version: str = AUDIT_VERSION
    snapshot_id: str
    screen_version: str
    grouping_version: str
    seed: str
    eligible_records: int
    eligible_groups: int
    items: tuple[AuditItem, ...]


def _rank(seed: str, key: str) -> str:
    return hashlib.sha256(f"{seed}|{key}".encode()).hexdigest()


def sample_groups(
    records: Iterable[SpecimenRecord], n: int, seed: str
) -> tuple[list[AuditItem], int, int]:
    """``n`` groups by seeded hash order; each represented by its lowest gbifID record."""
    representative: dict[str, SpecimenRecord] = {}
    sizes: Counter[str] = Counter()
    total = 0
    for record in records:
        total += 1
        sizes[record.group_key] += 1
        current = representative.get(record.group_key)
        if current is None or int(record.gbif_id) < int(current.gbif_id):
            representative[record.group_key] = record
    chosen = sorted(representative, key=lambda k: _rank(seed, k))[:n]
    items = [
        AuditItem(audit_id=f"A{i:02d}", group_size=sizes[k], record=representative[k])
        for i, k in enumerate(chosen, start=1)
    ]
    return items, total, len(representative)


def write_sample(sample: AuditSample, directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    sample_path = directory / "audit-50.json"
    sample_path.write_text(sample.model_dump_json(indent=2) + "\n", encoding="utf-8")
    worksheet = directory / "worksheet.csv"
    with worksheet.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(WORKSHEET_COLUMNS)
        for item in sample.items:
            r = item.record
            writer.writerow([item.audit_id, r.gbif_id, r.county, r.locality])
    return sample_path, worksheet


def load_sample(path: Path) -> AuditSample:
    return AuditSample.model_validate_json(path.read_text(encoding="utf-8"))


def run_rules(sample: AuditSample, index: Path, limit: int = 5) -> dict[str, Any]:
    """Run the rules baseline + uncertainty policy on every audited record (model input only)."""
    from localitylens.baseline.rules import Lexicon, RulesExtractor
    from localitylens.extract.validate import Severity
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo import uncertainty as policy
    from localitylens.geo.georeference import propose
    from localitylens.pipeline.interpret import interpret

    rows: list[dict[str, Any]] = []
    with Gazetteer(index) as gaz:
        extractor = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        gazetteer_snapshot = gaz.snapshot_id
        for item in sample.items:
            model_input = item.record.model_input()  # the allowlist is the only door in
            result = interpret(
                model_input.locality,
                extractor,
                gaz,
                supplied_county=model_input.county or None,
                limit=limit,
            )
            interp = result.validation.interpretation
            retrieval = result.retrieval
            top = retrieval.candidates[0] if retrieval and retrieval.candidates else None
            proposal = propose(interp, top) if interp is not None else None
            rows.append(
                {
                    "audit_id": item.audit_id,
                    "locality": model_input.locality,
                    "county": model_input.county,
                    "relation": result.extraction.relation.value,
                    "reference": (
                        interp.reference_feature.name
                        if interp is not None and interp.reference_feature is not None
                        else None
                    ),
                    "validation_errors": [
                        i.code.value
                        for i in result.validation.issues
                        if i.severity is Severity.ERROR
                    ],
                    "retrieval": retrieval.outcome.value if retrieval else None,
                    "candidates": len(retrieval.candidates) if retrieval else 0,
                    "top_candidate": None
                    if top is None
                    else {
                        "feature_id": top.feature_id,
                        "name": top.official_name,
                        "class": top.feature_class,
                        "county": top.county_name,
                        "match": top.match_kind.value,
                    },
                    "proposal": proposal.outcome.value if proposal else None,
                    "radius_lower_bound_m": (
                        round(proposal.radius_lower_bound_m)
                        if proposal and proposal.radius_lower_bound_m is not None
                        else None
                    ),
                    "radius_m": (
                        round(proposal.radius_m) if proposal and proposal.radius_m else None
                    ),
                }
            )
    return {
        "audit_version": sample.audit_version,
        "system": "rules",
        "extractor_version": extractor.version,
        "gazetteer_snapshot": gazetteer_snapshot,
        "specimen_snapshot": sample.snapshot_id,
        "uncertainty_policy": policy.POLICY_ID,
        "seed": sample.seed,
        "note": (
            "System output only. Correctness needs the owner's annotations; the top candidate is "
            "the rules ranking, not a reviewed choice, and no extent was supplied."
        ),
        "counts": {
            "relation": dict(Counter(r["relation"] for r in rows).most_common()),
            "retrieval": dict(Counter(str(r["retrieval"]) for r in rows).most_common()),
            "proposal": dict(Counter(str(r["proposal"]) for r in rows).most_common()),
        },
        "records": rows,
    }


def write_report(report: dict[str, Any], directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"audit-50-{report['extractor_version']}"
    json_path = directory / f"{stem}.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8")
    md = [
        f"# 50-record audit: {report['system']} baseline (`{report['extractor_version']}`)",
        "",
        f"Specimens `{report['specimen_snapshot']}` · gazetteer `{report['gazetteer_snapshot']}` "
        f"· policy `{report['uncertainty_policy']}` · seed `{report['seed']}`",
        "",
        f"> {report['note']}",
        "",
    ]
    for name, counts in report["counts"].items():
        md += [f"**{name}**: " + " · ".join(f"`{k}` {v}" for k, v in counts.items()), ""]
    md += [
        "| id | locality | relation | reference | retrieval | top candidate | proposal |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in report["records"]:
        top = r["top_candidate"]
        cand = f"{top['name']} ({top['class']}, {top['county']}, {top['match']})" if top else ""
        loc = r["locality"].replace("|", "\\|")
        md.append(
            f"| {r['audit_id']} | {loc} | {r['relation']} | {r['reference'] or ''} | "
            f"{r['retrieval'] or ''} | {cand} | {r['proposal'] or ''} |"
        )
    md_path = directory / f"{stem}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return json_path, md_path
