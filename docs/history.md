# Development history: the feasibility audit and what followed

This section was the README's account of the first milestone, from the 50-record audit to the
three locked-test releases and the dev samples after them. It is kept here unchanged except for
links. The current one-page summary is [results.md](results.md).

The first milestone is decided on real labels, not synthetic ones. Every record in the snapshot
is accounted for:

```text
311,988  GBIF records (CU Herbarium, DOI 10.15468/dl.hqxjjf)
206,444    excluded, each with a reason (other state, no state, withheld, ...)
105,544  eligible: Colorado, not withheld, real locality text
 40,444  distinct locality groups (same wording, same county)
     50  audit sample: seeded, one record per group → eval/audit/
```

Both systems have run on the sample: the rules baseline
([report](../eval/reports/audit-50-rules-1.md), [findings](../eval/reports/audit-50-rules-1-findings.md))
and Qwen3.5-4B ([report](../eval/reports/audit-50-llm-x1g2-qwen3.5-4b-q4km.md),
[findings](../eval/reports/audit-50-llm-x1g2-qwen3.5-4b-q4km-findings.md)), then both were scored
against a blind annotation of every record ([worksheet](../eval/audit/worksheet.csv),
[scores](../eval/reports/audit-50-score.md)).

> **Answer: yes for rules with an LLM fallback, no for the LLM alone.** Both were scored on
> the 120-record **locked test**, each under a declaration pushed before its run. The LLM
> alone gives **15 of 56** correct proposal candidates against the rules' **19** (release 1,
> −7 points). `hybrid-1` runs the rules and calls the LLM only where they reach no gazetteer
> candidate. It gives **25 of 56: +10.7 points** (95% CI +3.6 to +19.6, p = 0.031), just over
> the +10 point target ([release 2](../eval/reports/test-release-2.md)). With the current rules
> (rules-6) both gain 3: **hybrid-1 28 against rules 22 of 56, +10.7 points again** (same CI,
> 6 gained, 0 lost; [release 3](../eval/reports/test-release-3.md)).

| Correct proposal candidates | Rules | LLM v2 alone | **hybrid-1** |
|---|---|---|---|
| **Locked test, release 3** (rules-6; 56 answerable) | 22 (39%) | 18 (32%) | **28 (50%)** |
| Locked test, releases 1–2 (rules-1) | 19 (34%) | 15 (27%) | 25 (45%) |
| test-2, fresh sample (Claude-annotated, not independent; 80 answerable) | 34 (43%) | 31 (39%) | 43 (54%) |
| Validation (held out, now read; 32) | 13 (41%) | 15 (47%) | 16 (50%) |
| Audit (dev data; 31) | 14 (45%) | 12 (39%) | 14 (45%) |
| dev-1 (v2 was written on it; 29) | 16 (55%) | 18 (62%) | 18 (62%) |

**Against GEOLocate** (read samples, plan pinned before any query; [findings](../eval/reports/geolocate-findings.md)):
points within 5 km of the position each annotation supports. On the owner-annotated samples:
GEOLocate 58, rules 54, LLM 59, hybrid-1 61 of 85. GEOLocate gives a point for 82 of the 85,
but more of its points are wrong; ours abstain more often. Positions come from GNIS, which favours
our systems at short distances.

The rows below the test are the release-2 configuration; the rules changes that follow led to
release 3.

**Since release 2: rules-2.** The rules now read "air mi", spelled-out numbers before a unit
and a bare "ca" ([findings](../eval/reports/rules-2-findings.md)). On the audit they gain 3
records (14 → 17), and hybrid-1 also goes 14 → 17. These gains are in-sample, since the fixed
labels came from the audit findings. dev-1 and validation are unchanged, and no record got
worse. The locked test has not been scored with rules-2.

