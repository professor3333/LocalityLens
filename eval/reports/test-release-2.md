# Locked test, release 2: rules first, LLM as fallback

Release 1 answered the milestone **no**: the LLM on its own did not add 10 points of correct
proposals over the rules ([result](test-release-1.md)). Release 2 asks the same question of
**hybrid-1**, which runs the rules and calls the LLM only where the rules reach no gazetteer
candidate ([how it was chosen](hybrid-1-findings.md)). This is the authorised, one-time scoring
declared in [`declaration-2.json`](../benchmark/declaration-2.json). The declaration was
committed and pushed before hybrid-1 was combined or scored on these records.

- **Records:** the same 120 locked-test records and annotations as release 1.
- **System:** `hybrid-1`, with components `rules-1` and `llm-x2g2-qwen3.5-4b-q4km`
  (code commit `78095de`).
  - No system was rerun. hybrid-1 was built from release 1's component reports, whose
    hashes were pinned in the declaration and checked before combining. Both components are
    deterministic, so this matches a live hybrid run.
- **Published here:** totals only. Per-record outputs stay in the locked folder.

## Answer: yes, narrowly, by the declared rule

| Correct proposal candidates (of 56 answerable) | Rules | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| **Locked test** | 19 (34%) | 15 (27%) | **25 (45%)** |
| Validation (held out, now read) | 13 of 32 | 15 of 32 | 16 of 32 |
| Dev data (audit + dev-1) | 30 of 60 | 30 of 60 | 32 of 60 |

**hybrid-1 − rules: +10.7 points (95% bootstrap CI +3.6 to +19.6; exact sign test p = 0.031).**
6 records are correct only for the hybrid, and **none** only for the rules.

The declared rule says **"yes"** when the difference is at least +10 points and the interval's
lower bound is above zero. Both hold, so the answer for release 2 is yes. The margin is thin:

- **+10 points of 56 is 5.6 records, so 6 is the smallest gain that clears it.** One record
  fewer would have been "not shown".
- **The interval runs from +4 to +20.** The data show that the hybrid is better than the
  rules (the lower bound is above zero), but not that the true gain is at least 10 points.
- **Excluding the 23 unsure rows gives the same picture:** rules 17, hybrid 23 of 50
  (+12 points, CI +4 to +22, p = 0.031).
- **This beat the stated expectation.** The declaration expected about +5 points from dev and
  validation data. The test gain is about twice that.

## Caveats

- **This is the test's second scoring, and it is not independent of the first.** The
  components are release 1's outputs unchanged. The idea of a rules-first hybrid came partly
  from release 1's published test totals. The selection rule itself was chosen on dev data only,
  and no per-record test output was read.
- **"At comparable precision" cannot be measured yet.** The section 7 LLM-contribution target
  includes that condition. Feature extent is unknown, so no system computes proposals, and
  precision of `ready_for_review` records doesn't exist yet.
- **One annotator.** The self-consistency re-annotation has not been done yet.

## What changed against the rules

| Of 120 records (unless stated) | Rules | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| Critical interpretation exact | 56 | 47 | **58** |
| Relation read correctly | 69 | 66 | **70** |
| Qualifiers right | 103 | 85 | **104** |
| Extraction passed validation | **120** | 105 | **120** |
| Acceptable reference ranked first (of 56) | 25 | 25 | **33** |
| Acceptable reference in top 5 (of 56) | 26 | 26 | **35** |
| Unsupported records flagged unsupported (of 16) | 7 | **9** | 7 |
| References absent from GNIS reported absent (of 48) | 17 | **26** | 14 |
| Mean fields a curator must correct per record | 1.63 | 1.76 | **1.54** |

Correct proposal candidates by annotated type (answerable records):

| Type | Rules | LLM v2 alone | hybrid-1 |
|---|---|---|---|
| named feature (38) | 12 | 11 | **17** |
| direction only (7) | 5 | 0 | 5 |
| distance and direction (9) | 2 | 4 | 3 |
| distance only (2) | 0 | 0 | 0 |

**Reading the totals:**
- **The gain is in retrieval.** Where the rules' name reaches no candidate, the LLM's quote
  often does: an acceptable reference is ranked first in 33 answerable records instead of 25.
  Interpretation barely moves (critical exact 56 → 58).
- **It keeps the rules' strengths.** Direction-only labels, qualifiers and validity stay at
  the rules' level, because the LLM is never asked when the rules already reach a candidate.
- **It costs some honest "absent" answers** (17 → 14 of 48). Where the rules correctly find
  nothing and the LLM finds a wrong candidate, the hybrid takes it. The dev data showed the same
  cost (hybrid-1 findings).
- **The LLM's better refusals are not used.** Unsupported flagged stays at the rules' 7 of 16,
  because the "unsupported" gate lost correct records on dev data.

## Cost

- **The model was called on 47 of 120 records (39%)** and skipped on 73.
- 13 records use the LLM's result; 107 keep the rules'.
- **Model time is 39% of the LLM alone:** 590 s against 1,495 s for the batch, from release 1's
  recorded per-record times (Apple M1, 8 GB, warm).

## What this means

- **The milestone question now has two answers:**
  - LLM extraction **instead of** rules: no (release 1).
  - LLM extraction **as a fallback** to rules: yes, by the declared rule, with a thin margin
    and an interval that still includes gains below 10 points (release 2).
- **The LLM's value here is recall, not interpretation.** It reaches a gazetteer entry for
  names the rules can't parse. Most of what the rules read correctly, it reads no better.
- **Not measured:** proposal correctness, coverage, containment and reviewer time. These need
  feature extent (a reviewed-extent store), which neither system has.
- **The test has now been scored twice.** Any later release needs its own declaration, and
  each further scoring weakens the test as an unbiased check.
