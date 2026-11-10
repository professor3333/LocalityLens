# Model card: LocalityLens extraction

The language model in LocalityLens **reads** a specimen's locality description. It never
places it: coordinates and radii come only from GNIS records and deterministic geometry code.
This card describes the model as used in release `0.1.2` (the same model, prompt and settings as `0.1.0`;
0.1.2 adds the `selection-2` review check, which does not change the model's input or output).

## Intended use

- **What it does:** extracts place mentions, distance-and-direction relations, qualifiers and
  missing information from English Colorado specimen locality descriptions.
- **What that feeds:** *suggested* georeferences with source evidence, which a curator confirms
  or corrects before export.
- **How it runs:** as a fallback to a rules baseline (`hybrid-1`), the configuration that met
  the first milestone's target on the locked test.

## Not for

- accepting georeferences into a collection database without human review
- producing coordinates directly (the model never does; output with coordinate fields is
  rejected)
- reconstructing deliberately withheld or generalized sensitive-species locations
- treating `needs_information` or `unsupported` as "cannot be located"
- inferring places, distances or directions the label does not state
- other regions, non-English labels, OCR output, or route-relative descriptions
- claiming general georeferencing quality: GEOLocate was compared on read samples only, for
  point placement only ([findings](../eval/reports/geolocate-findings.md))

## Provenance

| Item | Value |
|---|---|
| Model | `Qwen/Qwen3.5-4B` at revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, Apache-2.0 |
| Weights | `unsloth/Qwen3.5-4B-GGUF` at `e87f176479d0855a907a41277aca2f8ee7a09523`, file `Qwen3.5-4B-Q4_K_M.gguf`, SHA-256 `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`, 2,740,937,888 bytes |
| Server | llama.cpp 0.8.0, build `b11960-8642541b2`, bound to 127.0.0.1, `-c 4096 -np 1 --no-context-shift` |
| Generation | temperature 0, top-k 1, seed 20261101, at most 512 tokens, thinking off |
| Prompt | `extraction-v2`, SHA-256 `8074f1f8…`: label text fenced as data, 11 few-shot examples with invented place names |
| Output contract | schema `extraction-1`, grammar 2 (JSON schema enforced by llama-server), quotes only, never offsets |
| Downstream | validation 3, core key 1, county context 1, rules `rules-6`, uncertainty policy `gbif-bp-2020/1`. Test releases 1 and 2 used validation 2 and `rules-1` |
| Data | gazetteer `gnis-co-2026-09-29`, specimens `gbif-cu-2026-11-01`; see the [dataset card](dataset_card.md) |

All of the above is pinned in [`release/manifest.json`](../release/manifest.json). Tests
compare it with the code's own constants, and changing any item is a version bump.
**Qwen3.5-2B** (Q4_K_M, pinned in [`release/manifest-2b.json`](../release/manifest-2b.json))
was compared on dev and validation data. On its own it gives 27 correct candidates of 92,
against 46 for 4B, and 51 of its 160 extractions quote text that is not in the label. As
hybrid-1's fallback it gives 49 against 51, at a quarter of the model time (p50 4.9 s against
20.4 s in the same session) ([findings](../eval/reports/qwen3.5-2b-findings.md)). 4B stays the
release model.

**Resources measured** on an Apple M1 with 8 GB: llama-server's own footprint is 629 MB on top
of the 2.74 GB memory-mapped model file. The prompt uses about 2,350 of the 4,096-token
budget.

## Training and evaluation data

- **No fine-tuning.** The model is used as published.
- **Few-shot examples** use invented names (Brindle Peak, Osgood, Tamsin Lake and others), so
  no evaluation label appears in the prompt.
- **Dev data:** the audit (50) and dev-1 (50) were used for prompt and rule iteration; dev-2,
  dev-3 and dev-4 (50 each, annotated by Claude) checked rules changes.
- **Held out:** validation (60) was scored with frozen systems and has since been read. The
  locked test (120) is scored only under declared releases (three so far).
- **The few-shot examples matter most:** without them, the same model and settings give 11
  correct proposal candidates of 92 owner-annotated dev and validation records instead of 46,
  and invalid extractions rise from 7 to 57 of 160
  ([ablation](../eval/reports/ablation-fewshot-findings.md)).
- Splits are grouped by wording and by collecting event. See the
  [dataset card](dataset_card.md) and [evaluation](evaluation.md).

## Metrics

On the locked test, correct proposal candidates of 56 answerable records:

| System | Release 1–2 (rules-1) | Release 3 (rules-6) | vs rules, release 3 |
|---|---|---|---|
| Rules | 19 | 22 | – |
| LLM v2 alone | 15 | 18 | −7.1 points (CI −21 to +7) |
| **hybrid-1** (rules first, LLM fallback) | **25** | **28** | **+10.7 points (CI +3.6 to +19.6)** |

