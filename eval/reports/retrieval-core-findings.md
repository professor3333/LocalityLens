# Core-match retrieval: generic words set aside

After prompt v2, most audit misses were retrieval failures shared by both systems
([prompt v2 findings](prompt-v2-findings.md)). This change adds a **core match** tier to the
gazetteer search, between exact and fuzzy matches.

## The rule (`gazetteer/keys.py`, `CORE_KEY_VERSION` 1)

The core of a name key:
- **removes** the summit generics (mount, mountain, peak, summit) wherever they appear, and a
  leading positional word (upper, lower, middle)
- **folds** canon to canyon and plurals (lakes → lake, peaks → peak)
- is **refused** when only generic words would remain ("Lower Lake", "Upper Creek", "Peak")

| Label | Core | GNIS feature found |
|---|---|---|
| Mt. Zenobia | zenobia | Zenobia Peak |
| Sockrider Mt. | sockrider | Sockrider Peak |
| Longs Peak summit | longs | Longs Peak |
| Lower Piney Lake | piney lake | Piney Lake (but **never** Upper Piney Lake) |

Two names with the same core but different positional words are not offered ("Lower" is evidence
*against* "Upper"). Core matches rank below every exact match, so nothing that matched exactly
before can be displaced. County, state and type still only rank, never filter. Exact keys and the
index are unchanged, and the core-key version is pinned in the release manifest and recorded in
every report.

## Results

Correct proposal candidates (prompt v2, grammar v2, validation v2):

| | Rules before → after | LLM v2 before → after |
|---|---|---|
| **audit** (31 answerable): the fix was designed from these misses | 13 → **14** | 10 → **12** |
| **dev-1** (29 answerable): the clean check | 16 → 16 | 18 → 18 |

- On the audit, the acceptable reference ranked first went from 16 to 18 (rules) and from 12 to
  14 (LLM). The two changed records are A26 (Mt. Zenobia → Zenobia Peak) and A35 (Lower Piney
  Lake → Piney Lake, where fuzzy matching had chosen Lone Pine Lake in another county).
- **On dev-1, no top candidate changed for either system.** dev-1's retrieval misses are other
  patterns:
  - a single-letter abbreviation ("Gem L."), which the key deliberately does not expand
  - a hill/mountain swap ("Flagstaff Hill" for GNIS "Flagstaff Mountain")
  - clause choices by the model
- v2 against the rules on the audit is now −7 points (95% CI −26 to +13, sign test p = 0.75).

**So:** the change does what it targets, with zero regressions across 100 annotated records.
It is **not yet shown to generalise**, because the only improvement is on the records it was
designed from. "hill" was deliberately not added, because that idea came from dev-1, and adding
it would spend dev-1's value as a check.

## Kept for comparison

Every report from before this change is kept with the suffix `-pre-core`.
