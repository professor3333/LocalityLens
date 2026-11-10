# Benchmark: held-out validation and locked test

The final comparison of the rules baseline, the LLM pipeline and later GEOLocate runs on records
**nobody has read during development**. Dev data is the [audit](../audit/) and the
[dev samples](../dev/).

| Split | Groups | Use |
|---|---|---|
| `validation/` | 60 | Choosing thresholds and settings, and checking a frozen change before the test |
| `test/` | 120 | **Locked.** Read only by the final, authorised evaluation, after targets are frozen. Scored three times (releases 1–3) |
| `test-2/` | 120 new + 20 blind repeats | **Locked.** A fresh held-out test for v0.1.0, declared before annotation (below) |
| `test-3/` | 120 "place, offset" labels | **Locked.** A fresh, targeted test of the selection-2 check, annotated by Codex (calibrated against the owner), declared before annotation |
| `test-4/` | 120 "place, offset" labels | **Locked.** A fresh test under the annotation guide's absent-place rule (GBIF BP §3.2.2), annotated by Claude (not independent), declared before annotation |
| `test-5/` | 120 "place, offset" labels | **Locked.** The deciding check of selection-2 under the absent-place rule, annotated by Codex (calibrated against the owner), declared before annotation |

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

**Annotator changed (2026-11-08).** At the owner's request, Claude annotated test-2, not the owner
([amendment](declaration-test-2-amendment-1.json), pushed after the annotation commit and before
any system runs). Claude also wrote the rules being compared, so test-2 is not independent of the
systems, as dev-2 to dev-4 were not. The 20 repeats now measure agreement between Claude and the
owner, not one annotator's self-consistency. Locked-test releases 1 to 3, annotated by the owner,
remain the independent evidence.

## test-4: annotator

[`declaration-test-4.json`](declaration-test-4.json) named the owner as annotator. The owner then
chose Claude ([amendment](declaration-test-4-amendment-1.json), pushed after the annotation commit
and before any system runs). Claude also wrote the systems and the error-stage script, so test-4's
results are not independent of them. Locked-test releases 1 to 3 remain the independent evidence.

## test-5: why, and who annotates

test-3 and test-4 disagree on selection-2: it failed on test-3 (Codex, before the absent-place
rule) and passed on test-4 (Claude, after it). Both the annotator and the guide changed between
them. test-5 keeps the new guide and changes the annotator back to someone who did not write the
systems.

```bash
uv run localitylens benchmark draw-extra --name test-5 --seed benchmark-5/1 --size 120 \
  --prefix S --shape place_offset --shape-version 2 --repeats 0 \
  --exclude-lock eval/splits-2.lock.json --exclude-lock eval/splits-3.lock.json \
  --exclude-lock eval/splits-4.lock.json --lock-out eval/splits-5.lock.json \
  --out eval/benchmark/test-5
```

- **Excluded:** 4,587 viewed or reserved groups, 37 more by repeated wording, and 788 components
  touching them (9,017 groups).
- **The lock:** [`../splits-5.lock.json`](../splits-5.lock.json) reserves 518 groups.
- **Checked by counts, hashes and key sets only:** 0 overlap with the four earlier locks and the
  viewed-groups registry; the worksheet has 120 rows.
- **Annotator:** the owner, or Codex on the owner's side, under the annotation guide at the hash
  pinned in [`declaration-test-5.json`](declaration-test-5.json). Not Claude: a Claude-annotated
  test-5 could not settle the question. Whoever annotates is recorded before any system runs.
- **Annotated by Codex** (worksheet commit 76307b3; [amendment](declaration-test-5-amendment-1.json),
  pushed before any system runs).

## Declared releases

| Release | Declaration | Result (correct proposal candidates, of 56 answerable) |
|---|---|---|
| 1 | [`declaration-1.json`](declaration-1.json), pushed before the run | rules 19, LLM v2 15: −7 points (CI −23 to +7), milestone answer **no** ([result](../reports/test-release-1.md)) |
| 2 | [`declaration-2.json`](declaration-2.json), pushed before the run | `hybrid-1` 25 against rules 19: +10.7 points (CI +3.6 to +19.6), answer **yes**, by one record ([result](../reports/test-release-2.md)) |
| 3 | [`declaration-3.json`](declaration-3.json), pushed before the run | `hybrid-1` with rules-6: 28 against rules-6 22: +10.7 points (CI +3.6 to +19.6), answer **yes**, again by one record ([result](../reports/test-release-3.md)) |
| test-2 | [`declaration-test-2.json`](declaration-test-2.json), pushed before annotation; [amendment 1](declaration-test-2-amendment-1.json) (Claude annotated), pushed before the run | `hybrid-1` 43 against rules-6 34 of 80 answerable: +11.3 points (CI +5.0 to +18.8), answer **yes**. Claude-annotated, so not independent ([result](../reports/test-2.md)) |

Per-record outputs of each test run stay in `test/reports/`, inside the locked folder, and are
not read during development. Only the totals are published in [`../reports/`](../reports/).

## Data licence

University of Colorado Museum of Natural History Herbarium Vascular Plant Collection, CC BY 4.0.
Cite: *GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf*.
Selection and annotation columns are modifications by this project. Label text is unchanged,
and no georeference fields are included.
