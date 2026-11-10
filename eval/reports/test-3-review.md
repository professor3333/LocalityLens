# test-3 review: a second annotator on the disputed rows

The computation planned in [the review plan](../calibration/test-3-review/README.md), pushed
before the sheet was annotated. Its amendment, recording the change of annotator, was pushed
before anything was computed. It ran once, from `scripts/score_test3_review.py`, and only counts
are published.

- **Annotator: Claude, at the owner's request,** not the owner as first planned. Claude also wrote
  the systems and the new guide rule.
  - **So this is not a human check.** "Correct under Claude's annotation" is not independent of
    the system.
  - **Agreement with Codex** is agreement between two AI annotators.
- **Used set:** this is a diagnosis. test-3's declared result ([13% → 17%](test-3.md)) stands.
- **The rows:** 23 hybrid-1 ready regions that Codex's annotations score wrong, drawn by seed
  from the [diagnosis](test-3-diagnosis.md) strata. They were annotated under the guide's new
  rule from GBIF Best Practices §3.2.2: when the most specific place is not in GNIS, annotate the
  next less specific clause.

## Results

| Rows (ready regions) | Sampled | Correct under Codex | Correct under Claude | Notes |
|---|---|---|---|---|
| Clause choice, Codex's place absent from GNIS | 10 of 21 | 0 | **6** | Claude also finds the place absent in 9 of 10 |
| Clause choice, Codex's place in GNIS | 10 of 20 | 0 | **2** | Same acceptable GNIS IDs as Codex in 7 of 10 |
| Other rows with an "unsure" marker | 3 | 0 | 1 | Every field agrees on 2 of 3 |
| **All 23** | 23 | 0 | **9** | |

- **The absent-place convention explains most of the gap.**
  - Claude agrees with Codex that the specific place is not in GNIS (9 of 10).
  - Under the BP fallback the record becomes answerable from the offset, and the system's offset
    region is then correct in 6 of 10.
  - The other 4 still fail on the reading or the reference.
- **Where the place is in GNIS, the system is mostly wrong under both annotators.** Claude
  accepts the same IDs as Codex in 7 of 10, and the system's region is correct in only 2 of 10.
  These are the clear system errors, and selection-2 holds back most of them
  ([diagnosis](test-3-diagnosis.md)).
- **Agreement over all 23 rows is low by construction:**
  - **Fields:** category 12 of 23, acceptable GNIS IDs 9 of 23, every field 9 of 23.
  - **Why:** the new rule turns Codex's 10 "reference absent" rows into answerable ones, and the
    rows were drawn because they were disputed.
  - **Not comparable** with the 54/60 calibration on the validation records.

## Estimate (not a measurement)

The planned estimate of hybrid-1's ready-region precision on test-3, with Claude's annotations
for the reviewed rows and the new rule:
- each stratum's share from its 10 seeded rows, scaled to 21 and 20;
- the other 12 ready regions keep Codex's judgement, except the 2 reviewed unsure rows.

| | Correct of 53 ready regions | Precision |
|---|---|---|
| Under Codex's annotations (declared result) | 7 | 13% |
| **Estimate, Claude's review + BP fallback** | **≈ 24.6** | **≈ 46%** (approx. 36–57%) |

- **The interval is wide:** each stratum rests on 10 rows. It is a normal approximation with a
  finite-population correction.
- **It is not a test result.** The annotator wrote the system and the rule, and the rule was
  chosen after the result was seen. It is still far below the 95% target.

## What this means

- **Most of test-3's 13% comes from the scoring convention, not from the system.** For "Place,
  N mi of Town" with Place absent from GNIS, BP's own rule makes the offset region the expected
  georeference.
- **The real system error is the in-GNIS case.** The label names a place GNIS has, and the system
  uses the town instead. That is about 2 in 10 correct here, and selection-2 holds most of these
  back.
- **Next evidence needs:**
  - fresh unread labels, annotated under the new rule;
  - an annotator other than Claude, ideally the owner;
  - a declaration made before annotation.
