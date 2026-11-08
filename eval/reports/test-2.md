# test-2: v0.1.0 on a fresh held-out sample (Claude-annotated)

The locked test had been scored three times, with rules changes in between, so test-2 was drawn
for v0.1.0 from labels nobody had read
([declaration](../benchmark/declaration-test-2.json), pushed before annotation). At the owner's
request **Claude annotated it, not the owner**
([amendment 1](../benchmark/declaration-test-2-amendment-1.json), pushed before any system
ran).

- **Records:** 120 new groups. One group per collecting-event component, after excluding
  everything viewed or reserved, repeated wording, and their components. The 20 blind validation
  repeats are scored separately (below).
- **Systems:** `rules-6`, `llm-x2g2-qwen3.5-4b-q4km` (prompt v2) and `hybrid-1`. These are the
  v0.1.0 pipeline, run once at 2733648.
  - LLM completion cache off, native llama-server.
  - Run 2026-11-08, 15:43–16:05 UTC.
- **Published here:** totals only. Per-record outputs stay in `eval/benchmark/test-2/reports/`.

> **Not independent evidence.** Claude also wrote rules-3 to rules-6 and much of the pipeline,
> so these annotations are not independent of the systems compared, as with dev-2 to dev-4. The
> independent evidence remains locked-test releases 1–3, annotated by the owner.

## Answer under the declared rule: yes

| Correct proposal candidates (of 80 answerable) | Rules (rules-6) | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| test-2 (Claude-annotated) | 34 (43%) | 31 (39%) | **43 (54%)** |
| Locked test, release 3 (owner-annotated, of 56) | 22 (39%) | 18 (32%) | 28 (50%) |

**hybrid-1 − rules-6: +11.3 points (95% bootstrap CI +5.0 to +18.8; sign test p = 0.004).**
9 records are correct only for the hybrid, and none only for the rules. The rule says yes when
the difference is at least +10 points and the lower bound is above zero.

- **Excluding the 27 rows with an unsure mark:** rules 32, hybrid 39 of 65, +10.8 points
  (CI +3.1 to +18.5, p = 0.016). Also yes.
- **The stated expectation** was +5 to +11 points, with "yes" and "not shown" both plausible.
  The result is at the top of that range.
- **LLM alone against the rules:** 31 against 34, −3.7 points (CI −15 to +8). As on the locked
  test, the LLM alone is not better than the rules.

## The sample differs from the locked test

| Category (of 120) | test-2 (Claude) | Locked test (owner) |
|---|---|---|
| Answerable | **80** | 56 |
| Reference absent from GNIS | **27** | 48 |
| Unsupported | 13 | 16 |

**The 20 repeats suggest much of this is the annotator.** On the repeats, the owner marked 8
references absent from GNIS and Claude marked 4; Claude marked 13 answerable, the owner 11.

- **What Claude does differently:** it finds an acceptable GNIS feature more often where the
  owner judged the reference absent.
- **Why it matters:** on test-2, records the owner might have called "absent" count as
  answerable, so the primary metric covers a different mix of records than on the locked test.
- **What the totals can't say:** whether that favours the hybrid or the rules. That would need
  per-record reading, which would turn test-2 into development data.

## Every measure, test-2

| Of 120 records unless stated | Rules | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| Correct proposal candidates (of 80) | 34 | 31 | **43** |
| Critical interpretation exact | 71 | 57 | 68 |
| Relation read correctly | 75 | 72 | 76 |
| Distance / unit / direction right | 95 / 96 / 90 | 92 / 92 / 85 | 97 / 97 / 91 |
| Qualifiers right | 106 | 92 | 104 |
| Extraction passed validation | 120 | 108 | 120 |
| Acceptable reference ranked first (of 80) | 37 | 47 | 53 |
| Candidate recall@5 (of 80) | 37 | 48 | 53 |
| Unsupported flagged unsupported (of 13) | 4 | 9 | 5 |
| References absent from GNIS reported absent (of 27) | 12 | 16 | 11 |
| Place names read as "no locality" | 0 | 2 | 0 |
| Mean fields a curator must correct | 1.51 | 1.66 | 1.35 |

By annotated type (correct candidates, answerable):

| Type | Rules | LLM | hybrid-1 |
|---|---|---|---|
| named feature (44) | 12 | 16 | 18 |
| distance and direction (23) | 14 | 13 | 17 |
| direction only (12) | 8 | 2 | 8 |
| distance only (1) | 0 | 0 | 0 |

**Reading:**
- **The hybrid's gain is retrieval again:** top-1 53 against the rules' 37. The LLM's quote
  reaches GNIS where the rules' name does not.
- **Critical interpretation is slightly worse for the hybrid** (68 against 71, −2.5 points,
  CI −7.5 to +2.5: 3 better, 6 worse). Its qualifiers are worse (104 against 106), while
  relation, distance, unit and direction are level or better. Which records cause this was not
  examined.
- **Direction-only labels stay the LLM's weak spot** (2 of 12). The hybrid keeps the rules
  there.

## Cost

- **The model was called on 51 of 120 records** and skipped on 69. 21 records use the LLM's
  result.
- **Model time:** 535 s for the hybrid against 1,301 s for the LLM alone (41%).
- **Latency per call:** p50 10.4 s, p95 17.3 s (Apple M1, 8 GB, warm server, cache off).

## Inter-annotator agreement: Claude against the owner, 20 blind repeats

These are 20 validation records, mixed into test-2 blind and annotated by Claude. They are
compared with the owner's original validation annotations, field by field. Three of them
(H021, H039, H057) were recognised from validation work, so agreement is also given without
them.

| Field agrees | All 20 | Without the 3 recognised (17) |
|---|---|---|
| Description type | 16 | 13 |
| Supported | 18 | 15 |
| Acceptable GNIS IDs (as a set, or both "absent") | 16 | 13 |
| Distance | 17 | 14 |
| Unit | 18 | 15 |
| Direction | 17 | 14 |
| Qualifiers | 18 | 15 |
| Category (answerable / absent / unsupported) | 16 | 13 |
| **Every field** | **12** | **9** |

- **Records the two annotate identically in every field:** 12 of 20, or 9 of 17 without the
  recognised three. Single fields agree on 13–18 of 20.
- **Most disagreement is about the reference:** whether it is in GNIS, and which IDs are
  acceptable. That matches the category shift above.
- **The repeats measure agreement between two annotators,** not the owner's self-consistency,
  which was the declaration's original purpose (amendment 1). The owner's self-consistency is
  still unmeasured.

## What this means

- **Under the declared rule test-2 says yes,** with a larger margin than the locked test
  (+11.3 points, 9 gained, 0 lost).
- **It is weak evidence.** The annotator also wrote the rules, and labels more references as
  findable than the owner does. Annotator agreement is moderate: every field agrees on 12 of 20.
- **The independent claim still rests on the locked test,** at the minimum margin.
- **A stronger claim would need the owner to annotate test-2 blind.** It has now been scored, so
  such an annotation would no longer be blind to these totals.
