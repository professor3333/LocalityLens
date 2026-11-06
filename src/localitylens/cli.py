"""Command-line entry point: ``localitylens <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from localitylens.extract.schema import FeatureType

if TYPE_CHECKING:
    from localitylens.geo.extents import ExtentStore
    from localitylens.geo.georeference import GeoreferenceProposal

_EXTENTS_HELP: Final = "reviewed-extent store (CSV) to take feature extents from"
_WITH_EXTENTS_HELP: Final = "use the -extents reports (runs made with --extents)"


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
    from localitylens.evaluation.audit import load_sample, run_rules, sample_label, write_report

    sample = load_sample(Path(args.sample))
    report = run_rules(sample, Path(args.index), extents=_load_extents(args))
    json_path, md_path = write_report(report, Path(args.out), sample_label(sample))
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
    from localitylens.evaluation.audit import sample_label

    sample = load_sample(Path(args.sample))
    cache_dir = None if args.no_cache else Path(args.cache)
    if cache_dir is not None and _is_locked(Path(args.sample)):
        print("cache off: the locked test split runs once, with nothing stored outside it")
        cache_dir = None
    report = run_llm(
        sample,
        Path(args.index),
        client,
        release,
        server=server,
        extents=_load_extents(args),
        cache_dir=cache_dir,
    )
    json_path, md_path = write_report(report, Path(args.out), sample_label(sample))
    for name, counts in report["counts"].items():
        print(f"{name:<10} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    if "cache" in report:
        print(f"cache      hits={report['cache']['hits']}  misses={report['cache']['misses']}")
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
    from localitylens.baseline.rules import RULES_VERSION
    from localitylens.evaluation.audit import sample_label
    from localitylens.release import load_release

    label = sample_label(sample)
    llm_id = load_release(Path(args.release)).extractor_id
    ext = "-extents" if args.with_extents else ""
    rules_path = Path(args.rules or f"{args.out}/{label}-{RULES_VERSION}{ext}.json")
    llm_path = Path(args.llm or f"{args.out}/{label}-{llm_id}{ext}.json")
    reports = {
        "rules": json.loads(rules_path.read_text(encoding="utf-8")),
        "llm": json.loads(llm_path.read_text(encoding="utf-8")),
    }
    suffix = ""
    if args.hybrid:
        reports["hybrid"] = json.loads(Path(args.hybrid).read_text(encoding="utf-8"))
        suffix = f"-{reports['hybrid']['extractor_version']}"
    suffix += ext
    meta = {name: rep["extractor_version"] for name, rep in reports.items()}
    meta["specimens"] = sample.snapshot_id
    full = score(check.annotations, reports)
    sure = score(check.annotations, reports, exclude_unsure=True)
    json_path, md_path = write_score_report(full, sure, meta, Path(args.out), label, suffix)
    for key in ("critical_exact_match", "reference_top1", "correct_proposal_candidates"):
        cells = "  ".join(
            f"{n}={full['systems'][n][key]['hits']}/{full['systems'][n][key]['n']}" for n in reports
        )
        print(f"{key:<28} {cells}")
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _audit_hybrid(args: argparse.Namespace) -> int:
    import json

    from localitylens.baseline.rules import RULES_VERSION
    from localitylens.evaluation.audit import load_sample, sample_label, write_report
    from localitylens.evaluation.hybrid import ReportMismatchError, combine_reports
    from localitylens.release import load_release

    label = sample_label(load_sample(Path(args.sample)))
    llm_id = load_release(Path(args.release)).extractor_id
    ext = "-extents" if args.with_extents else ""
    rules_path = Path(args.rules or f"{args.out}/{label}-{RULES_VERSION}{ext}.json")
    llm_path = Path(args.llm or f"{args.out}/{label}-{llm_id}{ext}.json")
    try:
        report = combine_reports(
            json.loads(rules_path.read_text(encoding="utf-8")),
            json.loads(llm_path.read_text(encoding="utf-8")),
        )
    except ReportMismatchError as exc:
        print(f"cannot combine: {exc}", file=sys.stderr)
        return 2
    json_path, md_path = write_report(report, Path(args.out), label)
    for name, counts in report["counts"].items():
        print(f"{name:<10} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _load_extents(args: argparse.Namespace) -> ExtentStore | None:
    """The reviewed-extent store named by ``--extents``, checked against the snapshot."""
    if not getattr(args, "extents", None):
        return None
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo.extents import load_store

    with Gazetteer(Path(args.index)) as gaz:
        return load_store(Path(args.extents), gaz)


_LOCKED: Final = Path("eval/benchmark/test")


def _is_locked(path: Path) -> bool:
    return path.resolve().is_relative_to(_LOCKED.resolve())


def _extents_worksheet(args: argparse.Namespace) -> int:
    from localitylens.evaluation.annotations import check_worksheet
    from localitylens.evaluation.audit import load_sample
    from localitylens.evaluation.score import _category
    from localitylens.extract.schema import RelationType
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo.extents import write_extent_worksheet

    if len(args.sample) != len(args.worksheet):
        print("give one --worksheet for each --sample, in the same order", file=sys.stderr)
        return 2
    if any(_is_locked(Path(p)) for p in [*args.sample, *args.worksheet]):
        print("refused: the locked test split is never used to build a worksheet", file=sys.stderr)
        return 2
    proposable = {RelationType.NAMED_FEATURE, RelationType.DISTANCE_AND_DIRECTION,
                  RelationType.DISTANCE_ONLY}  # fmt: skip
    ids: set[int] = set()
    with Gazetteer(Path(args.index)) as gaz:
        for sample_path, sheet in zip(args.sample, args.worksheet, strict=True):
            check = check_worksheet(Path(sheet), load_sample(Path(sample_path)), gaz)
            if check.errors:
                print(f"{sheet}: {len(check.errors)} errors; fix them first", file=sys.stderr)
                return 2
            for a in check.annotations:
                if _category(a) == "answerable" and a.relation in proposable:
                    ids |= a.acceptable_ids
            print(f"{sheet}: {len(ids)} features so far")
        try:
            n = write_extent_worksheet(Path(args.out), ids, gaz)
        except FileExistsError:
            print(f"refused: {args.out} exists and is never overwritten", file=sys.stderr)
            return 2
    print(f"wrote {n} pending rows to {args.out}")
    return 0


def _extents_check(args: argparse.Namespace) -> int:
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo.extents import STORE_VERSION, check_store

    with Gazetteer(Path(args.index)) as gaz:
        check = check_store(Path(args.store), gaz)
    for p in check.problems:
        print(f"  error   row {p.row:<4} {p.column:<18} {p.message}")
    print(
        f"{STORE_VERSION}: {len(check.entries)} reviewed, {check.pending} pending, "
        f"{len(check.problems)} problems"
    )
    return 2 if check.problems else 0


def _review_import(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import load_sample
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.review.importer import import_records
    from localitylens.review.store import ReviewStore

    if _is_locked(Path(args.sample)):
        print("refused: the locked test split is never imported for review", file=sys.stderr)
        return 2
    sample = load_sample(Path(args.sample))
    extents = _load_extents(args)
    _log_json(args)
    with Gazetteer(Path(args.index)) as gaz, ReviewStore(Path(args.db)) as store:
        rules, llm, release_id = _extractors(args, gaz, args.system)
        counts = import_records(
            store, [i.record for i in sample.items], sample.snapshot_id, gaz,
            system=args.system, rules=rules, llm=llm, release=release_id, extents=extents,
            process_now=not args.no_process,
        )  # fmt: skip
    print(f"imported {len(sample.items)} records ({args.system})")
    if args.no_process:
        print("  queued; process with `localitylens review work`")
    for status, n in sorted(counts.items()):
        print(f"  {status:<18} {n}")
    return 0


def _log_json(args: argparse.Namespace) -> None:
    """Telemetry sinks for a processing command: JSON lines (--log-json) and OpenTelemetry
    (LOCALITYLENS_OTEL=console|otlp)."""
    from localitylens.telemetry.otel import configure_from_env

    provider = configure_from_env()
    if provider is not None:
        import atexit

        atexit.register(provider.shutdown)  # flush batched spans on exit
    if getattr(args, "log_json", None):
        from localitylens.telemetry.trace import json_lines_handler

        Path(args.log_json).parent.mkdir(parents=True, exist_ok=True)
        json_lines_handler(args.log_json)


def _extractors(args: argparse.Namespace, gaz: Any, system: str) -> tuple[Any, Any, str]:
    """(rules, llm or None, release ID) for a system."""
    from localitylens.baseline.rules import Lexicon, RulesExtractor

    rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
    if system == "rules":
        return rules, None, "rules-only"
    from localitylens.extract.llm import LLMExtractor
    from localitylens.extract.llm_client import LlamaServerClient
    from localitylens.release import load_release

    release = load_release(Path(args.release))
    return rules, LLMExtractor(LlamaServerClient(args.url), release), release.release


def _review_work(args: argparse.Namespace) -> int:
    """Resume: work every pending job of active batches (or one batch)."""
    import time

    from localitylens.gazetteer.index import Gazetteer
    from localitylens.jobs.queue import JobQueue
    from localitylens.review.importer import work_batch
    from localitylens.review.store import ReviewStore

    extents = _load_extents(args)
    _log_json(args)
    with Gazetteer(Path(args.index)) as gaz, ReviewStore(Path(args.db)) as store:
        queue = JobQueue(store, clock=time.time, lease_s=args.lease, max_attempts=args.attempts)
        batches = [queue.batch(args.batch)] if args.batch else queue.batches()
        for b in batches:
            open_jobs = b.jobs.get("pending", 0) + b.jobs.get("leased", 0)
            if b.state.value != "active" or not open_jobs:
                continue
            rules, llm, _release = _extractors(args, gaz, b.system)
            counts = work_batch(store, queue, b.batch_id, gaz, rules=rules, llm=llm,
                                extents=extents, max_jobs=args.max_jobs)  # fmt: skip
            print(f"{b.batch_id} ({b.system}): " + (", ".join(
                f"{s} {n}" for s, n in sorted(counts.items())) or "nothing finished"))  # fmt: skip
    return 0


def _review_traces(args: argparse.Namespace) -> int:
    """Telemetry summary from the stored traces: outcomes, latency, model use (no label text)."""
    import json as _json
    import statistics
    from collections import Counter

    from localitylens.review.store import ReviewStore

    with ReviewStore(Path(args.db)) as store:
        traces = [_json.loads(t) for t in store.traces(args.batch)]
    print(f"{len(traces)} traces" + (f" (batch {args.batch})" if args.batch else ""))
    if not traces:
        return 0
    outcomes = Counter(t["outcome"] for t in traces)
    print("  outcomes  " + ", ".join(f"{k} {v}" for k, v in sorted(outcomes.items())))
    for system in sorted({t["system"] for t in traces}):
        ms = [
            t["stages"]["total_ms"]
            for t in traces
            if t["system"] == system and t.get("stages", {}).get("total_ms") is not None
        ]
        if ms:
            p95 = statistics.quantiles(ms, n=20)[18] if len(ms) >= 20 else max(ms)
            print(f"  {system:<8} {len(ms)} completed  p50 {statistics.median(ms):,.1f} ms"
                  f"  p95 {p95:,.1f} ms")  # fmt: skip
    calls = [t["model"] for t in traces if t.get("model", {}).get("called")]
    if calls:
        print(f"  model     {len(calls)} calls, {sum(m['used'] for m in calls)} used, "
              f"{sum(m['prompt_tokens'] for m in calls):,} prompt + "
              f"{sum(m['completion_tokens'] for m in calls):,} completion tokens, "
              f"{sum(m['cache_hits'] for m in calls)} cache hits")  # fmt: skip
    retries = sum(1 for t in traces if t["outcome"].startswith("retry:"))
    print(f"  retries   {retries}")
    return 0


def _review_jobs(args: argparse.Namespace) -> int:
    import time

    from localitylens.jobs.queue import JobQueue
    from localitylens.review.store import ReviewStore

    with ReviewStore(Path(args.db)) as store:
        queue = JobQueue(store, clock=time.time)
        rows = queue.batches()
        for b in rows:
            jobs = ", ".join(f"{s} {n}" for s, n in sorted(b.jobs.items())) or "no jobs"
            print(f"{b.batch_id}  {b.state.value:<9} {b.system:<6} {b.created_at}  {jobs}")
        print(f"{len(rows)} batches")
    return 0


def _review_cancel(args: argparse.Namespace) -> int:
    import time

    from localitylens.jobs.queue import JobQueue
    from localitylens.review.store import ReviewStore

    with ReviewStore(Path(args.db)) as store:
        queue = JobQueue(store, clock=time.time)
        if args.resume:
            print(f"{args.batch}: resumed, {queue.resume(args.batch)} jobs pending again")
        else:
            n = queue.cancel(args.batch)
            print(f"{args.batch}: cancelled, {n} pending jobs stopped (records stay queued)")
    return 0


def _review_queue(args: argparse.Namespace) -> int:
    from localitylens.domain.status import RecordStatus
    from localitylens.review.store import ReviewStore

    with ReviewStore(Path(args.db)) as store:
        rows = store.records(RecordStatus(args.status) if args.status else None)
        for rec in rows:
            p = store.latest_pipeline_proposal(rec["record_id"])
            g = p.proposal
            if g is not None and g.radius_m is not None:
                what = f"feature {g.feature_id}, radius {g.radius_m:,.0f} m"
            elif g is not None and (g.questions or g.reasons):
                what = (g.questions or g.reasons)[0]
            else:
                what = p.outcome
            print(f"{rec['record_id']:<14} {rec['status']:<18} {what[:90]}")
        print(f"{len(rows)} records")
    return 0


def _review_decide(args: argparse.Namespace) -> int:
    from localitylens.review.store import Action, ReviewError, ReviewStore

    store_extents = _load_extents(args)
    with ReviewStore(Path(args.db)) as store:
        try:
            d = store.decide(
                args.record, Action(args.action), reviewer=args.reviewer,
                rationale=args.rationale, feature_id=args.feature_id, extent_m=args.extent_m,
                extent_note=args.extent_note, key=args.key,
                extent_lookup=store_extents.get if store_extents is not None else None,
            )  # fmt: skip
        except ReviewError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        status = store.status(args.record)
    note = "stored" if d.created else "already stored (same decision)"
    edits = f"  edits {d.edits}" if d.edits else ""
    print(f"{d.action.value} {args.record}: {status}, {note}{edits}")
    return 0


def _review_export(args: argparse.Namespace) -> int:
    from localitylens.export.darwin_core import export_approved, export_unresolved
    from localitylens.review.store import ReviewStore

    with ReviewStore(Path(args.db)) as store:
        n = export_approved(store, Path(args.out))
        u = export_unresolved(store, Path(args.unresolved))
    print(f"approved   {n:>5}  -> {args.out}")
    print(f"unresolved {u:>5}  -> {args.unresolved}")
    return 0


def _review_serve(args: argparse.Namespace) -> int:
    from localitylens.web.app import config_from_env, serve

    config = config_from_env(
        Path(args.db), _load_extents(args), Path(args.out), Path(args.unresolved)
    )
    who = config.reviewer or "asked on each decision (set LOCALITYLENS_REVIEWER to fix it)"
    print(f"review screen on http://{args.host}:{args.port}/  db {args.db}  reviewer: {who}")
    serve(config, host=args.host, port=args.port)
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
    from localitylens.evaluation.benchmark import reserved_groups

    registry = Path(args.registry)
    viewed = {k for k, name in load_registry(registry).items() if name != args.name}
    viewed |= reserved_groups(Path(args.lock))  # held-out components are never dev data
    summary = ScreenSummary(snapshot_id="")
    items, records, groups, skipped = sample_strata(
        iter_snapshot(Path(args.snapshot), summary),
        quotas,
        args.seed,
        viewed,
        args.prefix,
        shape_version=args.shape_version,
        exclusion_version=args.exclusion_version,
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
        shape_version=args.shape_version,
        strata=quotas,
        excluded_viewed_groups=skipped,
        # omitted at version 1 so the samples drawn before it regenerate byte-identically
        exclusion_version=args.exclusion_version if args.exclusion_version != "1" else None,
    )
    sample_path, worksheet, written = write_sample(sample, Path(args.out), args.name)
    total = register(registry, args.name, (i.record.group_key for i in items))
    print(f"{args.name}: {len(items)} groups ({', '.join(f'{k} {v}' for k, v in quotas.items())})")
    print(f"  excluded {skipped} already-viewed groups; {len(total)} groups now registered")
    print(f"  sample     {sample_path}")
    state = "(annotate before any system runs on it)" if written else "exists; left untouched"
    print(f"  worksheet  {worksheet}  {state}")
    return 0


def _benchmark_draw(args: argparse.Namespace) -> int:
    """Prints counts and paths only: the held-out worksheets are never shown."""
    from localitylens.evaluation.audit import AuditSample, write_sample
    from localitylens.evaluation.benchmark import draw_splits, write_lock
    from localitylens.evaluation.dev_sample import load_registry
    from localitylens.ingest.specimens import (
        GROUPING_VERSION,
        SCREEN_VERSION,
        ScreenSummary,
        iter_snapshot,
    )

    viewed = set(load_registry(Path(args.registry)))
    summary = ScreenSummary(snapshot_id="")
    quotas = {"test": args.test, "validation": args.validation}
    splits, lock = draw_splits(
        iter_snapshot(Path(args.snapshot), summary),
        quotas,
        args.seed,
        viewed,
        {"test": "T", "validation": "V"},
    )
    lock = {"snapshot_id": summary.snapshot_id, "screen_version": SCREEN_VERSION,
            "grouping_version": GROUPING_VERSION, **lock}  # fmt: skip
    write_lock(Path(args.lock), lock)
    print(f"{summary.snapshot_id}: {lock['components']:,} leakage components; "
          f"{lock['excluded_viewed_components']} touch viewed groups and are excluded "
          f"({lock['excluded_viewed_groups']:,} groups)")  # fmt: skip
    for name, items in splits.items():
        sample = AuditSample(
            snapshot_id=summary.snapshot_id,
            screen_version=SCREEN_VERSION,
            grouping_version=GROUPING_VERSION,
            seed=args.seed,
            eligible_records=summary.eligible,
            eligible_groups=lock["eligible_groups"],
            items=tuple(items),
            name=name,
        )
        _, worksheet, written = write_sample(sample, Path(args.out) / name, name)
        state = "written" if written else "exists; left untouched"
        print(f"  {name:<10} {len(items):>4} groups  worksheet {worksheet} ({state})")
    print(f"  lock       {args.lock}  ({len(lock['reserved_groups']):,} groups reserved)")
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

    system = getattr(args, "system", "rules")
    hybrid_note: str | None = None
    with Gazetteer(Path(args.index)) as gaz:
        rules = RulesExtractor(Lexicon(gaz.county_names(), gaz.name_keys()))
        extractor: Extractor = rules
        if system in ("llm", "hybrid"):
            from localitylens.extract.llm import LLMExtractor
            from localitylens.extract.llm_client import LlamaServerClient
            from localitylens.release import load_release

            extractor = LLMExtractor(LlamaServerClient(args.url), load_release(Path(args.release)))
        try:
            if system == "hybrid":
                from localitylens.pipeline.hybrid import interpret_hybrid

                hybrid = interpret_hybrid(
                    args.text, rules, extractor, gaz, supplied_county=args.county, limit=args.limit
                )
                result = hybrid.result
                call = (
                    f"LLM failed ({hybrid.llm_error}), rules kept"
                    if hybrid.llm_error
                    else "LLM called"
                    if hybrid.llm_called
                    else "no LLM call"
                )
                hybrid_note = f"{hybrid.version}: {hybrid.source} result used; {call}"
            else:
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
        if extent is None and chosen is not None:
            store = _load_extents(args)
            extent = store.get(chosen.feature_id) if store is not None else None
        proposal = propose(interp, chosen, extent)
    if args.json:
        payload = {
            **({"hybrid": hybrid_note} if hybrid_note else {}),
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
    if hybrid_note:
        rows.insert(0, ("system", hybrid_note))
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
    aru.add_argument("--extents", help=_EXTENTS_HELP)
    aru.set_defaults(func=_audit_rules)
    alm = aud.add_parser("llm", help="run LLM extraction on the audit sample (llama-server)")
    alm.add_argument("--sample", default="eval/audit/audit-50.json")
    alm.add_argument("--index", default="data/derived/gazetteer.sqlite")
    alm.add_argument("--out", default="eval/reports")
    alm.add_argument("--url", default="http://127.0.0.1:8080")
    alm.add_argument("--release", default="release/manifest.json")
    alm.add_argument("--extents", help=_EXTENTS_HELP)
    alm.add_argument("--cache", default="eval/.cache/llm", help="completion cache directory")
    alm.add_argument("--no-cache", action="store_true", help="call the model for every record")
    alm.set_defaults(func=_audit_llm)
    asc = aud.add_parser("score", help="check the worksheet and score both systems against it")
    asc.add_argument("--sample", default="eval/audit/audit-50.json")
    asc.add_argument("--worksheet", default="eval/audit/worksheet.csv")
    asc.add_argument("--index", default="data/derived/gazetteer.sqlite")
    asc.add_argument("--rules", help="default: <out>/<sample>-<rules version>.json")
    asc.add_argument("--llm", help="default: <out>/<sample>-<release extractor id>.json")
    asc.add_argument("--release", default="release/manifest.json")
    asc.add_argument("--hybrid", help="also score this hybrid report (written as -score-<id>)")
    asc.add_argument("--out", default="eval/reports")
    asc.add_argument("--with-extents", action="store_true", help=_WITH_EXTENTS_HELP)
    asc.set_defaults(func=_audit_score)

    ahy = aud.add_parser("hybrid", help="combine the rules and LLM reports into a hybrid report")
    ahy.add_argument("--sample", default="eval/audit/audit-50.json")
    ahy.add_argument("--rules", help="default: <out>/<sample>-<rules version>.json")
    ahy.add_argument("--llm", help="default: <out>/<sample>-<release extractor id>.json")
    ahy.add_argument("--release", default="release/manifest.json")
    ahy.add_argument("--out", default="eval/reports")
    ahy.add_argument("--with-extents", action="store_true", help=_WITH_EXTENTS_HELP)
    ahy.set_defaults(func=_audit_hybrid)

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
    dsm.add_argument("--lock", default="eval/splits.lock.json")
    dsm.add_argument(
        "--shape-version",
        choices=("1", "2"),
        default="2",
        help="text shapes (1: dev-1, dev-2; 2 adds place_offset)",
    )
    dsm.add_argument(
        "--exclusion-version",
        choices=("1", "2"),
        default="2",
        help="1: by group key (dev-1, dev-2); 2: also by repeated wording",
    )
    dsm.set_defaults(func=_dev_sample)

    bm = sub.add_parser("benchmark", help="held-out validation and locked test splits")
    bm_sub = bm.add_subparsers(dest="benchmark_command", required=True)
    bd = bm_sub.add_parser("draw", help="draw the held-out splits (write-once lock)")
    bd.add_argument("--seed", required=True)
    bd.add_argument("--test", type=int, default=120)
    bd.add_argument("--validation", type=int, default=60)
    bd.add_argument("--snapshot", default="data/raw/gbif/2026-11-01")
    bd.add_argument("--registry", default="eval/viewed-groups.json")
    bd.add_argument("--lock", default="eval/splits.lock.json")
    bd.add_argument("--out", default="eval/benchmark")
    bd.set_defaults(func=_benchmark_draw)

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
    br.add_argument("--extents", help=_EXTENTS_HELP)
    br.set_defaults(func=_baseline_run)

    it = sub.add_parser(
        "interpret", help="interpret one locality with the rules, the LLM, or rules-first hybrid"
    )
    it.add_argument("text")
    it.add_argument("--system", choices=["rules", "llm", "hybrid"], default="llm")
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
    it.add_argument("--extents", help=_EXTENTS_HELP)
    it.set_defaults(func=_baseline_run)

    rv = sub.add_parser("review", help="curator review store: import, decide, export")
    rv_sub = rv.add_subparsers(dest="review_command", required=True)
    db_help = "review database (SQLite)"
    ri = rv_sub.add_parser("import", help="import a sample and run the pipeline on queued records")
    ri.add_argument("--sample", required=True)
    ri.add_argument("--system", choices=["rules", "llm", "hybrid"], default="hybrid")
    ri.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    ri.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ri.add_argument("--extents", help=_EXTENTS_HELP)
    ri.add_argument("--url", default="http://127.0.0.1:8080")
    ri.add_argument("--release", default="release/manifest.json")
    ri.add_argument("--log-json", help="also write each attempt's trace as a JSON line here")
    ri.add_argument(
        "--no-process",
        action="store_true",
        help="only queue the records; process later with `review work`",
    )
    ri.set_defaults(func=_review_import)
    rw = rv_sub.add_parser("work", help="process pending jobs (resumes an interrupted import)")
    rw.add_argument("--batch", help="only this batch")
    rw.add_argument("--max-jobs", type=int, help="stop after this many jobs")
    rw.add_argument("--lease", type=float, default=300.0, help="lease seconds per job")
    rw.add_argument("--attempts", type=int, default=3, help="attempts before a job fails")
    rw.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rw.add_argument("--index", default="data/derived/gazetteer.sqlite")
    rw.add_argument("--extents", help=_EXTENTS_HELP)
    rw.add_argument("--url", default="http://127.0.0.1:8080")
    rw.add_argument("--release", default="release/manifest.json")
    rw.add_argument("--log-json", help="also write each attempt's trace as a JSON line here")
    rw.set_defaults(func=_review_work)
    rt = rv_sub.add_parser("traces", help="telemetry summary: outcomes, latency, model use")
    rt.add_argument("--batch", help="only this batch")
    rt.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rt.set_defaults(func=_review_traces)
    rj = rv_sub.add_parser("jobs", help="list batches and their job states")
    rj.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rj.set_defaults(func=_review_jobs)
    rc = rv_sub.add_parser("cancel", help="cancel a batch (pending records stay queued)")
    rc.add_argument("batch")
    rc.add_argument("--resume", action="store_true", help="reactivate a cancelled batch instead")
    rc.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rc.set_defaults(func=_review_cancel)
    rq = rv_sub.add_parser("queue", help="list records with their status and what blocks them")
    rq.add_argument("--status", help="only this status, e.g. ready_for_review")
    rq.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rq.set_defaults(func=_review_queue)
    rd = rv_sub.add_parser("decide", help="approve (optionally with edits), reject or defer")
    rd.add_argument("record", help="record ID, e.g. gbif:1234")
    rd.add_argument("action", choices=["approve", "reject", "request_research"])
    rd.add_argument("--reviewer", required=True)
    rd.add_argument("--rationale", required=True)
    rd.add_argument("--feature-id", type=int, help="edit: choose another retrieved candidate")
    rd.add_argument("--extent-m", type=float, help="edit: reviewed extent (radial), metres")
    rd.add_argument("--extent-note", help="how the extent was determined (required with it)")
    rd.add_argument("--key", help="idempotency key (default: hash of the decision)")
    rd.add_argument("--extents", help=_EXTENTS_HELP)
    rd.add_argument("--index", default="data/derived/gazetteer.sqlite")
    rd.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rd.set_defaults(func=_review_decide)
    re_ = rv_sub.add_parser("export", help="Darwin Core CSV of approved records + unresolved")
    re_.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    re_.add_argument("--out", default="data/review/export/occurrences.csv")
    re_.add_argument("--unresolved", default="data/review/export/unresolved.csv")
    re_.set_defaults(func=_review_export)
    rs = rv_sub.add_parser("serve", help="the local review screen (queue, map, decisions)")
    rs.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rs.add_argument("--extents", help=_EXTENTS_HELP)
    rs.add_argument("--index", default="data/derived/gazetteer.sqlite")
    rs.add_argument("--host", default="127.0.0.1", help="loopback only")
    rs.add_argument("--port", type=int, default=8000)
    rs.add_argument("--out", default="data/review/export/occurrences.csv")
    rs.add_argument("--unresolved", default="data/review/export/unresolved.csv")
    rs.set_defaults(func=_review_serve)

    ex = sub.add_parser("extents", help="the reviewed-extent store (curator-measured radials)")
    ex_sub = ex.add_subparsers(dest="extents_command", required=True)
    ew = ex_sub.add_parser(
        "worksheet", help="write a new store with one pending row per annotated reference"
    )
    ew.add_argument("--sample", action="append", required=True, help="repeat per sample")
    ew.add_argument("--worksheet", action="append", required=True, help="one per --sample")
    ew.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ew.add_argument("--out", default="data/reviewed/extents.csv")
    ew.set_defaults(func=_extents_worksheet)
    ec = ex_sub.add_parser("check", help="check every row of the store against the snapshot")
    ec.add_argument("--store", default="data/reviewed/extents.csv")
    ec.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ec.set_defaults(func=_extents_check)

    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
