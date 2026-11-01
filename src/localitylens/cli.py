"""Command-line entry point: ``localitylens <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from localitylens.extract.schema import FeatureType

if TYPE_CHECKING:
    from localitylens.geo.georeference import GeoreferenceProposal


def _fetch_gnis(args: argparse.Namespace) -> int:
    from localitylens.data.gnis_fetch import fetch_gnis

    path, manifest = fetch_gnis(Path(args.raw_root), Path(args.manifest_dir))
    print(f"{manifest.snapshot_id} -> {path}")
    for f in manifest.files:
        print(f"  {f.name}  {f.size_bytes:>11,} bytes  sha256={f.sha256}")
    return 0


def _fetch_gbif(args: argparse.Namespace) -> int:
    from localitylens.data.gbif_fetch import fetch_gbif, read_credentials

    credentials = None if args.key else read_credentials(Path(args.env))
    path, manifest = fetch_gbif(
        Path(args.raw_root),
        Path(args.manifest_dir),
        credentials,
        key=args.key,
        poll_s=args.poll_seconds,
        on_status=lambda s: print(f"  {s}", flush=True),
    )
    print(f"{manifest.snapshot_id} -> {path}")
    print(f"  doi        https://doi.org/{manifest.doi}")
    print(f"  records    {manifest.record_count:,}" if manifest.record_count else "  records    ?")
    for f in manifest.files:
        print(f"  {f.name}  {f.size_bytes:>11,} bytes  sha256={f.sha256}")
    return 0


def _ingest_scan(args: argparse.Namespace) -> int:
    from localitylens.ingest.specimens import ExclusionReason, ScreenSummary, iter_snapshot

    summary = ScreenSummary(snapshot_id="")
    for _ in iter_snapshot(Path(args.snapshot), summary):
        pass
    print(f"{summary.snapshot_id}: {summary.total:,} records")
    print(
        f"  eligible            {summary.eligible:>8,}  in {len(summary.groups):,} locality groups"
    )
    for reason in ExclusionReason:
        print(f"  {reason.value:<22}{summary.excluded[reason]:>8,}")
    return 0


def _audit_sample(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import AuditSample, sample_groups, write_sample
    from localitylens.ingest.specimens import (
        GROUPING_VERSION,
        SCREEN_VERSION,
        ScreenSummary,
        iter_snapshot,
    )

    summary = ScreenSummary(snapshot_id="")
    items, records, groups = sample_groups(
        iter_snapshot(Path(args.snapshot), summary), args.n, args.seed
    )
    sample = AuditSample(
        snapshot_id=summary.snapshot_id,
        screen_version=SCREEN_VERSION,
        grouping_version=GROUPING_VERSION,
        seed=args.seed,
        eligible_records=records,
        eligible_groups=groups,
        items=tuple(items),
    )
    sample_path, worksheet, written = write_sample(sample, Path(args.out))
    print(f"{len(items)} of {groups:,} locality groups ({records:,} eligible records)")
    print(f"  sample     {sample_path}")
    if written:
        print(f"  worksheet  {worksheet}  (annotate before opening any system report)")
    else:
        print(f"  worksheet  {worksheet}  exists; left untouched")
    return 0


def _audit_rules(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import load_sample, run_rules, write_report

    report = run_rules(load_sample(Path(args.sample)), Path(args.index))
    json_path, md_path = write_report(report, Path(args.out))
    for name, counts in report["counts"].items():
        print(f"{name:<10} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _model_fetch(args: argparse.Namespace) -> int:
    from localitylens.data.model_fetch import copy_progress, fetch_model
    from localitylens.release import load_release

    pin = load_release(Path(args.release)).model
    print(f"{pin.id} @ {pin.upstream_revision[:12]}  {pin.gguf_repo}/{pin.gguf_file}")
    path = fetch_model(Path(args.models_dir), pin, progress=copy_progress(pin.gguf_size_bytes))
    print(f"verified {path}  sha256={pin.gguf_sha256}")
    return 0


def _model_check(args: argparse.Namespace) -> int:
    from localitylens.extract.llm_client import LlamaServerClient, ModelCallError
    from localitylens.release import load_release

    release = load_release(Path(args.release))
    try:
        props = LlamaServerClient(args.url).props()
    except ModelCallError as exc:
        print(f"  BAD  server           {exc.category.value}: {exc.detail}", file=sys.stderr)
        return 3
    model_path = str(props.get("model_path", ""))
    build = str(props.get("build_info", ""))
    n_ctx = (props.get("default_generation_settings") or {}).get("n_ctx")
    checks = {
        "model file": (Path(model_path).name == release.model.gguf_file, model_path),
        "llama.cpp build": (build == release.server.llama_cpp_build, build),
        "context": (n_ctx == release.context_budget_tokens, n_ctx),
    }
    for name, (ok, value) in checks.items():
        print(f"  {'ok ' if ok else 'BAD'}  {name:<16} {value}")
    return 0 if all(ok for ok, _ in checks.values()) else 1


def _audit_llm(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import load_sample, run_llm, write_report
    from localitylens.extract.llm_client import LlamaServerClient, ModelCallError
    from localitylens.release import load_release

    client = LlamaServerClient(args.url)
    try:
        props = client.props()
    except ModelCallError as exc:
        print(f"failed     {exc.category.value}: {exc.detail}", file=sys.stderr)
        return 3
    server = {
        "build_info": props.get("build_info"),
        "model_file": Path(str(props.get("model_path", ""))).name,
        "n_ctx": (props.get("default_generation_settings") or {}).get("n_ctx"),
    }
    release = load_release(Path(args.release))
    report = run_llm(
        load_sample(Path(args.sample)), Path(args.index), client, release, server=server
    )
    json_path, md_path = write_report(report, Path(args.out))
    for name, counts in report["counts"].items():
        print(f"{name:<10} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _audit_score(args: argparse.Namespace) -> int:
    import json

    from localitylens.evaluation.annotations import check_worksheet
    from localitylens.evaluation.audit import load_sample
    from localitylens.evaluation.score import score, write_score_report
    from localitylens.gazetteer.index import Gazetteer

    sample = load_sample(Path(args.sample))
    with Gazetteer(Path(args.index)) as gaz:
        check = check_worksheet(Path(args.worksheet), sample, gaz)
    for p in check.problems:
        print(f"  {p.level.value:<7} {p.audit_id:<4} {p.column:<20} {p.message}")
    if check.errors:
        print(f"{len(check.errors)} worksheet errors; fix them before scoring", file=sys.stderr)
        return 2
    reports = {
        "rules": json.loads(Path(args.rules).read_text(encoding="utf-8")),
        "llm": json.loads(Path(args.llm).read_text(encoding="utf-8")),
    }
    meta = {name: rep["extractor_version"] for name, rep in reports.items()}
    meta["specimens"] = sample.snapshot_id
    full = score(check.annotations, reports)
    sure = score(check.annotations, reports, exclude_unsure=True)
    json_path, md_path = write_score_report(full, sure, meta, Path(args.out))
    for key in ("critical_exact_match", "reference_top1", "correct_proposal_candidates"):
        cells = "  ".join(
            f"{n}={full['systems'][n][key]['hits']}/{full['systems'][n][key]['n']}" for n in reports
        )
        print(f"{key:<28} {cells}")
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _dev_register(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import load_sample
    from localitylens.evaluation.dev_sample import register

    sample = load_sample(Path(args.sample))
    groups = register(Path(args.registry), args.name, (i.record.group_key for i in sample.items))
    print(f"registered {len(sample.items)} groups as {args.name!r}; {len(groups)} viewed in total")
    return 0


def _dev_sample(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import AuditSample, write_sample
    from localitylens.evaluation.dev_sample import (
        SHAPE_VERSION,
        load_registry,
        register,
        sample_strata,
    )
    from localitylens.ingest.specimens import (
        GROUPING_VERSION,
        SCREEN_VERSION,
        ScreenSummary,
        iter_snapshot,
    )

    quotas = {}
    for q in args.quota:
        shape, _, count = q.partition("=")
        quotas[shape] = int(count)
    registry = Path(args.registry)
    viewed = {k for k, name in load_registry(registry).items() if name != args.name}
    summary = ScreenSummary(snapshot_id="")
    items, records, groups, skipped = sample_strata(
        iter_snapshot(Path(args.snapshot), summary), quotas, args.seed, viewed, args.prefix
    )
    sample = AuditSample(
        snapshot_id=summary.snapshot_id,
        screen_version=SCREEN_VERSION,
        grouping_version=GROUPING_VERSION,
        seed=args.seed,
        eligible_records=records,
        eligible_groups=groups,
        items=tuple(items),
        name=args.name,
        shape_version=SHAPE_VERSION,
        strata=quotas,
        excluded_viewed_groups=skipped,
    )
    sample_path, worksheet, written = write_sample(sample, Path(args.out), args.name)
    total = register(registry, args.name, (i.record.group_key for i in items))
    print(f"{args.name}: {len(items)} groups ({', '.join(f'{k} {v}' for k, v in quotas.items())})")
    print(f"  excluded {skipped} already-viewed groups; {len(total)} groups now registered")
    print(f"  sample     {sample_path}")
    state = "(annotate before any system runs on it)" if written else "exists; left untouched"
    print(f"  worksheet  {worksheet}  {state}")
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
    from localitylens.extract.llm_client import ModelCallError
    from localitylens.extract.validate import Severity
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.pipeline.interpret import Extractor, interpret

    with Gazetteer(Path(args.index)) as gaz:
        extractor: Extractor
        if getattr(args, "system", "rules") == "llm":
            from localitylens.extract.llm import LLMExtractor
            from localitylens.extract.llm_client import LlamaServerClient
            from localitylens.release import load_release

            extractor = LLMExtractor(LlamaServerClient(args.url), load_release(Path(args.release)))
        else:
            extractor = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        try:
            result = interpret(
                args.text, extractor, gaz, supplied_county=args.county, limit=args.limit
            )
        except ModelCallError as exc:
            print(f"failed     {exc.category.value}: {exc.detail}", file=sys.stderr)
            return 3

    interp = result.validation.interpretation
    retrieval = result.retrieval
    proposal = None
    if args.propose and interp is not None:
        from localitylens.geo.georeference import ExtentEstimate, ExtentSource, propose

        chosen = None
        if retrieval is not None and retrieval.candidates:
            if args.feature_id is None:
                chosen = retrieval.candidates[0]
            else:
                chosen = next(
                    (c for c in retrieval.candidates if c.feature_id == args.feature_id), None
                )
                if chosen is None:
                    print(f"feature {args.feature_id} is not among the candidates", file=sys.stderr)
                    return 2
        extent = (
            ExtentEstimate(
                radius_m=args.extent_m,
                source=ExtentSource.REVIEWED,
                rationale=args.extent_note or "supplied on the command line",
            )
            if args.extent_m is not None
            else None
        )
        proposal = propose(interp, chosen, extent)
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
            "proposal": proposal.model_dump(mode="json") if proposal else None,
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
    if proposal is not None:
        _print_proposal(proposal)
    return 0


def _print_proposal(p: GeoreferenceProposal) -> None:
    def m(value: float | None) -> str:
        return "unknown" if value is None else f"{value:,.0f} m"

    print(f"proposal    {p.outcome.value}  [{p.method}, policy {p.policy_id}]")
    if p.point is not None:
        print(
            f"  point     {p.point.latitude:.5f}, {p.point.longitude:.5f} ({p.point.datum.value})"
            f"   feature {p.feature_id}"
        )
    if p.point is not None or p.radius_lower_bound_m is not None:
        bound = f"   (at least {m(p.radius_lower_bound_m)} without extent)"
        print(f"  radius    {m(p.radius_m)}{bound if p.radius_m is None else ''}")
    for c in p.components:
        print(f"    {c.name.value:<21} {m(c.metres):>10}  {c.rule}")
    for a in p.assumptions:
        print(f"  assume    {a}")
    for q in p.questions:
        print(f"  ask       {q}")
    for r in p.reasons:
        print(f"  reason    {r}")


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
    fb = data.add_parser(
        "fetch-gbif", help="request + download the CU Herbarium GBIF snapshot (DOI) + manifest"
    )
    fb.add_argument("--env", default=".env", help="file with GBIF_USER, GBIF_PWD, GBIF_EMAIL")
    fb.add_argument("--key", help="resume an existing GBIF download key instead of requesting")
    fb.add_argument("--raw-root", default="data/raw/gbif")
    fb.add_argument("--manifest-dir", default="data/manifests")
    fb.add_argument("--poll-seconds", type=float, default=60.0)
    fb.set_defaults(func=_fetch_gbif)

    ing = sub.add_parser("ingest", help="specimen records").add_subparsers(
        dest="ingest_command", required=True
    )
    sc = ing.add_parser("scan", help="screen a GBIF snapshot and count exclusions by reason")
    sc.add_argument("--snapshot", default="data/raw/gbif/2026-11-01")
    sc.set_defaults(func=_ingest_scan)

    aud = sub.add_parser("audit", help="50-record feasibility audit").add_subparsers(
        dest="audit_command", required=True
    )
    asm = aud.add_parser("sample", help="seeded sample of locality groups + worksheet")
    asm.add_argument("--snapshot", default="data/raw/gbif/2026-11-01")
    asm.add_argument("--n", type=int, default=50)
    asm.add_argument("--seed", default="audit-50/1")
    asm.add_argument("--out", default="eval/audit")
    asm.set_defaults(func=_audit_sample)
    aru = aud.add_parser("rules", help="run the rules baseline on the audit sample")
    aru.add_argument("--sample", default="eval/audit/audit-50.json")
    aru.add_argument("--index", default="data/derived/gazetteer.sqlite")
    aru.add_argument("--out", default="eval/reports")
    aru.set_defaults(func=_audit_rules)
    alm = aud.add_parser("llm", help="run LLM extraction on the audit sample (llama-server)")
    alm.add_argument("--sample", default="eval/audit/audit-50.json")
    alm.add_argument("--index", default="data/derived/gazetteer.sqlite")
    alm.add_argument("--out", default="eval/reports")
    alm.add_argument("--url", default="http://127.0.0.1:8080")
    alm.add_argument("--release", default="release/manifest.json")
    alm.set_defaults(func=_audit_llm)
    asc = aud.add_parser("score", help="check the worksheet and score both systems against it")
    asc.add_argument("--sample", default="eval/audit/audit-50.json")
    asc.add_argument("--worksheet", default="eval/audit/worksheet.csv")
    asc.add_argument("--index", default="data/derived/gazetteer.sqlite")
    asc.add_argument("--rules", default="eval/reports/audit-50-rules-1.json")
    asc.add_argument("--llm", default="eval/reports/audit-50-llm-x1g2-qwen3.5-4b-q4km.json")
    asc.add_argument("--out", default="eval/reports")
    asc.set_defaults(func=_audit_score)

    mod = sub.add_parser("model", help="pinned local LLM").add_subparsers(
        dest="model_command", required=True
    )
    mf = mod.add_parser("fetch", help="download the pinned GGUF and verify its sha256")
    mf.add_argument("--release", default="release/manifest.json")
    mf.add_argument("--models-dir", default="models")
    mf.set_defaults(func=_model_fetch)
    mc = mod.add_parser("check", help="check the running llama-server against the manifest")
    mc.add_argument("--release", default="release/manifest.json")
    mc.add_argument("--url", default="http://127.0.0.1:8080")
    mc.set_defaults(func=_model_check)

    dev = sub.add_parser("dev", help="development samples").add_subparsers(
        dest="dev_command", required=True
    )
    drg = dev.add_parser("register", help="record a sample's groups as viewed (dev forever)")
    drg.add_argument("--sample", required=True)
    drg.add_argument("--name", required=True)
    drg.add_argument("--registry", default="eval/viewed-groups.json")
    drg.set_defaults(func=_dev_register)
    dsm = dev.add_parser("sample", help="stratified sample of unviewed locality groups")
    dsm.add_argument("--name", required=True, help="e.g. dev-1")
    dsm.add_argument("--seed", required=True)
    dsm.add_argument("--quota", action="append", required=True, help="shape=count, repeatable")
    dsm.add_argument("--prefix", default="D", help="row id prefix")
    dsm.add_argument("--snapshot", default="data/raw/gbif/2026-11-01")
    dsm.add_argument("--registry", default="eval/viewed-groups.json")
    dsm.add_argument("--out", required=True)
    dsm.set_defaults(func=_dev_sample)

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
    br.add_argument("--propose", action="store_true", help="add a point-radius proposal")
    br.add_argument("--feature-id", type=int, help="candidate to propose from (default: top)")
    br.add_argument("--extent-m", type=float, help="reviewed extent (geographic radial), metres")
    br.add_argument("--extent-note", help="why that extent (recorded with the proposal)")
    br.set_defaults(func=_baseline_run)

    it = sub.add_parser("interpret", help="interpret one locality with the rules or the LLM")
    it.add_argument("text")
    it.add_argument("--system", choices=["rules", "llm"], default="llm")
    it.add_argument("--url", default="http://127.0.0.1:8080", help="local llama-server")
    it.add_argument("--release", default="release/manifest.json")
    it.add_argument("--county", help="county from the record's structured fields")
    it.add_argument("--index", default="data/derived/gazetteer.sqlite")
    it.add_argument("--limit", type=int, default=5)
    it.add_argument("--json", action="store_true", help="machine-readable output")
    it.add_argument("--propose", action="store_true", help="add a point-radius proposal")
    it.add_argument("--feature-id", type=int, help="candidate to propose from (default: top)")
    it.add_argument("--extent-m", type=float, help="reviewed extent (geographic radial), metres")
    it.add_argument("--extent-note", help="why that extent (recorded with the proposal)")
    it.set_defaults(func=_baseline_run)

    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
