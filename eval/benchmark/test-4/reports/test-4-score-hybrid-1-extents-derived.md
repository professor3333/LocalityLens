# test-4: scores against Claude's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 120. Categories: answerable 107 · unsupported 7 · reference_absent 6. Annotated types: distance_and_direction 66 · named_feature 45 · route_relative 6 · direction_only 2 · between_features 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 120 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 67/120 (56%) | 62/120 (52%) | 72/120 (60%) |
| Extraction passed validation | 120/120 (100%) | 112/120 (93%) | 120/120 (100%) |
| Critical interpretation exact | 54/120 (45%) | 46/120 (38%) | 58/120 (48%) |
| Reference top-1 acceptable (answerable) | 55/107 (51%) | 48/107 (45%) | 62/107 (58%) |
| Reference in top 5 (answerable) | 59/107 (55%) | 52/107 (49%) | 67/107 (63%) |
| **Correct proposal candidates** (answerable) | 46/107 (43%) | 37/107 (35%) | 49/107 (46%) |
| Computed proposals that are correct | 31/56 (55%) | 27/53 (51%) | 33/60 (55%) |
| Unsupported records flagged unsupported | 2/7 (29%) | 6/7 (86%) | 2/7 (29%) |
| References absent from GNIS reported absent | 5/6 (83%) | 5/6 (83%) | 4/6 (67%) |
| Place names read as no locality | 0 | 0 | 0 |
| Mean fields to correct per record | 2.33 | 2.55 | 2.05 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 56/120 (47%) | 53/120 (44%) | 60/120 (50%) |
| Computed proposals that are correct | 31/56 (55%) | 27/53 (51%) | 33/60 (55%) |
| Useful coverage (of answerable) | 31/107 (29%) | 27/107 (25%) | 33/107 (31%) |

**Paired, correct proposal candidates (LLM − rules):** -8% (95% bootstrap CI -19% to +2%); LLM-only 12, rules-only 21, exact sign test p = 0.1628.

**Paired, critical exact match (LLM − rules):** -7% (95% bootstrap CI -18% to +4%); LLM-only 20, rules-only 28, exact sign test p = 0.3123.

**Paired, correct proposal candidates (hybrid − rules):** +3% (95% bootstrap CI +0% to +6%); hybrid-only 3, rules-only 0, exact sign test p = 0.25.

**Paired, critical exact match (hybrid − rules):** +3% (95% bootstrap CI +0% to +8%); hybrid-only 5, rules-only 1, exact sign test p = 0.2188.

<details><summary><b>Sensitivity: excluding 15 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 61/105 (58%) | 58/105 (55%) | 66/105 (63%) |
| Extraction passed validation | 105/105 (100%) | 98/105 (93%) | 105/105 (100%) |
| Critical interpretation exact | 48/105 (46%) | 43/105 (41%) | 52/105 (50%) |
| Reference top-1 acceptable (answerable) | 49/93 (53%) | 44/93 (47%) | 56/93 (60%) |
| Reference in top 5 (answerable) | 52/93 (56%) | 48/93 (52%) | 60/93 (64%) |
| **Correct proposal candidates** (answerable) | 41/93 (44%) | 34/93 (37%) | 44/93 (47%) |
| Computed proposals that are correct | 27/48 (56%) | 24/44 (55%) | 29/51 (57%) |
| Unsupported records flagged unsupported | 1/6 (17%) | 6/6 (100%) | 2/6 (33%) |
| References absent from GNIS reported absent | 5/6 (83%) | 5/6 (83%) | 4/6 (67%) |

Paired correct proposal candidates: -8% (CI -19% to +3%), p = 0.2649.

