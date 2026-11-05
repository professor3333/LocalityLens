# Reviewed feature extents (`extents-1`)

GNIS gives each feature a single representative point. A town, summit, valley or stream is
bigger than that, so a proposal's radius stays **unknown** until someone measures how far the
feature reaches. [`extents.csv`](extents.csv) holds those measurements, one row per GNIS
feature. Every value is a recorded map measurement that says who made it: a person, or a
named tool working through a map interface. LocalityLens code never computes or guesses one.

`propose` uses an extent from this file in place of "unknown". A record whose reference has a
reviewed extent (and no other blocking question) becomes `computed`, a full point-radius
region.

## What to measure

The **geographic radial**: the straight-line distance, in metres, from the point given in the
row (`latitude`, `longitude`, `datum`) **to the farthest point of the feature's boundary**
(Best Practices §3.4.1).

- **Measure from the row's point, not from the feature's middle.** Best Practices measures
  from a corrected center. Proposals start from the GNIS point, so this store does too. The
  radius is then never too small, and the circle still contains the whole feature.
- **Streams:** GNIS puts the point at the mouth, so the radial runs to the far end of the
  stream (its source, or the end of the named reach). It can be tens of kilometres, and that
  is the honest answer.
- **Populated places:** measure to the edge of the settled or incorporated area, and say in
  `note` which boundary you used and that it is the current one. Old labels may describe a
  smaller town.
- **Summits:** the boundary follows the valleys, saddles and plains that separate the mountain
  from its neighbours (Quick Reference Guide §2.1.2). Say in `note` what you took as the edge on
  each side.
- **Gaps:** this is a rule of this project, because the guide has none for passes. Across the
  ridge, a gap ends where each approach reaches its valley floor. Along the ridge, it ends at
  the straight-line midpoint toward each flanking summit or neighbouring pass, adapted from the
  guide's midpoint fallback.
- **Flats, basins, valleys, ranges:** measure to the farthest edge of the named landform as the
  map shows it. Say in `note` what you took as the edge.
- **If you can't defend a number, leave the row pending.** An empty `extent_m` is allowed. The
  record keeps asking for the extent, which is better than a wrong radius.

## How to fill a row

| Column | Fill in |
|---|---|
| `gnis_id` … `datum` | Already filled from the GNIS snapshot. **Don't edit them.** The checker refuses a row whose name, class, county, snapshot or point no longer matches. |
| `extent_m` | The radial in metres, as a plain number (`2400`, not `2.4 km`) |
| `method` | How you measured it (e.g. "measure tool on The National Map, to the far shoreline") |
| `source` | The map or reference you used, with its edition or date if shown |
| `reviewer` | Who measured it: your name or handle, or the tool's name if a tool did |
| `reviewed_on` | The date, as `YYYY-MM-DD` |
| `note` | Optional: the boundary you chose, doubts, anything a later reviewer should know |

Then check the file:

```console
$ uv run localitylens extents check
extents-1: 56 reviewed, 41 pending, 0 problems
```

## Rules

- **Don't look at specimen coordinates** while measuring. An extent describes the feature,
  not where a specimen was collected.
- **Features come from dev and validation annotations only.** The worksheet command refuses
  the locked test split. Extents for test references belong to a future declared release.
- **One row per feature.** A correction replaces the row's values. Git history keeps the old
  ones.
- **A changed file is a changed release input.** Reports record the store's SHA-256, and
  combining reports refuses components that used different stores.

## Where the rows came from

`uv run localitylens extents worksheet` wrote one pending row for every acceptable GNIS ID of
an answerable record whose annotated type can become a proposal (named feature, distance and
direction, distance only). It used the audit, dev-1 and validation worksheets, 97 features in
all. It never overwrites an existing file.

## How the measured rows were checked

- **Towns** (incorporated or census-designated place limits on The National Map): the extent
  must be at least the farthest vertex of the town's own polygon in the USGS `govunits`
  service. Matching is by place name, because those polygons carry census-entity GNIS IDs,
  not the populated-place IDs in this file.
- **Streams and any row whose note gives an end point:** the GRS80 geodesic distance from
  the row's point to that end point must not exceed the extent.
- **Summits and gaps:** the same geodesic check runs to the recorded far point. It tests the
  arithmetic, not where the edge was drawn, so these rows are rougher than town limits. Four
  far points were also placed on the USGS National Map 3D Viewer to confirm they fall where
  their notes say.
- **Summits and gaps, against elevation:** a USGS 3DEP profile (Elevation Point Query
  Service) along each measured line. A summit's profile must fall to its far point without
  crossing a separate summit (a rise of more than about 300 ft above a saddle), and a gap's
  approach must end on a valley floor. This check corrected Thunder Mountain and Veta Pass.
  Fremont Pass went back to pending, because its north side is mine-altered ground.
- **Towns stay pending** when The National Map has no limit of their own (Hesperus, Gothic,
  Climax, …). **Streams stay pending** when the far end of the named reach isn't clear.
  **Summits stay pending** when a slope or mesa surface runs on with no edge, or when the map
  can't settle what the name covers (Two Buttes). **Gaps stay pending** when an approach
  has no natural valley floor (Fremont Pass).
