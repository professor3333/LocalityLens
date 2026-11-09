# test-2: scores against Claude's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 120. Categories: answerable 80 · reference_absent 27 · unsupported 13. Annotated types: named_feature 66 · distance_and_direction 25 · direction_only 15 · route_relative 8 · between_features 3 · itinerary 1 · no_locality 1 · distance_only 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 120 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 75/120 (62%) | 72/120 (60%) | 76/120 (63%) |
| Extraction passed validation | 120/120 (100%) | 108/120 (90%) | 120/120 (100%) |
| Critical interpretation exact | 71/120 (59%) | 57/120 (48%) | 68/120 (57%) |
| Reference top-1 acceptable (answerable) | 37/80 (46%) | 47/80 (59%) | 53/80 (66%) |
| Reference in top 5 (answerable) | 37/80 (46%) | 48/80 (60%) | 53/80 (66%) |
| **Correct proposal candidates** (answerable) | 34/80 (42%) | 31/80 (39%) | 43/80 (54%) |
| Computed proposals that are correct | 8/12 (67%) | 9/15 (60%) | 10/16 (62%) |
| Unsupported records flagged unsupported | 4/13 (31%) | 9/13 (69%) | 5/13 (38%) |
| References absent from GNIS reported absent | 12/27 (44%) | 16/27 (59%) | 11/27 (41%) |
| Place names read as no locality | 0 | 2 | 0 |
| Mean fields to correct per record | 1.51 | 1.67 | 1.35 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 12/120 (10%) | 15/120 (12%) | 16/120 (13%) |
| Computed proposals that are correct | 8/12 (67%) | 9/15 (60%) | 10/16 (62%) |
| Useful coverage (of answerable) | 8/80 (10%) | 9/80 (11%) | 10/80 (12%) |

**Paired, correct proposal candidates (LLM − rules):** -4% (95% bootstrap CI -15% to +8%); LLM-only 10, rules-only 13, exact sign test p = 0.6776.

**Paired, critical exact match (LLM − rules):** -12% (95% bootstrap CI -22% to -2%); LLM-only 13, rules-only 27, exact sign test p = 0.0385.

**Paired, correct proposal candidates (hybrid − rules):** +11% (95% bootstrap CI +5% to +19%); hybrid-only 9, rules-only 0, exact sign test p = 0.0039.

**Paired, critical exact match (hybrid − rules):** -2% (95% bootstrap CI -8% to +2%); hybrid-only 3, rules-only 6, exact sign test p = 0.5078.

<details><summary><b>Sensitivity: excluding 27 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 61/93 (66%) | 58/93 (62%) | 62/93 (67%) |
| Extraction passed validation | 93/93 (100%) | 84/93 (90%) | 93/93 (100%) |
| Critical interpretation exact | 60/93 (64%) | 46/93 (50%) | 57/93 (61%) |
| Reference top-1 acceptable (answerable) | 32/65 (49%) | 41/65 (63%) | 45/65 (69%) |
| Reference in top 5 (answerable) | 32/65 (49%) | 41/65 (63%) | 45/65 (69%) |
| **Correct proposal candidates** (answerable) | 32/65 (49%) | 28/65 (43%) | 39/65 (60%) |
| Computed proposals that are correct | 8/11 (73%) | 8/13 (62%) | 9/13 (69%) |
| Unsupported records flagged unsupported | 4/11 (36%) | 7/11 (64%) | 5/11 (46%) |
| References absent from GNIS reported absent | 7/17 (41%) | 11/17 (65%) | 6/17 (35%) |

Paired correct proposal candidates: -6% (CI -20% to +8%), p = 0.5034.