Paired correct proposal candidates (hybrid − rules): +3% (CI +0% to +8%), p = 0.25.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) |
| distance_and_direction | 40/65 (62%) | 31/65 (48%) | 43/65 (66%) |
| named_feature | 6/40 (15%) | 6/40 (15%) | 6/40 (15%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| Q001 | answerable | C− R−  | C− R−  | C− R−  |
| Q002 | answerable | C− R+  | C− R−  | C− R+  |
| Q003 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q004 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q005 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| Q006 | answerable | C− R−  | C− R−  | C− R−  |
| Q007 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q008 | unsupported | C− R−  | C+ R+  | C− R−  |
| Q009 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q010 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q011 | answerable | C− R−  | C− R−  | C− R−  |
| Q012 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| Q013 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q014 | answerable | C− R−  | C− R+  | C− R+  |
| Q015 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q016 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| Q017 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q018 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q019 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q020 | unsupported | C− R−  | C− R+  | C− R+  |
| Q021 | answerable | C− R−  | C− R−  | C− R−  |
| Q022 | answerable | C− R−  | C+ R−  | C− R−  |
| Q023 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q024 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| Q025 | answerable | C− R−  | C− R−  | C− R−  |
| Q026 | answerable | C− R−  | C− R−  | C− R−  |
| Q027 | answerable | C− R−  | C− R−  | C− R−  |
| Q028 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q029 | answerable | C− R−  | C− R−  | C− R−  |
| Q030 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| Q031 | answerable | C+ R−  | C− R−  | C+ R−  |
| Q032 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q033 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| Q034 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q035 | answerable | C− R−  | C− R−  | C− R−  |
| Q036 | unsupported | C− R−  | C− R−  | C− R−  |
| Q037 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| Q038 | unsupported | C− R−  | C− R−  | C− R−  |
| Q039 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| Q040 | answerable | C− R−  | C− R−  | C− R−  |
| Q041 | answerable | C− R−  | C− R+  | C− R−  |
| Q042 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q043 | unsupported | C− R−  | C+ R−  | C− R−  |
| Q044 | answerable | C− R−  | C− R−  | C− R−  |
| Q045 | answerable | C− R−  | C− R−  | C− R−  |
| Q046 | answerable | C+ R−  | C− R+  | C− R+  |
| Q047 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q048 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q049 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| Q050 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q051 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q052 | answerable | C− R−  | C− R−  | C− R−  |
| Q053 | answerable | C− R−  | C+ R−  | C+ R−  |
| Q054 | answerable | C+ R−  | C− R−  | C+ R−  |
| Q055 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q056 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q057 | answerable | C− R−  | C− R−  | C− R−  |
| Q058 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q059 | answerable | C− R+  | C− R−  | C− R+  |
| Q060 | answerable | C− R−  | C− R−  | C− R−  |
| Q061 | answerable | C− R−  | C+ R−  | C− R−  |
| Q062 | answerable | C− R−  | C− R−  | C− R−  |
| Q063 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q064 | answerable | C− R−  | C− R−  | C− R−  |
| Q065 | answerable | C− R−  | C− R−  | C− R−  |
| Q066 | answerable | C− R−  | C− R−  | C− R−  |
| Q067 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| Q068 | answerable | C− R+  | C− R−  | C− R+  |
| Q069 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q070 | answerable | C+ R−  | C− R−  | C+ R−  |
| Q071 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q072 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q073 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q074 | answerable | C− R−  | C− R+  | C− R+  |
| Q075 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q076 | reference_absent | C− R−  | C− R−  | C− R−  |
| Q077 | answerable | C− R−  | C− R−  | C− R−  |
| Q078 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q079 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q080 | answerable | C− R−  | C− R−  | C− R−  |
| Q081 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q082 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q083 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| Q084 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| Q085 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q086 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q087 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q088 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| Q089 | unsupported | C− R−  | C+ R+  | C− R−  |
| Q090 | answerable | C− R−  | C− R−  | C− R−  |
| Q091 | answerable | C− R−  | C− R−  | C− R−  |
| Q092 | answerable | C− R+  | C− R−  | C− R+  |
| Q093 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q094 | answerable | C− R−  | C− R−  | C− R−  |
| Q095 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q096 | answerable | C− R−  | C− R−  | C− R−  |
| Q097 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q098 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q099 | answerable | C− R−  | C− R−  | C− R−  |
| Q100 | reference_absent | C− R−  | C+ R−  | C− R−  |
| Q101 | answerable | C+ R−  | C+ R−  | C+ R−  |
| Q102 | answerable | C− R−  | C− R+  | C− R+  |
| Q103 | answerable | C− R−  | C− R−  | C− R−  |
| Q104 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q105 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| Q106 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| Q107 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| Q108 | answerable | C− R−  | C− R−  | C− R−  |
| Q109 | answerable | C− R−  | C− R−  | C− R−  |
| Q110 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q111 | unsupported | C− R−  | C+ R−  | C+ R−  |
| Q112 | answerable | C− R−  | C− R−  | C− R−  |
| Q113 | answerable | C− R−  | C− R−  | C− R−  |
| Q114 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q115 | answerable | C− R+  | C− R−  | C− R+  |
| Q116 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| Q117 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| Q118 | answerable | C− R−  | C− R−  | C− R−  |
| Q119 | reference_absent | C− R−  | C− R−  | C− R−  |
| Q120 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |

</details>
