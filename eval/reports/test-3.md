# test-3: selection-2 on unread "place, offset" labels

A declared check ([declaration](../benchmark/declaration-test-3.json), pushed before
annotation; [amendment 1](../benchmark/declaration-test-3-amendment-1.json), pushed before the
run, corrects the declared release-manifest hash).

- **The question:** on labels nobody had read, does `selection-2` mostly hold back wrong regions,
  and does the share of ready regions that are correct rise?
- **Sample:** 120 unread labels of one shape, "place, offset" (for example "<place>, 3 mi N of
  <town>"). They were drawn after excluding every read or reserved group, repeated wording and
  linked collecting events.
- **Annotations:** by **Codex. Agreement with the owner: 54/60 on category, 55/60 on GNIS IDs**
  ([calibration](codex-calibration.md)). This is secondary evidence: Codex is not the owner, and
  its blindness can be stated but not checked.
  - Committed unchanged in ff55e8e (sha256 13135ff6…, 0 checker problems) before any run.
  - Categories: 63 answerable, 44 with a reference absent from GNIS, 13 unsupported. 23 records
    carry an "unsure" marker.
- **Systems:** hybrid-1 (rules-6 first, then llm-x2g2-qwen3.5-4b-q4km), with reviewed and
  [derived extents](derived-extents-findings.md), run without and with `--selection-2`.
- **Run:** once at f453685, 2026-11-09 15:49–16:44 UTC, LLM cache off, native llama-server.
- **Published here:** totals only. Per-record outputs stay in `eval/benchmark/test-3/reports/`.

## Result: does not work, by the rule stated in advance

| hybrid-1, 120 records, 63 answerable | Ready regions | Correct | Useful coverage |
|---|---|---|---|
| Without the check | 53 | 7 (13%) | 7 (11.1%) |
| With `selection-2` | 29 | 5 (17%) | 5 (7.9%) |

The declared rule needed both conditions:

| Condition | Needed | Measured | |
|---|---|---|---|
| Held-back regions: wrong vs correct | wrong ≥ 2 × correct | **22 wrong, 2 correct** (of 24) | met |
| Share of ready regions that are correct | +5 points | **+4.0 points** (13.2% → 17.2%) | not met |

**So `selection-2` does not work under this declaration.** It stays opt-in and off by default.

## What the numbers show

- **The check now picks the right records to hold.** It held back 22 wrong regions for every 2
  correct ones. On test-2, `selection-1` held 7 wrong and 8 correct. The held-back records
  behave as on the dev data it was written from (5 correct, 20 wrong).
- **Precision misses because the base is so low.** On this label shape, 46 of the 53 ready regions
  are wrong without the check, and 24 of 29 with it. Holding back 22 wrong regions cannot lift
  precision far when most of what is left is also wrong.
- **The low base can't be explained from totals alone.** The sample was chosen for the shape
  where wrong references concentrate. A different annotator than on test-2 may also count
  differently. These two causes can't be separated here, and per-record outputs are not read.
- **Rules alone and the LLM alone** show the same picture:

  | | Ready, correct (no check) | Ready, correct (with check) |
  |---|---|---|
  | Rules (rules-6) | 50, 5 | 26, 3 |
  | LLM alone | 43, 6 | 23, 3 |

## Secondary totals (descriptive, Codex-annotated)

**Correct proposal candidates, of 63 answerable** (the check only routes records, so these are
the same with and without it):

| Rules | LLM alone | hybrid-1 | hybrid − rules |
|---|---|---|---|
| 14 | 8 | 16 | +3.2 points (95% CI 0 to +7.9, sign p = 0.5): 2 gained, 0 lost |

- **Excluding unsure records** (53 answerable): rules 13, LLM 8, hybrid 15.
- **The LLM alone against rules:** −9.5 points (CI −20.6 to +1.6). It produced 113 valid
  extractions of 120.
- **Run time:** the LLM pass took 28.5 min (without the check) and 25.3 min (with it), for 120
  records each.

## Against the expectation stated in advance

- **Either outcome was called plausible.** The ratio condition passed by a wide margin, and the
  precision condition missed by one point.
- **"The targeted sample should hold more regions than test-2 did":** held. It held 24 regions,
  against 15 for `selection-1` on test-2.

## Run note

- **One technical failure.** The first score command also passed `--extents` and
  `--derived-extents`. `audit score` does not take them, because it reads the stores from the
  reports. argparse exited before anything was scored.
- **The fix.** Only the score step was rerun, with the declared options. Rules, LLM and hybrid
  ran once. The failed log is kept beside the outputs.

## What this means

- **`selection-2` is not adopted.** Using it later would need a new declaration and fresh unread
  labels.
- **It does separate wrong regions from right ones.** That makes it a candidate signal, for
  example to rank the review queue, not proof of a gain.
- **On "place, offset" labels, regions are mostly wrong whatever the check does:** 24 of the 29 it
  leaves ready. The reference choice for this shape is still the main shortfall. Fixing it needs
  more than holding regions back.
