# dev-4: scores against Claude's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 29 · reference_absent 13 · unsupported 8. Annotated types: named_feature 24 · distance_and_direction 14 · route_relative 4 · distance_only 2 · direction_only 2 · between_features 2 · itinerary 1 · admin_only 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 26/50 (52%) | 32/50 (64%) | 26/50 (52%) |
| Extraction passed validation | 50/50 (100%) | 47/50 (94%) | 50/50 (100%) |
| Critical interpretation exact | 18/50 (36%) | 25/50 (50%) | 18/50 (36%) |
| Reference top-1 acceptable (answerable) | 14/29 (48%) | 16/29 (55%) | 16/29 (55%) |
| Reference in top 5 (answerable) | 14/29 (48%) | 16/29 (55%) | 16/29 (55%) |
| **Correct proposal candidates** (answerable) | 9/29 (31%) | 14/29 (48%) | 10/29 (34%) |
| Computed proposals that are correct | 5/8 (62%) | 6/8 (75%) | 6/9 (67%) |
| Unsupported records flagged unsupported | 1/8 (12%) | 6/8 (75%) | 1/8 (12%) |
| References absent from GNIS reported absent | 8/13 (62%) | 9/13 (69%) | 8/13 (62%) |
| Place names read as no locality | 0 | 0 | 0 |
| Mean fields to correct per record | 2.2 | 1.86 | 2.22 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 8/50 (16%) | 8/50 (16%) | 9/50 (18%) |
| Computed proposals that are correct | 5/8 (62%) | 6/8 (75%) | 6/9 (67%) |
| Useful coverage (of answerable) | 5/29 (17%) | 6/29 (21%) | 6/29 (21%) |

**Paired, correct proposal candidates (LLM − rules):** +17% (95% bootstrap CI -3% to +38%); LLM-only 7, rules-only 2, exact sign test p = 0.1797.

**Paired, critical exact match (LLM − rules):** +14% (95% bootstrap CI -2% to +30%); LLM-only 13, rules-only 6, exact sign test p = 0.1671.

**Paired, correct proposal candidates (hybrid − rules):** +3% (95% bootstrap CI +0% to +10%); hybrid-only 1, rules-only 0, exact sign test p = 1.0.

**Paired, critical exact match (hybrid − rules):** +0% (95% bootstrap CI -8% to +8%); hybrid-only 2, rules-only 2, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 8 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 25/42 (60%) | 27/42 (64%) | 25/42 (60%) |
| Extraction passed validation | 42/42 (100%) | 39/42 (93%) | 42/42 (100%) |
| Critical interpretation exact | 17/42 (40%) | 21/42 (50%) | 17/42 (40%) |
| Reference top-1 acceptable (answerable) | 13/24 (54%) | 12/24 (50%) | 15/24 (62%) |
| Reference in top 5 (answerable) | 13/24 (54%) | 12/24 (50%) | 15/24 (62%) |
| **Correct proposal candidates** (answerable) | 9/24 (38%) | 11/24 (46%) | 10/24 (42%) |
| Computed proposals that are correct | 5/6 (83%) | 4/5 (80%) | 6/7 (86%) |
| Unsupported records flagged unsupported | 1/8 (12%) | 6/8 (75%) | 1/8 (12%) |
| References absent from GNIS reported absent | 7/10 (70%) | 7/10 (70%) | 7/10 (70%) |

Paired correct proposal candidates: +8% (CI -12% to +29%), p = 0.6875.

Paired correct proposal candidates (hybrid − rules): +4% (CI +0% to +12%), p = 1.0.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| admin_only | 0/0 | 0/0 | 0/0 |
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| distance_and_direction | 4/10 (40%) | 7/10 (70%) | 5/10 (50%) |
| distance_only | 1/2 (50%) | 1/2 (50%) | 1/2 (50%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 4/16 (25%) | 6/16 (38%) | 4/16 (25%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| G01 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| G02 | reference_absent | C− R−  | C− R−  | C− R−  |
| G03 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| G04 | answerable | C+ R−  | C− R+  | C− R+  |
| G05 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| G06 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| G07 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| G08 | unsupported | C− R−  | C− R−  | C− R−  |
| G09 | reference_absent | C− R−  | C− R−  | C− R−  |
| G10 | answerable | C− R+  | C+ R−  | C− R+  |
| G11 | unsupported | C− R+  | C− R+  | C− R+  |
| G12 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G13 | unsupported | C− R−  | C+ R−  | C− R−  |
| G14 | reference_absent | C− R−  | C+ R−  | C− R−  |
| G15 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| G16 | answerable | C+ R−  | C− R−  | C− R−  |
| G17 | reference_absent | C− R−  | C− R−  | C− R−  |
| G18 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| G19 | reference_absent | C− R−  | C− R−  | C− R−  |
| G20 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| G21 | answerable | C− R−  | C− R−  | C− R−  |
| G22 | answerable | C− R−  | C− R−  | C− R−  |
| G23 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| G24 | unsupported | C− R−  | C+ R+  | C+ R+  |
| G25 | answerable | C− R−  | C− R−  | C− R−  |
| G26 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G27 | answerable | C− R−  | C− R−  | C− R−  |
| G28 | unsupported | C− R−  | C− R−  | C− R−  |
| G29 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G30 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| G31 | unsupported | C− R−  | C+ R−  | C− R−  |
| G32 | unsupported | C− R−  | C+ R−  | C− R−  |
| G33 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G34 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G35 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| G36 | answerable | C− R−  | C− R+  | C− R−  |
| G37 | unsupported | C− R+  | C− R−  | C− R+  |
| G38 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| G39 | answerable | C− R+  | C− R−  | C− R+  |
| G40 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| G41 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G42 | answerable | C− R−  | C− R−  | C− R−  |
| G43 | answerable | C− R−  | C− R−  | C− R−  |
| G44 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| G45 | answerable | C− R−  | C− R−  | C− R−  |
| G46 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| G47 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| G48 | answerable | C− R−  | C− R−  | C− R−  |
| G49 | reference_absent | C− R−  | C− R−  | C− R−  |
| G50 | answerable | C− R+  | C+ R+ ✓ | C− R+  |

</details>
