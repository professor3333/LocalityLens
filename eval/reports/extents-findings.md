# Proposals with reviewed extents (dev and validation data)

Full regions, measured with the current store. Each system's frozen output is unchanged:
rules-2, LLM `llm-x2g2-qwen3.5-4b-q4km` (served from the completion cache, 160 hits, 0 misses)
and hybrid-1. They were rerun with `--extents data/reviewed/extents.csv`, so a reference with a
measured extent can reach `computed`, a full point-radius region. The locked test was not run.

## The store

`extents-1`: 57 of 97 rows reviewed, 40 pending.

| Measured | Rows | Source |
|---|---|---|
| Lakes and reservoirs | 3 | Google Maps |
| Populated places | 18 | USGS The National Map: incorporated and census-designated place limits |
| Streams | 17 | USGS The National Map: the named reach on USGS hydrography |
| Summits | 11 | USGS Topo basemap: 3DEP contours, GNIS names, NHD hydrography |
| Gaps | 8 | USGS Topo basemap: 3DEP contours, GNIS names, NHD hydrography |

Each row records who measured it, the method, the boundary used and the map readout.

### How rows were checked

- **Towns:** each extent is at least the farthest vertex of the town's own polygon in the USGS
  `govunits` service (layers 24 and 25). All 18 pass, 437 to 13,677 m against 440 to 14,000 m.
- **Streams and towns with a recorded end point:** the GRS80 geodesic distance from the GNIS
  point to that end point is at most the extent on all 22 rows.
- **Summits and gaps:** the geodesic distance from the GNIS point to the recorded far point is
  at most the extent on all 19 rows. This tests the arithmetic, not where the edge was drawn.
- **Summits and gaps, against the National Map 3D Viewer (4 rows):** pins placed on the recorded
  far points of Flagstaff Mountain, Hoosier Pass, Arapaho Pass and Weston Pass fall where their
  notes say. The Distance tool reads 2,187.78 m for Hoosier Pass, against 2,194 m from the tiles.

### How summits and gaps were bounded

These are terrain edges drawn by eye, not mapped limits, so they are rougher than town limits.

- **Summits** follow the Quick Reference Guide §2.1.2 rule for mountains: the boundary runs along
  the valleys, saddles and plains that separate the mountain from its neighbours.
- **Gaps** follow a rule of this project, because the guide has none for passes. Across the ridge,
  a gap ends where each approach reaches its valley floor. Along the ridge, it ends at the
  straight-line midpoint toward each flanking summit or neighbouring pass. That is adapted from
  the guide's midpoint fallback, which names neighbours of similar type, size or importance, so
  a summit is a looser neighbour than the guide describes.
- **The midpoint sets 3 of the 8 gap values** (Arapaho, Hoosier, Weston). These points are not on
  the crest: Hoosier's falls in the Bemrose Creek valley, more than 1 km north of the divide.
  Rifle Gap is a water gap, measured along the notch.
- **A first attempt was rejected:** running the boundary all the way to the flanking summits put
  Hoosier Pass's edge 4 km away on North Star Mountain.

### Still pending

- 9 towns with no polygon of their own (for example Hesperus, Gothic, Climax): the map shows
  no edge that can be defended
- 2 streams whose far end isn't clear
- 7 summits:
  - Zenobia Peak, Table Mountain, Vernal Mesa, Poverty Mesa, Fishers Peak Mesa and Black Mountain
    have at least one side where the slope or mesa surface runs on with no edge
  - Two Buttes has a clear main cone, but a lower hill with closed contours sits about 800 m SE.
    The name is plural, the map's label sits on the cone alone, and counting the hill would
    roughly double the radius. The choice isn't defensible from the map, so it stays pending
- 22 rows not measured yet: valleys, reservoirs, lakes, flats, ranges, a spring, a glacier, a basin
  and a ridge

## Results

| Pooled: audit + dev-1 + validation | rules-2 | LLM | hybrid-1 |
|---|---|---|---|
| Correct proposal candidates (of 92 answerable) | 46 | 46 | **51** |
| Computed regions (of 160 records) | 33 | 34 | **36** |
| … that are correct (precision) | 30 (91%) | 30 (88%) | **33 (92%)** |
| Useful coverage: correct regions of 92 answerable | 30 (33%) | 30 (33%) | **33 (36%)** |

| Per sample: computed, correct, coverage | rules-2 | LLM | hybrid-1 |
|---|---|---|---|
| Audit (50 records, 31 answerable) | 11 · 10 · 10/31 | 10 · 8 · 8/31 | 11 · 10 · 10/31 |
| dev-1 (50, 29) | 11 · 11 · 11/29 | 11 · 10 · 10/29 | 12 · 12 · 12/29 |
| Validation (60, 32) | 11 · 9 · 9/32 | 13 · 12 · 12/32 | 13 · 11 · 11/32 |

With 38 measured extents, before summits and gaps, hybrid-1 computed 25 regions, 23 correct, a
coverage of 23 of 92. Of the 11 new hybrid regions, 6 rest on gaps and 5 on summits. No system's
region uses Two Buttes, so returning it to pending changed no count.

Reports: `<sample>-{rules-2,llm-x2g2-qwen3.5-4b-q4km,hybrid-1}-extents` and
`<sample>-score-hybrid-1-extents`. Correct candidates are identical to the runs without the
store, as they should be: extents change regions, not interpretations or retrieval.

**"Correct" here does not test the extents.** It means the interpretation and the reference
are right. Whether each radius is the right size is not measured by these numbers.

## What blocks the rest

hybrid-1 has 51 correct candidates but only 33 correct regions. The other 18 are blocked by:

| Blocking question | Records |
|---|---|
| Extent pending: town | 6 |
| Extent pending: valley | 4 |
| Extent pending: flat, stream, glacier, summit | 4 |
| Reference not in the store (direction-only or multi-place labels, which the worksheet didn't cover) | 3 |
| Extent known, but "near" asks how near (by policy) | 1 |

**14 of the 18 need only a measurement**, though the 6 towns have no defensible edge today.
Measuring every one would put coverage at 47 of 92 at most, which is still below the 70% target.
The rest of the gap is interpretation and retrieval, the 41 answerable records with no correct
candidate.

## The three incorrect regions

Two are the known "locating offset chosen over the named collecting place" error, and they
happen with or without the LLM:

- **A37:** "… About halfway up south slope of Thunder Mt., 16 miles N of Grand Lake." The
  region is 16 mi N of Grand Lake (20,644 m). The annotation's reference is Thunder Mt.
- **V006:** "Vernal Mesa, 15 mi. east of Montrose." The region is 15 mi E of Montrose
  (23,555 m). The annotation's reference is Vernal Mesa.

The third is new, because Mount Shavano now has an extent:

- **V013:** "S. slope Mt. Shavano, 10 mi. n. w. Salida." The reference is right, but rules-2 reads
  the Salida offset as measured from Mount Shavano and reads "n. w." as N (14,497 m). The LLM
  reads this record correctly. hybrid-1 keeps the rules answer because it uses the rules first.

These are why every region goes to a curator before export.

## What this means

- **Precision is 92% for hybrid-1**, below the ≥95% target, on 36 computed regions. That is
  too few for a firm rate: one record is about 3 points.
- **Coverage is 36%** against the ≥70% target. Measuring the pending extents could raise it
  to about half. The rest needs better interpretation and retrieval.
- **These are dev and validation numbers.** The locked test has no measured extents. A test
  claim needs extents for its references, which only the owner can measure because they come
  from the test annotations, and a new declared release.
