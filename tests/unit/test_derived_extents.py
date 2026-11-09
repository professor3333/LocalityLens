"""Derived extents: shapefile reading, the place and NHD rules, the store check, and the rule
that a reviewed extent always wins. SYNTHETIC gazetteer (tests/support/synthetic_gnis.py) and
SYNTHETIC polygons and lines; no real geography."""

import io
import struct
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from localitylens.data.manifest import SnapshotManifest, write_manifest
from localitylens.data.shapefile import ShapefileError, read_polygons
from localitylens.evaluation.audit import extents_suffix
from localitylens.gazetteer.index import Gazetteer, build_index
from localitylens.geo.derived_extents import (
    METHOD_NHD,
    METHOD_PLACE_NAME,
    DerivedStoreError,
    derive_nhd,
    derive_places,
    load_derived,
    write_derived,
)
from localitylens.geo.extents import ExtentStore, ReviewedExtent
from localitylens.geo.georeference import ExtentSource

# Synthetic feature 4 "Old Camp (historical)" (Populated Place) sits at 39.2, -106.2 and
# feature 3 "Testa Lake" (Reservoir) at 40.2, -105.2.
SQUARE = ((-106.21, 39.19), (-106.21, 39.21), (-106.19, 39.21), (-106.19, 39.19), (-106.21, 39.19))
ELSEWHERE = ((-107.0, 38.0), (-107.0, 38.1), (-106.9, 38.1), (-106.9, 38.0), (-107.0, 38.0))
WITHIN = (-110.0, 37.0, -102.0, 41.0)


@pytest.fixture
def gaz(gnis_snapshot: tuple[Path, SnapshotManifest], tmp_path: Path):  # type: ignore[no-untyped-def]
    directory, manifest = gnis_snapshot
    write_manifest(directory / "manifest.json", manifest)
    build_index(directory, manifest, tmp_path / "g.sqlite")
    with Gazetteer(tmp_path / "g.sqlite") as g:
        yield g