**Then rules-3.** It fixes the two errors behind the incorrect regions
([findings](../eval/reports/rules-3-findings.md)):
- **Spaced directions:** "10 mi. n. w. Salida" is no longer cut to "10 mi. n".
- **The collecting place:** a named place written right before an offset is read as where the
  specimen was collected, when a position word puts it there ("S. slope of Thunder Mt.,
  16 miles N of Grand Lake") or the label opens with it and the offset is at least a mile
  ("Vernal Mesa, 15 mi. east of Montrose").

On these samples, correct candidates rise from 46 to 50 for the rules and from 51 to 55 for
hybrid-1, and no record gets worse. The gains are in-sample, because the rule was written
knowing these labels.

**Then rules-4.** rules-3 also let a broad feature replace a precise offset: "Arkansas River,
5 mi E of Salida" became a 1,500 km circle. Streams, ranges, parks and forests now keep the
offset ([findings](../eval/reports/rules-4-findings.md)). No score changes on these samples, because
none of them has such a label, but 360 of the 1,323 unread groups where rules-3 replaced an offset
go back to it.

**Then rules-5.** A distance range ("ca 20-21 air mi") was read as its second number, a silent
false precision. Ranges are now asked about: the distance is missing and an open question names
the range ([findings](../eval/reports/rules-5-findings.md)). On the read samples only A23 changes
(now correct, in-sample: rules 50 → 51, hybrid-1 55 → 56 of 92). On 38,272 unread groups,
217 ranges read as one number now ask instead. rules-6 adds "2 or 3 mi" ranges, which rules-5
still read as one number; no read or unread label outside dev-3 and the held-out groups changes
([findings](../eval/reports/rules-6-findings.md)).

**On fresh data: dev-2.** 50 new groups were annotated by Claude, at the owner's request, and
then scored once by a plan pushed before any system ran ([plan](../eval/dev/dev-2/scoring-plan.md),
[findings](../eval/reports/dev-2-findings.md)). Correct candidates of 36 answerable:

| rules-4 | LLM v2 | hybrid-1 |
|---|---|---|
| 19 (53%) | 17 (47%) | **21 (58%)** |

- **The overall picture holds on unseen labels.** hybrid-1 leads the rules by 2 records (CI +0
  to +14 points) and is never behind, and the LLM alone is not better than the rules. The rates
  are close to the in-sample rates, so there is no sign the rules were overfitted.
- **This is weaker evidence than the owner's blind sets.** Claude also wrote the rules, so the
  annotations are not independent of them, and the comparison may lean toward the rules.
- **rules-3 and rules-4 are still untested.** Only 3 dev-2 labels have a place right before an
  offset. rules-4 changes no reading, and rules-3 changes one (E29) and no score.
- **One label is a repeat:** E40, "Hoosier Pass.", has the same text as validation's V021,
  under a different county. Without it: 18 / 16 / 20 of 35. No locked-test text repeats a read
  one.

**Next on fresh data: dev-3.** 50 more groups, 35 of them "place, offset" labels (a clause, then
an offset such as "Vernal Mesa, 15 mi. E of Montrose"), the case rules-3 and rules-4 decide.
Samples now also skip any label whose wording repeats a read or held-out one under another
county ([how it was drawn](../eval/dev/README.md#dev-3)). Claude annotated it, so, as with dev-2,
it is not an independent check of rules Claude wrote. Scored once by a plan pushed first
([plan](../eval/dev/dev-3/scoring-plan.md), [findings](../eval/reports/dev-3-findings.md)), correct
candidates of 32 answerable:

| rules-6 | LLM v2 | hybrid-1 |
|---|---|---|
| 11 (34%) | 14 (44%) | **14 (44%)** |

- **hybrid-1 again leads the rules** (+3, CI +0 to +22 points, never behind), on harder labels
  than dev-2.
- **The place-or-offset rules show no gain.** Replaying rules-2 to rules-6 on the 24 answerable
  place-offset records: 6, 7, 6, 6, 6 correct. rules-3 finds the place in two labels, takes a
  broad region over the offset in one, and cuts a place at a sentence break in another; rules-4
  then reverts one of rules-3's gains. The in-sample gains (rules 46 → 50) did not carry over.
- **No full region is correct:** the 2 computed regions come from wrong readings.

**dev-4,** 50 more groups with 35 "place, offset" labels. It was drawn for the owner to annotate;
the owner then had Claude annotate it, so it is the same weak kind of evidence as dev-3. Scored
once by a plan pushed first ([plan](../eval/dev/dev-4/scoring-plan.md),
[findings](../eval/reports/dev-4-findings.md)), correct candidates of 29 answerable: rules-6 9,
**LLM 14**, hybrid-1 10.

- **The place-or-offset rules lose ground again:** rules-2 to rules-6 give 6, 6, 5, 5, 5 of 22
  place-offset records. Over dev-3 and dev-4 they gain 2 and lose 3.
- **The LLM reads those labels better,** and rules-first hybrid-1 never asks it when the rules
  reach any candidate (6 such records here). Over dev-2 to dev-4 the LLM and hybrid-1 tie at 45
  of 97, against 39 for the rules.
- **All 3 full regions are wrong** (offsets from Boulder and Grand Lake).

**A smaller model, Qwen3.5-2B,** is about 4× faster but misquotes labels: 51 of 160 extractions
fail validation. On dev and validation data it gives 27 correct candidates of 92 on its own,
against 46 for 4B. As hybrid-1's fallback it still reaches 49 against 4B's 51
([findings](../eval/reports/qwen3.5-2b-findings.md)).

**Full regions, with 67 measured extents and rules-6** (findings for
[extents](../eval/reports/extents-findings.md), [batch 4](../eval/reports/extents-batch-4-findings.md),
[rules-3](../eval/reports/rules-3-findings.md), [rules-4](../eval/reports/rules-4-findings.md) and
[rules-5](../eval/reports/rules-5-findings.md)):

| | Rules `rules-6` | LLM | **Hybrid `hybrid-1`** | Target |
|---|---|---|---|---|
| *Read samples (audit, dev-1, validation: 92 answerable)* | | | | |
| Regions computed | 32 | 33 | **35** | |
| … correct (precision) | 29 (91%) | 28 (85%) | **32 (91%)** | ≥ 95% |
| Useful coverage | 29 (32%) | 28 (30%) | **32 (35%)** | ≥ 70% |
| *dev-2, unseen labels (36 answerable)* | | | | |
| Regions computed | 10 | 8 | **11** | |
| … correct (precision) | 9 (90%) | 7 (88%) | **10 (91%)** | ≥ 95% |
| Useful coverage | 9 (25%) | 7 (19%) | **10 (28%)** | ≥ 70% |

- **Unseen labels behave like the read ones.** dev-2's 12 new extents took its regions from 2
  to 11, 10 of them correct (median correct radius 3.2 km).
- **More extents expose reading errors.** Every incorrect region that batch 4 added was already
  a wrong reading that used to stop at `needs_information`: an offset from Boulder chosen over
  the place named later (Rocky Flats ×2, Bluebell Canyon), and a range, "20-21 air mi", that the
  rules read as exactly 21 mi. rules-5 fixes the range. A recheck then sent Mount Shavano back
  to pending (no defensible edge), which removes one correct region (V013). Precision on the
  read samples is 91% (97% before batch 4). The target needs better readings, not more extents.
- **What blocks the rest:** extents with no defensible edge (towns with no mapped limit, long
  slopes, canyon passes) and direction-only labels with no distance.
- **"Correct" tests the interpretation and the reference,** not the size of the radius: one
  correct dev-2 region is 39 km.

> [!WARNING]
> **The 91% above is inflated by how extents were chosen.** Extents were measured only for the
> features the annotations accepted, so a wrong pick could never get a region.
> [Derived extents](../data/extents/README.md) give every feature with a Census place polygon or an
> NHD geometry a region (11,993 features, computed from the pinned snapshots; opt-in with
> `--derived-extents`). With them, hybrid-1's regions are 52 of which 33 are correct (63%) on the
> owner-annotated read samples. On Claude-annotated dev-3 and dev-4, mostly unmeasured features,
> they are 36 of which 14 are correct (39%), with useful coverage 0 → 23%
> ([findings](../eval/reports/derived-extents-findings.md)). The derived extents match hand
> measurements (median ratio 0.98 over 45 features). What fails is choosing the reference: a
> specific collecting place is named and missed, and "N mi of Town" wins.

**How to read the "yes":**
- **The margin is one record.** +10 points of 56 is 5.6 records, and the hybrid gains 6 while
  losing none.
- **The interval includes gains below 10 points.** It shows the hybrid beats the rules, not
  that the true gain is at least 10.
- **The test was scored twice.** The hybrid idea came partly from release 1's totals, though
  its rule was chosen on dev data only ([findings](../eval/reports/hybrid-1-findings.md)).
- **The gain is retrieval.** The LLM reaches a gazetteer entry for names the rules can't
  parse: top-1 acceptable 33 of 56 against 25. It calls the model on 39% of records.
- **Proposals are measured on dev and validation data only.** The locked test has no
  measured extents, so the target's "comparable precision" can't be checked there (see below).

<sub>Release 1, LLM alone: retrieval is level on the test (an acceptable reference ranked first
in 25 of 56 for both). The LLM loses on interpretation: direction-only labels (0 of 7 against 5), qualifiers (71%
against 86% right) and 15 of 120 outputs rejected by validation. It flags more unsupported
labels (9 against 7 of 16) and more references absent from GNIS (26 against 17 of 48). LLM
latency p50 11.7 s, p95 20.9 s per record (Apple M1, 8 GB). Release 2, hybrid-1: it keeps the
rules' direction-only, qualifier and validity results, but reports fewer references absent
from GNIS (14 against 17 of 48), and model time is 39% of the LLM alone.</sub>

<details>
<summary><b>The audit in detail</b> (dev data, prompt v1 and v2)</summary>

| Scored against annotations | Rules | LLM v1 | LLM v2 |
|---|---|---|---|
| **Correct proposal candidates, with core retrieval** (of 31 answerable) | **14 (45%)** | – | **12 (39%)** |
| Correct proposal candidates, before core retrieval | 13 (42%) | 9 (29%) | 10 (32%) |
| Relation read correctly (of 50) | 26 (52%) | 30 (60%) | 30 (60%) |
| Critical interpretation exact (of 50) | 24 (48%) | 20 (40%) | 22 (44%) |
| Acceptable reference ranked first (of 31) | 16 (52%) | 11 (36%) | 12 (39%) |
| Distance-and-direction labels right (of 9 answerable) | 5 | 7 | 6 |
| Named-place labels right (of 20 answerable) | 7 | 2 | 4 |
| Place names read as "no locality" | 0 | 7 | 1 |
| Unsupported labels flagged unsupported (of 4) | 0 | 4 | 4 |
| Mean fields a curator must correct per record | 1.88 | 2.08 | 1.82 |

<sub>A correct proposal candidate becomes a correct proposal once the feature extent is supplied.
Rows other than the first two are before core retrieval. Excluding the 10 rows the annotator
marked unsure, with core retrieval: rules 12/24, v2 10/24. v2 against the rules: −7 points
(95% CI −26 to +13, p = 0.75). The audit records are
dev data and too few for the final comparison, which uses the locked benchmark.</sub>

</details>

<details>
<summary><b>System outcomes before scoring</b></summary>

| On 50 real labels | Rules `rules-1` | LLM `llm-x1g2` (Qwen3.5-4B Q4_K_M) |
|---|---|---|
| Relation read | named feature 22 · distance + direction 14 · direction only 10 · other 2 · distance only 1 · route 1 | distance + direction 24 · named feature 13 · no locality 7 · route 5 · itinerary 1 |
| Rejected by validation | 0 | 9 (inexact quotes, contradictions, unparseable numbers) |
| Retrieval | candidates found 33 · absent from GNIS 14 · no reference 3 | candidates found 22 · absent from GNIS 12 · no reference 7 |
| Proposal | needs information 46 · unsupported 3 · computed 1 | needs information 27 · unsupported 13 · computed 1 |
| Time per record | milliseconds | p50 10.2 s · p95 14.7 s (Apple M1, 8 GB) |

</details>

<details>
<summary><b>What the audit already shows</b></summary>

- **Real labels are multi-clause.** Many chain a forest, a range, a road and an offset in one
  string. The rules read one clause, and not always the most specific one.
- **Unknown extent is the main blocker.** Most references are towns, summits and streams with a
  single GNIS point, so honest proposals ask for an extent. With 67 of the store's 115 rows
  measured, 11 audit records get a full region under the rules (9 of them correct).
- **Rules gaps with names:** "air mi", spelled-out numbers, ranges, road designations read as
  places, and leading words ("Above", "Near") absorbed into names. rules-2 fixes "air mi" and
  spelled-out numbers. rules-3 fixes spaced directions ("n. w.") and prefers a named collecting
  place written before an offset, rules-4 keeps the offset when that place is broad, and rules-5
  asks about distance ranges instead of reading their second number.
- **The LLM reads what the rules miss, and makes its own errors:** it handles "air mi",
  separates "Above"/"Near" from names and flags more route descriptions. It also called 7 labels
  that name a place "no locality", and 9 of its outputs were rejected by validation (as designed).
- **A grammar lesson:** the first LLM run failed 5 times because the decoding grammar allowed
  combinations that validation rejects, and greedy retries repeat themselves. The grammar now
  admits only valid combinations. The failed run is [kept](../eval/reports/audit-50-llm-x1-qwen3.5-4b-q4km.md).
- **Prompt v2 was built on fresh records.** A stratified dev sample, [`dev-1`](../eval/dev/),
  over-represents the failing label shapes, so the audit stays a check. Every group read in
  development is recorded in [`eval/viewed-groups.json`](../eval/viewed-groups.json) and excluded
  from any held-out split. v2 fixed the "no locality" error but barely moved the audit score.
- **Retrieval was the bottleneck.** A core-match tier now sets generic words aside ("Mt.
  Zenobia" finds GNIS "Zenobia Peak"; "Lower Piney Lake" finds "Piney Lake" but never "Upper
  Piney Lake"). It fixed the 2 audit records it was designed from, for both systems, and changed
  nothing on dev-1: no regressions, but no out-of-sample evidence yet.
- **A benchmark nobody had read.** Validation (60) and a locked test (120) are drawn from
  groups untouched by development, grouped by collecting event so that no trip spans two
  splits ([how](../eval/benchmark/)).
- **On validation the LLM led, narrowly.** It picks the right reference more often (top-1 18
  vs 15 of 32) but reads relations no better (critical interpretation 23 vs 25 of 60). The most
  common shared miss is the one prompt v2 targeted: "Vernal Mesa, 15 mi. east of Montrose" read
  as an offset from Montrose instead of as Vernal Mesa (5 records).
- **On the locked test it did not.** The lead seen on validation reversed to −7 points on 120
  unseen records, which is why the milestone is decided on the locked split and not on
  validation.
- **Supplied counties are not always counties.** 2,710 eligible records carry `Unknown`,
  `Unknown-E` or two counties (`Gunnison/Pitkin`). Retrieval now treats placeholders as
  missing, so the label's own county is used, and lets a two-county value match either county
  ([findings](../eval/reports/county-context-findings.md)). This changed no result on the dev or
  validation samples.

</details>
