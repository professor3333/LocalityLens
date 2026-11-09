# Derived extents: regions for unmeasured features, and what they expose

**Question.** Hand-measured extents cover 67 features, all of them references from the dev and
validation annotations. On test-2's fresh labels hybrid-1 computed **no** regions: every
proposal stopped at "needs information". Can authoritative polygons supply the extents, and
what happens when every feature can get a region?

**Data and method** ([`derived_extents.py`](../../src/localitylens/geo/derived_extents.py), version
`derived-extents-1`; numbers in [`derived-extents.json`](derived-extents.json)):

- **Places:** Census TIGER/Line 2025 place polygons (`tiger-place-co-2025`).
  - A GNIS populated place takes the polygon of the same name that contains its GNIS point.
  - A GNIS civil or census feature takes the polygon carrying its GNIS ID.
  - A place claimed by two polygons is left out.
- **Water:** USGS NHD for Colorado, published 2023-12-27 (`nhd-co-2023-12-27`). Every geometry
  carrying the feature's GNIS ID is used.
  - The GNIS point must be within 1 km of that geometry.
  - Features reaching the state line are left out (230): the state extract may cut them short.
- **Radial:** the geodesic distance from the GNIS point to the farthest vertex, rounded up to
  the next metre (the same definition as the reviewed store, BP §3.4.1).
- **Precedence:** a curator's reviewed extent always comes first. Derived extents are used only
  with `--derived-extents`, and every proposal says "derived … not curator-reviewed".
- **Result:** 11,993 features, out of the 916 place and 11,077 water candidates.
  `localitylens extents derive` rebuilds `data/extents/derived.csv` byte for byte from the
  pinned snapshots.

## The extents agree with hand measurements

45 features have both a reviewed and a derived extent:

| | Features | Derived ÷ reviewed, median | Range |
|---|---|---|---|
| Populated places | 24 | 0.98 | 0.94–1.00 |
| Streams | 16 | 0.98 | 0.81–1.18 |
| All | 45 | 0.98 | 0.81–1.18 |

- **Why derived runs about 2% lower:** hand measurements were rounded outward to two significant
  figures.
- **The outliers are streams:**
  - Hague Creek: 0.81. The hand measurement reached farther than the NHD reach carrying its
    GNIS ID.
  - Rock Creek: 1.18. The NHD reach runs longer than the hand-measured named reach.
  - Reviewed values win in both cases.

## Regions: more of them, and most of the new ones are wrong

hybrid-1, regions computed / correct (right interpretation and acceptable reference) / answerable:

| Samples | Reviewed extents only | + derived extents |
|---|---|---|
| Owner-annotated: audit, dev-1, validation | 35 / 32 / 92 (91% correct, coverage 35%) | 52 / 33 / 92 (63%, 36%) |
| Claude-annotated: dev-2 to dev-4 | 16 / 10 / 97 (63%, 10%) | 51 / 24 / 97 (47%, 25%) |
| of which dev-3 and dev-4, mostly unmeasured features | 5 / 0 / 61 | 36 / 14 / 61 (39%, 23%) |

**Of the 52 regions that derived extents add, 15 are correct.** The other 37:

| Why the region is wrong | Records |
|---|---|
| Wrong reference: the annotation names a different GNIS feature | 16 (14 distance-and-direction labels) |
| Wrong reference: the annotation says the true place is not in GNIS | 15 |
| Wrong reference: the label is unsupported (route or itinerary) | 4 |
| Right reference, interpretation wrong | 2 |

## What this means

- **The earlier 91% precision was an artefact.** The reviewed store measured only the features
  the annotations accepted, so a wrong pick could never get a region. When every feature can get
  one, regions are right 63% of the time on owner-annotated data, and 39–47% on Claude-annotated
  data.
- **The bottleneck is choosing the reference, not measuring it.** The typical miss is a label
  that names a specific collecting place (often missing from GNIS) and also gives "N mi of
  Town". The system takes the town. The rules-3 and rules-4 changes aimed at exactly this and
  showed no gain on dev-3 and dev-4.
- **Derived extents stay opt-in.** They turn "needs information" into regions on new labels
  (useful coverage 0 → 23% on dev-3 and dev-4). But most of those regions would then reach
  `ready_for_review` with the wrong place, against a target of 95% correct. Every proposal is
  still reviewed by a curator, and the extent source is shown.
- **Next:** a selection-confidence policy that keeps a computed region out of `ready_for_review`
  when the label names another place the reference does not explain. Develop it on dev data,
  then check it on unread data.
- **Not measured:** containment, since there are no independently defensible positions for these
  records. Also anything on the locked test or test-2.
