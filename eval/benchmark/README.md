# Benchmark: held-out validation and locked test

The final comparison of the rules baseline, the LLM pipeline and later GEOLocate runs on records
**nobody has read during development**. Dev data is the [audit](../audit/) and the
[dev samples](../dev/).

| Split | Groups | Use |
|---|---|---|
| `validation/` | 60 | Choosing thresholds and settings, and checking a frozen change before the test |
| `test/` | 120 | **Locked.** Read only by the final, authorised evaluation, after targets are frozen |

## How it was drawn

```bash
uv run localitylens benchmark draw --seed benchmark/1    # --validation 60 --test 120
```

1. Start from the 40,444 eligible locality groups of `gbif-cu-2026-11-01` (same screening and
   wording groups as the audit).
2. Join groups that share a collecting event (same collector, same exact date;
   `EVENT_GROUPING_VERSION` 1) into **leakage components**: 15,955 of them. Specimens from one
   trip can describe one place in different words, so they must never sit in different splits.
3. Exclude every component that touches a group read in development
   ([`../viewed-groups.json`](../viewed-groups.json)): 93 components, 3,550 groups.
4. Take groups in `sha256(seed | group_key)` order, at most one per component: the first 120 go
   to test and the next 60 to validation. The sample is uniform, not stratified, so it is
   representative of the collection.
5. Record the assignment in [`../splits.lock.json`](../splits.lock.json): group keys only, with
   a SHA-256 digest, and write-once. Every group of a held-out component (1,942) is
   **reserved**, and dev samples exclude reserved groups from now on.

## Order of work

1. ✅ **Annotate `validation/worksheet.csv`** with the [annotation guide](../annotation_guide.md).
   Done and scored with the frozen systems: LLM v2 15/32, rules 13/32 correct proposal
   candidates ([findings](../reports/validation-findings.md)). Validation has now been read, so
   a change designed from its misses must be checked elsewhere.
2. ✅ **Annotate `test/worksheet.csv`** the same way. The annotator reads it, but no development
   code and no assistant opens, prints or summarises it. CI never touches it.
3. **Freeze the targets and the release** (prompt, grammar, validation, retrieval, model,
   policy) before the test is scored.
4. Score validation freely. Score test **once per declared release**, as an authorised final run,
   and publish the result whether it is good or bad.

## Declared releases

| Release | Declaration | Result (correct proposal candidates, of 56 answerable) |
|---|---|---|
| 1 | [`declaration-1.json`](declaration-1.json), pushed before the run | rules 19, LLM v2 15: −7 points (CI −23 to +7), milestone answer **no** ([result](../reports/test-release-1.md)) |

Per-record outputs of each test run stay in `test/reports/`, inside the locked folder, and are
not read during development. Only the totals are published in [`../reports/`](../reports/).

## Data licence

University of Colorado Museum of Natural History Herbarium Vascular Plant Collection, CC BY 4.0.
Cite: *GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf*.
Selection and annotation columns are modifications by this project. Label text is unchanged,
and no georeference fields are included.
