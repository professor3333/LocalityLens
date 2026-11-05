# dev-3 scored (scored once by the pinned plan)

dev-3 is 50 groups drawn on 2026-11-05, 35 of them "place, offset" labels. Claude annotated it
at the owner's request before any system ran (0 checker problems). It was scored once by
[`eval/dev/dev-3/scoring-plan.md`](../dev/dev-3/scoring-plan.md), which was pushed first. The
code was frozen at rules-6 (`c848b4a`). The locked test was not run.

**Read every number here with the stated limit:** Claude also wrote the rules being tested, so
dev-3 is not an independent check of them.

## Results

| On dev-3 (32 answerable) | rules-6 | LLM v2 | hybrid-1 |
|---|---|---|---|
| **Correct proposal candidates** | 11 (34%) | 14 (44%) | **14 (44%)** |
| Critical interpretation exact (of 50) | 20 | 20 | 21 |
| Acceptable reference ranked first | 19 | 19 | 22 |
| Excluding the 11 unsure rows (25 answerable) | 9 | 12 | 12 |

- **hybrid-1 against the rules:** +3 records (+9 points, 95% bootstrap CI +0 to +22, exact sign
  test p = 0.25). Hybrid-only 3, rules-only 0. The LLM was called on 13 of 50 records and used
  on 3.
- **LLM against the rules:** +3 records (+9 points, CI −6 to +25, p = 0.45). LLM-only 5,
  rules-only 2. 10 of its 50 extractions were rejected by validation. Latency on 50 new calls:
  p50 11.3 s, p95 16.7 s (Apple M1, 8 GB).
- **Records:** 32 answerable, 10 with the reference absent from GNIS, 8 unsupported.
- **Harder than dev-2.** The rules get 34% here against 53% on dev-2, because dev-3 is mostly
  multi-clause "place, offset" labels. The order is the same as before: hybrid-1 ahead of the
  rules and never behind.

## The rule question: rules-3 to rules-6 against rules-2

As the plan set out, each rules version's `baseline/rules.py` was replayed through the current
pipeline and scorer ([`scripts/replay_rules_versions.py`](../../scripts/replay_rules_versions.py),
output [`dev-3-rules-question.json`](dev-3-rules-question.json)). The rules-6 replay matches
the committed rules-6 run on every record.

| Correct candidates | rules-2 | rules-3 | rules-4 | rules-5 | rules-6 |
|---|---|---|---|---|---|
| Place-offset stratum (24 answerable) | 6 | 7 | 6 | 6 | 6 |
| All answerable (32) | 11 | 12 | 11 | 11 | 11 |

**Result: not shown.** On the place-offset records rules-6 gains one record from rules-2 and
loses one (difference 0, CI −12.5 to +12.5 points, p = 1.0).

Eight records read differently across the versions:

| Record | Category | rules-2 | rules-3 | rules-4 to rules-6 | Annotation |
|---|---|---|---|---|---|
| F50 | answerable | offset from Grand Lake | **Thunder Pass** ✓ | **Thunder Pass** ✓ | Thunder Pass |
| F48 | answerable | **offset from Walden** ✓ | North Park | North Park | offset from Walden |
| F45 | answerable | offset from Hoosier Pass | **Monte Cristo Creek** ✓ | offset from Hoosier Pass | Monte Cristo Creek |
| F18 | answerable | offset from Bakerville | Arapaho National Forest | Arapaho National Forest | Engelmann Peak |
| F42 | answerable | offset from "Hwy" | San Luis Valley | San Luis Valley | San Luis Lake (a later clause) |
| F36 | reference absent | offset from Seedhouse G.S. | Little South Fork of Elk River | offset from Seedhouse G.S. | offset from Seedhouse G.S. (absent) |
| F43 | reference absent | offset from Woodland Park | Manitou Experimental Forest | same | Manitou Experimental Forest (absent, unsure) |
| F49 | reference absent | offset from "Hwy" | Peekaboo Basin | same | Peekaboo Basin (absent) |

- **The collecting-place rule (rules-3) helps and hurts in equal measure.** It finds the place
  in F50 and F45, and reads the annotated (but ungazetteered) place in F43 and F49. It takes a
  broad region over the annotated offset in F48 (North Park) and gives no gain on F42, whose
  place is in a later clause.
- **F18 is a span bug, not a rule choice.** The rule fires on "…Engelmann Peak, 3 miles north of
  Bakerville", the annotated place, but the place it finds runs across the sentence break
  ("Arapaho National Forest. Engelmann Peak") and the feature is cut to "Arapaho National
  Forest". It is found on dev-3, so a fix would be in-sample here.
- **rules-4's broad-feature rule cost F45 and fixed F36.** It sends a stream (Monte Cristo Creek)
  back to the offset, where the annotation takes the stream as the collecting place, and in F36
  it rightly keeps the offset over a stream.
- **rules-5 and rules-6 change nothing on dev-3.** No dev-3 label has a range of the kinds they
  fix, so rules-6 is not in-sample here.

## Regions

Only 2 records reach a full region, the same 2 for all three systems, and **both are wrong**:

| Record | System reading | Radius | Annotation |
|---|---|---|---|
| F13 | offset from Boulder | 14,678 m | reference absent from GNIS |
| F45 | offset from Hoosier Pass | 6,720 m | Monte Cristo Creek |

Useful coverage is 0 of 32. dev-3's references are mostly unmeasured, so this says little about
region precision, except that the regions computed here come from wrong readings, as in
[extents batch 4](extents-batch-4-findings.md).

## What this means

- **hybrid-1 stays ahead of the rules on new labels** (+3 here, +2 on dev-2, never behind),
  with weak, Claude-annotated evidence.
- **There is no evidence that the place-or-offset rules help.** Across rules-2 to rules-6 the
  gains and losses cancel on dev-3's answerable records. The in-sample gains on the read samples (rules 46 → 50)
  did not carry over.
- **The decision "place or offset" is the open problem.** A rule keyed on name words (broad or
  not) gets these labels right about as often as it gets them wrong. Any next change should be
  developed on read data and checked on data annotated by the owner, not by the rule's author.
- **Next independent evidence:** the owner's annotation of the 24 answerable place-offset
  records (blind to these results), or the locked test in a declared release.
