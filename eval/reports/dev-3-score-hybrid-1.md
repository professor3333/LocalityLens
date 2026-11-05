# dev-3: scores against Claude's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 50. Categories: answerable 32 · reference_absent 10 · unsupported 8. Annotated types: named_feature 24 · distance_and_direction 17 · route_relative 4 · between_features 2 · itinerary 1 · direction_only 1 · orthogonal_offsets 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 50 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 27/50 (54%) | 30/50 (60%) | 28/50 (56%) |
| Extraction passed validation | 50/50 (100%) | 40/50 (80%) | 50/50 (100%) |
| Critical interpretation exact | 20/50 (40%) | 20/50 (40%) | 21/50 (42%) |
| Reference top-1 acceptable (answerable) | 16/32 (50%) | 15/32 (47%) | 19/32 (59%) |
| Reference in top 5 (answerable) | 16/32 (50%) | 15/32 (47%) | 19/32 (59%) |
| **Correct proposal candidates** (answerable) | 11/32 (34%) | 14/32 (44%) | 14/32 (44%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/8 (38%) | 4/8 (50%) | 3/8 (38%) |
| References absent from GNIS reported absent | 5/10 (50%) | 4/10 (40%) | 5/10 (50%) |
| Place names read as no locality | 0 | 0 | 0 |
| Mean fields to correct per record | 2.3 | 2.62 | 2.16 |

**Paired, correct proposal candidates (LLM − rules):** +9% (95% bootstrap CI -6% to +25%); LLM-only 5, rules-only 2, exact sign test p = 0.4531.

**Paired, critical exact match (LLM − rules):** +0% (95% bootstrap CI -14% to +14%); LLM-only 6, rules-only 6, exact sign test p = 1.0.

**Paired, correct proposal candidates (hybrid − rules):** +9% (95% bootstrap CI +0% to +22%); hybrid-only 3, rules-only 0, exact sign test p = 0.25.

**Paired, critical exact match (hybrid − rules):** +2% (95% bootstrap CI +0% to +6%); hybrid-only 1, rules-only 0, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 11 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 22/39 (56%) | 24/39 (62%) | 23/39 (59%) |
| Extraction passed validation | 39/39 (100%) | 32/39 (82%) | 39/39 (100%) |
| Critical interpretation exact | 16/39 (41%) | 16/39 (41%) | 17/39 (44%) |
| Reference top-1 acceptable (answerable) | 14/25 (56%) | 13/25 (52%) | 17/25 (68%) |
| Reference in top 5 (answerable) | 14/25 (56%) | 13/25 (52%) | 17/25 (68%) |
| **Correct proposal candidates** (answerable) | 9/25 (36%) | 12/25 (48%) | 12/25 (48%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/5 (40%) | 2/5 (40%) | 2/5 (40%) |
| References absent from GNIS reported absent | 4/9 (44%) | 4/9 (44%) | 4/9 (44%) |

Paired correct proposal candidates: +12% (CI -8% to +32%), p = 0.4531.

Paired correct proposal candidates (hybrid − rules): +12% (CI +0% to +24%), p = 0.25.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| distance_and_direction | 7/15 (47%) | 9/15 (60%) | 8/15 (53%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 4/16 (25%) | 5/16 (31%) | 6/16 (38%) |
| orthogonal_offsets | 0/0 | 0/0 | 0/0 |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| F01 | unsupported | C+ R−  | C− R−  | C+ R−  |
| F02 | unsupported | C− R+  | C+ R+  | C− R+  |
| F03 | unsupported | C− R−  | C− R−  | C− R−  |
| F04 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| F05 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| F06 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F07 | reference_absent | C− R−  | C− R−  | C− R−  |
| F08 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| F09 | unsupported | C− R+  | C+ R+  | C− R+  |
| F10 | unsupported | C− R−  | C− R−  | C− R−  |
| F11 | answerable | C− R+  | C− R+  | C− R+  |
| F12 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| F13 | reference_absent | C− R−  | C− R−  | C− R−  |
| F14 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F15 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| F16 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F17 | answerable | C− R−  | C− R−  | C− R−  |
| F18 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| F19 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F20 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F21 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F22 | answerable | C+ R−  | C+ R−  | C+ R−  |
| F23 | answerable | C− R−  | C− R−  | C− R−  |
| F24 | answerable | C− R−  | C− R−  | C− R−  |
| F25 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| F26 | reference_absent | C− R−  | C− R−  | C− R−  |
| F27 | answerable | C− R+  | C− R−  | C− R+  |
| F28 | answerable | C− R−  | C− R−  | C− R−  |
| F29 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F30 | reference_absent | C− R−  | C− R−  | C− R−  |
| F31 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F32 | answerable | C− R−  | C− R−  | C− R−  |
| F33 | answerable | C− R+  | C− R−  | C− R+  |
| F34 | answerable | C− R−  | C− R−  | C− R−  |
| F35 | answerable | C− R−  | C− R−  | C− R−  |
| F36 | reference_absent | C− R−  | C− R−  | C− R−  |
| F37 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| F38 | answerable | C− R−  | C− R−  | C− R−  |
| F39 | unsupported | C− R+  | C− R+  | C− R+  |
| F40 | reference_absent | C− R−  | C− R−  | C− R−  |
| F41 | answerable | C− R−  | C− R−  | C− R−  |
| F42 | answerable | C+ R−  | C− R−  | C+ R−  |
| F43 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| F44 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| F45 | answerable | C− R−  | C− R−  | C− R−  |
| F46 | unsupported | C− R−  | C− R−  | C− R−  |
| F47 | unsupported | C− R−  | C+ R+  | C− R−  |
| F48 | answerable | C− R−  | C− R−  | C− R−  |
| F49 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| F50 | answerable | C+ R+ ✓ | C+ R−  | C+ R+ ✓ |

</details>