Paired correct proposal candidates (hybrid − rules): +11% (CI +3% to +18%), p = 0.0156.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 8/12 (67%) | 2/12 (17%) | 8/12 (67%) |
| distance_and_direction | 14/23 (61%) | 13/23 (56%) | 17/23 (74%) |
| distance_only | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 12/44 (27%) | 16/44 (36%) | 18/44 (41%) |
| no_locality | 0/0 | 0/0 | 0/0 |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| H002 | answerable | C− R−  | C+ R−  | C− R−  |
| H003 | reference_absent | C− R−  | C− R−  | C− R−  |
| H004 | unsupported | C− R−  | C− R−  | C− R−  |
| H005 | unsupported | C− R−  | C+ R+  | C+ R+  |
| H006 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H007 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H008 | answerable | C− R+  | C− R+  | C− R+  |
| H009 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H010 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H012 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H013 | reference_absent | C− R−  | C− R−  | C− R−  |
| H014 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H015 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H016 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H017 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H018 | reference_absent | C− R−  | C− R−  | C− R−  |
| H019 | answerable | C− R−  | C− R−  | C− R−  |
| H020 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H022 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H023 | unsupported | C− R+  | C+ R+  | C− R+  |
| H024 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| H025 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| H026 | answerable | C− R−  | C− R−  | C− R−  |
| H027 | answerable | C− R−  | C− R+  | C− R+  |
| H028 | answerable | C+ R−  | C− R+  | C− R+  |
| H029 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H030 | answerable | C+ R−  | C− R+  | C+ R−  |
| H031 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H032 | reference_absent | C− R−  | C+ R−  | C− R−  |
| H033 | reference_absent | C− R−  | C+ R−  | C− R−  |
| H034 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H035 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H036 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H038 | unsupported | C− R−  | C− R−  | C− R−  |
| H041 | unsupported | C− R−  | C− R−  | C− R−  |
| H042 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H043 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H044 | unsupported | C− R−  | C− R−  | C− R−  |
| H045 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H046 | answerable | C− R+  | C− R+  | C− R+  |
| H047 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H048 | answerable | C− R−  | C− R−  | C− R−  |
| H049 | reference_absent | C− R−  | C− R−  | C− R−  |
| H052 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H053 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H054 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H055 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| H056 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| H058 | answerable | C− R−  | C− R−  | C− R−  |
| H059 | answerable | C+ R−  | C− R+  | C− R+  |
| H060 | reference_absent | C− R−  | C− R−  | C− R−  |
| H062 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H064 | unsupported | C− R−  | C− R−  | C− R−  |
| H065 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H066 | answerable | C− R−  | C+ R−  | C− R−  |
| H067 | reference_absent | C− R−  | C+ R−  | C− R−  |
| H068 | answerable | C− R−  | C− R−  | C− R−  |
| H069 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H070 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| H071 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H073 | unsupported | C− R−  | C− R−  | C− R−  |
| H074 | answerable | C− R−  | C− R−  | C− R−  |
| H075 | unsupported | C+ R−  | C+ R+  | C+ R+  |
| H076 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H077 | answerable | C− R−  | C− R−  | C− R−  |
| H078 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H079 | unsupported | C− R−  | C− R−  | C− R−  |
| H080 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H081 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H082 | reference_absent | C+ R−  | C− R−  | C− R−  |
| H083 | reference_absent | C− R−  | C− R−  | C− R−  |
| H084 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H085 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H086 | unsupported | C− R−  | C+ R−  | C− R−  |
| H088 | reference_absent | C− R−  | C− R−  | C− R−  |
| H090 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H091 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H092 | reference_absent | C− R−  | C− R−  | C− R−  |
| H093 | reference_absent | C− R−  | C− R−  | C− R−  |
| H094 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H095 | answerable | C+ R−  | C− R−  | C+ R−  |
| H096 | answerable | C+ R−  | C− R+  | C− R+  |
| H097 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H098 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H099 | answerable | C+ R−  | C− R+  | C− R+  |
| H100 | unsupported | C− R−  | C− R−  | C− R−  |
| H101 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H103 | answerable | C− R−  | C− R−  | C− R−  |
| H105 | reference_absent | C− R−  | C+ R−  | C− R−  |
| H106 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| H107 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H108 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| H109 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H110 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| H111 | answerable | C+ R−  | C− R−  | C+ R−  |
| H113 | answerable | C− R−  | C− R+  | C− R+  |
| H114 | answerable | C− R−  | C− R−  | C− R−  |
| H115 | answerable | C− R−  | C− R−  | C− R−  |
| H116 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H117 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H118 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H119 | reference_absent | C− R−  | C+ R−  | C− R−  |
| H120 | answerable | C− R−  | C− R−  | C− R−  |
| H121 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H123 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H124 | answerable | C− R−  | C− R−  | C− R−  |
| H125 | answerable | C+ R−  | C+ R−  | C+ R−  |
| H126 | answerable | C+ R−  | C− R+  | C− R+  |
| H127 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H128 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H129 | answerable | C− R+  | C− R−  | C− R+  |
| H130 | unsupported | C+ R−  | C− R−  | C+ R−  |
| H132 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| H133 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| H134 | answerable | C− R−  | C− R−  | C− R−  |
| H135 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H136 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| H137 | answerable | C− R−  | C− R−  | C− R−  |
| H139 | answerable | C+ R−  | C− R−  | C+ R−  |
| H140 | reference_absent | C+ R−  | C+ R−  | C+ R−  |

</details>
