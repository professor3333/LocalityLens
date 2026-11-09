"""Agreement between two annotations of the same records (``AGREEMENT_VERSION`` 1).

Used to calibrate a second annotator against the owner before its annotations are used as
evidence: the same records are annotated blind by both, then compared field by field. Fields
and normalisation follow the worksheet checker, so formatting differences never count as
disagreement. Only counts are reported.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from localitylens.evaluation.annotations import Annotation, annotated_distance
from localitylens.evaluation.score import _category

AGREEMENT_VERSION: Final = "1"

FIELDS: Final[dict[str, Callable[[Annotation], Any]]] = {
    "description_type": lambda a: a.description_type,
    "supported": lambda a: a.supported,
    "acceptable_gnis_ids": lambda a: (a.acceptable_ids, a.reference_absent),
    "distance": lambda a: annotated_distance(a.distance) if a.distance else None,
    "unit": lambda a: a.unit,
    "direction": lambda a: a.direction,
    "qualifiers": lambda a: a.qualifiers,
    "category": _category,
}


@dataclass(frozen=True, slots=True)
class Agreement:
    rows: int
    by_field: dict[str, int]
    every_field: int
    categories_a: dict[str, int]
    categories_b: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {"agreement_version": AGREEMENT_VERSION, "rows": self.rows,
                "by_field": self.by_field, "every_field": self.every_field,
                "categories_a": self.categories_a, "categories_b": self.categories_b}  # fmt: skip


def agreement(
    a: Sequence[Annotation], b: Sequence[Annotation], pairs: Mapping[str, str]
) -> Agreement:
    """Compare annotation ``a[id]`` with ``b[pairs[id]]`` for every pair."""
    a_by = {x.audit_id: x for x in a}
    b_by = {x.audit_id: x for x in b}
    missing = [i for i, j in pairs.items() if i not in a_by or j not in b_by]
    if missing:
        raise ValueError(f"{len(missing)} pair(s) refer to rows that are not annotated")
    by_field = {name: 0 for name in FIELDS}
    every = 0
    cats_a: dict[str, int] = {}
    cats_b: dict[str, int] = {}
    for i, j in pairs.items():
        x, y = a_by[i], b_by[j]
        same = [get(x) == get(y) for get in FIELDS.values()]
        for name, ok in zip(FIELDS, same, strict=True):
            by_field[name] += ok
        every += all(same)
        cats_a[_category(x)] = cats_a.get(_category(x), 0) + 1
        cats_b[_category(y)] = cats_b.get(_category(y), 0) + 1
    return Agreement(rows=len(pairs), by_field=by_field, every_field=every,
                     categories_a=dict(sorted(cats_a.items())),
                     categories_b=dict(sorted(cats_b.items())))  # fmt: skip
