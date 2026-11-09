# dev-2: scores against Claude's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 36 · reference_absent 13 · unsupported 1. Annotated types: named_feature 38 · distance_and_direction 8 · direction_only 3 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 34/50 (68%) | 33/50 (66%) | 35/50 (70%) |
| Extraction passed validation | 50/50 (100%) | 44/50 (88%) | 50/50 (100%) |
| Critical interpretation exact | 32/50 (64%) | 29/50 (58%) | 33/50 (66%) |
| Reference top-1 acceptable (answerable) | 20/36 (56%) | 18/36 (50%) | 22/36 (61%) |
| Reference in top 5 (answerable) | 21/36 (58%) | 18/36 (50%) | 23/36 (64%) |
| **Correct proposal candidates** (answerable) | 19/36 (53%) | 17/36 (47%) | 21/36 (58%) |
| Computed proposals that are correct | 9/13 (69%) | 6/8 (75%) | 9/13 (69%) |
| Unsupported records flagged unsupported | 0/1 (0%) | 1/1 (100%) | 0/1 (0%) |
| References absent from GNIS reported absent | 2/13 (15%) | 7/13 (54%) | 2/13 (15%) |
| Place names read as no locality | 0 | 1 | 0 |
| Mean fields to correct per record | 1.16 | 1.62 | 1.04 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 13/50 (26%) | 8/50 (16%) | 13/50 (26%) |
| Computed proposals that are correct | 9/13 (69%) | 6/8 (75%) | 9/13 (69%) |
| Useful coverage (of answerable) | 9/36 (25%) | 6/36 (17%) | 9/36 (25%) |

**Paired, correct proposal candidates (LLM − rules):** -6% (95% bootstrap CI -25% to +14%); LLM-only 5, rules-only 7, exact sign test p = 0.7744.

**Paired, critical exact match (LLM − rules):** -6% (95% bootstrap CI -22% to +10%); LLM-only 7, rules-only 10, exact sign test p = 0.6291.

**Paired, correct proposal candidates (hybrid − rules):** +6% (95% bootstrap CI +0% to +14%); hybrid-only 2, rules-only 0, exact sign test p = 0.5.

**Paired, critical exact match (hybrid − rules):** +2% (95% bootstrap CI +0% to +6%); hybrid-only 1, rules-only 0, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 8 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 32/42 (76%) | 32/42 (76%) | 32/42 (76%) |
| Extraction passed validation | 42/42 (100%) | 39/42 (93%) | 42/42 (100%) |
| Critical interpretation exact | 31/42 (74%) | 28/42 (67%) | 31/42 (74%) |
| Reference top-1 acceptable (answerable) | 19/31 (61%) | 17/31 (55%) | 20/31 (64%) |
| Reference in top 5 (answerable) | 20/31 (64%) | 17/31 (55%) | 21/31 (68%) |
| **Correct proposal candidates** (answerable) | 19/31 (61%) | 16/31 (52%) | 20/31 (64%) |
| Computed proposals that are correct | 9/12 (75%) | 6/7 (86%) | 9/12 (75%) |
| Unsupported records flagged unsupported | 0/1 (0%) | 1/1 (100%) | 0/1 (0%) |
| References absent from GNIS reported absent | 1/10 (10%) | 6/10 (60%) | 1/10 (10%) |

Paired correct proposal candidates: -10% (CI -29% to +10%), p = 0.5488.

Paired correct proposal candidates (hybrid − rules): +3% (CI +0% to +10%), p = 1.0.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| direction_only | 2/2 (100%) | 1/2 (50%) | 2/2 (100%) |
| distance_and_direction | 4/8 (50%) | 5/8 (62%) | 5/8 (62%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 13/26 (50%) | 11/26 (42%) | 14/26 (54%) |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| E01 | answerable | C− R−  | C− R−  | C− R−  |
| E02 | answerable | C− R−  | C− R−  | C− R−  |
| E03 | reference_absent | C− R−  | C− R−  | C− R−  |
| E04 | reference_absent | C− R−  | C+ R−  | C− R−  |
| E05 | answerable | C− R+  | C− R−  | C− R+  |
| E06 | answerable | C− R−  | C− R−  | C− R−  |
| E07 | answerable | C+ R+ ✓ | C+ R−  | C+ R+ ✓ |
| E08 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E09 | answerable | C− R−  | C− R−  | C− R−  |
| E10 | reference_absent | C− R−  | C+ R−  | C− R−  |
| E11 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| E12 | unsupported | C− R−  | C− R−  | C− R−  |
| E13 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| E14 | answerable | C+ R−  | C− R−  | C+ R−  |
| E15 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| E16 | reference_absent | C− R−  | C− R−  | C− R−  |
| E17 | answerable | C− R−  | C+ R−  | C− R−  |
| E18 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| E19 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E20 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| E21 | answerable | C+ R−  | C+ R−  | C+ R−  |
| E22 | answerable | C+ R−  | C+ R+ ✓ | C+ R−  |
| E23 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| E24 | answerable | C+ R+ ✓ | C+ R−  | C+ R+ ✓ |
| E25 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| E26 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| E27 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E28 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E29 | answerable | C+ R−  | C+ R−  | C+ R−  |
| E30 | answerable | C+ R−  | C− R−  | C+ R−  |
| E31 | reference_absent | C− R−  | C− R−  | C− R−  |
| E32 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| E33 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E34 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| E35 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E36 | reference_absent | C− R−  | C+ R−  | C− R−  |
| E37 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| E38 | answerable | C− R−  | C− R−  | C− R−  |
| E39 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E40 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E41 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| E42 | answerable | C+ R−  | C+ R−  | C+ R−  |
| E43 | answerable | C+ R−  | C+ R+ ✓ | C+ R−  |
| E44 | reference_absent | C− R−  | C− R−  | C− R−  |
| E45 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E46 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E47 | reference_absent | C− R−  | C+ R−  | C− R−  |
| E48 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| E49 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| E50 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |

</details>
