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
_DERIVED_HELP: Final = (
    "derived-extent store (CSV), used where no reviewed extent exists; needs --extents"
)
_SELECTION_HELP: Final = (
    "hold a region back when the label names another typed feature (selection-1)"
)
_SELECTION_2_HELP: Final = (
    "selection-2: hold a region when another named place is in GNIS inside it, or not in GNIS"
)
_WITH_SELECTION_HELP: Final = "use the -sel reports (runs made with --selection-check)"
_WITH_DERIVED_HELP: Final = "use the -extents-derived reports (runs made with --derived-extents)"


def _pinned_gnis(release: str) -> str:
    """The gazetteer snapshot the release manifest pins."""
    from localitylens.release import load_release

    return load_release(Path(release)).gazetteer_snapshot


def _fetch_gnis(args: argparse.Namespace) -> int:
    from localitylens.data.gnis_fetch import fetch_gnis, fetch_pinned_gnis
    from localitylens.data.manifest import ChecksumMismatchError

    if args.latest:
        path, manifest = fetch_gnis(Path(args.raw_root), Path(args.manifest_dir))
        print(f"{manifest.snapshot_id} (current USGS files) -> {path}")
        print(f"  new manifest written to {args.manifest_dir}/{manifest.snapshot_id}.json")
        sources = ["USGS"] * len(manifest.files)
    else:
        snapshot_id = args.snapshot or _pinned_gnis(args.release)
        try:
            path, manifest, sources = fetch_pinned_gnis(
                snapshot_id, Path(args.raw_root), Path(args.manifest_dir)
            )
        except (FileNotFoundError, ChecksumMismatchError) as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        print(f"{manifest.snapshot_id} (pinned) -> {path}")
    for f, source in zip(manifest.files, sources, strict=True):
        print(f"  {f.name}  {f.size_bytes:>11,} bytes  sha256={f.sha256[:16]}…  from {source}")
    return 0


def _fetch_geometry(args: argparse.Namespace) -> int:
    from localitylens.data.geometry_fetch import SOURCES, fetch_geometry
    from localitylens.data.manifest import ChecksumMismatchError

    roots = {"nhd-co-2023-12-27": "data/raw/nhd", "tiger-place-co-2025": "data/raw/tiger"}
    wanted = list(SOURCES) if args.snapshot == "all" else [args.snapshot]
    for snapshot_id in wanted:
        try:
            path, manifest, sources = fetch_geometry(
                snapshot_id, Path(roots[snapshot_id]), Path(args.manifest_dir)
            )
        except (FileNotFoundError, ChecksumMismatchError) as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        for f, source in zip(manifest.files, sources, strict=True):
            print(f"{snapshot_id} -> {path}")
            print(f"  {f.name}  {f.size_bytes:>13,} bytes  sha256={f.sha256[:16]}…  from {source}")
    return 0


def _fetch_gbif(args: argparse.Namespace) -> int:
    from localitylens.data.gbif_fetch import fetch_gbif, fetch_pinned_gbif, read_credentials
    from localitylens.data.manifest import ChecksumMismatchError
    from localitylens.release import load_release

    if not (args.request or args.key):
        snapshot_id = args.snapshot or load_release(Path(args.release)).specimen_snapshot
        try:
            path, pinned, sources = fetch_pinned_gbif(
                snapshot_id, Path(args.raw_root), Path(args.manifest_dir)
            )
        except (FileNotFoundError, ChecksumMismatchError) as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        print(f"{pinned.snapshot_id} (pinned) -> {path}")
        print(f"  doi        https://doi.org/{pinned.doi}")
        for f, source in zip(pinned.files, sources, strict=True):
            print(f"  {f.name}  {f.size_bytes:>11,} bytes  sha256={f.sha256[:16]}…  from {source}")
        return 0
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


def _selection(args: argparse.Namespace) -> str | None:
    """The selection check a command asked for: selection-2, selection-1 or none."""
    if getattr(args, "selection_2", False):
        return "selection-2"
    return "selection-1" if getattr(args, "selection_check", False) else None


