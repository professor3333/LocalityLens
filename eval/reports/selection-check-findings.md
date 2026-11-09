# Selection check (`selection-1`): holding back regions whose reference is in doubt

[Derived extents](derived-extents-findings.md) showed that once every feature can get a region,
most wrong regions come from the choice of reference. The typical case is a label that names a
specific collecting place and also gives "N mi of Town", where the town is chosen. This check
looks at the label, not the geometry. A computed region whose label names another feature, with
a stated type that the proposal does not use, goes to `needs_information` with a question. The
region is kept, and a curator's approval answers the question.

**The rule** ([`resolve/selection.py`](../../src/localitylens/resolve/selection.py)):
1. The label is split at sentence and clause breaks.
2. A run of capitalised words *competes* when all of these hold:
   - its last word is one of the shared feature words (creek, lake, peak, pass, gulch, river…);
   - it is not a broad area (a range, mountains, hills, a wilderness, a park, forest or monument);
   - it is not the chosen reference, and does not contain it.

The rule is opt-in (`--selection-check`) and versioned, and reports carry `-sel`. It was written
from the dev and validation records below, so **every number here is in-sample**. Numbers are
in [`selection-check.json`](selection-check.json).

## Result on the read samples (hybrid-1, reviewed + derived extents)

| Samples | Ready regions | Correct | Useful coverage |
|---|---|---|---|
| Owner-annotated (audit, dev-1, validation; 92 answerable): no check | 52 | 33 (63%) | 36% |
| … with the check | 38 | 27 (**71%**) | 29% |
| Claude-annotated (dev-2 to dev-4; 97): no check | 51 | 24 (47%) | 25% |
| … with the check | 29 | 19 (**66%**) | 20% |
| dev-3 and dev-4 only (mostly unmeasured features): no check | 36 | 14 (39%) | 23% |
| … with the check | 18 | 12 (**67%**) | 20% |

**What it holds back:**
- **Owner-annotated:** 14 regions, 8 wrong and 6 correct.
- **Claude-annotated:** 22 regions, 17 wrong and 5 correct.
- **The correct ones it holds are genuinely ambiguous.** "Rocky Mountain National Park, Baker
  Gulch, 8 mi NNW of Grand Lake" names a gulch that could be the reference as well as the town.
  "Swede Spring on Cold Springs Mountain" names a mountain. Asking is defensible.

**What still gets through (21 wrong regions):**
- **Places with no feature word:** "Collegiate Peaks Overlook", "Rocky Flats Site", "Mount
  Calvary Cemetery".
- **References absent from GNIS,** where a same-named feature elsewhere is taken.
- **Labels where the annotation guide's choice between the offset's town and the collecting
  place is itself a judgment.**

**A broader rule was tried and rejected.** It counted any capitalised name other than the
reference.
- On owner-annotated data it reaches 86% correct (18 of 21 ready), but holds back 15 of the 33
  correct regions.
- It halves coverage for a precision the target (95%) still does not reach.

## What this means

- **The check moves precision from about 50–60% to about 70%,** at a cost of a few points of
  coverage. It is still far from the 95% target. Most of the remaining errors cannot be seen in
  the label text.
- **These are in-sample numbers.** A declared check on unread labels comes next (test-2, totals
  only).
- **The check does not change any region, extent or interpretation.** It only decides which
  computed regions a curator sees as ready and which come with a question.
