# test-4: wrong regions under the absent-place rule, and selection-2 again

A declared check ([declaration](../benchmark/declaration-test-4.json), pushed before
annotation; [amendment 1](../benchmark/declaration-test-4-amendment-1.json), pushed before the
run, records the change of annotator).

- **Sample:** 120 unread "place, offset" labels, drawn after excluding every read or reserved
  group, all earlier held-out sets, repeated wording and linked collecting events.
- **Annotations: by Claude.** The owner chose Claude instead of annotating test-4 themselves.
  - **Not independent:** Claude also wrote the systems, the stage script and the hypothesis
    tested here.
  - **Seen before:** several labels repeat wordings Claude annotated earlier (listed in the
    amendment).
  - **The rule:** annotated under the guide's absent-place rule (GBIF Best Practices §3.2.2),
    which 38 rows use.
  - **Categories:** 107 answerable, 6 reference absent, 7 unsupported.
- **Systems:** hybrid-1 (rules-6 first, then llm-x2g2-qwen3.5-4b-q4km), with reviewed and derived
  extents, without and with `--selection-2`.
- **Run:** once at 0d921e9, 2026-11-10 03:47–04:38 UTC, LLM cache off, native llama-server. No
  technical failures.
- **Published here:** totals only. Per-record outputs stay in `eval/benchmark/test-4/reports/`.

## Primary question: supported

Under the absent-place rule, do most wrong ready regions come from choosing another place when
the annotated place is in GNIS?

| hybrid-1 ready regions, no check (60) | Count |
|---|---|
| Correct | 33 |
| **Clause choice: another place chosen, annotated place in GNIS** | **18** |
| Same name, other GNIS feature | 4 |
| Annotated unsupported | 3 |
| Reading error, right reference | 2 |

**18 of the 27 wrong regions (67%)** are this stage, and it is the largest. The declared rule
(largest, and at least half) is met.

## Secondary results

| hybrid-1, 120 records, 107 answerable | Ready regions | Correct | Useful coverage |
|---|---|---|---|
| Without the check | 60 | 33 (55%) | 33 (30.8%) |
| With `selection-2` | 36 | 26 (72%) | 26 (24.3%) |

- **Precision without the check: 55%,** inside the 36–57% range stated in advance.
- **`selection-2` works by the test-3 rule.** It held back 24 regions, 17 wrong and 7 correct
  (17 ≥ 2 × 7), and precision rose 17.2 points (55% → 72%). It costs 6.5 points of useful
  coverage.
  - **Against the stated expectation:** the declaration expected it to fail.
  - **Stage by stage:** it held back 14 of the 18 "other place chosen" regions, and 7 correct
    ones. It left the 4 same-name, other-feature regions untouched.
- **Rules alone and LLM alone:**

  | | Ready, correct (no check) | Ready, correct (with check) |
  |---|---|---|
  | Rules (rules-6) | 56, 31 | 32, 24 |
  | LLM alone | 53, 27 | 33, 20 |

- **Correct proposal candidates, of 107 answerable** (the same with and without the check):

  | Rules | LLM alone | hybrid-1 | hybrid − rules |
  |---|---|---|---|
  | 46 | 37 | 49 | +2.8 points (95% CI 0 to +6.5, sign p = 0.25): 3 gained, 0 lost |

  - **Excluding unsure records** (93 answerable): rules 41, LLM 34, hybrid 44.
  - **The LLM alone:** 112 valid extractions of 120. Its pass took 23.8 min without the check and
    26.7 min with it.

## Against the expectations stated in advance

| | Expected | Measured |
|---|---|---|
| Precision without the check | about 46% (36–57%) | 55% |
| Primary | supported | supported |
| selection-2 | likely does not work | **works** |

## What this means, and what it doesn't

- **On Claude's annotations, the picture from the test-3 review holds on unread labels:**
  - With the absent-place rule, about half the ready regions are correct.
  - Most errors use the town when the label names a place GNIS has.
  - selection-2 removes most of those errors.
- **This is weak evidence.**
  - **Who annotated:** the annotator wrote the systems, the rule, the stage script and the
    hypothesis.
  - **Matches earlier:** Claude-annotated test-2 gave a similar precision (58%).
  - **What would show more:** owner-annotated data, which are the independent evidence (locked
    test, releases 1–3). An owner-annotated sample would show whether these numbers hold.
- **selection-2 is still not the default.** Its two declared checks disagree: it failed on
  test-3 (Codex, old guide) and passes on test-4 (Claude, new guide). The guide changed between
  them, and so did the annotator.
- **Precision is far from the 95% target,** and coverage is far from the 70% target.