def _audit_rules(args: argparse.Namespace) -> int:
    from localitylens.evaluation.audit import load_sample, run_rules, sample_label, write_report

    sample = load_sample(Path(args.sample))
    report = run_rules(sample, Path(args.index), extents=_load_extents(args),
                       selection=_selection(args))  # fmt: skip
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
        selection=_selection(args),
        cache_dir=cache_dir,
    )
    json_path, md_path = write_report(report, Path(args.out), sample_label(sample))
    for name, counts in report["counts"].items():
        print(f"{name:<10} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    if "cache" in report:
        print(f"cache      hits={report['cache']['hits']}  misses={report['cache']['misses']}")
    print(f"  report  {md_path}\n  data    {json_path}")
    return 0


def _audit_calibration_set(args: argparse.Namespace) -> int:
    """A blind copy of an annotated sample for a second annotator: renumbered in seeded order,
    blank worksheet, and the pairs back to the original IDs. Prints counts only."""
    import hashlib
    import json

    from localitylens.evaluation.audit import load_sample, write_sample

    out = Path(args.out)
    if (out / "pairs.json").exists():
        print(
            f"refused: {out}/pairs.json exists; a calibration set is written once", file=sys.stderr
        )
        return 2
    source = load_sample(Path(args.source))
    if args.ids:
        wanted = {line.strip() for line in Path(args.ids).read_text().splitlines() if line.strip()}
        unknown = wanted - {i.audit_id for i in source.items}
        if unknown:
            print(f"refused: {len(unknown)} listed IDs are not in the source", file=sys.stderr)
            return 2
        source = source.model_copy(
            update={"items": tuple(i for i in source.items if i.audit_id in wanted)}
        )

    def rank(item: Any) -> str:
        return hashlib.sha256(f"{args.seed}|{item.audit_id}".encode()).hexdigest()

    ordered = sorted(source.items, key=rank)
    width = len(str(len(ordered)))
    items = [i.model_copy(update={"audit_id": f"{args.prefix}{n:0{width}d}"})
             for n, i in enumerate(ordered, start=1)]  # fmt: skip
    pairs = {new.audit_id: old.audit_id for new, old in zip(items, ordered, strict=True)}
    sample = source.model_copy(update={"items": tuple(items), "name": args.name, "seed": args.seed})
    _, worksheet, written = write_sample(sample, out, args.name)
    with (out / "pairs.json").open("x", encoding="utf-8") as fh:
        json.dump({"source": args.source, "seed": args.seed, "pairs": pairs}, fh, indent=2)
        fh.write("\n")
    print(f"{args.name}: {len(items)} rows -> {worksheet} ({'written' if written else 'exists'})")
    return 0


def _audit_agreement(args: argparse.Namespace) -> int:
    """Field-by-field agreement of two annotations of the same records (counts only)."""
    import json

    from localitylens.evaluation.agreement import agreement
    from localitylens.evaluation.annotations import check_worksheet
    from localitylens.evaluation.audit import load_sample
    from localitylens.gazetteer.index import Gazetteer

    pairs = json.loads(Path(args.pairs).read_text(encoding="utf-8"))["pairs"]
    with Gazetteer(Path(args.index)) as gaz:
        a = check_worksheet(Path(args.worksheet_a), load_sample(Path(args.sample_a)), gaz)
        b = check_worksheet(Path(args.worksheet_b), load_sample(Path(args.sample_b)), gaz)
    if a.errors or b.errors:
        print(
            f"refused: worksheet errors (a: {len(a.errors)}, b: {len(b.errors)})", file=sys.stderr
        )
        return 2
    result = agreement(a.annotations, b.annotations, pairs)
    for name, n in result.by_field.items():
        print(f"  {name:<20} {n:>3} of {result.rows}")
    print(f"  {'every field':<20} {result.every_field:>3} of {result.rows}")
    print(f"  categories a {result.categories_a}  b {result.categories_b}")
    if args.out:
        Path(args.out).write_text(json.dumps(result.as_dict(), indent=2) + "\n", encoding="utf-8")
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
    ext = "-extents-derived" if args.with_derived else "-extents" if args.with_extents else ""
    ext += "-sel2" if args.with_selection_2 else "-sel" if args.with_selection else ""
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
    ext = "-extents-derived" if args.with_derived else "-extents" if args.with_extents else ""
    ext += "-sel2" if args.with_selection_2 else "-sel" if args.with_selection else ""
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
        if getattr(args, "derived_extents", None):
            from localitylens.geo.extents import ExtentStoreError

            raise ExtentStoreError(
                "--derived-extents needs --extents (reviewed extents come first)"
            )
        return None
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo.extents import load_store

    derived = getattr(args, "derived_extents", None)
    with Gazetteer(Path(args.index)) as gaz:
        return load_store(Path(args.extents), gaz, Path(derived) if derived else None)


def _extents_or_refuse(args: argparse.Namespace) -> Any:
    """The extent store, or False (after saying why) when it fails its check against the
    gazetteer: processing without the reviewed extents would silently change the proposals."""
    from localitylens.geo.extents import ExtentStoreError

    try:
        return _load_extents(args)
    except ExtentStoreError as exc:
        print(f"refused: {exc}"[:600], file=sys.stderr)
        print("  the extent store is pinned to a GNIS snapshot: build the gazetteer from it "
              "(`localitylens data fetch-gnis` then `localitylens gazetteer build`)",
              file=sys.stderr)  # fmt: skip
        return False


_LOCKED: Final = (
    Path("eval/benchmark/test"),
    Path("eval/benchmark/test-2"),
    Path("eval/benchmark/test-3"),
    Path("eval/benchmark/test-4"),
)


def _is_locked(path: Path) -> bool:
    return any(path.resolve().is_relative_to(d.resolve()) for d in _LOCKED)


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


def _extents_derive(args: argparse.Namespace) -> int:
    """Derived extents from the pinned NHD and TIGER snapshots. Prints counts only."""
    import zipfile

    from localitylens.data.manifest import load_manifest, verify_snapshot
    from localitylens.data.nhd import gnis_groups
    from localitylens.data.shapefile import read_polygons
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.geo.derived_extents import (
        derive_nhd,
        derive_places,
        ring_bounds,
        write_derived,
    )

    out = Path(args.out)
    if out.exists():
        print(f"refused: {out} exists; derived stores are written once", file=sys.stderr)
        return 2
    nhd_dir, tiger_dir = Path(args.nhd), Path(args.tiger)
    nhd_m, tiger_m = (
        load_manifest(nhd_dir / "manifest.json"),
        load_manifest(tiger_dir / "manifest.json"),
    )
    verify_snapshot(nhd_dir, nhd_m)
    verify_snapshot(tiger_dir, tiger_m)
    gpkg = Path(args.work) / "NHD_H_Colorado_State_GPKG.gpkg"
    if not gpkg.is_file():  # extracted into its own folder; the archive is never written to
        gpkg.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(nhd_dir / nhd_m.files[0].name) as zf:
            zf.extract(gpkg.name, gpkg.parent)
    archive = tiger_dir / tiger_m.files[0].name
    polygons = [(r.attributes, r.rings) for r in read_polygons(archive)]
    within = ring_bounds(ring for _, rings in polygons for ring in rings)
    with Gazetteer(Path(args.index)) as gaz:
        places = derive_places(polygons, gaz, tiger_m.snapshot_id)
        water = derive_nhd(gnis_groups(gpkg), gaz, nhd_m.snapshot_id, within)
        place_ids = {r.feature_id for r in places}
        rows = places + [r for r in water if r.feature_id not in place_ids]
        n = write_derived(out, rows, gaz.snapshot_id)
    print(f"derived {n:,} extents -> {out}")
    print(f"  places (TIGER)  {len(places):>6,}")
    print(f"  water (NHD)     {len(water):>6,}")
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


def _pair(text: str) -> tuple[str, str]:
    column, sep, term = text.partition("=")
    if not sep or not column.strip() or not term.strip():
        raise argparse.ArgumentTypeError(f"--map expects column=term, got {text!r}")
    return column.strip(), term.strip()


def _review_import(args: argparse.Namespace) -> int:
    from collections import Counter

    from localitylens.evaluation.audit import load_sample
    from localitylens.gazetteer.index import Gazetteer
    from localitylens.review.importer import import_records
    from localitylens.review.store import ReviewStore

    source = Path(args.sample or args.csv)
    if _is_locked(source):
        print("refused: the locked test split is never imported for review", file=sys.stderr)
        return 2
    record_ids: list[str] | None = None
    if args.csv:
        from localitylens.ingest.csv_import import MappingError, read_csv, write_rejects

        try:
            mapping = dict(_pair(m) for m in args.map or [])
            parsed = read_csv(source, mapping, encoding=args.encoding)
        except (MappingError, argparse.ArgumentTypeError) as exc:
            print(f"refused: {source}: {exc}", file=sys.stderr)
            return 2
        records = [r for _, r in parsed.records]
        record_ids = [rid for rid, _ in parsed.records]
        snapshot_id = parsed.snapshot_id
        print(f"{source}: {parsed.rows} rows, {len(records)} accepted, "
              f"{len(parsed.rejected)} refused (snapshot {snapshot_id})")  # fmt: skip
        for reason, n in sorted(Counter(r.reason for r in parsed.rejected).items()):
            print(f"  refused  {reason}: {n}")
        if parsed.ignored_answer_columns:
            print("  never read (answer-bearing): " + ", ".join(parsed.ignored_answer_columns))
        if parsed.rejected:
            rejects = Path(args.rejects or f"data/review/rejects-{snapshot_id}.csv")
            write_rejects(parsed, rejects)
            print(f"  refusals written to {rejects}")
    else:
        sample = load_sample(source)
        records = [i.record for i in sample.items]
        snapshot_id = sample.snapshot_id
    extents = _extents_or_refuse(args)
    if extents is False:
        return 2
    _log_json(args)
    with Gazetteer(Path(args.index)) as gaz, ReviewStore(Path(args.db)) as store:
        rules, llm, release_id = _extractors(args, gaz, args.system)
        counts = import_records(
            store, records, snapshot_id, gaz,
            system=args.system, rules=rules, llm=llm, release=release_id, extents=extents,
            selection=_selection(args), process_now=not args.no_process, record_ids=record_ids,
        )  # fmt: skip
    print(f"imported {len(records)} records ({args.system})")
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
    """Resume: work every pending job of active batches (or one batch). With --watch, keep
    polling for new jobs until SIGTERM/SIGINT, which stops after the current job."""
    import signal
    import time

    from localitylens.gazetteer.index import Gazetteer
    from localitylens.jobs.queue import JobQueue
    from localitylens.review.store import ReviewStore

    extents = _extents_or_refuse(args)
    if extents is False:
        return 2
    _log_json(args)
    stop = {"now": False}
    if args.watch:

        def _stop(signum: int, _frame: object) -> None:
            stop["now"] = True
            print(f"signal {signum}: stopping after the current job", flush=True)

        signal.signal(signal.SIGTERM, _stop)
        signal.signal(signal.SIGINT, _stop)
    with Gazetteer(Path(args.index)) as gaz, ReviewStore(Path(args.db)) as store:
        queue = JobQueue(store, clock=time.time, lease_s=args.lease, max_attempts=args.attempts)
        while True:
            _work_round(args, gaz, store, queue, extents, lambda: stop["now"])
            if not args.watch or stop["now"]:
                return 0
            for _ in range(int(args.poll * 10)):  # sleep in short steps to react to signals
                if stop["now"]:
                    return 0
                time.sleep(0.1)


def _work_round(
    args: argparse.Namespace,
    gaz: Any,
    store: Any,
    queue: Any,
    extents: Any,
    should_stop: Any,
) -> None:
    """One pass over the active batches with open jobs."""
    from localitylens.review.importer import work_batch

    batches = [queue.batch(args.batch)] if args.batch else queue.batches()
    for b in batches:
        open_jobs = b.jobs.get("pending", 0) + b.jobs.get("leased", 0)
        if b.state.value != "active" or not open_jobs:
            continue
        rules, llm, _release = _extractors(args, gaz, b.system)
        counts = work_batch(
            store, queue, b.batch_id, gaz, rules=rules, llm=llm, extents=extents,
            selection=_selection(args), max_jobs=args.max_jobs, should_stop=should_stop,
        )  # fmt: skip
        done = ", ".join(f"{s} {n}" for s, n in sorted(counts.items())) or "nothing finished"
        print(f"{b.batch_id} ({b.system}): {done}", flush=True)
        if should_stop():
            return


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


def _review_backup(args: argparse.Namespace) -> int:
    from localitylens.review.backup import backup
    from localitylens.review.store import ReviewError

    try:
        info = backup(Path(args.db), Path(args.out))
    except ReviewError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"backup {args.out}: {info.summary()}, integrity ok")
    return 0


