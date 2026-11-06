# Locked test, release 3: hybrid-1 with the current rules (rules-6)

Release 2 showed that rules with an LLM fallback clear the +10 point target, by one record
([result](test-release-2.md)). Since then the rules went from rules-1 to rules-6, and validation
and supplied-county handling changed. Release 3 asks whether the hybrid still adds 10 points
over the **improved** rules. This is the authorised, one-time scoring declared in
[`declaration-3.json`](../benchmark/declaration-3.json). The declaration was committed and
pushed (20:34:48 +05:45) before either component ran on these records.

- **Records:** the same 120 locked-test records and owner annotations as releases 1 and 2. The
  sample and worksheet hashes match the declaration.
- **Systems:** `rules-6`, `llm-x2g2-qwen3.5-4b-q4km` (prompt v2) and `hybrid-1` built from them.
  - Both components were rerun at code `8542e0f`, plus the declaration file only.
  - LLM completion cache off.
  - Run 15:16–15:38 UTC.
- **Published here:** totals only. Per-record outputs stay in
  `eval/benchmark/test/reports/release-3/`.

## Answer: yes, by the declared rule, again by the smallest possible margin

| Correct proposal candidates (of 56 answerable) | Rules | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| **Release 3** (rules-6, validation 3) | 22 (39%) | 18 (32%) | **28 (50%)** |
| Release 2 (rules-1, validation 2) | 19 (34%) | 15 (27%) | 25 (45%) |

**hybrid-1 − rules-6: +10.7 points (95% bootstrap CI +3.6 to +19.6; exact sign test
p = 0.031).** 6 records are correct only for the hybrid, and **none** only for the rules.

The rule says **"yes"** when the difference is at least +10 points and the interval's lower bound
is above zero. Both hold.

- **6 of 56 is the smallest gain that clears +10 points**, as in release 2. One record fewer
  would have been "not shown".
- **The interval runs from +4 to +20.** The hybrid is better than the rules, but a true gain
  below 10 points is not ruled out.
- **Excluding the 23 unsure rows gives the same picture:** rules 20, hybrid 26 of 50
  (+12 points, CI +4 to +22, p = 0.031).
- **The stated expectation was wrong again.** The declaration expected about +5 points from the
  read samples and said "yes" was unlikely.
  - The rules improved by 3 on the test.
  - The hybrid improved by the same 3, so the margin did not shrink.
  - Dev data has now underestimated the test margin twice.

**LLM alone against rules-6:** 18 against 22, −7.1 points (CI −21 to +7, p = 0.48). The LLM
alone is still not better than the rules.

## What changed since release 2 (descriptive, not paired)

| Of 120 records (unless stated) | rules-1 → **rules-6** | LLM v2 (val 2 → **3**) | hybrid-1 (r2 → **r3**) |
|---|---|---|---|
| Correct proposal candidates (of 56) | 19 → **22** | 15 → **18** | 25 → **28** |
| Critical interpretation exact | 56 → **62** | 47 → **50** | 58 → **63** |
| Relation read correctly | 69 → **75** | 66 → **67** | 70 → **76** |
| Qualifiers right | 103 → **106** | 85 → **87** | 104 → **106** |
| Extraction passed validation | 120 → 120 | 105 → **107** | 120 → 120 |
| Acceptable reference ranked first (of 56) | 25 → 24 | 25 → **27** | 33 → 32 |
| Acceptable reference in top 5 (of 56) | 26 → 25 | 26 → **28** | 35 → 34 |
| Unsupported flagged unsupported (of 16) | 7 → 7 | 9 → 9 | 7 → 7 |
| References absent from GNIS reported absent (of 48) | 17 → 17 | 26 → 26 | 14 → 14 |
| Mean fields a curator must correct | 1.63 → **1.54** | 1.76 → **1.66** | 1.54 → **1.46** |

By annotated type (correct candidates, answerable):

| Type | Rules r2 → r3 | LLM r2 → r3 | hybrid-1 r2 → r3 |
|---|---|---|---|
| named feature (38) | 12 → 12 | 11 → 11 | 17 → 17 |
| distance and direction (9) | 2 → **6** | 4 → **6** | 3 → **7** |
| direction only (7) | 5 → 4 | 0 → 1 | 5 → 4 |
| distance only (2) | 0 → 0 | 0 → 0 | 0 → 0 |

**Reading the changes:**

- **The rules' gain is in distance-and-direction labels** (2 → 6 of 9), where rules-2 to rules-6
  changed how numbers, units and offsets are read.
- **One direction-only label was lost** (5 → 4), and one reference dropped out of the top 1 and
  the top 5. These are totals: which records changed is not examined, because that would turn the
  test into development data.
- **The LLM's gain (15 → 18) comes without any change to the model or prompt.** The LLM's
  completions are deterministic, so this comes from validation version 3 and the
  supplied-county handling.
- **Named features did not move for any system.** The hybrid's advantage there (17 against 12)
  is unchanged, and it is all retrieval. Where the rules' name reaches no candidate, the LLM's
  quote often does.

## Cost

- **The model was called on 45 of 120 records (38%)** and skipped on 75. 13 records use the
  LLM's result; 107 keep the rules'.
- **Model time:** 479 s for the hybrid against 1,285 s for the LLM alone on all 120 (37%).
- **Model latency:** p50 9.9 s, p95 16.4 s per record. Apple M1 8 GB, warm server, cache off.

## Caveats

- **This is the third scoring of the locked test.** Releases 1 and 2 published test totals.
  The rules changes since were designed on dev and validation data, some in-sample on read
  records. No per-record test output was read.
- **The test is not independent of release 2.** The LLM component is the same model and prompt,
  and the 6 records the hybrid gains may overlap with release 2's 6. Which records they are
  has not been examined.
- **"At comparable precision" is not measurable on the test.** The section 7 target includes
  it, but no reviewed extents exist for test features, so no system computes test regions. On the
  read samples, hybrid-1's computed regions are 32 of 35 correct
  ([extents findings](extents-findings.md)).
- **One annotator.** The test was annotated once by the owner, with no self-consistency pass.
- **A process slip, recorded:** while updating docs after the run, a repository-wide text search
  matched two aggregate table rows in the locked folder's score files (top-5 counts, the same
  totals as above). No per-record content was shown.

## What this means

- **The milestone answer holds with the improved rules.** Running the rules first and the LLM
  only where they find nothing gives +10.7 points over the rules alone, the same margin as
  release 2.
- **The margin is still the minimum.** Further test scorings would add little evidence. A
  stronger claim needs new held-out, owner-annotated records.
