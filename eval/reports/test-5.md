# test-5: selection-2 with an annotator other than Claude

A declared check ([declaration](../benchmark/declaration-test-5.json), pushed before
annotation; [amendment 1](../benchmark/declaration-test-5-amendment-1.json), pushed before the
run, names the annotator).

- **Why:** selection-2's two earlier checks disagreed. It failed on [test-3](test-3.md) (Codex,
  before the absent-place rule) and passed on [test-4](test-4.md) (Claude, after it). test-5
  keeps the new guide and goes back to an annotator who did not write the systems.
- **Sample:** 120 unread "place, offset" labels, drawn after excluding every read or reserved
  group, all earlier held-out sets, repeated wording and linked collecting events.
- **Annotations: by Codex**, run on the owner's side.
  - **Calibration:** agreement with the owner is 54/60 on category and 55/60 on GNIS IDs
    ([calibration](codex-calibration.md)). That calibration was done before the absent-place
    rule.
  - **The rule:** 41 rows use the guide's absent-place rule (GBIF Best Practices §3.2.2).
  - **Categories:** 108 answerable, 5 reference absent, 7 unsupported.
- **Systems:** hybrid-1 (rules-6 first, then llm-x2g2-qwen3.5-4b-q4km), with reviewed and derived
  extents, without and with `--selection-2`.
- **Run:** once at a61c767, 2026-11-10 09:25–10:14 UTC, LLM cache off, native llama-server. No
  technical failures.
- **Published here:** totals only. Per-record outputs stay in `eval/benchmark/test-5/reports/`.

## Primary question: selection-2 works

| hybrid-1, 108 answerable | Ready regions | Correct | Useful coverage |
|---|---|---|---|
| Without the check | 37 | 12 (32%) | 12 (11.1%) |
| With `selection-2` | 19 | 8 (42%) | 8 (7.4%) |

- **Held back:** 18 regions, 14 wrong and 4 correct. 14 is at least 2 × 4, so the ratio is met.
- **Precision:** up 9.7 points, which clears the 5-point bar.
- **So by the test-3 rule (unchanged), it works.** That is what was expected in advance
  ("uncertain, leaning works").
- **The cost:** useful coverage falls by 3.7 points, from 12 regions to 8.

## Secondary results

**Where wrong regions come from: supported (test-4's rule, unchanged).**

| hybrid-1 ready regions, no check (37) | Count | Held back by selection-2 |
|---|---|---|
| Correct | 12 | 4 |
| **Clause choice: another place chosen, annotated place in GNIS** | **23** | **14** |
| Same name, other GNIS feature | 1 | 0 |
| Reading error (qualifiers), right reference | 1 | 0 |

23 of the 25 wrong regions (92%) are this stage, and it is the largest.

**Precision is lower than expected.**
- It is 32% without the check, below the 35–65% range stated in advance.
- Claude-annotated test-4 had 55% and test-2 58%.
- Almost all the wrong regions are labels where the annotated place is in GNIS and the system
  used the offset's town. Whether the drop comes from the annotator or from the sample can't be
  told apart here.

**Rules alone and LLM alone:**

| | Ready, correct (no check) | Ready, correct (with check) |
|---|---|---|
| Rules (rules-6) | 32, 11 | 15, 7 |
| LLM alone | 30, 10 | 16, 6 |

**Correct proposal candidates, of 108 answerable** (the same with and without the check):

| Rules | LLM alone | hybrid-1 | hybrid − rules |
|---|---|---|---|
| 25 | 21 | 28 | +2.8 points (95% CI 0 to +6.5, sign p = 0.25): 3 gained, 0 lost |

- **Excluding unsure records** (97 answerable): rules 24, LLM 21, hybrid 27.
- **LLM alone against rules:** −3.7 points (CI −12 to +4.6).
- **hybrid-1's LLM use:** it called the LLM on 38 records and took 11 answers from it.

**The LLM:**
- **Valid extractions:** 107 of 120 without the check and 106 with it.
- **Repeatability:** the two passes had identical prompts, with greedy decoding and the cache
  off, but 1 record's output differed. hybrid-1 took that record from the rules in both passes,
  so the hybrid totals and the decision don't depend on it.
- **Model time per record:** p50 11.4 s, p95 16.8 s; each pass took about 24 minutes.

## Against the expectations stated in advance

| | Expected | Measured |
|---|---|---|
| selection-2 | uncertain, leaning works | **works** |
| Precision without the check | about 50% (35–65%) | **32%** (below) |
| Stage rule | supported | supported (23 of 25) |

## What this means, and what it doesn't

- **selection-2 has now passed 2 of 3 declared checks:**
  - test-4, Claude-annotated;
  - test-5, Codex-annotated, under the current guide.

  On all three it held back mostly wrong regions (22/2, 17/7, 14/4). It failed on test-3 only
  on the size of the precision rise.
- **What the declaration said would follow:** propose turning selection-2 on by default in the
  next release. That is a manifest change the owner approves. It trades coverage for precision.
- **The system is still far from the targets on this label shape.**
  - **Precision:** 42% with the check (target 95%).
  - **Useful coverage:** 7.4% (target 70%).
  - **Main error:** almost every wrong region uses the offset's town when the label names a
    place GNIS has.
- **Secondary evidence:**
  - **Annotator:** Codex was calibrated against the owner, but not under the absent-place rule.
  - **Sample:** one label shape, about 37 ready regions. A few records could have moved the
    ratio.
  - **Independent evidence:** owner-annotated data (locked test, releases 1–3) remains the
    independent evidence.
