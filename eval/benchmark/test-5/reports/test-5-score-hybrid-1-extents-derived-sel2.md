# test-5: scores against Codex's annotations

rules `rules-6` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 120. Categories: answerable 108 · unsupported 7 · reference_absent 5. Annotated types: named_feature 74 · distance_and_direction 33 · route_relative 4 · direction_only 3 · between_features 3 · distance_only 3.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 120 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 56/120 (47%) | 59/120 (49%) | 57/120 (48%) |
| Extraction passed validation | 120/120 (100%) | 106/120 (88%) | 120/120 (100%) |
| Critical interpretation exact | 43/120 (36%) | 36/120 (30%) | 41/120 (34%) |
| Reference top-1 acceptable (answerable) | 33/108 (31%) | 38/108 (35%) | 39/108 (36%) |
| Reference in top 5 (answerable) | 34/108 (32%) | 39/108 (36%) | 40/108 (37%) |
| **Correct proposal candidates** (answerable) | 25/108 (23%) | 21/108 (19%) | 28/108 (26%) |
| Computed proposals that are correct | 7/15 (47%) | 6/16 (38%) | 8/19 (42%) |
| Unsupported records flagged unsupported | 3/7 (43%) | 5/7 (71%) | 4/7 (57%) |
| References absent from GNIS reported absent | 5/5 (100%) | 4/5 (80%) | 5/5 (100%) |
| Place names read as no locality | 0 | 0 | 0 |
| Mean fields to correct per record | 3.02 | 3.12 | 2.98 |

**Proposals with reviewed extents** (computed = full point-radius region, no blocking question):

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Computed proposals (of all records) | 15/120 (12%) | 16/120 (13%) | 19/120 (16%) |
| Computed proposals that are correct | 7/15 (47%) | 6/16 (38%) | 8/19 (42%) |
| Useful coverage (of answerable) | 7/108 (6%) | 6/108 (6%) | 8/108 (7%) |

**Paired, correct proposal candidates (LLM − rules):** -4% (95% bootstrap CI -12% to +5%); LLM-only 9, rules-only 13, exact sign test p = 0.5235.

**Paired, critical exact match (LLM − rules):** -6% (95% bootstrap CI -16% to +5%); LLM-only 17, rules-only 24, exact sign test p = 0.3489.

**Paired, correct proposal candidates (hybrid − rules):** +3% (95% bootstrap CI +0% to +6%); hybrid-only 3, rules-only 0, exact sign test p = 0.25.

**Paired, critical exact match (hybrid − rules):** -2% (95% bootstrap CI -7% to +2%); hybrid-only 3, rules-only 5, exact sign test p = 0.7266.

<details><summary><b>Sensitivity: excluding 15 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 47/105 (45%) | 53/105 (50%) | 49/105 (47%) |
| Extraction passed validation | 105/105 (100%) | 92/105 (88%) | 105/105 (100%) |
| Critical interpretation exact | 35/105 (33%) | 31/105 (30%) | 34/105 (32%) |
| Reference top-1 acceptable (answerable) | 32/97 (33%) | 38/97 (39%) | 38/97 (39%) |
| Reference in top 5 (answerable) | 33/97 (34%) | 39/97 (40%) | 39/97 (40%) |
| **Correct proposal candidates** (answerable) | 24/97 (25%) | 21/97 (22%) | 27/97 (28%) |
| Computed proposals that are correct | 7/14 (50%) | 6/14 (43%) | 8/18 (44%) |
| Unsupported records flagged unsupported | 3/5 (60%) | 3/5 (60%) | 3/5 (60%) |
| References absent from GNIS reported absent | 3/3 (100%) | 3/3 (100%) | 3/3 (100%) |

Paired correct proposal candidates: -3% (CI -12% to +6%), p = 0.6636.