def _review_restore(args: argparse.Namespace) -> int:
    from localitylens.review.backup import restore
    from localitylens.review.store import ReviewError

    try:
        info, moved = restore(Path(args.source), Path(args.db), replace=args.replace)
    except ReviewError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    if moved is not None:
        print(f"moved the previous store to {moved}")
    print(f"restored {args.db}: {info.summary()}, integrity ok")
    return 0


def _review_export(args: argparse.Namespace) -> int:
    from localitylens.export.darwin_core import export_approved, export_unresolved
    from localitylens.export.geojson import export_geojson
    from localitylens.review.store import ReviewStore

    geojson = Path(args.geojson) if args.geojson else Path(args.out).with_suffix(".geojson")
    with ReviewStore(Path(args.db)) as store:
        n = export_approved(store, Path(args.out))
        g = export_geojson(store, geojson)
        u = export_unresolved(store, Path(args.unresolved))
    print(f"approved   {n:>5}  -> {args.out}")
    print(f"geojson    {g:>5}  -> {geojson}")
    print(f"unresolved {u:>5}  -> {args.unresolved}")
    return 0


def _review_serve(args: argparse.Namespace) -> int:
    import dataclasses

    from localitylens.geo.extents import ExtentStoreError
    from localitylens.web.app import config_from_env, serve

    problem = None
    try:
        extents = _load_extents(args)
    except ExtentStoreError as exc:  # e.g. a gazetteer built from another snapshot
        extents, problem = None, str(exc)
        print(f"warning: extent store not loaded, /readyz reports it: {problem[:200]}")
    config = config_from_env(
        Path(args.db),
        extents,
        Path(args.out),
        Path(args.unresolved),
        Path(args.geojson) if args.geojson else None,
    )
    config = dataclasses.replace(config, extents_problem=problem)
    config = dataclasses.replace(config, release=Path(args.release), index=Path(args.index))
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
    for lock_path in args.lock or [
        "eval/splits.lock.json",
        "eval/splits-2.lock.json",
        "eval/splits-3.lock.json",
        "eval/splits-4.lock.json",
    ]:
        viewed |= reserved_groups(Path(lock_path))  # held-out components are never dev data
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


