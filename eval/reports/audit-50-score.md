# 50-record audit: scores against the owner's annotations

rules `rules-4` · llm `llm-x2g2-qwen3.5-4b-q4km` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 31 · reference_absent 15 · unsupported 4. Annotated types: named_feature 26 · distance_and_direction 15 · direction_only 5 · route_relative 3 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 30/50 (60%) | 30/50 (60%) |
| Extraction passed validation | 50/50 (100%) | 49/50 (98%) |
| Critical interpretation exact | 28/50 (56%) | 23/50 (46%) |
| Reference top-1 acceptable (answerable) | 19/31 (61%) | 15/31 (48%) |
| Reference in top 5 (answerable) | 19/31 (61%) | 15/31 (48%) |
| **Correct proposal candidates** (answerable) | 17/31 (55%) | 13/31 (42%) |
| Computed proposals that are correct | 1/1 (100%) | 0/0 |
| Unsupported records flagged unsupported | 0/4 (0%) | 4/4 (100%) |
| References absent from GNIS reported absent | 6/15 (40%) | 11/15 (73%) |
| Place names read as no locality | 0 | 1 |
| Mean fields to correct per record | 1.56 | 1.68 |

**Paired, correct proposal candidates (LLM − rules):** -13% (95% bootstrap CI -29% to +3%); LLM-only 2, rules-only 6, exact sign test p = 0.2891.

**Paired, critical exact match (LLM − rules):** -10% (95% bootstrap CI -26% to +8%); LLM-only 7, rules-only 12, exact sign test p = 0.3593.

<details><summary><b>Sensitivity: excluding 10 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 25/40 (62%) | 24/40 (60%) |
| Extraction passed validation | 40/40 (100%) | 39/40 (98%) |
| Critical interpretation exact | 23/40 (57%) | 19/40 (48%) |
| Reference top-1 acceptable (answerable) | 16/24 (67%) | 13/24 (54%) |
| Reference in top 5 (answerable) | 16/24 (67%) | 13/24 (54%) |
| **Correct proposal candidates** (answerable) | 15/24 (62%) | 11/24 (46%) |
| Computed proposals that are correct | 1/1 (100%) | 0/0 |
| Unsupported records flagged unsupported | 0/3 (0%) | 3/3 (100%) |
| References absent from GNIS reported absent | 6/13 (46%) | 9/13 (69%) |

Paired correct proposal candidates: -17% (CI -38% to +0%), p = 0.2188.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm |
|---|---|---|
| direction_only | 1/2 (50%) | 0/2 (0%) |
| distance_and_direction | 8/9 (89%) | 8/9 (89%) |
| itinerary | 0/0 | 0/0 |
| named_feature | 8/20 (40%) | 5/20 (25%) |
| route_relative | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm |
|---|---|---|---|
| A01 | reference_absent | C− R−  | C− R−  |
| A02 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A03 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A04 | answerable | C− R−  | C− R−  |
| A05 | reference_absent | C− R−  | C− R−  |
| A06 | answerable | C+ R+ ✓ | C− R−  |
| A07 | answerable | C+ R+ ✓ | C− R+  |
| A08 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A09 | unsupported | C− R+  | C+ R+  |
| A10 | answerable | C+ R−  | C− R−  |
| A11 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A12 | reference_absent | C+ R−  | C− R−  |
| A13 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A14 | reference_absent | C+ R−  | C− R−  |
| A15 | reference_absent | C− R−  | C− R−  |
| A16 | answerable | C+ R+ ✓ | C− R−  |
| A17 | answerable | C+ R−  | C− R−  |
| A18 | answerable | C+ R−  | C+ R−  |
| A19 | answerable | C− R−  | C− R−  |
| A20 | reference_absent | C+ R−  | C− R−  |
| A21 | reference_absent | C− R−  | C− R−  |
| A22 | reference_absent | C− R−  | C+ R−  |
| A23 | answerable | C− R−  | C− R−  |
| A24 | answerable | C+ R−  | C+ R+ ✓ |
| A25 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A26 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A27 | answerable | C+ R−  | C+ R−  |
| A28 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A29 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A30 | answerable | C+ R+ ✓ | C− R−  |
| A31 | reference_absent | C+ R−  | C+ R−  |
| A32 | answerable | C− R−  | C− R−  |
| A33 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A34 | unsupported | C− R−  | C+ R−  |
| A35 | answerable | C− R+  | C+ R+ ✓ |
| A36 | answerable | C+ R−  | C− R−  |
| A37 | answerable | C− R+  | C− R−  |
| A38 | unsupported | C− R−  | C+ R−  |
| A39 | answerable | C+ R+ ✓ | C− R−  |
| A40 | unsupported | C− R−  | C− R−  |
| A41 | reference_absent | C− R−  | C− R−  |
| A42 | answerable | C+ R+ ✓ | C− R−  |
| A43 | answerable | C− R−  | C− R+  |
| A44 | answerable | C− R−  | C− R−  |
| A45 | reference_absent | C− R−  | C− R−  |
| A46 | reference_absent | C− R−  | C− R−  |
| A47 | reference_absent | C− R−  | C+ R−  |
| A48 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| A49 | reference_absent | C− R−  | C+ R−  |
| A50 | reference_absent | C+ R−  | C+ R−  |

</details>
