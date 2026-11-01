# dev-1: scores against the owner's annotations

rules `rules-1` · llm `llm-x1g2-qwen3.5-4b-q4km` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 29 · reference_absent 17 · unsupported 4. Annotated types: named_feature 34 · distance_and_direction 7 · direction_only 5 · route_relative 2 · between_features 1 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 39/50 (78%) | 26/50 (52%) |
| Extraction passed validation | 50/50 (100%) | 38/50 (76%) |
| Critical interpretation exact | 34/50 (68%) | 17/50 (34%) |
| Reference top-1 acceptable (answerable) | 16/29 (55%) | 9/29 (31%) |
| Reference in top 5 (answerable) | 17/29 (59%) | 9/29 (31%) |
| **Correct proposal candidates** (answerable) | 16/29 (55%) | 8/29 (28%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/4 (75%) | 2/4 (50%) |
| References absent from GNIS reported absent | 9/17 (53%) | 6/17 (35%) |
| Place names read as no locality | 0 | 10 |
| Mean fields to correct per record | 0.96 | 2.2 |

**Paired, correct proposal candidates (LLM − rules):** -28% (95% bootstrap CI -45% to -10%); LLM-only 1, rules-only 9, exact sign test p = 0.0215.

**Paired, critical exact match (LLM − rules):** -34% (95% bootstrap CI -50% to -18%); LLM-only 3, rules-only 20, exact sign test p = 0.0005.

<details><summary><b>Sensitivity: excluding 9 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 34/41 (83%) | 23/41 (56%) |
| Extraction passed validation | 41/41 (100%) | 30/41 (73%) |
| Critical interpretation exact | 30/41 (73%) | 14/41 (34%) |
| Reference top-1 acceptable (answerable) | 14/25 (56%) | 8/25 (32%) |
| Reference in top 5 (answerable) | 15/25 (60%) | 8/25 (32%) |
| **Correct proposal candidates** (answerable) | 14/25 (56%) | 7/25 (28%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/2 (100%) | 1/2 (50%) |
| References absent from GNIS reported absent | 8/14 (57%) | 6/14 (43%) |

Paired correct proposal candidates: -28% (CI -48% to -8%), p = 0.0391.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm |
|---|---|---|
| between_features | 0/0 | 0/0 |
| direction_only | 1/2 (50%) | 1/2 (50%) |
| distance_and_direction | 4/5 (80%) | 2/5 (40%) |
| itinerary | 0/0 | 0/0 |
| named_feature | 11/22 (50%) | 5/22 (23%) |
| route_relative | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm |
|---|---|---|---|
| D01 | answerable | C− R−  | C− R−  |
| D02 | unsupported | C+ R−  | C− R−  |
| D03 | answerable | C− R−  | C+ R+ ✓ |
| D04 | reference_absent | C+ R−  | C+ R−  |
| D05 | answerable | C− R−  | C− R−  |
| D06 | reference_absent | C− R−  | C− R−  |
| D07 | answerable | C− R−  | C− R−  |
| D08 | unsupported | C− R−  | C− R−  |
| D09 | reference_absent | C+ R−  | C− R−  |
| D10 | reference_absent | C+ R−  | C+ R−  |
| D11 | answerable | C+ R+ ✓ | C+ R−  |
| D12 | reference_absent | C− R−  | C+ R−  |
| D13 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D14 | answerable | C+ R+ ✓ | C− R−  |
| D15 | answerable | C+ R+ ✓ | C− R−  |
| D16 | reference_absent | C+ R−  | C− R−  |
| D17 | answerable | C+ R−  | C− R−  |
| D18 | reference_absent | C− R−  | C− R−  |
| D19 | unsupported | C− R−  | C− R−  |
| D20 | answerable | C+ R−  | C− R−  |
| D21 | answerable | C− R−  | C− R−  |
| D22 | reference_absent | C− R−  | C− R−  |
| D23 | answerable | C+ R−  | C− R−  |
| D24 | reference_absent | C− R−  | C− R−  |
| D25 | reference_absent | C− R−  | C− R−  |
| D26 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D27 | answerable | C− R−  | C− R−  |
| D28 | unsupported | C− R−  | C+ R+  |
| D29 | answerable | C+ R−  | C− R−  |
| D30 | reference_absent | C+ R−  | C− R−  |
| D31 | reference_absent | C+ R−  | C+ R−  |
| D32 | reference_absent | C+ R−  | C+ R−  |
| D33 | answerable | C+ R−  | C− R−  |
| D34 | reference_absent | C− R−  | C− R−  |
| D35 | answerable | C+ R−  | C+ R−  |
| D36 | reference_absent | C+ R−  | C+ R−  |
| D37 | reference_absent | C+ R−  | C− R−  |
| D38 | answerable | C+ R+ ✓ | C− R−  |
| D39 | answerable | C+ R+ ✓ | C− R−  |
| D40 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D41 | answerable | C+ R+ ✓ | C− R−  |
| D42 | answerable | C+ R+ ✓ | C− R−  |
| D43 | answerable | C+ R+ ✓ | C− R−  |
| D44 | reference_absent | C+ R−  | C− R−  |
| D45 | answerable | C+ R−  | C− R+  |
| D46 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D47 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D48 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| D49 | answerable | C+ R+ ✓ | C− R−  |
| D50 | answerable | C+ R+ ✓ | C+ R+ ✓ |

</details>
