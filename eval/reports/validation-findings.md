# Validation: the first held-out comparison

The 60 validation records were drawn from groups that nobody had read during development
([how](../benchmark/)). The owner annotated them blind, before any system ran on them. Both
systems then ran **unchanged**:

- rules `rules-1`
- LLM `llm-x2g2-qwen3.5-4b-q4km`: prompt `extraction-v2`, grammar 2, validation 2, core key 1,
  Qwen3.5-4B Q4_K_M, greedy decoding

Nothing was tuned on these records before scoring. Reports:
[rules](validation-rules-1.md), [LLM](validation-llm-x2g2-qwen3.5-4b-q4km.md),
[scores](validation-score.md).

## Result

| Correct proposal candidates (of 32 answerable) | Rules | LLM v2 |
|---|---|---|
| **validation** (held out) | 13 (41%) | **15 (47%)** |
| audit (dev data) | 14 (45%) | 12 (39%) |
| dev-1 (v2 built on it) | 16 of 29 | 18 of 29 |

- **LLM − rules on validation: +6 points (95% bootstrap CI −9 to +22; exact sign test
  p = 0.69).** 11 records are correct for both systems, 4 only for the LLM and 2 only for the
  rules. 15 of 32 are missed by both.
- **The milestone target (+10 points) is not met, and the difference is not significant.** The
  direction favours the LLM for the first time on unseen records, but 6 records separate the
  systems, and an interval this wide cannot tell +6 from −9.
- Unsupported records were flagged by both systems in 3 of 4 cases. References absent from GNIS
  were reported absent by both in 12 of 24 cases.
- Critical interpretation exact (all 60): rules 25, LLM 23. The LLM's lead comes from choosing
  the right reference (top-1 acceptable: rules 15, LLM 18 of 32), not from reading relations
  better.
- Excluding the 11 rows the annotator marked unsure gives the same answerable count and result
  (the unsure markers sit on non-answerable rows).

## Where each system wins

| Record | Label shape | Winner | Why |
|---|---|---|---|
| V002 | misspelt bare name ("Genessee Mountain") | LLM | the rules read it as `other`; fuzzy retrieval then finds Genesee Mountain |
| V013 | "S. slope Mt. Shavano, 10 mi. n. w. Salida" | LLM | the named feature is the collecting place; the rules also read the spaced "n. w." as N |
| V045 | "Cirque of the Peck Glacier …" | LLM | the rules keep "Cirque of the" in the name |
| V057 | "12 mi N of Wray of East-trending side road …" | LLM | the rules run the name on into "Wray of East-trending" |
| V012 | "drainage N of North Peak" | rules | the LLM says `named_feature` but keeps the direction N |
| V060 | "Bluebell Canyon, south edge of Boulder" | rules | the LLM picks the locating clause, Boulder |

## Why both miss 15 answerable records

| Pattern | Records | Notes |
|---|---|---|
| **Locating offset chosen over the named collecting place** | V006, V009, V014, V016, V055 | e.g. "Vernal Mesa, 15 mi. east of Montrose". Both systems pick Montrose. Prompt v2's rule 3 and its "Fenn Basin, ca. 7 mi W of Osgood" example target exactly this, and the model still fails |
| A context clause chosen (park, site, trail, basin) | V007, V029, V030, V031, V059 | "Boulder Mountain Parks" for Bear Pk.; "Sawtooth Peak" for Buchanan Pass |
| Qualifier scope | V048, V049 (LLM); V015 (rules) | the reference is right, but "near" belongs to the town in "Along Conejos River, Near Antonito", not to the river |
| Stream junction | V035 | annotated as two named features; the LLM says `between_features`, the rules `other` |
| Invalid LLM extraction | V008 | 3 of 60 LLM outputs failed validation |

The biggest single pattern is the one prompt v2 was written to fix. It worked on dev-1, where
the shape was common, and did not transfer to the audit or to validation. This is the strongest
evidence so far that prompt wording alone will not close the gap with a 4B model.

## Latency

LLM p50 17.8 s and p95 30.2 s per record (Apple M1, 8 GB), against p50 9.7 s on the audit run
with the same prompt length (2,377 vs 2,351 tokens) and no retries. During this run the machine
had little free memory, and llama-server processed prompts at 85–157 tokens/s. The figure is
reported as measured, not as the machine's best speed.

## Checker changes made before scoring

The worksheet checker did not recognise two forms the annotator copied from labels: `Half` as
a distance (V004) and `~` as an approximate marker (V040). Both were added, with tests. The
annotations were not changed. `just` (V023, V030) is still not a qualifier type, as in the
audit and dev-1, so it is ignored with a warning.

## What this does and does not show

- It is the first comparison on records that development never saw, but it has 32 answerable
  records and one annotator.
- **Validation is now read.** Its misses are listed above, so any change designed from them
  must be checked somewhere else. The locked test (120) stays unread and is the only unbiased
  measure left.
- Prompt v2 and retrieval stay frozen. Nothing here was changed in response to these results.
