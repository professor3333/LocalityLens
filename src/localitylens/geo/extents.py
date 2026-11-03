"""The reviewed-extent store (``extents-1``): curator-measured feature extents, one per GNIS ID.

GNIS gives a representative point, not a feature's shape, so a proposal's radius stays unknown
until someone has measured how far the feature reaches (invariant 6). This store holds those
measurements. Nothing in it is computed or guessed by code: every value is entered by a
reviewer, with the method, source and date, and is checked against the pinned snapshot.

**What is measured.** The *geographic radial* of BP §3.4.1 is the distance from the point used
as the georeference's origin to the farthest point of the feature's boundary. BP measures it
from a corrected center. This store measures it **from the GNIS representative point printed in
the row**, because that point is the one ``propose`` uses. That radius is never smaller than the
radial from a corrected center, so the circle still contains the whole feature. A
corrected-center option (a reviewed point plus a smaller radius) is a later version.

**Format.** A UTF-8 CSV with :data:`EXTENT_COLUMNS`. The identity and point columns are
copied from the snapshot by :func:`write_extent_worksheet` and must still match it. A row with
an empty ``extent_m`` is *pending*: it carries no extent and is not an error. A row with an
extent needs ``method``, ``source``, ``reviewer`` and an ISO ``reviewed_on`` date, which BP
§3.4.1 asks to be recorded with the extent.
"""

from __future__ import annotations

import csv
import hashlib
import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

from localitylens.gazetteer.index import FeatureSummary, Gazetteer
from localitylens.geo.georeference import ExtentEstimate, ExtentSource

STORE_VERSION: Final = "extents-1"
MEASURED_FROM: Final = "GNIS representative point"
CITE_RADIAL: Final = "BP §3.4.1"

EXTENT_COLUMNS: Final = (
    "gnis_id",
    "official_name",
    "feature_class",
    "county",
    "gazetteer_snapshot",
    "latitude",
    "longitude",
    "datum",
    "extent_m",
    "method",
    "source",
    "reviewer",
    "reviewed_on",
    "note",
)
_REQUIRED_WHEN_REVIEWED: Final = ("method", "source", "reviewer", "reviewed_on")
_POINT_TOLERANCE_DEG: Final = 1e-9


class ExtentStoreError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class StoreProblem:
    row: int  # 1-based data row; 0 = the header or the whole file
    column: str
    message: str


@dataclass(frozen=True, slots=True)
class ReviewedExtent:
    feature_id: int
    official_name: str
    extent_m: float
    method: str
    source: str
    reviewer: str
    reviewed_on: date
    note: str

    def estimate(self) -> ExtentEstimate:
        note = f" Note: {self.note}" if self.note else ""
        return ExtentEstimate(
            radius_m=self.extent_m,
            source=ExtentSource.REVIEWED,
            rationale=(
                f"radial of {self.official_name} from the {MEASURED_FROM} ({CITE_RADIAL}), "
                f"{self.method}; source: {self.source}; reviewed by {self.reviewer} on "
                f"{self.reviewed_on.isoformat()} ({STORE_VERSION}).{note}"
            ),
        )


@dataclass(slots=True)
class StoreCheck:
    entries: dict[int, ReviewedExtent] = field(default_factory=dict)
    pending: int = 0
    problems: list[StoreProblem] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ExtentStore:
    path: Path
    sha256: str
    entries: dict[int, ReviewedExtent]
    pending: int

    def get(self, feature_id: int) -> ExtentEstimate | None:
        entry = self.entries.get(feature_id)
        return entry.estimate() if entry is not None else None

    def summary(self) -> dict[str, Any]:
        """What a report records about the store it used."""
        return {
            "version": STORE_VERSION,
            "sha256": self.sha256,
            "reviewed": len(self.entries),
            "pending": self.pending,
        }


def _same_point(text: str, value: float) -> bool:
    try:
        return math.isclose(float(text), value, rel_tol=0.0, abs_tol=_POINT_TOLERANCE_DEG)
    except ValueError:
        return False


