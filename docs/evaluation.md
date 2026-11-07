# Evaluation

How LocalityLens is measured, what counts as correct, and what has been measured so far. Data
sources, sampling and annotation are described in the [dataset card](dataset_card.md).

## What counts as correct

A **proposal** is correct only when:
- its **critical interpretation** (relation, distance, unit, direction, qualifiers) matches
  the annotation, **and**
- its selected reference feature is one of the annotation's **acceptable GNIS IDs**.

A region is useful only when it contains the defensible reference position, judged together
with its size: a huge region is not a success. `needs_information` and `unsupported` mean "not
proposable by this release", never "the locality is unusable". Output supports curator review
and is not an authoritative georeference.

A record reaches a full region only when its reference has a measured extent, so the main
measure across all splits is the **correct proposal candidate**: an answerable record whose
critical interpretation matches and whose **top-ranked** candidate is acceptable. It becomes a
correct proposal once the feature's extent is supplied and no other question blocks it.
With the [extent store](../data/reviewed/) (67 of 115 features measured), dev and validation
runs also report regions computed, their precision and useful coverage
([findings](../eval/reports/extents-findings.md), [batch 4](../eval/reports/extents-batch-4-findings.md)):
with rules-6, hybrid-1 computes 35 regions on the 160 read records, 32 correct (91%), a useful
coverage of 32 of 92 answerable (35%); on dev-2's unseen labels, 11 regions, 10 correct (91%),
a useful coverage of 10 of 36 (28%). "Correct" tests the
interpretation and the reference, not the size of the radius.

## Metrics (`evaluation/score.py`)

| Metric | Over | Meaning |
|---|---|---|
| **Correct proposal candidates** | answerable records | Primary metric (above) |
| Critical interpretation exact | all records | Relation, distance, unit, direction and qualifiers all match |
| Field accuracy | all records | Each of distance, unit, direction, qualifiers separately |
| Relation read correctly | all records | The relation type alone |
| Extraction passed validation | all records | Quotes found in the text, values consistent, schema valid |
| Reference top-1 / top-5 acceptable | answerable records | Retrieval quality |
| Unsupported flagged unsupported | unsupported records | Abstention on out-of-scope labels |
| Absent reported absent | records whose reference is not in GNIS | Abstention when there is nothing to find |
| Place names read as "no locality" | all records | A known LLM error |
| Mean fields to correct | all records | Critical fields, plus the reference, a curator would fix |
| Computed proposals, precision, useful coverage | runs with the extent store | Section 7 proposal targets: regions computed, how many are correct, and correct regions over answerable records |

**Statistics:**
- **Paired bootstrap** over records: 10,000 resamples, seed 20261101, 95% percentile interval.
- **Exact two-sided sign test** on discordant records.
- **Sensitivity:** every comparison is repeated without the rows that carry an unsure (`?`)
  annotation. It is reported, never decisive.

## Protocol

1. **Dev data** (audit, dev-1) is for developing prompts, rules and selection rules. A change
   made from a sample's misses is in-sample on that sample and is reported as such.
2. **Validation** is scored with frozen systems. It has now been read, so a change designed
   from its misses needs another check.
3. **The locked test** is scored only under a **declaration**: a JSON file committed and pushed
   **before** the run. It pins the code commit, release manifest, data hashes, primary metric,
   target and decision rule.
   - Each system runs once.
   - Per-record outputs stay in the locked folder and are never read.
   - Only totals are published, whatever they show.
   - Any later change is a new release with a new declaration.

**Decision rule** (all three declarations):
- **yes:** the difference is at least +10 points **and** the interval's lower bound is above 0
- **no:** the interval's upper bound is below +10
- **not shown:** anything else

## Results

Everything below was measured; nothing is extrapolated. Results on dev data are in-sample
wherever the system was changed from that sample's misses, and they say so.

- **LLM v2:** Qwen3.5-4B Q4_K_M, prompt `extraction-v2`, greedy decoding.
- **hybrid-1:** runs the rules first, and the LLM only where the rules reach no gazetteer
  candidate. It is the release system.

### Locked test: the milestone answer

Correct proposal candidates of 56 answerable records, each release under its own declaration
pushed before the run:

| Release | Rules | LLM v2 alone | hybrid-1 | Primary comparison | Answer |
|---|---|---|---|---|---|
| [1](../eval/reports/test-release-1.md) (rules-1, validation 2) | 19 | 15 | – | LLM − rules: −7 points (CI −23 to +7) | **no** |
| [2](../eval/reports/test-release-2.md) (same components) | 19 | 15 | 25 | hybrid − rules: +10.7 points (CI +3.6 to +19.6, p = 0.031) | **yes** |
| [3](../eval/reports/test-release-3.md) (rules-6, validation 3) | 22 | 18 | **28** | hybrid − rules: +10.7 points (CI +3.6 to +19.6, p = 0.031) | **yes** |

