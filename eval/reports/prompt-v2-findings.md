# Prompt v2: developed on dev-1, checked on the audit

Option 1 of the audit decision: develop extraction prompt v2 on a fresh dev sample
([`dev-1`](../dev/), annotated blind by the owner), freeze it, then check it on the
[audit](../audit/). Model, quantisation, grammar and generation settings are unchanged
(Qwen3.5-4B Q4_K_M, grammar v2, greedy). Every run is kept in this folder.

## Three changes, measured one at a time

| Stage | What changed | Report |
|---|---|---|
| v1 baseline | none | `dev-1-score-x1g2-validate-v1` |
| Step A | **validation v2**: an admin mention or qualifier whose quote is not in the label is dropped with a warning instead of failing the record. Critical components still fail hard. The rules are unaffected | `dev-1-score-x1g2-validate-v2` |
| Step B | **prompt `extraction-v2`**: new rules and 11 invented examples aimed at the dev-1 failure patterns | `dev-1-score-x2g2`, `audit-50-score` |

Step A came from a dev-1 finding: the model copied "Colo." from a v1 few-shot example into
labels that do not contain it, and once wrote the string `"null"` as a quote. One invented
context word then voided the whole extraction.

Prompt v2 targets the dev-1 failure patterns:
- bare place names read as "no locality" (now: a place name on its own is a named feature)
- the clause used to *locate* the place chosen instead of the collecting place itself
  ("Silver Lake, near Boulder" → Silver Lake)
- "route relative" used without a distance along a route
- compass words inside names turned into directions ("North Cheyenne Canon")
- invented qualifiers ("At Arboles" read as near)
- quotes and missing-component declarations that contradict the label

## Results

Correct proposal candidates: the critical interpretation and the top-ranked reference both
match the annotation, on answerable records.

| | Rules | LLM v1 | v1 + validation v2 | **LLM v2** |
|---|---|---|---|---|
| **dev-1** (in-sample for v2; 29 answerable) | 16 | 8 | 9 | **18** |
| **audit** (v2 not built from it; 31 answerable) | 13 | 9 | – | **10** |

On the audit, v2 against the rules: −10 points (95% CI −29 to +10, sign test p = 0.51). Excluding
the annotator's unsure rows gives 9/24 against 11/24.

**The dev-1 gain did not transfer.** v2 doubled its score on the sample it was written against
and gained one record on the audit. v1 → v2 changed only 3 audit records (2 gained, 1 lost).
Part of this is expected overfitting. Part is that dev-1 deliberately over-represents bare
names, which v2 fixes, while the audit's misses lie elsewhere.

What did transfer to the audit:
- "no locality" readings of place names: 7 → 1
- extractions passing validation: 41/50 → 48/50
- references absent from GNIS reported as absent: 7/15 → 11/15 (rules 6/15)
- unchanged from v1: every unsupported record still flagged (4/4; rules 0/4)

## Where the audit misses are now

19 of v2's 21 audit misses involve the reference, and **15 of the 31 answerable records are
missed by both systems**. Where the interpretation is right but the reference is wrong, the
cause is retrieval, which both systems share:

| Label says | GNIS has | Why retrieval misses |
|---|---|---|
| Mt. Zenobia | Zenobia Peak | generic word swapped (Mt./Mount ↔ Peak/Mountain) |
| Sockrider Mt. | Sockrider Peak | generic word swapped |
| Lower Piney Lake | Piney Lake | a positional prefix; fuzzy matching then prefers Lone Pine Lake in the wrong county |
| Gunnison Canon | Black Canyon of the Gunnison | historical/descriptive name |
| Longs Peak summit (v2 output for "2 mi NE of Longs Peak summit") | Longs Peak | v2 keeps a trailing descriptor in the name; v1 did not. A regression in v2, seen on the README example |

A retrieval key that ignores interchangeable generic words, and positional prefixes, is a
deterministic change that helps both systems. It is the clearest next lever.

## Discipline notes

- Prompt v2 was frozen after one dev-1 iteration, before it touched the audit. It will not be
  tuned on the audit.
- The audit check is not unbiased: the audit's findings shaped how dev-1 was drawn. Unbiased
  numbers come only from the locked test split, drawn from groups that are not in
  [`../viewed-groups.json`](../viewed-groups.json).
- One annotator throughout.
- Latency on the M1 is unchanged by the longer prompt (2,345–2,385 tokens): audit p50 10.2 s,
  p95 15.6 s.