def _benchmark_draw_extra(args: argparse.Namespace) -> int:
    """A further held-out split (test-2). Prints counts and paths only, never a record."""
    import json

    from localitylens.evaluation.audit import AuditSample, load_sample, write_sample
    from localitylens.evaluation.benchmark import (
        _rank,
        draw_extra,
        reserved_groups,
        write_lock,
    )
    from localitylens.evaluation.dev_sample import load_registry
    from localitylens.ingest.specimens import (
        GROUPING_VERSION,
        SCREEN_VERSION,
        ScreenSummary,
        iter_snapshot,
    )

    out, lock_out = Path(args.out), Path(args.lock_out)
    repeats_path = out / "repeats.json"
    if repeats_path.exists() or lock_out.exists():
        print(f"refused: {repeats_path} or {lock_out} exists; the draw is write-once",
              file=sys.stderr)  # fmt: skip
        return 2
    exclude = set(load_registry(Path(args.registry)))
    for lock_path in args.exclude_lock:
        exclude |= reserved_groups(Path(lock_path))
    repeats = []
    if args.repeats_from and args.repeats:
        source = load_sample(Path(args.repeats_from))
        picked = sorted(source.items, key=lambda i: _rank(args.repeat_seed, i.audit_id))
        repeats = picked[: args.repeats]
    eligible = None
    if args.shape:
        from localitylens.evaluation.dev_sample import text_shape

        def eligible(r: Any) -> bool:
            return bool(text_shape(r.locality, args.shape_version) == args.shape)

    summary = ScreenSummary(snapshot_id="")
    records = list(iter_snapshot(Path(args.snapshot), summary))
    items, mapping, lock = draw_extra(
        records, name=args.name, size=args.size, seed=args.seed, prefix=args.prefix,
        exclude=exclude, repeats=repeats, eligible=eligible,
    )  # fmt: skip
    lock = {"snapshot_id": summary.snapshot_id, "screen_version": SCREEN_VERSION,
            "grouping_version": GROUPING_VERSION, **lock}  # fmt: skip
    write_lock(lock_out, lock)
    sample = AuditSample(snapshot_id=summary.snapshot_id, screen_version=SCREEN_VERSION,
                         grouping_version=GROUPING_VERSION, seed=args.seed,
                         eligible_records=summary.eligible, eligible_groups=lock["eligible_groups"],
                         items=tuple(items), name=args.name)  # fmt: skip
    _, worksheet, written = write_sample(sample, out, args.name)
    with repeats_path.open("x", encoding="utf-8") as fh:
        json.dump({"source": args.repeats_from, "repeat_seed": args.repeat_seed,
                   "repeats": mapping}, fh, indent=2, sort_keys=True)  # fmt: skip
        fh.write("\n")
    print(f"{summary.snapshot_id}: {lock['components']:,} leakage components")
    print(f"  excluded: {lock['excluded_given_groups']:,} viewed or reserved groups, "
          f"{lock['excluded_wording_groups']:,} more by repeated wording, "
          f"{lock['excluded_viewed_components']:,} components touching them "
          f"({lock['excluded_viewed_groups']:,} groups)")  # fmt: skip
    shape = f" (text shape {args.shape}, version {args.shape_version})" if args.shape else ""
    print(f"  {args.name}: {args.size} new groups{shape} + {len(mapping)} blind repeats from "
          f"{args.repeats_from} = {len(items)} rows; worksheet {worksheet} "
          f"({'written' if written else 'exists; left untouched'})")  # fmt: skip
    print(f"  lock {lock_out} ({len(lock['reserved_groups']):,} groups reserved)")
    return 0


