# Model card: LocalityLens extraction

The language model in LocalityLens **reads** a specimen's locality description. It never
places it: coordinates and radii come only from GNIS records and deterministic geometry code.
This card describes the model as used in release `0.1.0-dev`.

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
- claiming general georeferencing quality: no GEOLocate comparison has been run yet

## Provenance

| Item | Value |
|---|---|
| Model | `Qwen/Qwen3.5-4B` at revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, Apache-2.0 |
| Weights | `unsloth/Qwen3.5-4B-GGUF` at `e87f176479d0855a907a41277aca2f8ee7a09523`, file `Qwen3.5-4B-Q4_K_M.gguf`, SHA-256 `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`, 2,740,937,888 bytes |
| Server | llama.cpp 0.8.0, build `b11960-8642541b2`, bound to 127.0.0.1, `-c 4096 -np 1 --no-context-shift` |
| Generation | temperature 0, top-k 1, seed 20261101, at most 512 tokens, thinking off |
| Prompt | `extraction-v2`, SHA-256 `8074f1f8…`: label text fenced as data, 11 few-shot examples with invented place names |
| Output contract | schema `extraction-1`, grammar 2 (JSON schema enforced by llama-server), quotes only, never offsets |
| Downstream | validation 3, core key 1, county context 1, rules `rules-2`, uncertainty policy `gbif-bp-2020/1`. Test releases 1 and 2 used validation 2 and `rules-1` |
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
- **Dev data:** the audit (50) and dev-1 (50) were used for prompt and rule iteration.
- **Held out:** validation (60) was scored with frozen systems. The locked test (120) is
  scored only under declared releases.
- Splits are grouped by wording and by collecting event. See the
  [dataset card](dataset_card.md) and [evaluation](evaluation.md).

## Metrics

On the locked test, correct proposal candidates of 56 answerable records:

| System | Correct | vs rules |
|---|---|---|
| Rules `rules-1` | 19 | – |
| LLM v2 alone | 15 | −7 points (CI −23 to +7) |
| **hybrid-1** (rules first, LLM fallback) | **25** | **+10.7 points (CI +3.6 to +19.6)** |

**Other test figures for the LLM alone** (of 120 unless stated):

| Measure | Value |
|---|---|
| Critical interpretation exact | 47 |
| Relation read correctly | 66 |
| Qualifiers right | 85 |
| Extraction passed validation | 105 |
| Unsupported records flagged (of 16) | 9 |
| References absent from GNIS reported absent (of 48) | 26 |
| Latency, warm | p50 11.7 s, p95 20.9 s |

For hybrid-1, the model is called on 39% of records.

With 56 measured extents, on dev and validation data, hybrid-1 computes 35 full regions of 160
records, 32 of them correct (91%, target ≥ 95%), a useful coverage of 35% (target ≥ 70%).
Containment, and these measures on the locked test, are not measured yet. See
[evaluation](evaluation.md) for definitions and every report.

## Known failure modes

**Observed** in the reports:
- **Direction-only labels.** The model read only 2 of 15 test labels as `direction_only`,
  and got 0 of the 7 answerable ones right.
- **Qualifiers dropped or mis-scoped:** 71% right on the test, against the rules' 86%.
  Scope also goes wrong: in "Along X, near Town", "near" belongs to the town.
- **Schema-valid but semantically wrong output.** 15 of 120 test extractions passed the
  JSON schema but failed deterministic validation. Their reasons were not examined, so the
  test stays unread. On dev data the causes included quotes not found in the text.
- **Bare place names read as "no locality":** 7 of 50 under prompt v1, and 2 of 120 under v2
  on the test.
- **A locating offset chosen over the named collecting place**, despite a prompt rule against
  it. This was the largest shared miss on validation.
- **Generic words absorbed into names** ("Longs Peak summit" read as one name), which can
  then miss the gazetteer.
- **A wrong candidate where the rules correctly found none.** The hybrid inherits this:
  absent-reported drops from 17 to 14 of 48 on the test.

**Listed in the project plan but not yet tested systematically** (adversarial set to come):
- direction reversal and compound bearings
- "m" read as miles against metres
- elevations read as distances
- multi-offset descriptions collapsed into one
- injected instructions in label text (label text is fenced as data, and the model has no
  tools)
- historical names and changed county boundaries

## Release process

- **Thresholds and settings** are chosen on dev and validation data, never on the test.
  No selection-confidence thresholds are set yet.
- **A release candidate** is a new release manifest. Before the test is scored, a declaration
  pins the code commit, manifest hash, data hashes, metric, target and decision rule. It is
  committed and pushed first, and its result is published whatever it shows. Releases 1 and 2
  are in [`eval/benchmark/`](../eval/benchmark/).
- **Rollback** means restoring the complete previous bundle (model file, prompt, schema,
  generation settings, gazetteer snapshot, policies). Deployment and a tested rollback are not
  built yet.
