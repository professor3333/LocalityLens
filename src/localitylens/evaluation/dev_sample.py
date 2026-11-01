"""Dev samples for prompt and rule development, and the registry of every viewed group.

Anything read during development is dev data forever. ``eval/viewed-groups.json`` records
every locality group that has been sampled for viewing (the audit, each dev sample), and every
later sample, including the locked test split, must exclude those groups.

Dev samples are stratified by the *shape* of the label text so that rare failure types are
represented. Shapes use only the label text, never answer-bearing fields.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Final

from localitylens.evaluation.audit import AuditItem
from localitylens.ingest.specimens import SpecimenRecord

SHAPE_VERSION: Final = "1"
REGISTRY_VERSION: Final = "1"
DEFAULT_REGISTRY: Final = Path("eval/viewed-groups.json")

_NUMBER: Final = r"(?:\d+(?:[.,]\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?|\d*\s*[½¼¾]|\d+/\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|twenty)"  # noqa: E501
_OFFSET: Final = re.compile(
    rf"\b{_NUMBER}\s*(?:air\s+|road\s+|aerial\s+)?(?:mi|miles?|km|kilomet\w*|ft|feet|yds?|yards?)\b\.?",
    re.IGNORECASE,
)
_WORD: Final = re.compile("[A-Za-z][A-Za-z'\u2019.\\-]*")


def text_shape(locality: str) -> str:
    """``offset``: a number followed by a distance unit. ``bare``: at most three words and no
    digits (a place name on its own). ``other``: everything else."""
    if _OFFSET.search(locality):
        return "offset"
    if not re.search(r"\d", locality) and len(_WORD.findall(locality)) <= 3:
        return "bare"
    return "other"


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, str]:
    """``{group_key: sample name}`` for every group already sampled for viewing."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("registry_version") != REGISTRY_VERSION:
        raise ValueError(f"{path}: unknown registry version")
    groups: dict[str, str] = data["groups"]
    return groups


def register(path: Path, sample_name: str, group_keys: Iterable[str]) -> dict[str, str]:
    """Add groups under ``sample_name``. A group already registered keeps its first sample."""
    groups = load_registry(path)
    for key in group_keys:
        groups.setdefault(key, sample_name)
    payload = {
        "registry_version": REGISTRY_VERSION,
        "note": "Locality groups read during development. They belong to dev and must be "
        "excluded from every held-out split.",
        "counts": dict(sorted(Counter(groups.values()).items())),
        "groups": dict(sorted(groups.items())),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return groups


def _rank(seed: str, key: str) -> str:
    return hashlib.sha256(f"{seed}|{key}".encode()).hexdigest()


def sample_strata(
    records: Iterable[SpecimenRecord],
    quotas: Mapping[str, int],
    seed: str,
    exclude: Iterable[str],
    id_prefix: str,
) -> tuple[list[AuditItem], int, int, int]:
    """Per shape, the first ``quota`` unviewed groups in seeded hash order.

    Returns (items, eligible records, eligible groups, groups excluded as already viewed).
    Each group is represented by its lowest-gbifID record, as in the audit.
    """
    excluded = set(exclude)
    representative: dict[str, SpecimenRecord] = {}
    sizes: Counter[str] = Counter()
    total = 0
    for record in records:
        total += 1
        sizes[record.group_key] += 1
        current = representative.get(record.group_key)
        if current is None or int(record.gbif_id) < int(current.gbif_id):
            representative[record.group_key] = record
    skipped = sum(1 for k in representative if k in excluded)
    pools: dict[str, list[str]] = {shape: [] for shape in quotas}
    for key, record in representative.items():
        shape = text_shape(record.locality)
        if key not in excluded and shape in pools:
            pools[shape].append(key)
    chosen: list[str] = []
    for shape, quota in quotas.items():
        pool = sorted(pools[shape], key=lambda k: _rank(seed, k))
        if len(pool) < quota:
            raise ValueError(f"only {len(pool)} unviewed '{shape}' groups for a quota of {quota}")
        chosen += pool[:quota]
    chosen.sort(key=lambda k: _rank(seed, k))  # interleave shapes so annotation order is blind
    items = [
        AuditItem(audit_id=f"{id_prefix}{i:02d}", group_size=sizes[k], record=representative[k])
        for i, k in enumerate(chosen, start=1)
    ]
    return items, total, len(representative), skipped