Paired correct proposal candidates (hybrid − rules): +3% (CI +0% to +7%), p = 0.25.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 1/3 (33%) | 0/3 (0%) | 1/3 (33%) |
| distance_and_direction | 15/31 (48%) | 12/31 (39%) | 16/31 (52%) |
| distance_only | 1/2 (50%) | 0/2 (0%) | 1/2 (50%) |
| named_feature | 8/72 (11%) | 9/72 (12%) | 10/72 (14%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| S001 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| S002 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S003 | answerable | C− R−  | C− R−  | C− R−  |
| S004 | answerable | C− R−  | C− R−  | C− R−  |
| S005 | answerable | C− R−  | C− R+  | C− R−  |
| S006 | unsupported | C− R−  | C+ R+  | C+ R+  |
| S007 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S008 | answerable | C− R−  | C− R−  | C− R−  |
| S009 | answerable | C+ R−  | C+ R−  | C+ R−  |
| S010 | answerable | C− R−  | C− R−  | C− R−  |
| S011 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S012 | answerable | C− R−  | C− R−  | C− R−  |
| S013 | answerable | C− R−  | C− R−  | C− R−  |
| S014 | answerable | C+ R−  | C− R−  | C− R−  |
| S015 | answerable | C+ R−  | C+ R−  | C+ R−  |
| S016 | answerable | C− R+  | C− R+  | C− R+  |
| S017 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S018 | answerable | C− R−  | C− R−  | C− R−  |
| S019 | answerable | C+ R−  | C− R−  | C+ R−  |
| S020 | answerable | C+ R−  | C− R−  | C− R−  |
| S021 | answerable | C− R−  | C− R+  | C− R−  |
| S022 | answerable | C− R−  | C− R−  | C− R−  |
| S023 | answerable | C− R−  | C− R−  | C− R−  |
| S024 | answerable | C− R−  | C− R−  | C− R−  |
| S025 | answerable | C− R+  | C− R−  | C− R+  |
| S026 | answerable | C− R−  | C− R+  | C− R+  |
| S027 | answerable | C− R−  | C− R−  | C− R−  |
| S028 | answerable | C− R−  | C+ R−  | C− R−  |
| S029 | answerable | C− R−  | C− R−  | C− R−  |
| S030 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S031 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| S032 | answerable | C− R+  | C− R+  | C− R+  |
| S033 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| S034 | answerable | C− R−  | C− R−  | C− R−  |
| S035 | answerable | C− R−  | C− R−  | C− R−  |
| S036 | answerable | C− R−  | C− R−  | C− R−  |
| S037 | answerable | C− R−  | C− R−  | C− R−  |
| S038 | answerable | C+ R−  | C− R+  | C− R+  |
| S039 | answerable | C− R−  | C− R−  | C− R−  |
| S040 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S041 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S042 | answerable | C− R+  | C− R+  | C− R+  |
| S043 | answerable | C− R−  | C− R−  | C− R−  |
| S044 | answerable | C− R−  | C− R−  | C− R−  |
| S045 | answerable | C− R+  | C− R+  | C− R+  |
| S046 | answerable | C− R−  | C+ R−  | C− R−  |
| S047 | answerable | C+ R−  | C+ R−  | C+ R−  |
| S048 | answerable | C+ R−  | C− R−  | C− R−  |
| S049 | answerable | C− R−  | C− R−  | C− R−  |
| S050 | answerable | C− R−  | C− R−  | C− R−  |
| S051 | answerable | C− R−  | C− R−  | C− R−  |
| S052 | answerable | C− R−  | C− R−  | C− R−  |
| S053 | answerable | C− R−  | C− R−  | C− R−  |
| S054 | unsupported | C− R−  | C+ R−  | C− R−  |
| S055 | unsupported | C− R−  | C− R−  | C− R−  |
| S056 | answerable | C− R−  | C− R−  | C− R−  |
| S057 | answerable | C− R−  | C− R−  | C− R−  |
| S058 | answerable | C− R−  | C− R−  | C− R−  |
| S059 | answerable | C− R−  | C− R−  | C− R−  |
| S060 | answerable | C− R−  | C+ R−  | C− R−  |
| S061 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| S062 | answerable | C− R−  | C− R−  | C− R−  |
| S063 | answerable | C+ R−  | C− R−  | C− R−  |
| S064 | answerable | C− R−  | C+ R−  | C− R−  |
| S065 | answerable | C− R−  | C− R−  | C− R−  |
| S066 | answerable | C− R−  | C− R+  | C− R−  |
| S067 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| S068 | answerable | C+ R−  | C+ R−  | C+ R−  |
| S069 | answerable | C− R+  | C− R−  | C− R+  |
| S070 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| S071 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S072 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S073 | answerable | C− R−  | C− R−  | C− R−  |
| S074 | answerable | C− R−  | C− R−  | C− R−  |
| S075 | answerable | C− R−  | C− R−  | C− R−  |
| S076 | answerable | C− R−  | C− R+  | C− R+  |
| S077 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S078 | answerable | C− R−  | C− R−  | C− R−  |
| S079 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S080 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S081 | unsupported | C− R−  | C− R−  | C− R−  |
| S082 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| S083 | answerable | C+ R−  | C− R+  | C+ R−  |
| S084 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| S085 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S086 | answerable | C− R−  | C+ R−  | C− R−  |
| S087 | answerable | C− R−  | C+ R−  | C− R−  |
| S088 | unsupported | C− R−  | C+ R−  | C− R−  |
| S089 | answerable | C− R−  | C− R+  | C− R−  |
| S090 | unsupported | C− R+  | C− R+  | C− R+  |
| S091 | answerable | C− R+  | C− R−  | C− R+  |
| S092 | answerable | C− R−  | C− R−  | C− R−  |
| S093 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| S094 | answerable | C− R−  | C− R−  | C− R−  |
| S095 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| S096 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S097 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S098 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| S099 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| S100 | answerable | C− R−  | C− R+  | C− R−  |
| S101 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| S102 | reference_absent | C− R−  | C− R−  | C− R−  |
| S103 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S104 | answerable | C− R−  | C− R−  | C− R−  |
| S105 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| S106 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| S107 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S108 | answerable | C− R−  | C− R−  | C− R−  |
| S109 | answerable | C− R−  | C− R−  | C− R−  |
| S110 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S111 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |
| S112 | answerable | C− R−  | C− R−  | C− R−  |
| S113 | answerable | C+ R−  | C+ R−  | C+ R−  |
| S114 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S115 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| S116 | answerable | C− R−  | C− R+  | C− R−  |
| S117 | answerable | C− R−  | C+ R+ ✓ | C− R−  |
| S118 | unsupported | C+ R−  | C− R−  | C+ R−  |
| S119 | answerable | C− R−  | C− R−  | C− R−  |
| S120 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |

</details>
