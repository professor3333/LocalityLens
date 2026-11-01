"""SQLite gazetteer: build from a verified GNIS snapshot, then search by name with context.

Search order: exact key match on official names, exact match on variant names, then fuzzy
(RapidFuzz) matches to fill the remaining slots. Admin context and feature type **rank**
candidates but never filter them out. GNIS records only a feature's primary county, and old
labels use old boundaries, so a county mismatch is evidence to show, not a reason to drop.

An empty result means ``feature_absent_from_index``. That is a different outcome from several
candidates that cannot be told apart, which the caller handles as ``candidates_unresolved``.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict
from rapidfuzz import fuzz, process

from localitylens.data.manifest import SnapshotManifest, verify_snapshot
from localitylens.extract.schema import FeatureType
from localitylens.gazetteer.gnis import (
    CLASS_TO_TYPE,
    COMPATIBLE_CLASSES,
    read_domestic,
    read_variants,
)
from localitylens.gazetteer.keys import (
    NAME_KEY_VERSION,
    core_compatible,
    core_key,
    county_key,
    name_key,
)
from localitylens.geo.geodesy import Coordinate, Datum

INDEX_SCHEMA_VERSION: Final = "2"
DEFAULT_FUZZY_CUTOFF: Final = 85.0

_SCHEMA: Final = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE feature (
    feature_id    INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    feature_class TEXT NOT NULL,
    state_name    TEXT NOT NULL,
    state_fips    TEXT NOT NULL,
    county_name   TEXT NOT NULL,
    county_fips   TEXT NOT NULL,
    map_name      TEXT NOT NULL,
    prim_lat      REAL NOT NULL,
    prim_lon      REAL NOT NULL,
    source_lat    REAL,
    source_lon    REAL,
    bgn_type      TEXT NOT NULL,
    date_edited   TEXT NOT NULL,
    historical    INTEGER NOT NULL CHECK (historical IN (0, 1))
);
CREATE TABLE name (
    id         INTEGER PRIMARY KEY,
    feature_id INTEGER NOT NULL REFERENCES feature(feature_id),
    name       TEXT NOT NULL,
    name_key   TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN ('official', 'variant')),
    citation   TEXT NOT NULL,
    source_date TEXT NOT NULL
);
CREATE INDEX name_key_idx ON name(name_key);
"""


class MatchKind(StrEnum):
    EXACT_OFFICIAL = "exact_official"
    EXACT_VARIANT = "exact_variant"
    CORE_OFFICIAL = "core_official"  # same name once generic words are set aside (keys.core_key)
    CORE_VARIANT = "core_variant"
    FUZZY_OFFICIAL = "fuzzy_official"
    FUZZY_VARIANT = "fuzzy_variant"


# Exact official and exact variant matches are the SAME tier: a former name on a historical
# label ("Mt. Evans" for today's Mount Blue Sky) is as valid as a current one. Context then
# decides, and "official" is only the last tie-breaker.
_TIER: Final[dict[MatchKind, int]] = {
    MatchKind.EXACT_OFFICIAL: 3,
    MatchKind.EXACT_VARIANT: 3,
    MatchKind.CORE_OFFICIAL: 2,
    MatchKind.CORE_VARIANT: 2,
    MatchKind.FUZZY_OFFICIAL: 1,
    MatchKind.FUZZY_VARIANT: 1,
}
_OFFICIAL: Final = frozenset(
    {MatchKind.EXACT_OFFICIAL, MatchKind.CORE_OFFICIAL, MatchKind.FUZZY_OFFICIAL}
)