- **The margin is the smallest that clears +10 points, twice:** 6 records gained and none lost.
  One record fewer would have been "not shown".
- **The interval runs from about +4 to +20.** The hybrid is better than the rules, but a true
  gain below 10 points is not ruled out.
- **The test has been scored three times.** Changes between releases were designed on dev and
  validation data. No per-record test output has been read.

**Every measure on the test, release 3** (of 120 records unless stated):

| Measure | Rules (rules-6) | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| Correct proposal candidates (of 56) | 22 | 18 | **28** |
| Critical interpretation exact | 62 | 50 | 63 |
| Relation read correctly | 75 | 67 | 76 |
| Distance right | 89 | 95 | 90 |
| Unit right | 93 | 98 | 94 |
| Direction right | 84 | 83 | 83 |
| Qualifiers right | 106 | 87 | 106 |
| Extraction passed validation (quotes resolve to spans) | 120 | 107 | 120 |
| Acceptable reference ranked first (of 56) | 24 | 27 | 32 |
| Candidate recall@5 (of 56) | 25 | 28 | 34 |
| Unsupported flagged unsupported (of 16) | 7 | 9 | 7 |
| References absent from GNIS reported absent (of 48) | 17 | 26 | 14 |
| Place names read as "no locality" | 0 | 2 | 0 |
| Mean fields a curator must correct | 1.54 | 1.66 | 1.46 |

- **Where the hybrid gains, it gains through retrieval:** the LLM's quote reaches GNIS where the
  rules' name does not (top-1 32 against 24).
- **What it costs:** fewer absent references reported as absent (14 against 17).
- **The model is called on 45 of 120 records (38%).** Model time is 479 s against 1,285 s for the
  LLM alone on all 120. Latency per call: p50 9.9 s, p95 16.4 s (Apple M1, 8 GB, warm server,
  completion cache off).
- MRR is not computed: the score reports top-1 and top-5 only.

### Ablations and model comparisons (read samples only)

- **Few-shot examples** ([findings](../eval/reports/ablation-fewshot-findings.md)): without its 11
  invented examples, prompt v2 falls from 46 to 11 correct proposal candidates of 92
  owner-annotated records (−38 points, CI −49 to −27). Invalid extractions rise from 7 to 57 of
  160. The examples carry most of the LLM's result.
- **Qwen3.5-2B against 4B** ([findings](../eval/reports/qwen3.5-2b-findings.md)): alone, 27
  against 46 of 92. As hybrid-1's fallback, 49 against 51, at a quarter of the model time.
- **Not run:** the second LLM call (candidate comparison: not built), admin context removed from
  the prompt, and other quantizations.

### Against GEOLocate (read samples only)

Plan pinned before any query; 310 read-sample labels, no locked-test label
([findings](../eval/reports/geolocate-findings.md)). Points within 5 km / 1 km of the position the
annotation supports:

| Annotations | GEOLocate | rules-6 | LLM v2 | hybrid-1 |
|---|---|---|---|---|
| Owner (85 records) | **58** / 44 | 54 / 51 | 59 / 53 | **61** / 58 |
| Claude (91 records) | **63** / 44 | 54 / 47 | 51 / 47 | **62** / 54 |

- **At 5 km the two are level,** and both are ahead of the rules alone.
- **GEOLocate gives a point almost always** (82 of 85). Ours give fewer (hybrid 71) and abstain
  where GEOLocate guesses.
- **The 1 km gap is mostly a bias of the method:** positions come from GNIS, where our correct
  picks land exactly.
- **This compares point placement only.** GEOLocate ran with default settings and no curator,
  and our systems are partly tuned on these samples.

### Regions and uncertainty (dev and validation only)

With 67 of 115 reference features measured in the [extent store](../data/reviewed/), hybrid-1
computes 35 full regions on the 160 read records, 32 with the right interpretation and reference
(91%; target ≥ 95%). That is a useful coverage of 32 of 92 answerable (35%; target ≥ 70%). On
dev-2's labels: 11 regions, 10 correct (91%), coverage 10 of 36 (28%)
([findings](../eval/reports/extents-findings.md), [batch 4](../eval/reports/extents-batch-4-findings.md)).
No test feature has a measured extent, so no system computes test regions.

<details>
<summary><b>Development history: dev and validation scores by rules version</b></summary>

Correct proposal candidates, against the rules baseline `rules-1`:

| Set (answerable) | Rules | LLM v2 alone | hybrid-1 | Status |
|---|---|---|---|---|
| **Locked test** (56) | 19 | 15 | **25** | Release 1: LLM −7 points (CI −23 to +7): **no**. Release 2: hybrid +10.7 points (CI +3.6 to +19.6): **yes**, by one record |
| Validation (32) | 13 | 15 | 16 | Read; weak check |
| Audit (31) | 14 | 12 | 14 | Dev data |
| dev-1 (29) | 16 | 18 | 18 | Dev data; prompt v2 written on it |

