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

- **On the dev data it was written from, the check moved precision from about 50–60% to about
  70%,** at a cost of a few points of coverage. It is still far from the 95% target. Most of the remaining errors cannot be seen in
  the label text.
- **These are in-sample numbers, and they did not hold up.** On test-2's unread labels (declared
  check, totals only), the check held back 8 correct and 7 wrong regions. Correct ready regions
  went from 58% to 63%, and useful coverage fell from 22.5% to 12.5%
  ([result](test-2-regions.md)). `selection-1` is kept as a failed experiment: opt-in, never the
  default.
- **The check does not change any region, extent or interpretation.** It only decides which
  computed regions a curator sees as ready and which come with a question.

## selection-2: ask GNIS before holding a region back

selection-1 held back every region whose label names another typed feature, and on unread labels
it held back as many correct regions as wrong ones. **selection-2** asks GNIS about each such
feature, and holds the region back only when:
- **the feature is in GNIS** (exact or core name match) **and its point lies inside the proposed
  region:** the label's offset points at a more specific, real place; or
- **the feature is not in GNIS at all:** the label names a place this gazetteer cannot place.

A feature that GNIS places outside the region, such as "along the Arikaree River", is treated
as a separate landmark and does not count. A synthetic test found that a capitalised sentence
opener ("Below Vela Lake") was glued onto the name. selection-2 drops such words; selection-1
is frozen as it was.

In-sample on the read samples (hybrid-1, reviewed + derived extents):

| | No check | selection-1 | **selection-2** |
|---|---|---|---|
| Owner-annotated: ready / correct | 52 / 33 (63%) | 38 / 27 (71%) | **43 / 30 (70%)** |
| … useful coverage | 36% | 29% | **33%** |
| … held back: correct / wrong | – | 6 / 8 | **3 / 6** |
| Claude-annotated: ready / correct | 51 / 24 (47%) | 29 / 19 (66%) | **35 / 22 (63%)** |
| … useful coverage | 25% | 20% | **23%** |
| … held back: correct / wrong | – | 5 / 17 | **2 / 14** |

- **The trade on read data:** about the same precision as selection-1, with half the coverage
  loss.
- **Also tried, not adopted:** switching the reference to the in-region place, rather than
  holding the region. It fixed 4 Claude-annotated records but broke 3 correct ones, 2 of them
  owner-annotated.
- **These are still in-sample numbers.** selection-2 is tested next on a fresh, unread sample of
  "place, offset" labels annotated by Codex, under a declaration pushed before annotation.
