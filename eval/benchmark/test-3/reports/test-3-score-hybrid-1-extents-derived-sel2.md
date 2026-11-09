# test-3: scores against the owner's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 120. Categories: answerable 63 · reference_absent 44 · unsupported 13. Annotated types: named_feature 63 · distance_and_direction 34 · route_relative 6 · direction_only 6 · between_features 6 · distance_only 4 · itinerary 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 120 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 42/120 (35%) | 46/120 (38%) | 42/120 (35%) |
| Extraction passed validation | 120/120 (100%) | 113/120 (94%) | 120/120 (100%) |
| Critical interpretation exact | 29/120 (24%) | 30/120 (25%) | 30/120 (25%) |
| Reference top-1 acceptable (answerable) | 16/63 (25%) | 10/63 (16%) | 18/63 (29%) |
| Reference in top 5 (answerable) | 16/63 (25%) | 11/63 (18%) | 18/63 (29%) |
| **Correct proposal candidates** (answerable) | 14/63 (22%) | 8/63 (13%) | 16/63 (25%) |
| Computed proposals that are correct | 3/26 (12%) | 3/23 (13%) | 5/29 (17%) |
| Unsupported records flagged unsupported | 6/13 (46%) | 9/13 (69%) | 6/13 (46%) |
| References absent from GNIS reported absent | 14/44 (32%) | 21/44 (48%) | 13/44 (30%) |
| Place names read as no locality | 0 | 0 | 0 |
| Mean fields to correct per record | 3.27 | 3.18 | 3.23 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 26/120 (22%) | 23/120 (19%) | 29/120 (24%) |
| Computed proposals that are correct | 3/26 (12%) | 3/23 (13%) | 5/29 (17%) |
| Useful coverage (of answerable) | 3/63 (5%) | 3/63 (5%) | 5/63 (8%) |

**Paired, correct proposal candidates (LLM − rules):** -10% (95% bootstrap CI -21% to +2%); LLM-only 4, rules-only 10, exact sign test p = 0.1796.

**Paired, critical exact match (LLM − rules):** +1% (95% bootstrap CI -9% to +10%); LLM-only 17, rules-only 16, exact sign test p = 1.0.

**Paired, correct proposal candidates (hybrid − rules):** +3% (95% bootstrap CI +0% to +8%); hybrid-only 2, rules-only 0, exact sign test p = 0.5.

**Paired, critical exact match (hybrid − rules):** +1% (95% bootstrap CI -2% to +4%); hybrid-only 2, rules-only 1, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 23 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 35/97 (36%) | 35/97 (36%) | 34/97 (35%) |
| Extraction passed validation | 97/97 (100%) | 90/97 (93%) | 97/97 (100%) |
| Critical interpretation exact | 24/97 (25%) | 21/97 (22%) | 24/97 (25%) |
| Reference top-1 acceptable (answerable) | 15/53 (28%) | 9/53 (17%) | 17/53 (32%) |
| Reference in top 5 (answerable) | 15/53 (28%) | 9/53 (17%) | 17/53 (32%) |
| **Correct proposal candidates** (answerable) | 13/53 (24%) | 8/53 (15%) | 15/53 (28%) |
| Computed proposals that are correct | 3/22 (14%) | 3/18 (17%) | 5/25 (20%) |
| Unsupported records flagged unsupported | 4/7 (57%) | 3/7 (43%) | 3/7 (43%) |
| References absent from GNIS reported absent | 9/37 (24%) | 14/37 (38%) | 8/37 (22%) |

Paired correct proposal candidates: -9% (CI -23% to +4%), p = 0.2668.