These rows are the release configuration (rules-1, validation 2). Since then, rules-2 and
validation 3 give audit 17 / 13 / 17, dev-1 16 / 18 / 18 and validation 13 / 15 / 16. The
audit gains are in-sample ([rules-2 findings](../eval/reports/rules-2-findings.md)). rules-3 then
gives audit 17 / 13 / 17, dev-1 17 / 18 / 19 and validation 16 / 15 / 19, also in-sample
([rules-3 findings](../eval/reports/rules-3-findings.md)). rules-4 keeps the offset when the place
is a broad feature and changes none of these numbers
([rules-4 findings](../eval/reports/rules-4-findings.md)). On fresh data, dev-2 (36 answerable,
scored once by a pinned plan) gives rules-4 19, LLM 17 and hybrid-1 21
([dev-2 findings](../eval/reports/dev-2-findings.md)). Claude annotated dev-2 at the owner's
request and also wrote the rules, so this is weaker evidence than the owner's blind annotations.
Only 3 of its labels are the kind rules-3
and rules-4 decide, so it does not test them. rules-5 asks about distance ranges instead of
reading their second number; on the read samples it changes only A23 (in-sample, rules 50 → 51,
hybrid-1 55 → 56 of 92; [rules-5 findings](../eval/reports/rules-5-findings.md)). rules-6 adds
"2 or 3 mi" ranges and changes no read label ([rules-6 findings](../eval/reports/rules-6-findings.md)). dev-3 is drawn for that (35 of 50 "place, offset"
labels, text shape version 2). Claude annotated it (same limit) and it was scored once by a
pinned plan: rules-6 11, LLM 14, hybrid-1 14 of 32 answerable. Replaying rules-2 to rules-6 on
its 24 answerable place-offset records gives 6, 7, 6, 6, 6 correct: no evidence that the
place-or-offset rules help ([dev-3 findings](../eval/reports/dev-3-findings.md)). dev-4 (also
Claude-annotated, plan pushed before any run) gives rules-6 9, LLM 14, hybrid-1 10 of 29, and
6, 6, 5, 5, 5 of 22 place-offset records across rules-2 to rules-6
([dev-4 findings](../eval/reports/dev-4-findings.md)). From dev-3 on, samples also exclude
labels whose wording repeats a read or reserved group under another county (exclusion version
2, [dev samples](../eval/dev/README.md)).

</details>

**Full reports:**
- [release 1](../eval/reports/test-release-1.md) · [release 2](../eval/reports/test-release-2.md)
  · [release 3](../eval/reports/test-release-3.md)
  · [validation](../eval/reports/validation-findings.md)
- [audit](../eval/reports/audit-50-score.md) · [dev-1](../eval/reports/dev-1-score.md)
- [hybrid selection](../eval/reports/hybrid-1-findings.md) ·
  [prompt v2](../eval/reports/prompt-v2-findings.md) ·
  [core retrieval](../eval/reports/retrieval-core-findings.md)

Failed and superseded experiments stay in [`eval/reports/`](../eval/reports/). Runs answered from
the completion cache (`extract/cache.py`) record 0 model seconds and are never used for latency.

## Not measured yet

- **Proposal precision and useful coverage on the locked test.** The test references have no
  measured extents. On dev and validation they are measured with a partly filled store.
- **Containment with region size, and reviewer time.**
- **GEOLocate on held-out data.** It has been compared on read samples only (above).
- **The second LLM call** (candidate comparison: not built), other quantizations, and a scored
  adversarial set on real labels. The adversarial behaviour tests below use synthetic data.
- **Review policy thresholds** (`configs/review_policy.yaml`, planned): no selection-confidence
  thresholds are set yet. A record reaches `ready_for_review` whenever its region is computed,
  whatever the selection evidence, so the curator still judges the choice of feature.
- **Annotation self-consistency** (a repeat pass on a subset by the same annotator).

## Adversarial tests

[`tests/adversarial/`](../tests/adversarial/test_adversarial.py) runs every adversarial case in
the test plan end to end on synthetic data, and checks that the system abstains, flags or
refuses: swapped directions, missing or ambiguous units, repeated place names, conflicting
counties and states, injected instructions (including a label that tries to close the prompt's
data fence and a model that obeys and returns coordinates), unknown landmarks, withheld
locations, malformed model output, a worker crash after the model call, cancelled batches and
oversized input. They are behaviour tests, not a scored adversarial evaluation set.

Writing them found one gap: the guard on the model's free-text questions caught coordinates
only with three or more decimals or a degree sign, so a pair like "40.0, -105.0" passed. It now
also matches latitude/longitude pairs. None of the 469 cached model completions (105 questions)
is affected.

