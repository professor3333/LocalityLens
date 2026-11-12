# Switching to the place selection-2 finds: not worth building

**Question.** selection-2 holds a ready region back when the label names another place that GNIS
has inside the region, or one GNIS lacks. Would using that other place instead give correct
regions?

**Method** ([script](../../scripts/selection_switch_feasibility.py),
[counts](selection-switch-feasibility.json)):
- **Data:** the read samples only, so this is in-sample.
  - audit-50, dev-1 and validation are owner-annotated.
  - dev-2 to dev-4 are Claude-annotated.
  - No held-out set is used.
- **Records:** every hybrid-1 region with derived extents that selection-2 holds back.
- **The switch:** take the first "inside" place's first exact or core GNIS match inside the
  region, read as a named feature (offset and qualifiers dropped).
- **Judged** with the scorer's own `judge()`. A region also needs a reviewed or derived extent.
- **Sanity check:** the held-back counts reproduce the earlier dev totals (owner-annotated: 6
  wrong and 3 correct held back; Claude-annotated: 14 and 2).

## Result

| Held-back regions | Owner-annotated | Claude-annotated | All |
|---|---|---|---|
| Held back | 9 | 16 | 25 |
| Only for a place GNIS lacks (no switch possible) | 5 | 6 | 11 |
| With a place GNIS has inside the region | 4 | 10 | 14 |
| … that place is an acceptable reference | 1 | 7 | 8 |
| … the switched reading is a correct proposal candidate | 0 | 4 | 4 |
| … that place has an extent | 2 | 4 | 6 |
| **… a correct region after switching** | **0** | **1** | **1** |

- **Why so few:**
  - **The place is often not the annotated reference:** it is acceptable in 8 of 14, and in 1
    of 4 on owner-annotated data.
  - **The annotated reading is often not a bare named feature:** in 4 of the 8 where the place
    is acceptable.
  - **Most of these places have no extent:** 3 gaps, 3 summits, a valley and a basin, against
    2 lakes and 4 streams that have one. Derived extents cover towns, streams and lakes; summits
    and gaps have hand measurements only for features already reviewed.
- **An automatic switch** would add at most 1 correct region to the 103 ready regions of these
  samples, so it is not pursued.
- **A review-screen suggestion** ("use this place instead") would name an acceptable place 8
  times in 14 (once in 4 on owner data), and most of those places would still get no region.
  Not built.

## What it shows

- **The main error isn't one switch away.** Where the label names a place GNIS has, the fix
  needs three things that are mostly missing here:
  - the right one of several named places;
  - the annotated reading;
  - an extent for small terrain features.
- **selection-2 stays as it is:** it holds these regions back for the curator. That remains the
  better behaviour than drawing a region around the wrong place.
- **Limits:** 14 cases, read data, mostly Claude-annotated, and dev annotations made before the
  absent-place rule.
