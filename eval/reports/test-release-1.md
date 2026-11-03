# Locked test, release 1: the milestone answer

The first milestone asks whether the LLM pipeline gives **more correct, useful proposals than
the rules baseline**, with a target of **+10 points**. This is the authorised, one-time run on
the locked test split, scored exactly as declared in
[`declaration-1.json`](../benchmark/declaration-1.json). The declaration was committed and pushed
before any system ran on these records.

- **Records:** 120, drawn from groups that nobody had read during development, one per
  collecting-event component ([how](../benchmark/)). The owner annotated them blind.
- **Systems:** rules `rules-1` and LLM `llm-x2g2-qwen3.5-4b-q4km`:
  - prompt `extraction-v2`, grammar 2, validation 2, core key 1
  - Qwen3.5-4B Q4_K_M, greedy decoding
  - code commit `f90ea0c`
- **Published here:** totals only. Per-record outputs stay in the locked folder.

## Answer: no, not with this release

| Correct proposal candidates (of 56 answerable) | Rules | LLM v2 |
|---|---|---|
| **Locked test** | **19 (34%)** | 15 (27%) |
| Validation (held out, now read) | 13 of 32 | 15 of 32 |
| Audit (dev data) | 14 of 31 | 12 of 31 |

**LLM − rules: −7 points (95% bootstrap CI −23 to +7; exact sign test p = 0.50).** 8 records
are correct only for the LLM, and 12 only for the rules.

The declared decision rule says **"no"** when the whole interval lies below the +10 point
target. The upper bound is +7, so the data rule the target out for this release. They do not
show that the rules are better, because the interval includes zero. Excluding the 23 rows with
an unsure annotation gives the same picture: rules 17, LLM 15 of 50 (−4 points, CI −20 to +12).

## What each system does better

| Of 120 records (unless stated) | Rules | LLM v2 |
|---|---|---|
| Critical interpretation exact | **56 (47%)** | 47 (39%) |
| Relation read correctly | **69 (58%)** | 66 (55%) |
| Distance / unit right | 88 / 92 | **93 / 96** |
| Direction right | **83** | 80 |
| Qualifiers right | **103 (86%)** | 85 (71%) |
| Extraction passed validation | **120** | 105 (15 rejected) |
| Acceptable reference ranked first (of 56) | 25 | 25 |
| Unsupported records flagged unsupported (of 16) | 7 | **9** |
| References absent from GNIS reported absent (of 48) | 17 | **26** |
| Place names read as "no locality" | **0** | 2 |
| Mean fields a curator must correct per record | **1.63** | 1.76 |

Correct proposal candidates by annotated type (answerable records):

| Type | Rules | LLM v2 |
|---|---|---|
| named feature (38) | 12 | 11 |
| direction only (7) | **5** | 0 |
| distance and direction (9) | 2 | **4** |
| distance only (2) | 0 | 0 |

**Reading the totals:**
- **Retrieval is level.** Both systems rank an acceptable reference first in 25 of 56
  answerable records, so the gap comes from interpretation.
- **The LLM loses on direction-only labels.** It reads relations as `direction_only` twice,
  against 15 annotated, and gets none of the 7 answerable ones right.
- **It also loses on qualifiers and validity:**
  - qualifier accuracy is 71% against the rules' 86%
  - 15 of its 120 outputs failed validation, against 3 of 60 on validation and 2 of 50 on the
    audit
- **It wins on refusing what can't be done.** It flags more unsupported labels (9 against 7)
  and reports more references absent from GNIS (26 against 17). This is useful for review, but
  it doesn't count toward correct proposals.

These are totals only. Per-record errors on the test are not examined, because doing so would
turn the test into development data.

## Latency

LLM p50 11.7 s and p95 20.9 s per record (Apple M1, 8 GB, warm, no retries), within the 30 s
and 90 s targets. The rules take milliseconds.

## What this means

- **The milestone question has an answer for this configuration:** a 4B local model with
  quote-only extraction and prompt v2 does **not** give 10 more points of correct proposals
  than a rules baseline sharing the same retrieval and geometry. Its gains on the audit and
  validation did not hold.
- **What the result does not cover:**
  - other models or sizes (2B, larger), a second LLM call, or a different prompt or extraction
    design
  - the parts of the project unrelated to the LLM: the gazetteer, uncertainty policy and review
    workflow serve both systems
- **The test split has now been scored once.** A later release needs its own declaration, and
  the result for this release stays published as it is.
- **Section 7 targets not measured** for this release: proposal correctness, coverage,
  containment and reviewer time. Feature extent is unknown, so neither system computes
  proposals.
- **One annotator.** The self-consistency re-annotation has not been done yet.
