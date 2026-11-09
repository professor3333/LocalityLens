# Results at v0.1.1: what is shown, how strongly, and what failed

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

## Failed or not adopted

- **`selection-1`** held a region back when the label names another typed feature.
  - Read data: precision rose to about 70%.
  - Unread test-2: it held back 8 correct and 7 wrong regions, and halved coverage
    ([result](../eval/reports/test-2-regions.md)). It is opt-in and not recommended.
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
