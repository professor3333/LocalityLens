# hybrid-1: rules first, LLM as fallback

The locked test of release 1 answered the milestone "no" ([result](test-release-1.md)). On its
own, the LLM did not beat the rules. This experiment asks whether the two **together** do
better than the rules alone.

## The rule (`pipeline/hybrid.py`, `HYBRID_VERSION` hybrid-1)

1. Run the rules. If their interpretation is valid and reaches at least one gazetteer
   candidate, use it, with **no model call**.
2. Otherwise call the LLM, and use its result only if it is valid and reaches a candidate.
3. Otherwise keep the rules' result. A failed model call never makes a record worse.

Each record takes one system's whole result, never a field-by-field mix.

## How it was chosen: dev data only

Both component systems are deterministic, so their existing reports show exactly what any
selection rule would produce. Five rules were tried on the two dev samples (audit and dev-1,
60 answerable records), and every result is kept here:

| Selection rule (dev data) | Correct candidates | vs rules | Lost |
|---|---|---|---|
| Rules alone | 30 | – | – |
| LLM alone | 30 | ±0 | 7 |
| **Fallback: LLM where the rules reach no candidate** | **32** | **+2** | **0** |
| Fallback, but only where the rules found no reference at all | 30 | ±0 | 0 |
| Fallback + the LLM's "unsupported" verdict as a gate | 29 | −1 | 3 |
| Fallback + "unsupported" gate only where the rules have no candidate | 32 | +2 | 0 |
| Fallback + prefer the LLM's "absent" over a fuzzy rules match | 31 | +1 | 1 |
| **Oracle**: always the system that is right (upper bound) | 37 | +7 | 0 |

**The "unsupported" gate costs records the rules had right.** The LLM's ability to flag
unsupported labels looked useful in release 1's totals. Used as a gate, though, it overrides
correct rules readings, so hybrid-1 does not use it. The simplest rule (fallback) was the best
one with no losses, and it was the one chosen.

**Even a perfect selector gains only about 12 points on dev data** (37 against 30 of 60). The
two systems mostly fail on the *same* records, so no way of combining them can add much.

## Results

| Correct proposal candidates | Rules | LLM v2 | **hybrid-1** | hybrid − rules (95% CI) | LLM calls |
|---|---|---|---|---|---|
| Audit (dev) | 14/31 | 12/31 | **14/31** | ±0 | 16 of 50 |
| dev-1 (dev) | 16/29 | 18/29 | **18/29** | +7 pts (0 to +17) | 18 of 50 |
| Validation (already read) | 13/32 | 15/32 | **16/32** | +9 pts (0 to +22) | 26 of 60 |
| **All three** | 43/92 | 45/92 | **48/92** | **+5 pts** | 60 of 160 |

- **hybrid-1 never loses a record the rules had right.** That holds in all 160 records: 5
  gained, 0 lost.
- It is at least as good as either component on every sample.
- **It calls the model on 38% of records**, so a batch needs well under half the LLM-only
  model time.
- **It costs something on references missing from GNIS:**
  - where the rules correctly report "absent" and the LLM finds a wrong candidate, the hybrid
    takes the wrong candidate
  - absent reported absent: audit 6 → 4, validation 12 → 11
  - mean corrections per record on the audit: 1.84 → 2.08
- **Validation is a weak check.** Its records were read when release 1 was scored, and some of
  its LLM-only wins (a misspelt name, "Cirque of the …") illustrate what fallback recovers.
  Only the locked test can give an unbiased number.

## What this means for the milestone

- **The expected gain is about +5 points**, and the dev-data ceiling is about +12. Clearing
  the +10 target on the locked test would need the hybrid to do far better there than on any
  sample seen so far.
- **The choice to try a hybrid came partly from release 1's test totals** (the LLM did better
  at refusing what cannot be done). Any test score for hybrid-1 must state this.
- **hybrid-1 is still the best system measured:** never worse than the rules, and cheaper than
  the LLM alone.

## Locked test (release 2, scored after these findings)

Declared in [`declaration-2.json`](../benchmark/declaration-2.json) and scored once: hybrid-1
**25 of 56** against the rules' 19, **+10.7 points** (CI +3.6 to +19.6), 6 gained and none
lost. That clears the +10 point target by one record, about twice the gain expected above
([result](test-release-2.md)).
