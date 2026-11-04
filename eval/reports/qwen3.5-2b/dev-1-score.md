# dev-1: scores against the owner's annotations

rules `rules-2` · llm `llm-x2g2-qwen3.5-2b-q4km` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 29 · reference_absent 17 · unsupported 4. Annotated types: named_feature 34 · distance_and_direction 7 · direction_only 5 · route_relative 2 · between_features 1 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 39/50 (78%) | 39/50 (78%) |
| Extraction passed validation | 50/50 (100%) | 37/50 (74%) |
| Critical interpretation exact | 34/50 (68%) | 27/50 (54%) |
| Reference top-1 acceptable (answerable) | 16/29 (55%) | 18/29 (62%) |
| Reference in top 5 (answerable) | 17/29 (59%) | 18/29 (62%) |
| **Correct proposal candidates** (answerable) | 16/29 (55%) | 16/29 (55%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/4 (75%) | 1/4 (25%) |
| References absent from GNIS reported absent | 9/17 (53%) | 10/17 (59%) |
| Place names read as no locality | 0 | 0 |
| Mean fields to correct per record | 1.0 | 1.64 |

**Paired, correct proposal candidates (LLM − rules):** +0% (95% bootstrap CI -17% to +21%); LLM-only 4, rules-only 4, exact sign test p = 1.0.

**Paired, critical exact match (LLM − rules):** -14% (95% bootstrap CI -28% to +0%); LLM-only 3, rules-only 10, exact sign test p = 0.0923.

<details><summary><b>Sensitivity: excluding 9 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 34/41 (83%) | 33/41 (80%) |
| Extraction passed validation | 41/41 (100%) | 32/41 (78%) |
| Critical interpretation exact | 30/41 (73%) | 24/41 (58%) |
| Reference top-1 acceptable (answerable) | 14/25 (56%) | 15/25 (60%) |
| Reference in top 5 (answerable) | 15/25 (60%) | 15/25 (60%) |
| **Correct proposal candidates** (answerable) | 14/25 (56%) | 13/25 (52%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/2 (100%) | 1/2 (50%) |
| References absent from GNIS reported absent | 8/14 (57%) | 10/14 (71%) |

Paired correct proposal candidates: -4% (CI -24% to +16%), p = 1.0.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm |
|---|---|---|
| between_features | 0/0 | 0/0 |
| direction_only | 1/2 (50%) | 1/2 (50%) |
| distance_and_direction | 4/5 (80%) | 2/5 (40%) |
| itinerary | 0/0 | 0/0 |
| named_feature | 11/22 (50%) | 13/22 (59%) |
| route_relative | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm |
|---|---|---|---|
| D01 | answerable | C− R−  | C− R−  |
| D02 | unsupported | C+ R−  | C− R−  |
| D03 | answerable | C− R−  | C+ R−  |
| D04 | reference_absent | C+ R−  | C+ R−  |
| D05 | answerable | C− R−  | C− R−  |
| D06 | reference_absent | C− R−  | C− R−  |
| D07 | answerable | C− R−  | C+ R+ ✓ |
| D08 | unsupported | C− R−  | C− R−  |
| D09 | reference_absent | C+ R−  | C+ R−  |
| D10 | reference_absent | C+ R−  | C− R−  |
| D11 | answerable | C+ R+ ✓ | C+ R−  |
| D12 | reference_absent | C− R−  | C− R−  |
| D13 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D14 | answerable | C+ R+ ✓ | C− R+  |
| D15 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D16 | reference_absent | C+ R−  | C+ R−  |
| D17 | answerable | C+ R−  | C+ R−  |
| D18 | reference_absent | C− R−  | C− R−  |
| D19 | unsupported | C− R−  | C− R−  |
| D20 | answerable | C+ R−  | C− R−  |
| D21 | answerable | C− R−  | C+ R+ ✓ |
| D22 | reference_absent | C− R−  | C− R−  |
| D23 | answerable | C+ R−  | C+ R+ ✓ |
| D24 | reference_absent | C− R−  | C− R−  |
| D25 | reference_absent | C− R−  | C− R−  |
| D26 | answerable | C+ R+ ✓ | C− R−  |
| D27 | answerable | C− R−  | C− R−  |
| D28 | unsupported | C− R−  | C− R−  |
| D29 | answerable | C+ R−  | C+ R−  |
| D30 | reference_absent | C+ R−  | C− R−  |
| D31 | reference_absent | C+ R−  | C+ R−  |
| D32 | reference_absent | C+ R−  | C− R−  |
| D33 | answerable | C+ R−  | C− R−  |
| D34 | reference_absent | C− R−  | C− R−  |
| D35 | answerable | C+ R−  | C− R−  |
| D36 | reference_absent | C+ R−  | C+ R−  |
| D37 | reference_absent | C+ R−  | C+ R−  |
| D38 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D39 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D40 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D41 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D42 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D43 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D44 | reference_absent | C+ R−  | C+ R−  |
| D45 | answerable | C+ R−  | C+ R+ ✓ |
| D46 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D47 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D48 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D49 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D50 | answerable | C+ R+ ✓ | C− R+  |

</details>