def _shapefile_zip(path: Path, records: list[tuple[str, tuple[tuple[float, float], ...]]]) -> None:
    """A minimal polygon shapefile (one ring each) with a NAME field, as the format defines."""
    body = b""
    for n, (_, ring) in enumerate(records, start=1):
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        content = struct.pack("<i4d2i", 5, min(xs), min(ys), max(xs), max(ys), 1, len(ring))
        content += struct.pack("<i", 0) + b"".join(struct.pack("<2d", *p) for p in ring)
        body += struct.pack(">2i", n, len(content) // 2) + content
    header = struct.pack(">7i", 9994, 0, 0, 0, 0, 0, (100 + len(body)) // 2)
    header += struct.pack("<2i8d", 1000, 5, 0, 0, 0, 0, 0, 0, 0, 0)
    width = 20
    dbf = struct.pack("<4BIHH20x", 3, 126, 1, 1, len(records), 32 + 32 + 1, 1 + width)
    dbf += b"NAME".ljust(11, b"\x00") + b"C" + b"\x00" * 4 + bytes([width, 0]) + b"\x00" * 14
    dbf += b"\x0d" + b"".join(b" " + name.encode().ljust(width) for name, _ in records) + b"\x1a"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("p.shp", header + body)
        zf.writestr("p.dbf", dbf)
        zf.writestr("p.cpg", "UTF-8")
    path.write_bytes(buf.getvalue())


def test_the_shapefile_reader_returns_rings_and_attributes(tmp_path: Path) -> None:
    _shapefile_zip(tmp_path / "p.zip", [("Old Camp", SQUARE), ("Nowhere", ELSEWHERE)])
    recs = list(read_polygons(tmp_path / "p.zip"))
    assert [r.attributes["NAME"] for r in recs] == ["Old Camp", "Nowhere"]
    assert recs[0].rings == (SQUARE,)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("p.shp", b"\x00" * 120)  # wrong file code
        zf.writestr("p.dbf", b"\x00" * 40)
    (tmp_path / "bad.zip").write_bytes(buf.getvalue())
    with pytest.raises(ShapefileError):
        list(read_polygons(tmp_path / "bad.zip"))


def test_a_place_takes_the_polygon_of_its_name_that_contains_its_point(gaz: Gazetteer) -> None:
    rows = derive_places([({"NAME": "Old Camp", "GEOID": "0800001"}, [SQUARE]),
                          ({"NAME": "Old Camp", "GEOID": "0800002"}, [ELSEWHERE])],
                         gaz, "tiger-test")  # fmt: skip
    assert [(r.feature_id, r.method, r.source_ids) for r in rows] == [
        (4, METHOD_PLACE_NAME, "GEOID 0800001")
    ]
    assert 1300 < rows[0].extent_m < 1600  # corner of a 0.02° square from its centre, ~1.4 km
    ambiguous = derive_places([({"NAME": "Old Camp"}, [SQUARE]), ({"NAME": "Old Camp"}, [SQUARE])],
                              gaz, "tiger-test")  # fmt: skip
    assert ambiguous == []  # two polygons claim the place: left out


def test_nhd_geometry_counts_only_on_its_point_and_inside_the_covered_area(gaz: Gazetteer) -> None:
    near = np.array([[-105.2, 40.2], [-105.25, 40.25]])  # starts at Testa Lake's point
    far = np.array([[-104.0, 39.0], [-104.1, 39.1]])  # nowhere near Testa Peak (feature 1)
    crossing = np.array([[-105.3, 40.3], [-101.0, 40.3]])  # Upper Vela Lake, leaves the area
    rows = derive_nhd([(3, near, {"NHDWaterbody": 1}), (1, far, {"NHDFlowline": 2}),
                       (8, crossing, {"NHDFlowline": 1})], gaz, "nhd-test", WITHIN)  # fmt: skip
    assert [(r.feature_id, r.method, r.source_ids) for r in rows] == [
        (3, METHOD_NHD, "NHDWaterbody x1")
    ]
    assert rows[0].extent_m > 6000  # ~6.9 km to the far vertex


def test_a_reviewed_extent_beats_a_derived_one(gaz: Gazetteer, tmp_path: Path) -> None:
    near = np.array([[-105.2, 40.2], [-105.25, 40.25]])
    path = tmp_path / "derived.csv"
    rows = derive_nhd([(3, near, {"NHDWaterbody": 1})], gaz, "nhd-test", WITHIN)
    rows += derive_places([({"NAME": "Old Camp", "GEOID": "1"}, [SQUARE])], gaz, "tiger-test")
    assert write_derived(path, rows, gaz.snapshot_id) == 2
    with pytest.raises(FileExistsError):
        write_derived(path, rows, gaz.snapshot_id)
    derived = load_derived(path, gaz)
    reviewed = ReviewedExtent(feature_id=3, official_name="Testa Lake", extent_m=650.0,
                              method="measured", source="synthetic map", reviewer="tester",
                              reviewed_on=date(2026, 11, 9), note="")  # fmt: skip
    store = ExtentStore(path=Path("extents.csv"), sha256="0" * 64, entries={3: reviewed},
                        pending=0, derived=derived)  # fmt: skip
    lake, camp = store.get(3), store.get(4)
    assert lake is not None
    assert lake.source is ExtentSource.REVIEWED
    assert lake.radius_m == 650.0
    assert camp is not None
    assert camp.source is ExtentSource.DERIVED
    assert "not curator-reviewed" in camp.rationale
    assert store.get(1) is None
    summary = store.summary()
    assert summary["derived"]["derived"] == 2
    assert extents_suffix({"extent_store": summary}) == "-extents-derived"
    assert extents_suffix({"extent_store": {"version": "extents-1"}}) == "-extents"


def test_a_derived_row_that_disagrees_with_the_snapshot_is_refused(
    gaz: Gazetteer, tmp_path: Path
) -> None:
    rows = derive_places([({"NAME": "Old Camp", "GEOID": "1"}, [SQUARE])], gaz, "tiger-test")
    path = tmp_path / "derived.csv"
    write_derived(path, rows, gaz.snapshot_id)
    text = path.read_text(encoding="utf-8").replace("Old Camp (historical)", "Old Camp")
    path.write_text(text, encoding="utf-8")
    with pytest.raises(DerivedStoreError, match="official_name"):
        load_derived(path, gaz)
