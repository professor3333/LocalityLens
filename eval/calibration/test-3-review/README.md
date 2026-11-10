# Owner review of disputed test-3 rows

**What this is:** a diagnosis of a used set, not an evaluation. test-3 was scored once
([result](../../reports/test-3.md)), and the [diagnosis](../../reports/test-3-diagnosis.md)
found that 41 of hybrid-1's 46 wrong ready regions are clause choices. This review asks
whether those rows are system errors, annotator (Codex) errors, or a convention question.
- **No result changes.** test-3's declared result stands.
- **Nothing designed from this review** may be claimed as tested on test-3.

This plan was committed and pushed **before the owner annotated anything**.

## The sheet

`worksheet.csv` holds 23 test-3 rows, renumbered `R01`–`R23` in seeded order
(`test-3-review/1`), blank. It was built by `localitylens audit calibration-set --source
eval/benchmark/test-3/test-3.json --name test-3-review --seed test-3-review/1 --prefix R --out
eval/calibration/test-3-review --ids <list>`.

The rows are hybrid-1 ready regions (no selection check), drawn by
`eval/benchmark/test-3/diagnosis/review-strata.json`:

| Stratum | Drawn | Of |
|---|---|---|
| Clause choice, Codex's place absent from GNIS | 10 | 21 |
| Clause choice, Codex's place in GNIS | 10 | 20 |
| Other ready regions with an "unsure" marker | 3 | 3 |

## How the owner annotates

- **Follow [`../../annotation_guide.md`](../../annotation_guide.md)** as it stands at this
  commit, including the new rule for a most specific place that isn't in GNIS (BP §3.2.2: annotate
  the next less specific clause, and note `absent-specific: …`).
- **Do not open:** `pairs.json`; anything under `eval/benchmark/test-3/`; `eval/reports/test-3*`.
  These hold Codex's annotations and the system outputs for the same records.
- **Commit:** the worksheet is committed unchanged and must pass the checker. Fixes go in a
  further, recorded commit.

## What is computed, once, counts only

Each R row is mapped back to its P row with `pairs.json`.

1. **Clause choice, place in GNIS (10):**
   - how often the owner accepts the same GNIS IDs as Codex;
   - how often the system's ready region is correct under the owner's annotation.
2. **Clause choice, place absent (10):**
   - how often the owner also finds the specific place absent (`absent-specific` in notes, or
     `absent`);
   - how often the system's ready region is correct under the owner's annotation, with the
     fallback rule.
3. **Unsure rows (3):** agreement on every field, reported only.
4. **All 23:** agreement on category and acceptable GNIS IDs (`localitylens audit agreement`),
   and ready regions correct under the owner's annotations against under Codex's.
5. **An estimate, labelled as one,** of hybrid-1 ready-region precision on test-3 under the
   owner's annotations:
   - each stratum's correct share, from its 10 seeded rows only, is scaled by its size (21, 20);
   - of the 3 unsure rows, one is an undrawn in-GNIS clause-choice row: it is reported in item
     3 and left out of the scaling;
   - the other 2 are among the 12 remaining ready regions (7 correct, 5 annotated unsupported),
     and the owner's judgement replaces Codex's for them; the other 10 keep Codex's;
   - with a note that 10-row strata give wide intervals.

Published as `eval/reports/test-3-review.{md,json}`.

## What it can and can't show

- **It can show** whether the low precision comes mostly from the system choosing the wrong
  clause, from Codex's annotations, or from the absent-place convention.
- **It can't show** what a future rule would achieve. That needs fresh, unread labels and a new
  declaration.
- **The owner is independent of Codex and did not write the systems.** The owner is one
  annotator, and these rows were chosen because the system and Codex disagree on them.
