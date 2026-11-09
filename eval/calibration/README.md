# Calibrating a second annotator (Codex) against the owner

The owner's time is the bottleneck for fresh annotations. Claude's annotations are not used for
held-out claims, because Claude wrote the systems being tested. Codex, an AI coding assistant
from another provider, did not write this code. Its annotations could serve as **secondary**
evidence, but only once it is shown to agree with the owner.

This plan was committed and pushed **before Codex annotated anything**. The thresholds below
cannot be changed after the fact.

## Procedure

1. **The calibration set** is [`validation/`](validation/): the 60 validation records the owner
   annotated, renumbered `C01`–`C60` in seeded order (`calibration-1/1`), with a blank worksheet.
   - Built by `localitylens audit calibration-set --source
     eval/benchmark/validation/validation.json --name calibration-validation --seed
     calibration-1/1 --prefix C --out eval/calibration/validation`.
   - `pairs.json` maps each `C` row back to its `V` row.
2. **Codex fills `validation/worksheet.csv`.** It follows
   [`../annotation_guide.md`](../annotation_guide.md) and looks GNIS IDs up in the pinned
   snapshot (`localitylens gazetteer search`).
   - **Codex must not open:** `pairs.json`; anything under `eval/benchmark/`, `eval/reports/`,
     `eval/audit/`, `eval/dev/` or `demo/`; and the repository history. These hold the owner's
     annotations of the same records and system outputs for them.
   - **This cannot be enforced, only stated.** The result will say so.
3. **The owner commits the worksheet unchanged** in one commit naming Codex as annotator. It
   must pass the worksheet checker; fixes go in a further commit, recorded.
4. **Agreement is computed once:**
   `localitylens audit agreement --sample-a
   eval/calibration/validation/calibration-validation.json --worksheet-a
   eval/calibration/validation/worksheet.csv --sample-b
   eval/benchmark/validation/validation.json --worksheet-b
   eval/benchmark/validation/worksheet.csv --pairs eval/calibration/validation/pairs.json`.
   Counts are published in `eval/reports/codex-calibration.{md,json}`.

## The decision, stated in advance

Codex is accepted as a second annotator **only if both** hold on the 60 records:

| Field | Needed | Why this field |
|---|---|---|
| Record category (answerable / reference absent / unsupported) | ≥ 51 of 60 (85%) | It decides which records count as answerable |
| Acceptable GNIS IDs (the same set, or both "absent") | ≥ 48 of 60 (80%) | It decides whether a pick is correct |

For comparison, Claude and the owner agreed on 16 of 20 (80%) for both fields on test-2's
repeats. Every other field, and the count of rows where every field agrees, is reported but does
not decide.

- **If Codex passes:**
  1. A fresh sample of unread labels is drawn, targeted at the remaining failure mode: an offset
     from a town plus another named place.
  2. Its declaration, which pins the rule to be tested before annotation, is pushed.
  3. Codex then annotates it.
  4. Results are labelled "Codex-annotated; agreement with the owner X of 60 (category), Y of
     60 (GNIS IDs)".
- **If Codex fails:** no Codex annotation is used as evidence, and the result is published as it
  is.

## Provenance

Codex is named as the annotator of the worksheets it fills, in docs, reports and the commit
messages that add them. Commits stay under the owner's identity.
