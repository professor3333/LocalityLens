# rules-3: spaced directions and the collecting place before an offset

rules-3 fixes two rules errors found while measuring extents. All three incorrect hybrid-1
regions came from them. Both fixes were designed on the audit, dev-1 and validation samples,
which have all been read, so **every gain below is in-sample**. dev-2 (drawn for this change,
not yet annotated) and a declared test release are the honest checks. The locked test was not
run.

## The two errors

1. **A spaced direction was cut short.** In "S. slope Mt. Shavano, 10 mi. n. w. Salida." the
   pattern for "Place, 10 mi N" let the direction stop at "n." and read "10 mi N of
   Mt. Shavano". An abbreviated direction can no longer end where another follows ("n. w.").
   No new pattern reads "10 mi. n. w. Salida" without "of": V013 is the only label written
   that way in the 160 records.
2. **The offset's town won over the named collecting place.** In "Vernal Mesa, 15 mi. east of
   Montrose." the rules measured from Montrose. The annotation guide takes the most specific
   clause, and the annotations take Vernal Mesa.

## The rule for the second error

A gazetteer-known place written right before an "N units DIR of X" offset (or a distance-only
offset) becomes the reference, and the offset is read as locating it, when either:

- **a position word puts the specimen on the place**: slope, side, flank, summit, top, foot,
  base, edge, mouth, head, shore or rim ("S. slope of Thunder Mt., 16 miles N of Grand Lake";
  "slope of Douglas Mt., 3/5 mi. SW of Greystone"), or
- **the label opens with the place and the offset is at least a mile** ("Vernal Mesa, 15 mi.
  east of Montrose"). Below a mile, the offset region is about as small as most named places,
  and the annotation takes the offset ("Rollins Pass, 0.3 mi. N. of Needle Eye Tunnel").

The place must end right before the offset's comma or semicolon. It is never a road or trail
name ("Coffee Pot Road, 8 mi W of Hwy 301"), nor a name after "toward", "to", "from", "along"
or "via" ("toward Independence Pass, 11 mi. E of Aspen"). The offset is kept as an open
question for the curator, and a qualifier inside it ("ca. 7 miles west") no longer qualifies
the place.

**What changed on the read samples:** 8 of the 160 records.
- **The new rule:** 7 records (A36, A37, D07, D27, V006, V014, V016).
- **The direction fix:** V013.
- **Relation:** the annotation's (named feature) on all 8.
- **Reference:** the annotation's on 7. The exception is A36, "Chico Basin Ranch, ca. 28 miles
  SE of Colorado Springs. Dry uplands above Black Squirrel Creek.", where the annotation's
  reference comes from a later clause.

The rule leaves alone every label where the annotation took the offset, including:
- V058, "Rollins Pass, 0.3 mi. N. of Needle Eye Tunnel" (under a mile)
- D15, "Rocky Mountain National Park, Baker Gulch, 8 mi. NNW of Grand Lake" (Baker Gulch does
  not open the label)
- D14, "toward Independence Pass, 11 mi. E of Aspen" (a route)
- A14 and A42 (road names)

It misses A05 and V055, where other text sits between the place and the offset.

## Results (dev and validation data; in-sample)

| Correct proposal candidates | rules-2 | rules-3 | hybrid-1 before | hybrid-1 now |
|---|---|---|---|---|
| Audit (31 answerable) | 17 | 17 | 17 | 17 |
| dev-1 (29) | 16 | 17 | 18 | 19 |
| Validation (32) | 13 | 16 | 16 | 19 |
| **All (92)** | 46 | **50** | 51 | **55** |

- **Gained:** D07 (Mineral Basin), V006 (Vernal Mesa), V013 (Mt. Shavano) and V016 (Table
  Mesa), in both rules and hybrid-1.
- **Lost:** none, in any sample or system.
- **Reference now right, record still not correct:**
  - A37 now reaches Thunder Mountain. The annotation's qualifier "About halfway" is not a
    known qualifier word, so the annotation carries none, while the rules report "About" as
    approximate. That is an existing annotation warning, left as it is.
  - D27 and V014 now have the right interpretation. Their reference is still not ranked first:
    Red Creek instead of the Colorado River, and Douglas Mt. not matched.

**With the 56 reviewed extents:**

| | rules-3 | LLM | hybrid-1 |
|---|---|---|---|
| Regions computed | 31 | 33 | **34** |
| … correct | 30 (97%) | 29 (88%) | **33 (97%)** |
| Useful coverage (of 92) | 30 (33%) | 29 (32%) | **33 (36%)** |

Before rules-3, hybrid-1 computed 35 regions, 32 correct (91%). The incorrect regions of V006
and V013 are gone: V006 now asks for the Vernal Mesa extent, which is pending, and V013 is a
correct region around Mount Shavano. The one incorrect region left is A37, on the qualifier
above.

**97% is in-sample.** The rule was written knowing these records, so it says nothing yet
about the ≥95% target on unseen labels.

Reports: `<sample>-rules-3[-extents]`, `<sample>-hybrid-1[-extents]`,
`<sample>-score[-hybrid-1][-extents]`. The rules-2-era hybrid and score reports are kept as
`*-pre-rules-3`.
