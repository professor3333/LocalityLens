# Project summary at v0.1.3

What was built, what was shown, what failed, and where to pick up. Details are in
[results](results.md), [evaluation](evaluation.md) and the
[Definition-of-Done audit](definition-of-done.md).

## What was built

A local georeferencing workbench for historical specimen labels (University of Colorado
Herbarium, Colorado, English).
- **Reading:** a small local model (Qwen3.5-4B through llama.cpp), with a rules baseline run first.
- **Geography:** code alone finds places in a pinned USGS GNIS snapshot and computes regions,
  with every uncertainty component cited from the GBIF Best Practices.
- **Review:** a curator reviews each proposal on a local map screen before it is exported as
  Darwin Core CSV or GeoJSON.
- **Operations:**
  - **Jobs:** a persistent job queue with recovery, per-attempt traces, a JSON API and
    Docker Compose;
  - **Data and demo:** backups, pinned and mirrored data, and a static replay demo;
  - **Releases:** a workflow that re-evaluates every tagged release and checks the deployment
    on Linux.

## What was shown

| Claim | Evidence |
|---|---|
| Rules first, with the LLM as a fallback (hybrid-1), beat the rules by ≥ 10 points of correct proposal candidates | Locked test, owner-annotated, declared before each run: +10.7 points in releases 2 and 3 (28 vs 22 of 56). The smallest margin that clears the target |
| The LLM alone does not beat the rules | Locked-test releases 1 and 3 |
| selection-2 holds back mostly wrong regions | Three declared checks on unread labels (Codex- or Claude-annotated): 53 wrong vs 13 correct held back; passed 2 of 3 |
| Results are reproducible | A fresh clone reruns 160 records identically, record for record; data rebuilds byte for byte |
| It deploys and recovers | Compose with llama-server on Linux takes a sample from upload to export and keeps decisions across a restart; backup, restore and rollback rehearsed |

## What failed or stays short

- **Precision of ready regions:** 55–66% on read data and 32% on unread "place, offset" labels.
  The target is 95%.
- **Useful coverage:** about 30%, against a target of 70%.
- **The main error:** the label names a specific place and the system uses the offset town. The
  rules changes (rules-3 to rules-6), switching to the place GNIS finds, and a model call to
  choose the clause all failed on dev data. The place is often a position on a feature, a
  partial name, or not in GNIS at all.
- **Candidate recall@5:** 61% on the locked test, against a target of 95%.
- **Quantization parity:** the shipped Q4_K_M loses 2.3 to 3.2 points to Q8_0, against a
  1-point gate. Correct proposals are within one record. The quant is kept and the failure
  recorded, so no release image is pushed.
- **Not measured:** reviewer time, which needs human reviewers, and containment with region
  size on the locked test.

## How the evidence was kept honest

- **Held-out sets were never read** during development. Each run was declared and pushed before
  annotation or scoring, and only totals were published.
- **Annotators are named.** The owner annotated the locked test, Codex the calibrated test-3 and
  test-5, and Claude the weaker, non-independent sets.
- **Failed experiments are kept** in `eval/reports/`.

## Where to pick up

1. **A reviewer-time pilot with two or three people:** the project's main unmeasured claim.
2. **Place extraction and matching:** positions on features ("N slope of X"), partial and
   variant names. Develop it on dev data, then check it on a fresh declared sample.
3. **Same-name ambiguity** (`candidates_unresolved`): small, but build it if curators run into
   it.
