# Benchmark: held-out validation and locked test

The final comparison of the rules baseline, the LLM pipeline and later GEOLocate runs on records
**nobody has read during development**. Dev data is the [audit](../audit/) and the
[dev samples](../dev/).

| Split | Groups | Use |
|---|---|---|
| `validation/` | 60 | Choosing thresholds and settings, and checking a frozen change before the test |
| `test/` | 120 | **Locked.** Read only by the final, authorised evaluation, after targets are frozen. Scored three times (releases 1–3) |
| `test-2/` | 120 new + 20 blind repeats | **Locked.** A fresh held-out test for v0.1.0, declared before annotation (below) |

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

## test-2: a fresh held-out test

The locked test has been scored three times and the rules changed in between, so v0.1.0's
claim needs records that played no part in any of it.

```bash
uv run localitylens benchmark draw-extra --name test-2 --seed benchmark-2/1 --size 120 \
    --prefix H --repeats-from eval/benchmark/validation/validation.json --repeats 20 \
    --repeat-seed selfcheck-1/1 --out eval/benchmark/test-2
```

1. **Excluded first:**
   - the 2,192 groups that were viewed in development or reserved by the first lock;
   - 31 more groups with the same wording under another county;
   - every leakage component touching any of them: 422 components, 6,608 groups.
2. **The draw:** 120 groups, at most one per remaining component, in `sha256(seed | group_key)`
   order (uniform, as for the first test).
3. **Blind repeats:** 20 validation records, chosen by `selfcheck-1/1`, are mixed in. All 140
   rows are renumbered `H001`–`H140` in seeded order, so a repeat cannot be told apart by its ID
   or position. `repeats.json` maps them back. It holds IDs only, and the annotator does not
   open it, nor the validation worksheet, until annotation is finished. The repeats measure the
   annotator's self-consistency; they are never scored as test records.
4. **The lock:** [`../splits-2.lock.json`](../splits-2.lock.json) holds the new groups' keys, and
   reserves all 956 groups of their components. It is write-once with a digest. Dev samples
   exclude both locks from now on.

Checked by counts, hashes and key sets only:
- no reserved group overlaps the first lock or the viewed-groups registry;
- the worksheet has 140 rows.

Nobody but the annotator reads `test-2/`. [`declaration-test-2.json`](declaration-test-2.json)
was pushed before annotation began.

## Declared releases

| Release | Declaration | Result (correct proposal candidates, of 56 answerable) |
|---|---|---|
| 1 | [`declaration-1.json`](declaration-1.json), pushed before the run | rules 19, LLM v2 15: −7 points (CI −23 to +7), milestone answer **no** ([result](../reports/test-release-1.md)) |
| 2 | [`declaration-2.json`](declaration-2.json), pushed before the run | `hybrid-1` 25 against rules 19: +10.7 points (CI +3.6 to +19.6), answer **yes**, by one record ([result](../reports/test-release-2.md)) |
| 3 | [`declaration-3.json`](declaration-3.json), pushed before the run | `hybrid-1` with rules-6: 28 against rules-6 22: +10.7 points (CI +3.6 to +19.6), answer **yes**, again by one record ([result](../reports/test-release-3.md)) |

Per-record outputs of each test run stay in `test/reports/`, inside the locked folder, and are
not read during development. Only the totals are published in [`../reports/`](../reports/).

## Data licence

University of Colorado Museum of Natural History Herbarium Vascular Plant Collection, CC BY 4.0.
Cite: *GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf*.
Selection and annotation columns are modifications by this project. Label text is unchanged,
and no georeference fields are included.
