# dev-1: scores against the owner's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 29 · reference_absent 17 · unsupported 4. Annotated types: named_feature 34 · distance_and_direction 7 · direction_only 5 · route_relative 2 · between_features 1 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 40/50 (80%) | 37/50 (74%) | 40/50 (80%) |
| Extraction passed validation | 50/50 (100%) | 46/50 (92%) | 50/50 (100%) |
| Critical interpretation exact | 35/50 (70%) | 30/50 (60%) | 35/50 (70%) |
| Reference top-1 acceptable (answerable) | 17/29 (59%) | 20/29 (69%) | 19/29 (66%) |
| Reference in top 5 (answerable) | 18/29 (62%) | 20/29 (69%) | 20/29 (69%) |
| **Correct proposal candidates** (answerable) | 17/29 (59%) | 18/29 (62%) | 19/29 (66%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/4 (75%) | 2/4 (50%) | 3/4 (75%) |
| References absent from GNIS reported absent | 9/17 (53%) | 13/17 (76%) | 9/17 (53%) |
| Place names read as no locality | 0 | 1 | 0 |
| Mean fields to correct per record | 0.88 | 1.16 | 0.86 |

**Paired, correct proposal candidates (LLM − rules):** +3% (95% bootstrap CI -10% to +17%); LLM-only 3, rules-only 2, exact sign test p = 1.0.

**Paired, critical exact match (LLM − rules):** -10% (95% bootstrap CI -22% to +2%); LLM-only 2, rules-only 7, exact sign test p = 0.1797.

**Paired, correct proposal candidates (hybrid − rules):** +7% (95% bootstrap CI +0% to +17%); hybrid-only 2, rules-only 0, exact sign test p = 0.5.

**Paired, critical exact match (hybrid − rules):** +0% (95% bootstrap CI +0% to +0%); hybrid-only 0, rules-only 0, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 9 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 34/41 (83%) | 32/41 (78%) | 34/41 (83%) |
| Extraction passed validation | 41/41 (100%) | 37/41 (90%) | 41/41 (100%) |
| Critical interpretation exact | 30/41 (73%) | 26/41 (63%) | 30/41 (73%) |
| Reference top-1 acceptable (answerable) | 14/25 (56%) | 17/25 (68%) | 16/25 (64%) |
| Reference in top 5 (answerable) | 15/25 (60%) | 17/25 (68%) | 17/25 (68%) |
| **Correct proposal candidates** (answerable) | 14/25 (56%) | 16/25 (64%) | 16/25 (64%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/2 (100%) | 1/2 (50%) | 2/2 (100%) |
| References absent from GNIS reported absent | 8/14 (57%) | 12/14 (86%) | 8/14 (57%) |

Paired correct proposal candidates: +8% (CI -8% to +24%), p = 0.625.

Paired correct proposal candidates (hybrid − rules): +8% (CI +0% to +20%), p = 0.5.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 1/2 (50%) | 1/2 (50%) | 1/2 (50%) |
| distance_and_direction | 4/5 (80%) | 4/5 (80%) | 4/5 (80%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 12/22 (55%) | 13/22 (59%) | 14/22 (64%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| D01 | answerable | C− R−  | C− R−  | C− R−  |
| D02 | unsupported | C+ R−  | C− R−  | C+ R−  |
| D03 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| D04 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D05 | answerable | C− R−  | C+ R−  | C− R−  |
| D06 | reference_absent | C− R−  | C− R−  | C− R−  |
| D07 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| D08 | unsupported | C− R−  | C− R−  | C− R−  |
| D09 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| D10 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D11 | answerable | C+ R+ ✓ | C+ R−  | C+ R+ ✓ |
| D12 | reference_absent | C− R−  | C− R−  | C− R−  |
| D13 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D14 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D15 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D16 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D17 | answerable | C+ R−  | C− R−  | C+ R−  |
| D18 | reference_absent | C− R−  | C− R−  | C− R−  |
| D19 | unsupported | C− R−  | C− R−  | C− R−  |
| D20 | answerable | C+ R−  | C− R−  | C+ R−  |
| D21 | answerable | C− R−  | C− R+  | C− R−  |
| D22 | reference_absent | C− R−  | C− R−  | C− R−  |
| D23 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| D24 | reference_absent | C− R−  | C− R−  | C− R−  |
| D25 | reference_absent | C− R−  | C− R−  | C− R−  |
| D26 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D27 | answerable | C− R−  | C− R−  | C− R−  |
| D28 | unsupported | C− R−  | C− R+  | C− R+  |
| D29 | answerable | C+ R−  | C− R−  | C+ R−  |
| D30 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| D31 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D32 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D33 | answerable | C+ R−  | C+ R−  | C+ R−  |
| D34 | reference_absent | C− R−  | C− R−  | C− R−  |
| D35 | answerable | C+ R−  | C+ R−  | C+ R−  |
| D36 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D37 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D38 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D39 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D40 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D41 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D42 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D43 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D44 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| D45 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| D46 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D47 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D48 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D49 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| D50 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |

</details>
