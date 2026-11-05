# rules-4: broad features keep the offset

rules-3 let a known place written before an offset replace the offset. Hand-written test labels
showed that it also did this for places far too broad to be a collecting place. rules-4 stops
that before dev-2 is scored, and fixes a crash found while measuring it. **Nobody has read dev-2,
and nothing here used it or the locked test.**

## The problem

| Label (hand-written, not from any sample) | rules-2 | rules-3 | rules-4 |
|---|---|---|---|
| Arkansas River, 5 mi E of Salida | From Salida, needs extent (at least 6.5 km) | Full region, **1,500 km** | From Salida, needs extent |
| Colorado River, 4 mi W of Glenwood Springs | From Glenwood Springs, needs extent (at least 5.3 km) | Full region, **1,300 km** | From Glenwood Springs, needs extent |
| San Juan Mountains, 12 mi E of Silverton | From Silverton, needs extent (at least 15 km) | Range, needs extent (lower bound 39 m) | From Silverton, needs extent |
| Rocky Mountain National Park, 3 mi W of Estes Park | From Estes Park, needs extent | Park, needs extent | From Estes Park, needs extent |
| Boulder, 2 mi W of Boulder | From Boulder | Boulder itself | From Boulder |

A 1,500 km circle around a river's mouth answers nothing, and the score would have counted it as
correct whenever the river was the annotated reference, because precision ignores region size.

## The rule

The place written before an offset no longer replaces it when:

- **its last words state a broad feature:** a stream (the shared `TYPE_WORDS` table, plus "R."), a
  range or hills (Mountains, Mtns., Mts., Range, Hills), a park or forest (National Park, State
  Park, National Forest, State Forest, National Monument) or a wilderness
- **it is the offset's own base** ("Boulder, 2 mi W of Boulder")

This applies whether or not a position word comes first ("West side of Gunnison River, 4 mi E of
Delta"). "Park" alone stays out because it is usually a town (Estes Park).

## Results

### Read samples (in-sample)

No score changes on audit, dev-1 or validation, and no record gains or loses. The LLM reports
were reused unchanged.

| With the 56 reviewed extents | rules-4 | LLM | hybrid-1 |
|---|---|---|---|
| Correct proposal candidates (of 92) | 50 | 46 | **55** |
| Regions computed | 31 | 33 | **34** |
| … correct | 30 (97%) | 29 (88%) | **33 (97%)** |
| Useful coverage (of 92) | 30 (33%) | 29 (32%) | **33 (36%)** |

**One reading changes, for the worse:** D27, "Pond, west side of Colorado R. near mouth of Red
Creek, 9½ mi N of Grand Lake." rules-3 read Red Creek as a named feature, which matched the
annotated relation, though not the annotated reference (the Colorado River). rules-4 goes back to
the offset from Grand Lake, so the relation no longer matches. The record was not correct either
way.

These samples cannot justify this change, because no read record opens with a broad feature. The
reason for it is the table above and the count below.

### Unread groups (counts only)

To measure how often this happens, rules-3 and rules-4 were compared on every locality group
outside the viewed registry and the reserved set, 38,352 of the snapshot's 40,444. Only counts were
printed, with no label text or names, so those groups stay unread.

| | Groups |
|---|---|
| rules-3: a place replaces an offset | 1,323 |
| rules-4: a place replaces an offset | 963 |
| **Returned to the offset by rules-4** | **360 (27% of the rule's cases)** |
| … stream | 190 |
| … range or hills | 127 |
| … park, forest, monument, wilderness | 35 |
| … not classified by the count | 8 |
| rules-4: reads an offset | 11,616 |

So the case is uncommon overall, under 1% of groups, but it was over a quarter of what the rule
did. The count shows how often the rules differ, not which reading is right.

## The crash

Any label with "Mt" and no dot ("Mt Evans.") raised `KeyError` in the rules extractor, and had
done since rules-1: `mt` counted as a head word but isn't in `TYPE_WORDS`. The 280 records run so
far happened to avoid it. It hits 5 of the 38,352 unread groups on rules-3 and none on rules-4.

A dotless "Mt" now states no feature type. The name is still read, and the type only ranks
candidates. It was not added to `TYPE_WORDS`, because that table also checks LLM output and the
frozen LLM runs would change. A test now requires every head word to be in the table.

## What this does not settle

- **The word list is a judgment, not a measurement.** "Gunnison River, 4 mi E of Delta" may really
  mean the river. How such labels are annotated on dev-2 is the first evidence.
- **Names that don't state their breadth still win:** "South Park, 8 mi W of Fairplay" takes South
  Park, and valleys and basins are not excluded.
- **A town that opens a label still wins:** "Lyons, 3 mi N of Boulder" takes Lyons. There is no
  evidence yet either way.
- **Precision still ignores region size**, so a bare "Arkansas River." still counts as a correct
  1,500 km region when that is the annotated reference. Reports on dev-2 should show region sizes
  next to the score.

Reports: `<sample>-rules-4[-extents]`, `<sample>-hybrid-1[-extents]`,
`<sample>-score[-hybrid-1][-extents]`. The rules-3-era hybrid and score reports are kept as
`*-pre-rules-4`.
