"""Held-out benchmark splits (validation, locked test), drawn so nothing can leak across them.

Leakage unit: a **component** of locality groups linked by shared collecting events (same
collector, same exact date). Specimens from one trip can describe one place in different words;
grouping by wording alone would let such near-duplicates fall into different splits.

Rules (see the leakage controls in docs/dataset_card.md):

* A component never spans two splits; each held-out split takes at most one group per
  component, so its records are as independent as the data allow.
* Components that contain any group already read in development (``eval/viewed-groups.json``)
  are excluded from held-out splits.
* Every group in a held-out component is **reserved** in ``eval/splits.lock.json``: later dev
  samples must exclude them.
* The lock records group keys only, never label text, and is write-once.

The test worksheet is for the owner's annotation. Development code and Claude never open,
print or summarise it; only the final, authorised evaluation reads it.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, Final

from localitylens.evaluation.audit import AuditItem
from localitylens.ingest.specimens import SpecimenRecord

SPLIT_VERSION: Final = "1"
EVENT_GROUPING_VERSION: Final = "1"
EXTRA_VERSION: Final = "1"  # draw_extra: further held-out splits after the first lock
DEFAULT_LOCK: Final = Path("eval/splits.lock.json")
_FULL_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}")


class LockExistsError(RuntimeError):
    pass


def event_key(record: SpecimenRecord) -> tuple[str, str] | None:
    """(collector, exact day), or None when either is missing or the date is partial/a range."""
    collector = " ".join(record.recorded_by.casefold().split())
    date = record.event_date
    if not collector or "/" in date or not _FULL_DATE.fullmatch(date[:10]):
        return None
    return collector, date[:10]


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)  # deterministic root


def leakage_components(
    records: Iterable[SpecimenRecord],
) -> tuple[dict[str, SpecimenRecord], Counter[str], dict[str, str]]:
    """(representative record per group, records per group, component root per group)."""
    representative: dict[str, SpecimenRecord] = {}
    sizes: Counter[str] = Counter()
    events: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    uf = _UnionFind()
    for record in records:
        g = record.group_key
        sizes[g] += 1
        uf.find(g)
        current = representative.get(g)
        if current is None or int(record.gbif_id) < int(current.gbif_id):
            representative[g] = record
        if (key := event_key(record)) is not None:
            events[key].add(g)
    for groups in events.values():
        ordered = sorted(groups)
        for g in ordered[1:]:
            uf.union(ordered[0], g)
    return representative, sizes, {g: uf.find(g) for g in representative}


def _rank(seed: str, key: str) -> str:
    return hashlib.sha256(f"{seed}|{key}".encode()).hexdigest()


def draw_splits(
    records: Iterable[SpecimenRecord],
    quotas: Mapping[str, int],
    seed: str,
    viewed: Iterable[str],
    prefixes: Mapping[str, str],
) -> tuple[dict[str, list[AuditItem]], dict[str, Any]]:
    """Held-out splits in quota order, one group per component, plus the lock content."""
    representative, sizes, component = leakage_components(records)
    members: defaultdict[str, set[str]] = defaultdict(set)
    for g, root in component.items():
        members[root].add(g)
    viewed_set = set(viewed)
    tainted = {component[g] for g in viewed_set if g in component}
    pool = sorted((g for g in representative if component[g] not in tainted),
                  key=lambda g: _rank(seed, g))  # fmt: skip
    chosen: list[str] = []
    used: set[str] = set()
    need = sum(quotas.values())
    for g in pool:
        if component[g] in used:
            continue
        used.add(component[g])
        chosen.append(g)
        if len(chosen) == need:
            break
    if len(chosen) < need:
        raise ValueError(f"only {len(chosen)} independent components for {need} groups")
    splits: dict[str, list[AuditItem]] = {}
    start = 0
    for name, quota in quotas.items():
        keys = chosen[start : start + quota]
        start += quota
        splits[name] = [
            AuditItem(audit_id=f"{prefixes[name]}{i:03d}", group_size=sizes[k],
                      record=representative[k])
            for i, k in enumerate(keys, start=1)
        ]  # fmt: skip
    reserved = sorted(g for root in used for g in members[root])
    lock: dict[str, Any] = {
        "split_version": SPLIT_VERSION,
        "event_grouping_version": EVENT_GROUPING_VERSION,
        "seed": seed,
        "eligible_groups": len(representative),
        "components": len(members),
        "excluded_viewed_components": len(tainted),
        "excluded_viewed_groups": sum(len(members[r]) for r in tainted),
        "sizes": dict(quotas),
        "splits": {
            name: sorted(i.record.group_key for i in items) for name, items in splits.items()
        },
        "reserved_groups": reserved,
    }
    return splits, lock


def lock_digest(lock: Mapping[str, Any]) -> str:
    body = {k: v for k, v in lock.items() if k != "sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def write_lock(path: Path, lock: dict[str, Any]) -> None:
    """Write-once: an existing lock may only be regenerated identically."""
    content = json.dumps({**lock, "sha256": lock_digest(lock)}, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != content:
        raise LockExistsError(f"{path} exists with different content; splits are frozen")
    path.write_text(content, encoding="utf-8")


def load_lock(path: Path = DEFAULT_LOCK) -> dict[str, Any] | None:
    if not path.exists():
        return None
    lock: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if lock.get("sha256") != lock_digest(lock):
        raise ValueError(f"{path}: digest mismatch; the split assignment was altered")
    return lock


def reserved_groups(path: Path = DEFAULT_LOCK) -> set[str]:
    lock = load_lock(path)
    return set(lock["reserved_groups"]) if lock else set()


DEFAULT_LOCK_2: Final = Path("eval/splits-2.lock.json")


def wording_matches(records: Iterable[SpecimenRecord], keys: Iterable[str]) -> set[str]:
    """Every group whose wording (text key, county ignored) equals that of a group in ``keys``."""
    from localitylens.ingest.specimens import text_key

    wanted = set(keys)
    by_group: dict[str, str] = {}
    for r in records:
        by_group.setdefault(r.group_key, text_key(r.locality))
    texts = {t for g, t in by_group.items() if g in wanted}
    return {g for g, t in by_group.items() if t in texts}


def draw_extra(
    records: list[SpecimenRecord],
    *,
    name: str,
    size: int,
    seed: str,
    prefix: str,
    exclude: Iterable[str],
    repeats: Iterable[AuditItem] = (),
) -> tuple[list[AuditItem], dict[str, str], dict[str, Any]]:
    """A further held-out split after the first lock (``EXTRA_VERSION`` 1).

    Excluded: every group in ``exclude`` (viewed and already reserved), every group with the
    same wording, and every leakage component touching either. One group per remaining
    component, in seeded order. ``repeats`` (already annotated items, for a blind
    self-consistency check) are mixed in, and all items are renumbered in seeded order, so a
    repeat cannot be told apart by its ID or position. Returns (items, new ID → original ID of
    each repeat, lock content). The lock lists the new split's group keys only.
    """
    excluded = set(exclude)
    widened = excluded | wording_matches(records, excluded)
    splits, lock = draw_splits(records, {name: size}, seed, widened, {name: prefix})
    tagged = [(f"new|{i.record.group_key}", i) for i in splits[name]]
    tagged += [(f"repeat|{i.audit_id}", i) for i in repeats]
    tagged.sort(key=lambda t: _rank(seed, t[0]))
    items: list[AuditItem] = []
    mapping: dict[str, str] = {}
    for n, (tag, item) in enumerate(tagged, start=1):
        new_id = f"{prefix}{n:03d}"
        if tag.startswith("repeat|"):
            mapping[new_id] = item.audit_id
        items.append(item.model_copy(update={"audit_id": new_id}))
    lock = {**lock, "extra_version": EXTRA_VERSION,
            "excluded_given_groups": len(excluded),
            "excluded_wording_groups": len(widened - excluded)}  # fmt: skip
    return items, mapping, lock


def split_repeats(
    sample_path: Path, worksheet_path: Path, repeats_path: Path, out: Path
) -> tuple[int, int]:
    """Separate a drawn split's new rows from its blind repeats, for scoring.

    Writes ``<name>-new.json`` and ``worksheet-new.csv`` (the new rows only, IDs unchanged: the
    set the systems are scored on) and ``repeats-annotated.csv`` (the repeat rows, with the
    original ID in ``original_id``: the self-consistency check). Never prints a row; refuses an
    existing output folder. Returns (new rows, repeat rows).
    """
    import csv

    from localitylens.evaluation.audit import WORKSHEET_COLUMNS, load_sample

    if out.exists():
        raise FileExistsError(f"{out} exists: the split is written once")
    sample = load_sample(sample_path)
    mapping: dict[str, str] = json.loads(repeats_path.read_text(encoding="utf-8"))["repeats"]
    with worksheet_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = [i.audit_id for i in sample.items]
    if [r["audit_id"] for r in rows] != ids or not set(mapping) <= set(ids):
        raise ValueError("the worksheet, sample and repeats do not describe the same rows")
    out.mkdir(parents=True)
    new_items = tuple(i for i in sample.items if i.audit_id not in mapping)
    name = sample.name or "sample"
    new_sample = sample.model_copy(update={"items": new_items})
    (out / f"{name}-new.json").write_text(
        new_sample.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8"
    )
    with (out / "worksheet-new.csv").open("x", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, WORKSHEET_COLUMNS)
        w.writeheader()
        w.writerows(
            {c: r[c] for c in WORKSHEET_COLUMNS} for r in rows if r["audit_id"] not in mapping
        )
    with (out / "repeats-annotated.csv").open("x", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["original_id", *WORKSHEET_COLUMNS])
        w.writeheader()
        w.writerows({"original_id": mapping[r["audit_id"]], **{c: r[c] for c in WORKSHEET_COLUMNS}}
                    for r in rows if r["audit_id"] in mapping)  # fmt: skip
    return len(new_items), len(mapping)