Paired correct proposal candidates (hybrid − rules): +4% (CI +0% to +9%), p = 0.5.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| distance_and_direction | 7/18 (39%) | 7/18 (39%) | 9/18 (50%) |
| distance_only | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) |
| itinerary | 0/0 | 0/0 | 0/0 |
| named_feature | 7/42 (17%) | 1/42 (2%) | 7/42 (17%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| P001 | answerable | C+ R−  | C− R−  | C+ R−  |
| P002 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| P003 | answerable | C− R−  | C− R−  | C− R−  |
| P004 | unsupported | C− R−  | C+ R+  | C+ R+  |
| P005 | answerable | C− R−  | C− R−  | C− R−  |
| P006 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| P007 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| P008 | unsupported | C− R−  | C+ R−  | C− R−  |
| P009 | answerable | C− R−  | C− R−  | C− R−  |
| P010 | reference_absent | C− R−  | C− R−  | C− R−  |
| P011 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| P012 | unsupported | C− R−  | C− R−  | C− R−  |
| P013 | unsupported | C− R−  | C+ R−  | C− R−  |
| P014 | answerable | C− R−  | C− R−  | C− R−  |
| P015 | answerable | C− R−  | C− R−  | C− R−  |
| P016 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P017 | answerable | C− R−  | C− R−  | C− R−  |
| P018 | answerable | C− R−  | C− R−  | C− R−  |
| P019 | reference_absent | C− R−  | C− R−  | C− R−  |
| P020 | answerable | C− R−  | C− R−  | C− R−  |
| P021 | answerable | C− R−  | C− R−  | C− R−  |
| P022 | unsupported | C+ R−  | C+ R+  | C+ R+  |
| P023 | reference_absent | C− R−  | C− R−  | C− R−  |
| P024 | answerable | C− R−  | C− R−  | C− R−  |
| P025 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| P026 | answerable | C− R−  | C− R−  | C− R−  |
| P027 | unsupported | C− R−  | C− R+  | C− R+  |
| P028 | answerable | C− R−  | C− R−  | C− R−  |
| P029 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| P030 | reference_absent | C− R−  | C− R−  | C− R−  |
| P031 | answerable | C− R−  | C− R−  | C− R−  |
| P032 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| P033 | answerable | C− R−  | C− R−  | C− R−  |
| P034 | unsupported | C− R−  | C− R−  | C− R−  |
| P035 | unsupported | C− R−  | C− R+  | C− R−  |
| P036 | unsupported | C− R−  | C− R+  | C− R+  |
| P037 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| P038 | reference_absent | C− R−  | C− R−  | C− R−  |
| P039 | reference_absent | C− R−  | C− R−  | C− R−  |
| P040 | answerable | C− R−  | C+ R−  | C− R−  |
| P041 | reference_absent | C− R−  | C− R−  | C− R−  |
| P042 | unsupported | C− R−  | C− R−  | C− R−  |
| P043 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| P044 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P045 | reference_absent | C− R−  | C− R−  | C− R−  |
| P046 | reference_absent | C− R−  | C− R−  | C− R−  |
| P047 | answerable | C− R−  | C+ R−  | C− R−  |
| P048 | answerable | C− R−  | C− R−  | C− R−  |
| P049 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P050 | unsupported | C− R−  | C− R−  | C− R−  |
| P051 | answerable | C+ R−  | C+ R−  | C+ R−  |
| P052 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P053 | answerable | C− R−  | C− R−  | C− R−  |
| P054 | reference_absent | C− R−  | C− R−  | C− R−  |
| P055 | answerable | C− R−  | C− R−  | C− R−  |
| P056 | reference_absent | C− R−  | C− R−  | C− R−  |
| P057 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P058 | answerable | C+ R−  | C− R−  | C− R−  |
| P059 | reference_absent | C− R−  | C− R−  | C− R−  |
| P060 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P061 | reference_absent | C− R−  | C− R−  | C− R−  |
| P062 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| P063 | answerable | C− R+  | C− R−  | C− R+  |
| P064 | answerable | C− R−  | C− R−  | C− R−  |
| P065 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P066 | answerable | C+ R−  | C− R−  | C+ R−  |
| P067 | answerable | C− R−  | C− R−  | C− R−  |
| P068 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P069 | answerable | C− R−  | C− R−  | C− R−  |
| P070 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P071 | reference_absent | C− R−  | C− R−  | C− R−  |
| P072 | reference_absent | C− R−  | C− R−  | C− R−  |
| P073 | unsupported | C− R−  | C− R−  | C− R−  |
| P074 | answerable | C− R−  | C− R−  | C− R−  |
| P075 | reference_absent | C− R−  | C− R−  | C− R−  |
| P076 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P077 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| P078 | answerable | C− R−  | C− R+  | C− R−  |
| P079 | reference_absent | C− R−  | C− R−  | C− R−  |
| P080 | reference_absent | C− R−  | C− R−  | C− R−  |
| P081 | reference_absent | C− R−  | C− R−  | C− R−  |
| P082 | answerable | C− R−  | C− R−  | C− R−  |
| P083 | reference_absent | C− R−  | C− R−  | C− R−  |
| P084 | answerable | C− R−  | C− R−  | C− R−  |
| P085 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P086 | answerable | C+ R−  | C− R−  | C+ R−  |
| P087 | answerable | C− R−  | C− R−  | C− R−  |
| P088 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| P089 | reference_absent | C− R−  | C− R−  | C− R−  |
| P090 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P091 | answerable | C− R−  | C− R−  | C− R−  |
| P092 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P093 | reference_absent | C− R−  | C− R−  | C− R−  |
| P094 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P095 | reference_absent | C− R−  | C− R−  | C− R−  |
| P096 | answerable | C− R−  | C− R−  | C− R−  |
| P097 | answerable | C− R−  | C− R−  | C− R−  |
| P098 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P099 | answerable | C− R−  | C− R−  | C− R−  |
| P100 | answerable | C− R−  | C+ R−  | C− R−  |
| P101 | answerable | C− R−  | C− R−  | C− R−  |
| P102 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| P103 | reference_absent | C− R−  | C− R−  | C− R−  |
| P104 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| P105 | reference_absent | C− R−  | C− R−  | C− R−  |
| P106 | reference_absent | C− R−  | C− R−  | C− R−  |
| P107 | unsupported | C− R−  | C− R−  | C− R−  |
| P108 | answerable | C+ R−  | C+ R−  | C+ R−  |
| P109 | answerable | C− R−  | C− R−  | C− R−  |
| P110 | reference_absent | C− R−  | C+ R−  | C− R−  |
| P111 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P112 | answerable | C− R−  | C− R−  | C− R−  |
| P113 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| P114 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| P115 | reference_absent | C− R−  | C− R−  | C− R−  |
| P116 | reference_absent | C− R−  | C− R−  | C− R−  |
| P117 | answerable | C− R−  | C− R−  | C− R−  |
| P118 | reference_absent | C− R−  | C− R−  | C− R−  |
| P119 | answerable | C− R−  | C− R+  | C− R−  |
| P120 | answerable | C− R−  | C− R−  | C− R−  |

</details>