**Other test figures for the LLM alone** (of 120 unless stated):

| Measure | Release 1 | Release 3 |
|---|---|---|
| Critical interpretation exact | 47 | 50 |
| Relation read correctly | 66 | 67 |
| Qualifiers right | 85 | 87 |
| Extraction passed validation | 105 | 107 |
| Unsupported records flagged (of 16) | 9 | 9 |
| References absent from GNIS reported absent (of 48) | 26 | 26 |
| Latency, warm | p50 11.7 s, p95 20.9 s | p50 9.9 s, p95 16.4 s |

The model and prompt are the same in every release; the gains come from validation version 3
and supplied-county handling. hybrid-1 calls the model on 39% (release 2) and 38% (release 3)
of test records. All test measures are in [evaluation](evaluation.md#locked-test-the-milestone-answer).

On **test-2**, a fresh sample annotated by Claude rather than the owner (so not independent of
the rules Claude wrote): rules-6 34, LLM alone 31, hybrid-1 43 of 80 answerable, +11.3 points
(CI +5.0 to +18.8) ([result](../eval/reports/test-2.md)).

With 67 measured extents and rules-6, on the read dev and validation data (160 records), hybrid-1
computes 35 full regions, 32 of them correct (91%; target ≥ 95%), a useful coverage of 35%
(target ≥ 70%). On dev-2's unseen labels it computes 11, 10 correct (91%), a useful coverage of
28% ([batch 4 findings](../eval/reports/extents-batch-4-findings.md)). That precision is inflated:
extents existed only for features the annotations accepted. With polygon-derived extents for every
feature, regions are 63% correct on owner-annotated read data and 39–47% on Claude-annotated data
([findings](../eval/reports/derived-extents-findings.md)). The usual error is the reference
choice, not the reading.
Containment, and these measures on the locked test, are not measured yet. See
[evaluation](evaluation.md) for definitions and every report.

## Known failure modes

**Observed** in the reports:
- **Direction-only labels.** In release 1 the model read only 2 of 15 test labels as
  `direction_only`, and got 0 of the 7 answerable ones right (1 of 7 in release 3).
- **Qualifiers dropped or mis-scoped:** 87 of 120 right on the test (release 3), against the
  rules' 106.
  Scope also goes wrong: in "Along X, near Town", "near" belongs to the town.
- **Schema-valid but semantically wrong output.** 13 of 120 test extractions (release 3; 15
  in release 1) passed the JSON schema but failed deterministic validation. Their reasons were not examined, so the
  test stays unread. On dev data the causes included quotes not found in the text.
- **Bare place names read as "no locality":** 7 of 50 under prompt v1, and 2 of 120 under v2
  on the test.
- **A locating offset chosen over the named collecting place**, despite a prompt rule against
  it. This was the largest shared miss on validation.
- **Generic words absorbed into names** ("Longs Peak summit" read as one name), which can
  then miss the gazetteer.
- **A wrong candidate where the rules correctly found none.** The hybrid inherits this:
  absent-reported drops from 17 to 14 of 48 on the test.

**Covered by behaviour tests on synthetic data, not measured on real labels**
([adversarial tests](../tests/adversarial/test_adversarial.py)): swapped directions, missing or
ambiguous units ("m" as miles or metres), repeated place names, conflicting counties, injected
instructions (label text is fenced as data, the model has no tools, and coordinates in its output
are rejected), unknown landmarks and malformed output. The system abstains, flags or refuses in
each case; how often the model itself errs on such labels is not measured.

**Not tested:** elevations read as distances, multi-offset descriptions collapsed into one, and
historical names or changed county boundaries beyond what the read samples contain.

## Release process

- **Thresholds and settings** are chosen on dev and validation data, never on the test.
  No numeric selection-confidence thresholds are set. The one selection rule (`selection-2`,
  default from 0.1.2) was adopted after declared checks on unread labels.
- **A release candidate** is a new release manifest. Before the test is scored, a declaration
  pins the code commit, manifest hash, data hashes, metric, target and decision rule. It is
  committed and pushed first, and its result is published whatever it shows. Releases 1 to 3
  are in [`eval/benchmark/`](../eval/benchmark/).
- **Rollback** means restoring the complete previous bundle (model file, prompt, schema,
  generation settings, gazetteer snapshot, policies) from git and the pinned downloads, and
  the review-store backup taken before the upgrade. The procedure is in
  [deployment](deployment.md); it was rehearsed on a fresh clone on 2026-11-07.
