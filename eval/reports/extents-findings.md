# Proposals with reviewed extents (dev and validation data)

The first measurement of full regions. Each system's frozen output is unchanged: rules-2, LLM
`llm-x2g2-qwen3.5-4b-q4km` (served from the completion cache, 160 hits, 0 misses) and
hybrid-1. They were rerun with `--extents data/reviewed/extents.csv`, so a reference with a
measured extent can reach `computed`, a full point-radius region. The locked test was not run.

## The store

`extents-1`: 38 of 97 rows reviewed, 59 pending.

| Measured | Rows | Source |
|---|---|---|
| Lakes and reservoirs | 3 | Google Maps |
| Populated places | 18 | USGS The National Map: incorporated and census-designated place limits |
| Streams | 17 | USGS The National Map: the named reach on USGS hydrography |

Each row records who measured it, the method, the boundary used and the map readout. Two independent checks
were run before committing:

- **Towns:** each extent is at least the farthest vertex of the town's own polygon in the USGS
  `govunits` service (layers 24 and 25). All 18 pass, 437 to 13,677 m against 440 to 14,000 m.
- **Streams and towns with a recorded end point:** the GRS80 geodesic distance from the GNIS
  point to that end point is at most the extent on all 22 rows.

**Still pending:**
- 9 towns with no polygon of their own (for example Hesperus, Gothic, Climax): the map shows
  no edge that can be defended
- 2 streams whose far end isn't clear
- all summits, gaps, valleys, flats and the glacier, which have not been measured yet

## Results

| Pooled: audit + dev-1 + validation | rules-2 | LLM | hybrid-1 |
|---|---|---|---|
| Correct proposal candidates (of 92 answerable) | 46 | 46 | **51** |
| Computed regions (of 160 records) | 23 | 24 | **25** |
| … that are correct (precision) | 21 (91%) | 21 (88%) | **23 (92%)** |
| Useful coverage: correct regions of 92 answerable | 21 (23%) | 21 (23%) | **23 (25%)** |

| Per sample: computed, correct, coverage | rules-2 | LLM | hybrid-1 |
|---|---|---|---|
| Audit (50 records, 31 answerable) | 8 · 7 · 7/31 | 6 · 5 · 5/31 | 8 · 7 · 7/31 |
| dev-1 (50, 29) | 7 · 7 · 7/29 | 9 · 8 · 8/29 | 8 · 8 · 8/29 |
| Validation (60, 32) | 8 · 7 · 7/32 | 9 · 8 · 8/32 | 9 · 8 · 8/32 |

Reports: `<sample>-{rules-2,llm-x2g2-qwen3.5-4b-q4km,hybrid-1}-extents` and
`<sample>-score-hybrid-1-extents`. Correct candidates are identical to the runs without the
store, as they should be: extents change regions, not interpretations or retrieval.

## What blocks the rest

hybrid-1 has 51 correct candidates but only 23 correct regions. The other 28 are blocked by:

| Blocking question | Records |
|---|---|
| Extent pending: town | 6 |
| Extent pending: gap | 6 |
| Extent pending: summit | 5 |
| Extent pending: valley | 4 |
| Extent pending: flat, stream, glacier | 3 |
| Reference not in the store (direction-only or multi-place labels, which the worksheet didn't cover) | 3 |
| Extent known, but "near" asks how near (by policy) | 1 |

**24 of the 28 need only a measurement.** Measuring every pending row would put coverage at
about 47 of 92 at most, which is still below the 70% target. The rest of the gap is
interpretation and retrieval, the 41 answerable records with no correct candidate.

## The two incorrect regions

Both are the known "locating offset chosen over the named collecting place" error. The same
error happens with or without the LLM:

- **A37:** "… About halfway up south slope of Thunder Mt., 16 miles N of Grand Lake." The
  region is 16 mi N of Grand Lake (20,644 m). The annotation's reference is Thunder Mt.
- **V006:** "Vernal Mesa, 15 mi. east of Montrose." The region is 15 mi E of Montrose
  (23,555 m). The annotation's reference is Vernal Mesa.

These are why every region goes to a curator before export.

## What this means

- **Precision is 92% for hybrid-1**, below the ≥95% target, on 25 computed regions. That is
  too few for a firm rate: one record is 4 points.
- **Coverage is 25%** against the ≥70% target. Measuring the pending extents could raise it
  to about half. The rest needs better interpretation and retrieval.
- **These are dev and validation numbers.** The locked test has no measured extents. A test
  claim needs extents for its references, which only the owner can measure because they come
  from the test annotations, and a new declared release.
