# test-2 regions: the selection check on unread labels

A declared second scoring of test-2
([declaration](../benchmark/declaration-test-2-regions.json), pushed before the run).

- **The question:** on labels nobody has read, does the selection check (`selection-1`) raise
  the share of ready regions that are correct, and what does it cost?
- **Systems:** hybrid-1 with reviewed + [derived extents](derived-extents-findings.md), without
  and with the check.
- **Run:** once at 2a22383, 2026-11-09 03:41–04:29 UTC, LLM cache off.
- **Published here:** totals only. Per-record outputs stay in
  `eval/benchmark/test-2/reports-regions/`.
- **Annotations:** by Claude, who also wrote the rules, the derived extents and the check.
  Not independent.

## Result: the check does not hold up on unread labels

| hybrid-1, 120 records, 80 answerable | Ready regions | Correct | Useful coverage |
|---|---|---|---|
| Without the check | 31 | 18 (58%) | 18 (22.5%) |
| With the check | 16 | 10 (63%) | 10 (12.5%) |

- **It holds back 15 regions: 8 correct and 7 wrong.** On unread labels it is about as likely to
  hold back a right region as a wrong one.
- **On the read samples it was written from,** it held back 25 wrong against 11 correct, and
  raised precision from about 50–60% to about 70%. Most of that gain was fitted to those records.
- **Against the expectation stated in advance:**
  - Without the check: 58% correct, inside the expected 40–60%.
  - With the check: 63%, inside the expected 60–70%, but only because it starts higher.
  - Coverage lost: 10 points, against an expected 3–5.
- **Other totals:** for the rules alone, 26 ready, 15 correct without the check and 12 / 8 with
  it. For the LLM alone, 25 / 17 and 15 / 9. Correct proposal candidates are unchanged (rules 34,
  LLM 31, hybrid 43 of 80, as in the [first test-2 scoring](test-2.md)): the check only routes
  records.

## What this means

- **`selection-1` is not recommended.** It stays opt-in, versioned and documented as a failed
  experiment. It is never on by default.
- **Derived extents on unread labels:** 31 ready regions, 18 correct (58%). That is better than
  the 39–47% on Claude-annotated dev data, and far from the 95% target.
- **Better reference choice would need evidence the label text alone does not give.** For
  example, whether the other named place exists in GNIS near the proposed point, or a second
  model call that compares candidates. Any such rule needs a fresh, unread check like this one.
