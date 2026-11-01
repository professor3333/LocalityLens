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

    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