def check_store(path: Path, gazetteer: Gazetteer) -> StoreCheck:
    """Check every row against the snapshot. Problems are errors: a wrong extent is never used."""
    result = StoreCheck()

    def problem(row: int, column: str, message: str) -> None:
        result.problems.append(StoreProblem(row, column, message))

    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows or tuple(rows[0]) != EXTENT_COLUMNS:
        problem(0, "header", f"expected columns {','.join(EXTENT_COLUMNS)}")
        return result
    seen: set[int] = set()
    for n, raw in enumerate(rows[1:], start=1):
        if not any(cell.strip() for cell in raw):
            continue
        if len(raw) != len(EXTENT_COLUMNS):
            problem(n, "row", f"{len(raw)} fields, expected {len(EXTENT_COLUMNS)}")
            continue
        row = {k: v.strip() for k, v in zip(EXTENT_COLUMNS, raw, strict=True)}
        try:
            fid = int(row["gnis_id"])
        except ValueError:
            problem(n, "gnis_id", f"{row['gnis_id']!r} is not a GNIS ID")
            continue
        if fid in seen:
            problem(n, "gnis_id", f"{fid} appears twice")
            continue
        seen.add(fid)
        feature = gazetteer.feature(fid)
        if feature is None:
            problem(n, "gnis_id", f"{fid} is not in the GNIS snapshot")
            continue
        if not _identity_matches(n, row, feature, gazetteer.snapshot_id, problem):
            continue
        if not row["extent_m"]:
            if any(row[k] for k in _REQUIRED_WHEN_REVIEWED):
                problem(n, "extent_m", "review fields are filled but extent_m is empty")
            else:
                result.pending += 1
            continue
        entry = _reviewed(n, row, feature, problem)
        if entry is not None:
            result.entries[fid] = entry
    return result


def _identity_matches(
    n: int,
    row: dict[str, str],
    feature: FeatureSummary,
    snapshot_id: str,
    problem: Any,
) -> bool:
    ok = True
    expected = {
        "official_name": feature.official_name,
        "feature_class": feature.feature_class,
        "county": feature.county_name,
        "gazetteer_snapshot": snapshot_id,
        "datum": feature.primary_point.datum.value,
    }
    for column, value in expected.items():
        if row[column] != value:
            problem(n, column, f"{row[column]!r} does not match the snapshot ({value!r})")
            ok = False
    point = feature.primary_point
    for column, degrees in (("latitude", point.latitude), ("longitude", point.longitude)):
        if not _same_point(row[column], degrees):
            problem(n, column, f"{row[column]!r} is not the snapshot's point ({degrees})")
            ok = False
    return ok


def _reviewed(
    n: int, row: dict[str, str], feature: FeatureSummary, problem: Any
) -> ReviewedExtent | None:
    ok = True
    try:
        extent = float(row["extent_m"])
    except ValueError:
        problem(n, "extent_m", f"{row['extent_m']!r} is not a number of metres")
        return None
    if not math.isfinite(extent) or extent <= 0:
        problem(n, "extent_m", "must be a positive number of metres")
        ok = False
    for column in _REQUIRED_WHEN_REVIEWED:
        if not row[column]:
            problem(n, column, "required when extent_m is given")
            ok = False
    reviewed_on: date | None = None
    if row["reviewed_on"]:
        try:
            reviewed_on = date.fromisoformat(row["reviewed_on"])
        except ValueError:
            problem(n, "reviewed_on", f"{row['reviewed_on']!r} is not an ISO date (YYYY-MM-DD)")
            ok = False
    if not ok or reviewed_on is None:
        return None
    return ReviewedExtent(
        feature_id=feature.feature_id,
        official_name=feature.official_name,
        extent_m=extent,
        method=row["method"],
        source=row["source"],
        reviewer=row["reviewer"],
        reviewed_on=reviewed_on,
        note=row["note"],
    )


def load_store(path: Path, gazetteer: Gazetteer) -> ExtentStore:
    """Load a store that passes :func:`check_store`; refuse one with any problem."""
    check = check_store(path, gazetteer)
    if check.problems:
        first = "; ".join(f"row {p.row} {p.column}: {p.message}" for p in check.problems[:3])
        raise ExtentStoreError(f"{len(check.problems)} problem(s) in {path}: {first}")
    return ExtentStore(
        path=path,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        entries=check.entries,
        pending=check.pending,
    )


def write_extent_worksheet(path: Path, feature_ids: Iterable[int], gazetteer: Gazetteer) -> int:
    """Write a new store with one pending row per feature. Never overwrites an existing file."""
    ids = sorted(set(feature_ids))
    features = [gazetteer.feature(fid) for fid in ids]
    missing = [fid for fid, f in zip(ids, features, strict=True) if f is None]
    if missing:
        raise ExtentStoreError(f"not in the GNIS snapshot: {missing[:5]}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(EXTENT_COLUMNS)
        for f in features:
            assert f is not None
            p = f.primary_point
            writer.writerow([f.feature_id, f.official_name, f.feature_class, f.county_name,
                             gazetteer.snapshot_id, repr(p.latitude), repr(p.longitude),
                             p.datum.value, "", "", "", "", "", ""])  # fmt: skip
    return len(ids)
