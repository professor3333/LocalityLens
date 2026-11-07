"""Backup and restore of the review store: the decisions are the one thing that cannot be rebuilt.

Everything else in a deployment is rebuilt from pinned inputs (code and release manifest from
git, the model by its SHA-256, GNIS from the pinned snapshot, extents from git). The review
store holds curator decisions, so it is backed up, and restored on rollback.

* **Backup** uses SQLite's online backup API on a read-only connection. The copy is consistent
  even while the review screen or the worker is writing (WAL mode), and it never changes the
  source, not even its schema version. The copy is one self-contained file (rollback journal,
  not WAL) and is checked with ``PRAGMA integrity_check``.
* **Restore** is for a stopped deployment. It refuses a backup that fails its check or was made
  by a newer store schema than this code reads, and refuses while another connection is
  writing to the store. (An idle open connection cannot be detected, so stop the review screen
  and the worker first.) An existing store is never deleted: it is moved aside, with its WAL files,
  to ``<name>.before-restore-<UTC time>``.
* **Rollback** restores the backup taken *before* an upgrade: a store opened by newer code
  carries the newer schema, which older code refuses.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from localitylens.review.store import _UPGRADABLE, STORE_SCHEMA_VERSION, ReviewError

BACKUP_VERSION: Final = "backup-1"
READABLE: Final = frozenset({*_UPGRADABLE, STORE_SCHEMA_VERSION})  # schemas this code opens
_COUNTED: Final = ("record", "proposal", "decision")
_SIDECARS: Final = ("-wal", "-shm")


@dataclass(frozen=True, slots=True)
class StoreInfo:
    path: Path
    schema: str
    counts: dict[str, int]  # rows in record, proposal, decision

    def summary(self) -> str:
        c = self.counts
        return (f"schema {self.schema}: {c['record']} records, {c['proposal']} proposals, "
                f"{c['decision']} decisions")  # fmt: skip


def _read_only(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise ReviewError(f"no store at {path}")
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)


def inspect(path: Path) -> StoreInfo:
    """Check a store or backup without changing it: integrity, schema, row counts."""
    con = _read_only(path)
    try:
        try:
            status = con.execute("PRAGMA integrity_check").fetchone()[0]
        except sqlite3.DatabaseError as exc:
            raise ReviewError(f"{path} is not a readable database: {exc}") from exc
        if status != "ok":
            raise ReviewError(f"{path} failed its integrity check: {status}")
        try:
            row = con.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
        except sqlite3.DatabaseError as exc:
            raise ReviewError(f"{path} is not a review store: {exc}") from exc
        if row is None:
            raise ReviewError(f"{path} has no schema version")
        counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in _COUNTED}
        return StoreInfo(path=path, schema=row[0], counts=counts)
    finally:
        con.close()


def backup(db: Path, out: Path) -> StoreInfo:
    """Copy the store to ``out`` (which must not exist), consistently, and check the copy."""
    if out.exists():
        raise ReviewError(f"{out} exists: a backup never overwrites a file")
    inspect(db)  # refuse to back up a damaged or foreign file
    out.parent.mkdir(parents=True, exist_ok=True)
    src, dst = _read_only(db), sqlite3.connect(out)
    try:
        src.backup(dst)
        dst.execute("PRAGMA journal_mode=DELETE")  # one self-contained file, no -wal/-shm
    finally:
        src.close()
        dst.close()
    return inspect(out)


def _assert_unused(db: Path) -> None:
    """Refuse while another connection is writing (a busy screen or worker)."""
    con = sqlite3.connect(db, timeout=0, isolation_level=None)
    try:
        con.execute("BEGIN EXCLUSIVE")
        con.execute("ROLLBACK")
    except sqlite3.OperationalError as exc:
        raise ReviewError(
            f"{db} is in use: stop the review screen and the worker before restoring"
        ) from exc
    finally:
        con.close()


def restore(
    src: Path,
    db: Path,
    *,
    replace: bool = False,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> tuple[StoreInfo, Path | None]:
    """Restore ``src`` into ``db``. Returns the restored store's info and where the old one went."""
    info = inspect(src)
    if info.schema not in READABLE:
        raise ReviewError(f"{src} has store schema {info.schema}, which this release cannot read "
                          f"(it reads {', '.join(sorted(READABLE))})")  # fmt: skip
    moved: Path | None = None
    if db.exists():
        if not replace:
            raise ReviewError(f"{db} exists: pass --replace to move it aside and restore")
        _assert_unused(db)
        stamp = now().strftime("%Y%m%dT%H%M%SZ")
        moved = db.with_name(f"{db.name}.before-restore-{stamp}")
        if moved.exists():
            raise ReviewError(f"{moved} exists already")
        db.rename(moved)
        for suffix in _SIDECARS:  # un-checkpointed changes travel with the file they belong to
            side = db.with_name(db.name + suffix)
            if side.exists():
                side.rename(moved.with_name(moved.name + suffix))
    db.parent.mkdir(parents=True, exist_ok=True)
    source, target = _read_only(src), sqlite3.connect(db)
    try:
        source.backup(target)
        target.execute("PRAGMA journal_mode=DELETE")  # the store turns WAL on when it opens
    finally:
        source.close()
        target.close()
    return inspect(db), moved
