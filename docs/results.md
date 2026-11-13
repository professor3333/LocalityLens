# Results at v0.1.3: what is shown, how strongly, and what failed

One page. Every number comes from a committed report, linked below; the full measures and
definitions are in [evaluation](evaluation.md).

## Independent evidence (owner-annotated, held out, declared before each run)

**Locked test, 120 records, 56 answerable.** Correct proposal candidates are records whose
critical interpretation matches and whose top-ranked reference is acceptable:

| | Rules | LLM alone (Qwen3.5-4B) | **hybrid-1** (rules first, LLM fallback) |
|---|---|---|---|
| Release 3 (rules-6, the components in v0.1.x) | 22 | 18 | **28** |

- **hybrid-1 − rules: +10.7 points** (95% CI +3.6 to +19.6, p = 0.031): the +10 point target is
  met. The margin is the smallest that clears it (6 records gained, 0 lost), and the same margin
  appeared in release 2 ([release 3](../eval/reports/test-release-3.md)).
- **The LLM alone does not beat the rules** (releases 1 and 3).
- **The test has been scored three times.** Changes between releases were designed on dev data.

## Weak evidence (Claude-annotated or read data)

- **test-2, 120 fresh records, declared before annotation, Claude-annotated:** hybrid-1 43 vs
  rules 34 of 80 answerable, +11.3 points ([result](../eval/reports/test-2.md)).
  - **Why weak:** the annotator also wrote the rules, and marks more references as findable in
    GNIS than the owner does. On 20 blind repeats the two agree on every field for 12.
- **The LLM's few-shot examples carry most of its result.** Without them, it gets 11 instead of
  46 of 92 on read samples ([ablation](../eval/reports/ablation-fewshot-findings.md)).
- **GEOLocate, on read samples:** within 5 km of the defensible position, GEOLocate 58 and
  hybrid-1 61 of 85. GEOLocate answers more often; ours abstains more
  ([comparison](../eval/reports/geolocate-findings.md)).

## Regions: the main shortfall

A proposal needs the feature's extent to become a region. Extents came first from hand
measurements (67 features), and now also from Census place polygons and USGS NHD geometry
(11,993 features, opt-in; derived extents match hand measurements to a median ratio of 0.98)
([derived extents](../eval/reports/derived-extents-findings.md)).

| hybrid-1 regions | Ready | Correct | Useful coverage | Targets |
|---|---|---|---|---|
| Read samples, hand extents only | 35 | 32 (91%) | 35% | ≥ 95% / ≥ 70% |
| Read samples, + derived extents | 52 | 33 (63%) | 36% | |
| **test-2 (unread), + derived extents** | 31 | 18 (58%) | 22.5% | |

- **The 91% was an artefact.** Hand extents existed only for references the annotations
  accepted, so a wrong pick could never get a region.
- **The real weakness is choosing the reference.** A label names a specific collecting place
  (often not in GNIS) and gives "N mi of Town", and the town is chosen.

## Adopted in v0.1.2: the selection check

`selection-2` holds a full region back for the curator when the label names another place that
GNIS has inside the region, or one GNIS lacks. From v0.1.2, `review import` and `review work`
apply it by default (`--no-selection` turns it off). It was adopted because it passed the last
of three declared checks, each on 120 unread "place, offset" labels and declared before
annotation:

| Check | Annotator | Held back: wrong / correct | Precision of ready regions | Result |
|---|---|---|---|---|
| [test-3](../eval/reports/test-3.md) | Codex, before the absent-place rule | 22 / 2 | 13% → 17% | does not work (+4.0 < +5) |
| [test-4](../eval/reports/test-4.md) | Claude (not independent) | 17 / 7 | 55% → 72% | works |
| [test-5](../eval/reports/test-5.md) | Codex, under the absent-place rule | 14 / 4 | 32% → 42% | works |

- **What it changes:** nothing in the correct proposal candidates, so releases 1–3 still describe
  the system. It moves ready regions to `needs_information` with a question, and approving
  answers it.
- **What it costs:** useful coverage on these labels (test-5: 11.1% → 7.4%).
- **What it doesn't fix:** precision stays far below 95%. Most wrong regions name a place GNIS
  has while the system uses the offset's town (test-5: 23 of 25).
- **None of the three checks was owner-annotated.**

## Failed or not adopted

