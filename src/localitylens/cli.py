"""Command-line entry point: ``localitylens <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from localitylens.extract.schema import FeatureType


def _fetch_gnis(args: argparse.Namespace) -> int:
    from localitylens.data.gnis_fetch import fetch_gnis

    path, manifest = fetch_gnis(Path(args.raw_root), Path(args.manifest_dir))
    print(f"{manifest.snapshot_id} -> {path}")
    for f in manifest.files:
        print(f"  {f.name}  {f.size_bytes:>11,} bytes  sha256={f.sha256}")
    return 0


def _build(args: argparse.Namespace) -> int:
    from localitylens.data.manifest import load_manifest
    from localitylens.gazetteer.index import build_index

    snapshot = Path(args.snapshot)
    manifest = load_manifest(snapshot / "manifest.json")
    build_index(snapshot, manifest, Path(args.out))
    print(f"built {args.out} from {manifest.snapshot_id}")
    return 0


def _search(args: argparse.Namespace) -> int:
    from localitylens.gazetteer.index import Gazetteer

    ftype = FeatureType(args.type) if args.type else None
    with Gazetteer(Path(args.index)) as gaz:
        results = gaz.search(
            args.name, state=args.state, county=args.county, feature_type=ftype, limit=args.limit
        )
        if not results:
            print("feature_absent_from_index")
            return 0
        for c in results:
            flags = " ".join(
                f"{k}={'y' if v else 'n'}"
                for k, v in (
                    ("type", c.type_match), ("county", c.county_match), ("state", c.state_match)
                )
                if v is not None
            )  # fmt: skip
            print(
                f"{c.feature_id:>8}  {c.official_name:<32} {c.feature_class:<16} "
                f"{c.county_name:<12} {c.match_kind.value:<15} sim={c.name_similarity:5.1f} "
                f"{flags}  ({c.primary_point.latitude:.5f}, {c.primary_point.longitude:.5f})"
            )
    return 0


def _baseline_run(args: argparse.Namespace) -> int:
    import json

    from localitylens.baseline.rules import Lexicon, RulesExtractor
    from localitylens.extract.validate import Severity
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.pipeline.interpret import interpret

    with Gazetteer(Path(args.index)) as gaz:
        extractor = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        result = interpret(args.text, extractor, gaz, supplied_county=args.county, limit=args.limit)

    interp = result.validation.interpretation
    retrieval = result.retrieval
    if args.json:
        payload = {
            "extractor": result.extractor_version,
            "normalized_text": result.text.text,
            "extraction": result.extraction.model_dump(mode="json"),
            "interpretation": interp.model_dump(mode="json") if interp else None,
            "issues": [
                {"code": i.code.value, "severity": i.severity.value, "path": i.path}
                for i in result.validation.issues
            ],
            "retrieval": None
            if retrieval is None
            else {
                "outcome": retrieval.outcome.value,
                "query": retrieval.query,
                "county_context": retrieval.county_context,
                "county_source": retrieval.county_source,
                "candidates": [c.model_dump(mode="json") for c in retrieval.candidates],
            },
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    def span(s: object) -> str:
        return f"[{getattr(s, 'start', '?')}:{getattr(s, 'end', '?')}]"

    rows: list[tuple[str, str]] = [("extractor", result.extractor_version)]
    errors = [i for i in result.validation.issues if i.severity is Severity.ERROR]
    if interp is None:
        rows.append(("validation", "FAILED: " + ", ".join(i.code.value for i in errors)))
    else:
        rows.append(("relation", interp.relation.value))
        if interp.relation_span:
            rows.append(("quote", f'"{interp.relation_span.text}" {span(interp.relation_span)}'))
        if f := interp.reference_feature:
            ftype = f" type={f.feature_type.value}" if f.feature_type else ""
            rows.append(("feature", f"{f.name} {span(f.span)}{ftype}"))
        if d := interp.distance:
            unit = d.unit.value if d.unit else "(unit missing)"
            rows.append(("distance", f"{d.quantity.value:g} {unit} {span(d.value_span)}"))
        if r := interp.direction:
            rows.append(("direction", f"{r.point.value} {span(r.span)}"))
        if interp.admin_mentions:
            admin = " · ".join(f'{a.level.value} "{a.span.text}"' for a in interp.admin_mentions)
            rows.append(("admin", admin))
        if interp.qualifiers:
            rows.append(("qualifiers", ", ".join(q.kind.value for q in interp.qualifiers)))
        rows.append(("missing", ", ".join(m.value for m in interp.missing) or "none"))
        for q in interp.open_questions:
            rows.append(("question", q))
    if retrieval is not None:
        context = (
            f" (county context: {retrieval.county_context}, from {retrieval.county_source})"
            if retrieval.county_context
            else ""
        )
        rows.append(("retrieval", retrieval.outcome.value + context))
    for key, value in rows:
        print(f"{key:<11} {value}")
    if retrieval is not None:
        for n, c in enumerate(retrieval.candidates, 1):
            flags = " ".join(
                f"{k}={'y' if v else 'n'}"
                for k, v in (("type", c.type_match), ("county", c.county_match))
                if v is not None
            )
            print(
                f"  {n}. {c.feature_id:>7}  {c.official_name:<26} {c.feature_class:<15} "
                f"{c.county_name:<12} {c.match_kind.value:<15} {flags}"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="localitylens")
    sub = parser.add_subparsers(dest="command", required=True)

    data = sub.add_parser("data", help="source snapshots").add_subparsers(
        dest="data_command", required=True
    )
    fg = data.add_parser("fetch-gnis", help="download a GNIS Colorado snapshot + manifest")
    fg.add_argument("--raw-root", default="data/raw/gnis")
    fg.add_argument("--manifest-dir", default="data/manifests")
    fg.set_defaults(func=_fetch_gnis)

    gaz = sub.add_parser("gazetteer", help="GNIS name index").add_subparsers(
        dest="gaz_command", required=True
    )
    b = gaz.add_parser("build", help="build the SQLite index from a verified snapshot")
    b.add_argument("--snapshot", required=True, help="data/raw/gnis/<publication date>")
    b.add_argument("--out", default="data/derived/gazetteer.sqlite")
    b.set_defaults(func=_build)

    s = gaz.add_parser("search", help="look up a place name")
    s.add_argument("name")
    s.add_argument("--index", default="data/derived/gazetteer.sqlite")
    s.add_argument("--state", default="Colorado")
    s.add_argument("--county")
    s.add_argument("--type", choices=[t.value for t in FeatureType])
    s.add_argument("--limit", type=int, default=5)
    s.set_defaults(func=_search)

    base = sub.add_parser("baseline", help="rules baseline").add_subparsers(
        dest="baseline_command", required=True
    )
    br = base.add_parser("run", help="interpret one locality description with the rules")
    br.add_argument("text")
    br.add_argument("--county", help="county from the record's structured fields")
    br.add_argument("--index", default="data/derived/gazetteer.sqlite")
    br.add_argument("--limit", type=int, default=5)
    br.add_argument("--json", action="store_true", help="machine-readable output")
    br.set_defaults(func=_baseline_run)

    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
