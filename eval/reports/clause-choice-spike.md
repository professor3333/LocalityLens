# Clause-choice spike: one model call to pick the collecting place (negative)

**Question.** In "Place, N mi DIR of Town" labels, hybrid-1 usually uses the town where the
annotation names the place. Can one schema-constrained model call choose between the label's
places better, given the GNIS evidence for each?

**Method** ([script](../../scripts/clause_choice_spike.py),
[prompt](../../scripts/clause_choice_prompt-v1.txt), [counts](clause-choice-spike.json)):
- **Data:** read dev data only, so this is in-sample.
  - audit-50, dev-1 and validation are owner-annotated.
  - dev-2 to dev-4 are Claude-annotated.
  - The labels are "place, offset" ones (text shape 2).
- **The options:**
  - **A:** hybrid-1's current reading;
  - **B onwards:** each other clause of the label that GNIS matches exactly or by core name, with
    its name, class, county and distance from the offset point.
- **The call:** the release model (Qwen3.5-4B Q4_K_M), greedy, with the answer constrained to one
  option letter. Three few-shot examples use invented names.
- **No tuning:** the prompt was written once and run once.
- **Scoring:** the scorer's `judge()`. A switched option is read as a named feature.
- **Compared with:** hybrid-1, a plain rule (switch to a place GNIS puts inside the offset
  region) and the best option available (the ceiling).

## Result

| Labels | Owner-annotated | Claude-annotated | All |
|---|---|---|---|
| "Place, offset" labels | 23 | 75 | 98 |
| Answerable, with a hybrid-1 reference | 13 | 45 | 58 |
| … with another clause GNIS has (a real choice) | 5 | 14 | 19 |

| On the 19 with a choice | Right reference | Correct proposal candidate |
|---|---|---|
| hybrid-1 | 9 | 6 |
| Plain rule (switch if inside the region) | 11 | 7 |
| **Model choice** | **10** | **7** |
| Best option available | 14 | 9 |

- **No better than the rule.**
  - **Against hybrid-1:** the model fixed 4 wrong choices and broke 3 right ones.
  - **On owner-annotated labels:** right references 2 against hybrid-1's 2, and correct
    candidates 1 against 2.
- **The ceiling is small.** Even a perfect chooser among these options gains 3 correct
  candidates on 98 labels. Most answerable labels (39 of 58 with a reference) name no other place
  that GNIS has as a whole clause.

## What it shows

- **Not pursued:** the prompt, the declared test and a second model call in the pipeline.
- **The error on these labels isn't a choice among places GNIS lists.**
  - **Annotated place not offered:** it often isn't a whole clause GNIS matches exactly. It may
    be a position on a feature, a partial name, or a variant.
  - **Absent from GNIS:** in other labels the annotated place isn't in GNIS at all.
  - **Implication:** better clause choice needs better place extraction and matching first, which
    are the earlier retrieval findings.
- **Limits:** 19 labels, read data, mostly Claude-annotated, and annotations from before the
  absent-place rule. The options come only from whole clauses with exact or core GNIS matches.
