# dev-4 scored (scored once by the pinned plan)

dev-4 is 50 groups drawn on 2026-11-06, 35 of them "place, offset" labels, drawn to test the
place-or-offset rules independently of their author. **The owner then decided that Claude
annotates it** (commit `90b36be`), so, like dev-3, it is not an independent check of rules
Claude wrote. The plan was revised to say so and pushed with the annotations at 08:24:48, before
any system ran (first output 08:25:26). Scored by
[`eval/dev/dev-4/scoring-plan.md`](../dev/dev-4/scoring-plan.md); code frozen at rules-6
(`c8069be`, plus the annotator name in reports). The locked test was not run.

**One run, resumed once.** The LLM run was killed after 12 of 50 completions when the session
that started it ended. It was restarted with the completion cache: 12 hits, 38 new calls.
Decoding is greedy, so the output is what one uninterrupted run gives. The rules-6 reports
written before the interruption reproduce byte for byte.

## Results

| On dev-4 (29 answerable) | rules-6 | LLM v2 | hybrid-1 |
|---|---|---|---|
| **Correct proposal candidates** | 9 (31%) | **14 (48%)** | 10 (34%) |
| Critical interpretation exact (of 50) | 18 | 25 | 18 |
| Acceptable reference ranked first | 16 | 18 | 19 |
| Excluding the 8 unsure rows (24 answerable) | 9 | 11 | 10 |

- **LLM against the rules:** +5 records (+17 points, 95% bootstrap CI −3 to +38, exact sign
  test p = 0.18). LLM-only 7, rules-only 2. 3 of its 50 extractions were rejected by
  validation. Latency on the 38 new calls: p50 10.2 s, p95 16.3 s (Apple M1, 8 GB).
- **hybrid-1 against the rules:** +1 record (CI +0 to +10, p = 1.0), never behind. The LLM was
  called on 18 records and used on 5.
- **Records:** 29 answerable, 13 with the reference absent from GNIS, 8 unsupported.

**Why hybrid-1 trails the LLM here.** hybrid-1 asks the LLM only when the rules reach no
gazetteer candidate. In 6 records the rules reached a wrong candidate and the LLM, never asked,
had it right (G07, G18, G23, G30, G47, G50). Three of those are the place-or-offset decision:

| Record | Rules (rules-6) | LLM | Annotation |
|---|---|---|---|
| G18 | offset from Douglas Pass | Cathedral Creek ✓ | Cathedral Creek |
| G23 | Mesa de Maya (collecting place) | offset from Kim ✓ | offset from Kim |
| G47 | offset from Grand Lake | Lulu Mountain ✓ | Lulu Mountain |

In G30 and G50 both systems pick the same reference, and the LLM's critical fields are right
where the rules' are not.

## The rule question (primary)

Each rules version replayed on dev-4 ([`dev-4-rules-question.json`](dev-4-rules-question.json),
by `scripts/replay_rules_versions.py --sample dev-4`):

| Correct candidates | rules-2 | rules-3 | rules-4 | rules-5 | rules-6 |
|---|---|---|---|---|---|
| Place-offset stratum (22 answerable) | 6 | 6 | 5 | 5 | 5 |
| All answerable (29) | 10 | 10 | 9 | 9 | 9 |

**Result: "against", by the plan's definition, with the smallest possible margin.** rules-6
gains one place-offset record from rules-2 (G34, Steamboat Mt.) and loses two (G05, G23):
difference −1 of 22 (CI −18 to +9 points, p = 1.0). As the plan said, a one-record margin
proves little. The expectation stated in the plan was "no difference".
**Sensitivity:** G19 and G38 (near repeats) are both "reference absent", so they are not in
this comparison and the result is the same without them.

What the versions did on dev-4:
- **rules-3 helps once and hurts twice.** It finds Steamboat Mt. (G34). It reads "East of
  Tolland" as a place name (G05), and it takes Mesa de Maya over the annotated offset (G23). In
  G16 it keeps the position word in the name ("Slope of Caribou Hill"), which GNIS doesn't
  match.
- **rules-4 reverts rules-3's other gain** (G22, "Shale Hills" read as a broad place), as it did
  with Monte Cristo Creek on dev-3.
- **rules-5 changes one unsupported label** (G37: a range no longer misread lets the collecting
  place, Mount Guyot, be read). rules-6 changes nothing.

## Regions

3 records reach a full region under the rules and hybrid-1, and 1 under the LLM. **All are
wrong**: offsets from Boulder (G14, 14,678 m; G42, 15,418 m) and from Grand Lake the reservoir
(G47, 20,644 m). Useful coverage is 0 of 29.

## dev-2 to dev-4 together (all annotated by Claude)

| Correct candidates | rules | LLM v2 | hybrid-1 |
|---|---|---|---|
| dev-2 (36) | 19 | 17 | 21 |
| dev-3 (32) | 11 | 14 | 14 |
| dev-4 (29) | 9 | 14 | 10 |
| **Total (97)** | **39** | **45** | **45** |

rules-5 and rules-6 read dev-2 exactly as rules-4 did, so its rules column holds for rules-6. The place-or-offset rules have shown no gain on
two fresh samples (dev-3: 6 → 6, dev-4: 6 → 5 of the place-offset records).

## What this means

- **The place-or-offset rules do not earn their keep.** Across dev-3 and dev-4 they gain 2
  place-offset records and lose 3 against rules-2. Their in-sample gains (rules 46 → 50) did
  not carry over. A next step is to drop rules-3's collecting-place branch, or replace it, and
  check that on data not used to build it.
- **On these labels the LLM reads the place-or-offset choice better than the rules,** and
  rules-first hybrid-1 throws that away whenever the rules reach any candidate. On three
  fresh samples hybrid-1 and the LLM alone tie (45 each of 97), both ahead of the rules (39).
  A hybrid that asks the LLM on multi-clause labels, even when the rules find a candidate, is
  the obvious variant to develop on dev data.
- **Every full region on dev-3 and dev-4 is wrong,** because the references these labels need
  rarely have extents, while the wrong ones (Boulder, Grand Lake) do.
- **These are all Claude-annotated samples.** Independent evidence still needs the owner's
  annotation or the locked test in a declared release.
