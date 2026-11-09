# Derived extents

`derived.csv` holds feature extents computed from authoritative geometry, for features with no
curator-measured extent in [`../reviewed/extents.csv`](../reviewed/). It is used only when a
command is given `--derived-extents`, and a reviewed extent always takes precedence.

| Features | Source | Rule |
|---|---|---|
| Towns and census-designated places | U.S. Census Bureau, 2025 TIGER/Line Shapefiles: Places, Colorado ([manifest](../manifests/tiger-place-co-2025.json)) | A GNIS populated place takes the polygon of the same name that contains its GNIS point; civil and census features take the polygon carrying their GNIS ID |
| Streams, lakes, reservoirs, canals, glaciers | U.S. Geological Survey, National Hydrography Dataset Best Resolution for Colorado, published 2023-12-27 ([manifest](../manifests/nhd-co-2023-12-27.json)) | Every NHD geometry carrying the feature's GNIS ID. The GNIS point must lie within 1 km of it, and features reaching the state line are left out |

**The extent** is the geodesic distance (GRS80; all three sources are NAD83) from the GNIS
representative point to the farthest vertex, rounded up to the next metre. This is the same
radial as the reviewed store (Georeferencing Best Practices §3.4.1).

- **Format:** each row also records the method, the source snapshot, the source features and
  the vertex count.
- **Rebuild:** `localitylens extents derive` (needs both snapshots: `localitylens data
  fetch-geometry`) rebuilds the file byte for byte. On load, every row is checked against the
  pinned GNIS snapshot.

**Limits:**
- **Boundaries are current, not historical.** A town was often smaller when a label was written.
- **The extent does not make the right place:** see the
  [findings](../../eval/reports/derived-extents-findings.md).
- **Not curator-reviewed:** every proposal that uses one says so.

**Licence:**
- **NHD:** U.S. Government work, public domain in the United States.
- **TIGER/Line:** not copyrighted. The Census Bureau requires acknowledgement as the source.
  The boundaries are for statistical purposes and are not legal land descriptions.
