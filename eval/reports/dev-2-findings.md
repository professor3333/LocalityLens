# dev-2 scored (fresh dev data, scored once by the pinned plan)

dev-2 is 50 groups drawn on 2026-11-05 after rules-3 and before rules-4. The owner annotated it
from the guide and GNIS (0 checker problems), and it was scored once by
[`eval/dev/dev-2/scoring-plan.md`](../dev/dev-2/scoring-plan.md), which was pushed before any
system ran. The code was frozen at rules-4 (`2bfc227`). The locked test was not run.

## Results

| On dev-2 (36 answerable) | rules-4 | LLM v2 | hybrid-1 |
|---|---|---|---|
| **Correct proposal candidates** | 19 (53%) | 17 (47%) | **21 (58%)** |
| Critical interpretation exact (of 50) | 32 | 29 | 33 |
| Acceptable reference ranked first | 20 | 18 | 22 |
| Excluding the 8 unsure rows (31 answerable) | 19 | 16 | 20 |
| Excluding E40 (35 answerable, see below) | 18 | 16 | 20 |

- **hybrid-1 against the rules:** +2 records (+6 points, 95% bootstrap CI +0 to +14, exact sign
  test p = 0.5). Hybrid-only 2, rules-only 0.
- **LLM against the rules:** −2 records (−6 points, CI −25 to +14, p = 0.77). LLM-only 5,
  rules-only 7.
- **The LLM** was called on 14 of 50 records in hybrid-1 and used on 2. On its own it had 6 of 50
  extractions rejected by validation. Latency on 49 new calls: p50 9.9 s, p95 20.6 s (Apple M1,
  8 GB).
- **Records:** 36 answerable, 13 with the reference absent from GNIS, 1 unsupported.

**Against the read samples.** These rates are close to the in-sample rates on audit, dev-1 and
validation together: rules-4 50/92 (54%), LLM 46/92 (50%), hybrid-1 55/92 (60%). So there is no
sign that the rules were overfitted to the read samples. dev-2 cannot say whether rules-3 and
rules-4 themselves generalise, as the next section shows.

## Rules-3 and rules-4 on dev-2: almost no evidence

Only 3 records have a known place written right before an offset, the case these rules decide.
They were listed from the rules' output before the annotations were read. Running the exact code
of each version on them:

| Record | rules-2 | rules-3 | rules-4 | Annotation | Correct? |
|---|---|---|---|---|---|
| E01 | offset from Cowdrey | same | same | named: Trappers Gulch (unsure) | no, in every version |
| E05 | offset from Blue Hill | same | same | offset from Blue Hill (unsure) | no: relation and reference right, but "approx." from another clause is read as qualifying the offset |
| E29 | offset from Boulder | named: Rocky Flats Site | same | named: Woman Ck. | no: rules-3 gets the relation right but the wrong place, and Rocky Flats Site is not in GNIS |

- **rules-4 changes nothing on dev-2.** No dev-2 record has a broad place in a position where
  rules-3 would have used it.
- **rules-3 changes one reading (E29) and no score.** Like A36 in the read samples, the
  annotation's place comes from a later clause, so the rule picks the right relation but the
  wrong place.

The annotator also wrote rules-4, so on these records the annotation is not independent of the
rule. With 3 records and no score changes, that does not move any total, but it means dev-2 is
not the test of these rules. A sample stratified toward "place, offset" labels, or the locked
test in a declared release, would be.

## Regions

The extent store holds few dev-2 references, so only 2 records reach a full region:

| Record | Region | Correct |
|---|---|---|
| E24, Swede Spring | 42 m: the guide's 3 m spring default plus coordinate precision | yes |
| E40, Hoosier Pass | 2,239 m: the measured extent, 2,200 m | yes |

Useful coverage is 2 of 36 for the rules and for hybrid-1. That says nothing about precision on
unseen data, and only that dev-2's references still need extents.

**Update (extents batch 4):** after 12 of dev-2's references were measured, hybrid-1 computes 11
regions on dev-2, 10 correct (useful coverage 10 of 36). The plan's reports above are kept as
`dev-2-*-extents-plan`. See the [batch 4 findings](extents-batch-4-findings.md).

## A repeated label: E40 is not unseen

E40, "Hoosier Pass.", has exactly the same text as validation's V021. Their supplied counties
differ (blank against "Park/Summit"), so the grouping counted them as different groups. The
model input holds no county for E40, so the LLM saw the same prompt: the run reports one cache
hit. E40 is correct for all three systems. Without it, the counts are 18 / 16 / 20 of 35.

- **The cause:** groups are keyed by locality text and supplied county, so identical text with
  a different county can fall in different splits.
- **The locked test is not affected:** by text hashes only, none of its 120 locality texts
  repeats a text in audit, dev-1, validation or dev-2.
- **Future samples:** identical text with a different county should count as already viewed.
  That is a grouping change (a new grouping version), not made here.

## What this means

- **Fresh data agrees with the read samples on the overall picture.** hybrid-1 is ahead of the
  rules by a small, consistent margin (+2 here, never behind), and the LLM alone is not better
  than the rules.
- **The collecting-place rules are still untested on unseen data.** dev-2 has almost none of
  the labels they decide.
- **Next evidence:**
  - extents for dev-2's references, for regions on unseen data
  - a stratified sample, or a declared test release (which needs the owner's authorisation),
    for the place-before-offset rules