class Candidate(BaseModel):
    """One retrieved feature plus the evidence for why it was retrieved and how it ranks."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    feature_id: int
    official_name: str
    matched_name: str
    match_kind: MatchKind
    name_similarity: float
    feature_class: str
    feature_type: FeatureType | None
    state_name: str
    county_name: str
    primary_point: Coordinate
    source_point: Coordinate | None
    historical: bool
    variant_citation: str | None
    variant_source_date: str | None
    state_match: bool | None
    county_match: bool | None
    type_match: bool | None


def build_index(snapshot_dir: Path, manifest: SnapshotManifest, out_path: Path) -> None:
    """Verify the snapshot, then write a fresh index atomically to ``out_path``."""
    verify_snapshot(snapshot_dir, manifest)
    domestic = snapshot_dir / manifest.files[0].name
    all_names = snapshot_dir / manifest.files[1].name

    features = sorted(read_domestic(domestic), key=lambda f: f.feature_id)
    ids = {f.feature_id for f in features}
    variants = sorted(read_variants(all_names, ids), key=lambda v: (v.feature_id, v.name))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.executescript(_SCHEMA)
        con.executemany(
            "INSERT INTO meta VALUES (?, ?)",
            [
                ("index_schema_version", INDEX_SCHEMA_VERSION),
                ("name_key_version", NAME_KEY_VERSION),
                ("snapshot_id", manifest.snapshot_id),
                ("manifest_sha256", manifest.sha256()),
                ("datum", Datum.NAD83.value),
            ],
        )
        con.executemany(
            "INSERT INTO feature VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    f.feature_id, f.name, f.feature_class, f.state_name, f.state_fips,
                    f.county_name, f.county_fips, f.map_name, f.prim_lat, f.prim_lon,
                    f.source_lat, f.source_lon, f.bgn_type, f.date_edited, int(f.historical),
                )
                for f in features
            ],
        )  # fmt: skip
        rows = [(f.feature_id, f.name, name_key(f.name), "official", "", "") for f in features]
        seen = {(f.feature_id, name_key(f.name)) for f in features}
        for v in variants:
            key = name_key(v.name)
            if key and (v.feature_id, key) not in seen:
                seen.add((v.feature_id, key))
                rows.append((v.feature_id, v.name, key, "variant", v.citation, v.source_date))
        con.executemany(
            "INSERT INTO name (feature_id, name, name_key, kind, citation, source_date) "
            "VALUES (?,?,?,?,?,?)",
            rows,
        )
        con.commit()
    finally:
        con.close()
    tmp.replace(out_path)


class Gazetteer:
    """Read-only search over a built index."""

    def __init__(self, path: Path) -> None:
        if not path.is_file():
            raise FileNotFoundError(f"gazetteer index not found: {path}")
        self._con = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
        self._con.row_factory = sqlite3.Row
        self.meta: dict[str, str] = {
            r["key"]: r["value"] for r in self._con.execute("SELECT key, value FROM meta")
        }
        if self.meta.get("name_key_version") != NAME_KEY_VERSION:
            raise RuntimeError("index was built with a different name-key version; rebuild it")
        if self.meta.get("index_schema_version") != INDEX_SCHEMA_VERSION:
            raise RuntimeError("index was built with a different schema version; rebuild it")
        by_key: defaultdict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
        for r in self._con.execute("SELECT id, feature_id, name, name_key, kind FROM name"):
            by_key[r["name_key"]].append((r["id"], r["feature_id"], r["name"], r["kind"]))
        self._by_key = dict(by_key)
        self._keys = sorted(self._by_key)
        by_core: defaultdict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
        for key, rows in self._by_key.items():
            if (core := core_key(key)) is not None:
                by_core[core].extend(rows)
        self._by_core = dict(by_core)

    def close(self) -> None:
        self._con.close()

    def __enter__(self) -> Gazetteer:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def snapshot_id(self) -> str:
        return self.meta["snapshot_id"]

    def name_keys(self) -> frozenset[str]:
        """Every indexed name key (official and variant)."""
        return frozenset(self._by_key)

    def describe(self, feature_ids: Iterable[int]) -> dict[int, str]:
        """``{id: "Name (Class, County)"}`` for the IDs that exist; missing IDs are absent."""
        out: dict[int, str] = {}
        for fid in set(feature_ids):
            row = self._con.execute(
                "SELECT name, feature_class, county_name FROM feature WHERE feature_id = ?", (fid,)
            ).fetchone()
            if row is not None:
                out[fid] = f"{row['name']} ({row['feature_class']}, {row['county_name']})"
        return out

    def county_names(self, state: str = "Colorado") -> frozenset[str]:
        rows = self._con.execute(
            "SELECT DISTINCT county_name FROM feature WHERE state_name = ?", (state,)
        )
        return frozenset(r["county_name"] for r in rows)

    def search(
        self,
        name: str,
        *,
        state: str | None = "Colorado",
        county: str | None = None,
        feature_type: FeatureType | None = None,
        limit: int = 5,
        fuzzy_cutoff: float = DEFAULT_FUZZY_CUTOFF,
    ) -> list[Candidate]:
        query = name_key(name)
        if not query or limit < 1:
            return []

        # feature_id -> best (kind, name row id, similarity)
        hits: dict[int, tuple[MatchKind, int, float]] = {}

        def offer(fid: int, kind: MatchKind, name_id: int, sim: float) -> None:
            current = hits.get(fid)
            official = kind in _OFFICIAL
            if current is None:
                hits[fid] = (kind, name_id, sim)
                return
            cur_official = current[0] in _OFFICIAL
            if (_TIER[kind], sim, official) > (_TIER[current[0]], current[2], cur_official):
                hits[fid] = (kind, name_id, sim)

        for name_id, fid, _matched, kind in self._by_key.get(query, []):
            exact = MatchKind.EXACT_OFFICIAL if kind == "official" else MatchKind.EXACT_VARIANT
            offer(fid, exact, name_id, 100.0)

        if (core := core_key(query)) is not None:
            for name_id, fid, matched, kind in self._by_core.get(core, []):
                matched_key = name_key(matched)
                if not core_compatible(query, matched_key):
                    continue
                tier = MatchKind.CORE_OFFICIAL if kind == "official" else MatchKind.CORE_VARIANT
                offer(fid, tier, name_id, float(fuzz.ratio(query, matched_key)))

        if len(hits) < limit:
            for key, score, _ in process.extract(
                query, self._keys, scorer=fuzz.ratio, score_cutoff=fuzzy_cutoff, limit=limit * 4
            ):
                if key == query:
                    continue
                for name_id, fid, _matched, kind in self._by_key[key]:
                    fuzzy = (
                        MatchKind.FUZZY_OFFICIAL if kind == "official" else MatchKind.FUZZY_VARIANT
                    )
                    offer(fid, fuzzy, name_id, float(score))

        if not hits:
            return []
        candidates = [
            self._candidate(fid, kind, name_id, sim, state, county, feature_type)
            for fid, (kind, name_id, sim) in hits.items()
        ]
        candidates.sort(key=_rank_key)
        return candidates[:limit]

    def _candidate(
        self,
        fid: int,
        kind: MatchKind,
        name_id: int,
        sim: float,
        state: str | None,
        county: str | None,
        feature_type: FeatureType | None,
    ) -> Candidate:
        r = self._con.execute("SELECT * FROM feature WHERE feature_id = ?", (fid,)).fetchone()
        n = self._con.execute(
            "SELECT name, kind, citation, source_date FROM name WHERE id = ?", (name_id,)
        ).fetchone()
        is_variant = n["kind"] == "variant"
        source = (
            Coordinate(latitude=r["source_lat"], longitude=r["source_lon"], datum=Datum.NAD83)
            if r["source_lat"] is not None
            else None
        )
        return Candidate(
            feature_id=fid,
            official_name=r["name"],
            matched_name=n["name"],
            match_kind=kind,
            name_similarity=sim,
            feature_class=r["feature_class"],
            feature_type=CLASS_TO_TYPE.get(r["feature_class"]),
            state_name=r["state_name"],
            county_name=r["county_name"],
            primary_point=Coordinate(
                latitude=r["prim_lat"], longitude=r["prim_lon"], datum=Datum.NAD83
            ),
            source_point=source,
            historical=bool(r["historical"]),
            variant_citation=(n["citation"] or None) if is_variant else None,
            variant_source_date=(n["source_date"] or None) if is_variant else None,
            state_match=None if state is None else r["state_name"].casefold() == state.casefold(),
            county_match=None
            if county is None
            else county_key(r["county_name"]) == county_key(county),
            type_match=(
                None
                if feature_type is None
                else r["feature_class"] in COMPATIBLE_CLASSES.get(feature_type, frozenset())
            ),
        )


def _rank_key(c: Candidate) -> tuple[int, int, int, int, float, int, int]:
    official = c.match_kind in _OFFICIAL
    return (
        -_TIER[c.match_kind],
        -int(c.type_match is True),
        -int(c.state_match is True),
        -int(c.county_match is True),
        -c.name_similarity,
        -int(official),
        c.feature_id,
    )