def _benchmark_split_repeats(args: argparse.Namespace) -> int:
    """Counts only: the rows themselves are never printed."""
    from localitylens.evaluation.benchmark import split_repeats

    folder = Path(args.folder)
    try:
        new, rep = split_repeats(folder / f"{args.name}.json", folder / "worksheet.csv",
                                 folder / "repeats.json", folder / "scoring")  # fmt: skip
    except (FileExistsError, ValueError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(
        f"{args.name}: {new} new rows -> {folder}/scoring/{args.name}-new.json + worksheet-new.csv"
    )
    print(f"  {rep} repeat rows -> {folder}/scoring/repeats-annotated.csv")
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

    if args.snapshot:
        snapshot = Path(args.snapshot)
    else:
        from localitylens.data.gnis_fetch import snapshot_directory

        snapshot = snapshot_directory(Path("data/raw/gnis"), _pinned_gnis(args.release))
    if not (snapshot / "manifest.json").is_file():
        print(f"refused: no GNIS snapshot at {snapshot} (run `localitylens data fetch-gnis`)",
              file=sys.stderr)  # fmt: skip
        return 2
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
    fg = data.add_parser(
        "fetch-gnis", help="download the pinned GNIS Colorado snapshot (or --latest)"
    )
    fg.add_argument("--raw-root", default="data/raw/gnis")
    fg.add_argument("--manifest-dir", default="data/manifests")
    fg.add_argument("--snapshot", help="a committed snapshot ID (default: the release's pin)")
    fg.add_argument(
        "--latest", action="store_true", help="the current USGS files instead, with a new manifest"
    )
    fg.add_argument("--release", default="release/manifest.json")
    fg.set_defaults(func=_fetch_gnis)
    fgeo = data.add_parser(
        "fetch-geometry", help="NHD and TIGER snapshots for derived extents (pinned, checksummed)"
    )
    fgeo.add_argument(
        "--snapshot", default="all", choices=["all", "nhd-co-2023-12-27", "tiger-place-co-2025"]
    )
    fgeo.add_argument("--manifest-dir", default="data/manifests")
    fgeo.set_defaults(func=_fetch_geometry)
    fb = data.add_parser(
        "fetch-gbif", help="download the pinned CU Herbarium snapshot (or --request a new one)"
    )
    fb.add_argument("--snapshot", help="a committed snapshot ID (default: the release's pin)")
    fb.add_argument("--release", default="release/manifest.json")
    fb.add_argument(
        "--request", action="store_true", help="request a new GBIF download (needs an account)"
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
    aru.add_argument("--derived-extents", help=_DERIVED_HELP)
    aru.add_argument("--selection-check", action="store_true", help=_SELECTION_HELP)
    aru.add_argument("--selection-2", action="store_true", help=_SELECTION_2_HELP)
    aru.set_defaults(func=_audit_rules)
    alm = aud.add_parser("llm", help="run LLM extraction on the audit sample (llama-server)")
    alm.add_argument("--sample", default="eval/audit/audit-50.json")
    alm.add_argument("--index", default="data/derived/gazetteer.sqlite")
    alm.add_argument("--out", default="eval/reports")
    alm.add_argument("--url", default="http://127.0.0.1:8080")
    alm.add_argument("--release", default="release/manifest.json")
    alm.add_argument("--extents", help=_EXTENTS_HELP)
    alm.add_argument("--derived-extents", help=_DERIVED_HELP)
    alm.add_argument("--selection-check", action="store_true", help=_SELECTION_HELP)
    alm.add_argument("--selection-2", action="store_true", help=_SELECTION_2_HELP)
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
    asc.add_argument("--with-derived", action="store_true", help=_WITH_DERIVED_HELP)
    asc.add_argument("--with-selection", action="store_true", help=_WITH_SELECTION_HELP)
    asc.add_argument("--with-selection-2", action="store_true", help="use the -sel2 reports")
    asc.set_defaults(func=_audit_score)
    acs = aud.add_parser("calibration-set", help="blind, renumbered copy of an annotated sample")
    acs.add_argument("--source", required=True, help="an annotated sample (JSON)")
    acs.add_argument("--name", required=True)
    acs.add_argument("--seed", required=True)
    acs.add_argument("--prefix", default="C")
    acs.add_argument("--out", required=True)
    acs.add_argument("--ids", help="keep only the records listed in this file (one ID per line)")
    acs.set_defaults(func=_audit_calibration_set)
    aag = aud.add_parser("agreement", help="agreement of two annotations of the same records")
    aag.add_argument("--sample-a", required=True)
    aag.add_argument("--worksheet-a", required=True)
    aag.add_argument("--sample-b", required=True)
    aag.add_argument("--worksheet-b", required=True)
    aag.add_argument("--pairs", required=True, help='JSON with {"pairs": {id_a: id_b}}')
    aag.add_argument("--index", default="data/derived/gazetteer.sqlite")
    aag.add_argument("--out", help="also write the counts as JSON")
    aag.set_defaults(func=_audit_agreement)

    ahy = aud.add_parser("hybrid", help="combine the rules and LLM reports into a hybrid report")
    ahy.add_argument("--sample", default="eval/audit/audit-50.json")
    ahy.add_argument("--rules", help="default: <out>/<sample>-<rules version>.json")
    ahy.add_argument("--llm", help="default: <out>/<sample>-<release extractor id>.json")
    ahy.add_argument("--release", default="release/manifest.json")
    ahy.add_argument("--out", default="eval/reports")
    ahy.add_argument("--with-extents", action="store_true", help=_WITH_EXTENTS_HELP)
    ahy.add_argument("--with-derived", action="store_true", help=_WITH_DERIVED_HELP)
    ahy.add_argument("--with-selection", action="store_true", help=_WITH_SELECTION_HELP)
    ahy.add_argument("--with-selection-2", action="store_true", help="use the -sel2 reports")
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
    dsm.add_argument("--lock", action="append",
                     help="split lock whose reserved groups are excluded, repeatable "
                     "(default: eval/splits.lock.json and eval/splits-2.lock.json)")  # fmt: skip
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
    bx = bm_sub.add_parser("draw-extra", help="a further held-out split (write-once lock)")
    bx.add_argument("--name", required=True, help="e.g. test-2")
    bx.add_argument("--seed", required=True)
    bx.add_argument("--size", type=int, default=120)
    bx.add_argument("--prefix", required=True, help="row id prefix, e.g. H")
    bx.add_argument("--snapshot", default="data/raw/gbif/2026-11-01")
    bx.add_argument("--registry", default="eval/viewed-groups.json")
    bx.add_argument("--exclude-lock", action="append", default=["eval/splits.lock.json"])
    bx.add_argument("--lock-out", default="eval/splits-2.lock.json")
    bx.add_argument("--repeats-from", help="an annotated sample (JSON) for blind repeats")
    bx.add_argument("--repeats", type=int, default=20)
    bx.add_argument("--repeat-seed", default="")
    bx.add_argument("--shape", help="draw only labels of this text shape, e.g. place_offset")
    bx.add_argument("--shape-version", default="2")
    bx.add_argument("--out", required=True)
    bx.set_defaults(func=_benchmark_draw_extra)
    bsr = bm_sub.add_parser("split-repeats", help="separate new rows from blind repeats to score")
    bsr.add_argument("--name", required=True, help="e.g. test-2")
    bsr.add_argument("--folder", required=True, help="e.g. eval/benchmark/test-2")
    bsr.set_defaults(func=_benchmark_split_repeats)
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
    b.add_argument("--snapshot", help="data/raw/gnis/<date> (default: the release's pinned one)")
    b.add_argument("--release", default="release/manifest.json")
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
    br.add_argument("--derived-extents", help=_DERIVED_HELP)
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
    it.add_argument("--derived-extents", help=_DERIVED_HELP)
    it.set_defaults(func=_baseline_run)

    rv = sub.add_parser("review", help="curator review store: import, decide, export")
    rv_sub = rv.add_subparsers(dest="review_command", required=True)
    db_help = "review database (SQLite)"
    ri = rv_sub.add_parser("import", help="import a sample and run the pipeline on queued records")
    src = ri.add_mutually_exclusive_group(required=True)
    src.add_argument("--sample", help="a project sample (JSON)")
    src.add_argument("--csv", help="your own records: CSV with Darwin Core columns")
    ri.add_argument(
        "--map",
        action="append",
        metavar="COLUMN=TERM",
        help="map a CSV column onto a Darwin Core term (repeatable)",
    )
    ri.add_argument("--rejects", help="where to write the refused rows (CSV)")
    ri.add_argument("--encoding", default="utf-8-sig", help="CSV text encoding")
    ri.add_argument("--system", choices=["rules", "llm", "hybrid"], default="hybrid")
    ri.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    ri.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ri.add_argument("--extents", help=_EXTENTS_HELP)
    ri.add_argument("--derived-extents", help=_DERIVED_HELP)
    ri.add_argument("--selection-check", action="store_true", help=_SELECTION_HELP)
    ri.add_argument("--selection-2", action="store_true", help=_SELECTION_2_HELP)
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
    rw.add_argument("--derived-extents", help=_DERIVED_HELP)
    rw.add_argument("--selection-check", action="store_true", help=_SELECTION_HELP)
    rw.add_argument("--selection-2", action="store_true", help=_SELECTION_2_HELP)
    rw.add_argument("--url", default="http://127.0.0.1:8080")
    rw.add_argument("--release", default="release/manifest.json")
    rw.add_argument("--log-json", help="also write each attempt's trace as a JSON line here")
    rw.add_argument(
        "--watch",
        action="store_true",
        help="keep polling for new jobs (the Docker worker); stop with SIGTERM",
    )
    rw.add_argument("--poll", type=float, default=5.0, help="seconds between polls with --watch")
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
    rd.add_argument("--derived-extents", help=_DERIVED_HELP)
    rd.add_argument("--index", default="data/derived/gazetteer.sqlite")
    rd.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rd.set_defaults(func=_review_decide)
    re_ = rv_sub.add_parser(
        "export", help="Darwin Core CSV + GeoJSON of approved records, and the unresolved report"
    )
    re_.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    re_.add_argument("--out", default="data/review/export/occurrences.csv")
    re_.add_argument("--geojson", help="GeoJSON (RFC 7946, WGS 84) of the same approved "
                     "records (default: --out with the suffix .geojson)")  # fmt: skip
    re_.add_argument("--unresolved", default="data/review/export/unresolved.csv")
    re_.set_defaults(func=_review_export)
    rb = rv_sub.add_parser(
        "backup", help="consistent copy of the review store (safe while running)"
    )
    rb.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rb.add_argument("--out", required=True, help="new file; never overwritten")
    rb.set_defaults(func=_review_backup)
    rr = rv_sub.add_parser(
        "restore", help="restore a backup into a stopped deployment (the old store is kept)"
    )
    rr.add_argument("--from", dest="source", required=True, help="a file made by review backup")
    rr.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rr.add_argument(
        "--replace", action="store_true", help="move an existing store aside, then restore"
    )
    rr.set_defaults(func=_review_restore)
    rs = rv_sub.add_parser("serve", help="the local review screen (queue, map, decisions)")
    rs.add_argument("--db", default="data/review/review.sqlite", help=db_help)
    rs.add_argument("--extents", help=_EXTENTS_HELP)
    rs.add_argument("--derived-extents", help=_DERIVED_HELP)
    rs.add_argument("--index", default="data/derived/gazetteer.sqlite")
    rs.add_argument("--host", default="127.0.0.1", help="loopback only")
    rs.add_argument("--port", type=int, default=8000)
    rs.add_argument("--release", default="release/manifest.json")
    rs.add_argument("--out", default="data/review/export/occurrences.csv")
    rs.add_argument("--geojson", help="default: --out with the suffix .geojson")
    rs.add_argument("--unresolved", default="data/review/export/unresolved.csv")
    rs.set_defaults(func=_review_serve)

    ex = sub.add_parser("extents", help="the reviewed-extent store (curator-measured radials)")
    ex_sub = ex.add_subparsers(dest="extents_command", required=True)
    ed = ex_sub.add_parser("derive", help="derived extents from the pinned NHD and TIGER snapshots")
    ed.add_argument("--nhd", default="data/raw/nhd/2023-12-27")
    ed.add_argument("--tiger", default="data/raw/tiger/2025")
    ed.add_argument(
        "--work", default="data/derived/nhd-extract", help="where the GeoPackage is extracted"
    )
    ed.add_argument("--index", default="data/derived/gazetteer.sqlite")
    ed.add_argument("--out", default="data/extents/derived.csv")
    ed.set_defaults(func=_extents_derive)
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