- **A model call to choose the collecting place** (read dev data, one prompt, run once): on 19
  "place, offset" labels with a real choice, it picks the right reference in 10 against hybrid-1's 9
  and a plain GNIS-inside rule's 11 (correct candidates 7, 6, 7). The ceiling over all options is
  only 9 ([spike](../eval/reports/clause-choice-spike.md)). Not pursued.
- **Quantization parity gate:** the shipped Q4_K_M loses 2.3 to 3.2 points of critical exact
  match to Q8_0 (48.7% vs 51.0% and 51.9% in two runs, 310 dev and validation records), against
  the release spec's 1-point
  limit. The difference is not significant (p = 0.30), and correct proposals are within one
  record. Q4_K_M is kept, and the release check records the failure
  ([parity](../eval/reports/quantization-parity.md)).
- **Switching to the place selection-2 finds** (read dev data, counts only): of 25 held-back
  regions, 14 name a place GNIS has inside the region. Switching to it would give 1 correct region:
  the place is an acceptable reference in 8, the reading matches in 4, and only 6 have an extent.
  Not built ([feasibility](../eval/reports/selection-switch-feasibility.md)).
- **`selection-1`** held a region back when the label names another typed feature.
  - Read data: precision rose to about 70%.
  - Unread test-2: it held back 8 correct and 7 wrong regions, and halved coverage
    ([result](../eval/reports/test-2-regions.md)). It is opt-in and not recommended.
- **`selection-2`, its first check** (adopted later, above): it holds a region back only when GNIS
  places the other named place inside the region, or doesn't have it.
  - **test-3:** 120 unread "place, offset" labels, Codex-annotated (agreement with the owner
    54/60 on category, 55/60 on GNIS IDs), declared before annotation.
  - **It held back 22 wrong and 2 correct regions.** Precision rose only from 13% to 17%,
    against the +5 points needed, so under the declared rule it does not work
    ([result](../eval/reports/test-3.md)).
  - **On this label shape, most regions are wrong either way.** Of the 53 ready regions
    without the check, 7 are correct.
  - **Diagnosis** (counts only, used set): 41 of the 46 wrong regions are a clause choice. In 21
    of them the annotated place is absent from GNIS, a case the annotation guide doesn't settle
    ([diagnosis](../eval/reports/test-3-diagnosis.md)).
  - **Second-annotator review of 23 disputed rows** (Claude, at the owner's request; not a human
    check, and Claude wrote the systems), under the guide's new BP §3.2.2 rule (annotate the
    offset when the specific place is not in GNIS):
    - with Codex's place absent from GNIS, 6 of 10 offset regions become correct;
    - with the place in GNIS, 2 of 10 are correct.
    - **Estimated ready-region precision ≈ 46%** (approx. 36–57%) instead of 13%. This is an
      estimate, not a test result ([review](../eval/reports/test-3-review.md)).
- **test-4** (120 fresh "place, offset" labels, Claude-annotated at the owner's choice under the
  absent-place rule, declared before annotation; not independent): hybrid-1 60 ready regions, 33
  correct (55%). 18 of the 27 wrong ones name a place GNIS has while the system uses another (the
  declared primary question: supported). selection-2 held back 17 wrong and 7 correct regions,
  precision 55% → 72%, coverage 30.8% → 24.3%: it passes the test-3 rule here, against the
  stated expectation ([result](../eval/reports/test-4.md)).
- **test-5** (120 fresh "place, offset" labels, Codex-annotated under the absent-place rule,
  declared before annotation, to settle selection-2): hybrid-1 37 ready regions, 12 correct (32%,
  coverage 11.1%); 23 of the 25 wrong ones name a place GNIS has. selection-2 held back 14 wrong
  and 4 correct, precision 32% → 42%, coverage 11.1% → 7.4%: **it works by the test-3 rule**, and
  has now passed 2 of 3 declared checks ([result](../eval/reports/test-5.md)).
- **The rules-3 to rules-6 changes for "place, offset" labels** showed no gain on the samples
  drawn to test them (dev-3, dev-4).
- **Qwen3.5-2B** as the fallback gives 49 against 4B's 51 of 92, at a quarter of the model time.
  It is not adopted ([findings](../eval/reports/qwen3.5-2b-findings.md)).
- **The Docker `llm` profile** on an 8 GB laptop takes 540 s per record. Run llama-server
  natively there ([deployment](deployment.md)).

## Not measured

- Regions and containment on owner-annotated held-out data.
- Reviewer time.
- The second model call: not built.
- Annotator self-consistency.
- A deployment on a Linux host.
