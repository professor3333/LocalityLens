# test: scores against the owner's annotations

rules `rules-1` · llm `llm-x2g2-qwen3.5-4b-q4km` · specimens `gbif-cu-2026-11-01`

Annotated records: 120. Categories: answerable 56 · reference_absent 48 · unsupported 16. Annotated types: named_feature 70 · distance_and_direction 17 · direction_only 15 · route_relative 8 · between_features 6 · distance_only 2 · itinerary 1 · admin_only 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 120 records; wide intervals.

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 69/120 (57%) | 66/120 (55%) |
| Extraction passed validation | 120/120 (100%) | 105/120 (88%) |
| Critical interpretation exact | 56/120 (47%) | 47/120 (39%) |
| Reference top-1 acceptable (answerable) | 25/56 (45%) | 25/56 (45%) |
| Reference in top 5 (answerable) | 26/56 (46%) | 26/56 (46%) |
| **Correct proposal candidates** (answerable) | 19/56 (34%) | 15/56 (27%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 7/16 (44%) | 9/16 (56%) |
| References absent from GNIS reported absent | 17/48 (35%) | 26/48 (54%) |
| Place names read as no locality | 0 | 2 |
| Mean fields to correct per record | 1.63 | 1.76 |

**Paired, correct proposal candidates (LLM − rules):** -7% (95% bootstrap CI -23% to +7%); LLM-only 8, rules-only 12, exact sign test p = 0.5034.

**Paired, critical exact match (LLM − rules):** -8% (95% bootstrap CI -18% to +3%); LLM-only 18, rules-only 27, exact sign test p = 0.2327.

<details><summary><b>Sensitivity: excluding 23 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 57/97 (59%) | 55/97 (57%) |
| Extraction passed validation | 97/97 (100%) | 86/97 (89%) |
| Critical interpretation exact | 47/97 (48%) | 40/97 (41%) |
| Reference top-1 acceptable (answerable) | 22/50 (44%) | 23/50 (46%) |
| Reference in top 5 (answerable) | 23/50 (46%) | 24/50 (48%) |
| **Correct proposal candidates** (answerable) | 17/50 (34%) | 15/50 (30%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 5/10 (50%) | 7/10 (70%) |
| References absent from GNIS reported absent | 13/37 (35%) | 21/37 (57%) |

Paired correct proposal candidates: -4% (CI -20% to +12%), p = 0.8145.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm |
|---|---|---|
| admin_only | 0/0 | 0/0 |
| between_features | 0/0 | 0/0 |
| direction_only | 5/7 (71%) | 0/7 (0%) |
| distance_and_direction | 2/9 (22%) | 4/9 (44%) |
| distance_only | 0/2 (0%) | 0/2 (0%) |
| itinerary | 0/0 | 0/0 |
| named_feature | 12/38 (32%) | 11/38 (29%) |
| route_relative | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm |
|---|---|---|---|
| T001 | answerable | C+ R+ ✓ | C+ R−  |
| T002 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T003 | answerable | C+ R−  | C+ R+ ✓ |
| T004 | reference_absent | C+ R−  | C+ R−  |
| T005 | reference_absent | C− R−  | C− R−  |
| T006 | answerable | C+ R+ ✓ | C− R+  |
| T007 | unsupported | C− R−  | C+ R−  |
| T008 | unsupported | C− R−  | C− R−  |
| T009 | answerable | C− R−  | C− R−  |
| T010 | answerable | C− R−  | C− R+  |
| T011 | answerable | C− R−  | C+ R+ ✓ |
| T012 | answerable | C+ R−  | C+ R+ ✓ |
| T013 | reference_absent | C− R−  | C+ R−  |
| T014 | reference_absent | C+ R−  | C+ R−  |
| T015 | reference_absent | C− R−  | C− R−  |
| T016 | unsupported | C+ R−  | C− R−  |
| T017 | answerable | C− R−  | C− R+  |
| T018 | reference_absent | C− R−  | C− R−  |
| T019 | answerable | C+ R−  | C+ R−  |
| T020 | unsupported | C− R+  | C+ R−  |
| T021 | answerable | C− R−  | C− R−  |
| T022 | answerable | C− R+  | C− R−  |
| T023 | reference_absent | C+ R−  | C+ R−  |
| T024 | reference_absent | C− R−  | C− R−  |
| T025 | reference_absent | C+ R−  | C− R−  |
| T026 | unsupported | C− R−  | C+ R−  |
| T027 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T028 | answerable | C− R+  | C+ R+ ✓ |
| T029 | unsupported | C− R−  | C− R−  |
| T030 | reference_absent | C− R−  | C− R−  |
| T031 | answerable | C+ R−  | C− R−  |
| T032 | answerable | C+ R+ ✓ | C− R+  |
| T033 | reference_absent | C+ R−  | C− R−  |
| T034 | answerable | C− R−  | C− R+  |
| T035 | reference_absent | C+ R−  | C− R−  |
| T036 | reference_absent | C+ R−  | C+ R−  |
| T037 | answerable | C− R−  | C− R−  |
| T038 | reference_absent | C− R−  | C− R−  |
| T039 | unsupported | C− R−  | C− R−  |
| T040 | reference_absent | C+ R−  | C− R−  |
| T041 | unsupported | C− R−  | C− R−  |
| T042 | unsupported | C+ R−  | C+ R−  |
| T043 | answerable | C+ R−  | C− R−  |
| T044 | answerable | C− R−  | C− R−  |
| T045 | reference_absent | C− R−  | C− R−  |
| T046 | answerable | C− R−  | C− R−  |
| T047 | reference_absent | C+ R−  | C+ R−  |
| T048 | reference_absent | C+ R−  | C− R−  |
| T049 | unsupported | C− R−  | C− R−  |
| T050 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T051 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T052 | answerable | C− R+  | C− R+  |
| T053 | reference_absent | C+ R−  | C− R−  |
| T054 | reference_absent | C− R−  | C− R−  |
| T055 | answerable | C+ R−  | C− R−  |
| T056 | reference_absent | C+ R−  | C+ R−  |
| T057 | answerable | C− R−  | C− R−  |
| T058 | reference_absent | C+ R−  | C− R−  |
| T059 | reference_absent | C+ R−  | C− R−  |
| T060 | answerable | C− R−  | C− R−  |
| T061 | answerable | C+ R+ ✓ | C− R−  |
| T062 | reference_absent | C− R−  | C+ R−  |
| T063 | reference_absent | C− R−  | C− R−  |
| T064 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T065 | answerable | C+ R−  | C+ R−  |
| T066 | reference_absent | C− R−  | C− R−  |
| T067 | reference_absent | C+ R−  | C− R−  |
| T068 | unsupported | C− R−  | C− R−  |
| T069 | answerable | C− R−  | C+ R+ ✓ |
| T070 | answerable | C− R−  | C− R−  |
| T071 | reference_absent | C− R−  | C+ R−  |
| T072 | reference_absent | C− R−  | C+ R−  |
| T073 | answerable | C+ R−  | C+ R+ ✓ |
| T074 | reference_absent | C+ R−  | C− R−  |
| T075 | answerable | C− R−  | C− R−  |
| T076 | answerable | C+ R−  | C+ R+ ✓ |
| T077 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T078 | reference_absent | C− R−  | C+ R−  |
| T079 | unsupported | C− R−  | C+ R−  |
| T080 | reference_absent | C− R−  | C− R−  |
| T081 | reference_absent | C− R−  | C+ R−  |
| T082 | reference_absent | C− R−  | C− R−  |
| T083 | answerable | C+ R+ ✓ | C− R+  |
| T084 | unsupported | C− R−  | C− R−  |
| T085 | reference_absent | C− R−  | C− R−  |
| T086 | answerable | C+ R+ ✓ | C− R−  |
| T087 | answerable | C+ R+ ✓ | C− R−  |
| T088 | answerable | C− R−  | C− R−  |
| T089 | answerable | C− R−  | C− R+  |
| T090 | reference_absent | C− R−  | C− R−  |
| T091 | answerable | C+ R+ ✓ | C− R−  |
| T092 | reference_absent | C+ R−  | C+ R−  |
| T093 | reference_absent | C− R−  | C+ R−  |
| T094 | reference_absent | C+ R−  | C− R−  |
| T095 | answerable | C+ R+ ✓ | C− R−  |
| T096 | reference_absent | C+ R−  | C+ R−  |
| T097 | answerable | C− R−  | C− R−  |
| T098 | unsupported | C+ R−  | C− R−  |
| T099 | reference_absent | C+ R−  | C+ R−  |
| T100 | answerable | C+ R+ ✓ | C− R+  |
| T101 | answerable | C− R−  | C− R−  |
| T102 | answerable | C− R−  | C− R−  |
| T103 | reference_absent | C− R−  | C− R−  |
| T104 | answerable | C+ R+ ✓ | C+ R−  |
| T105 | reference_absent | C+ R−  | C− R−  |
| T106 | answerable | C+ R−  | C+ R+ ✓ |
| T107 | answerable | C− R−  | C+ R−  |
| T108 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| T109 | unsupported | C+ R−  | C+ R−  |
| T110 | answerable | C− R−  | C− R−  |
| T111 | reference_absent | C− R−  | C+ R−  |
| T112 | reference_absent | C+ R−  | C+ R−  |
| T113 | reference_absent | C+ R−  | C+ R−  |
| T114 | unsupported | C− R−  | C− R−  |
| T115 | reference_absent | C− R−  | C− R−  |
| T116 | answerable | C− R+  | C− R−  |
| T117 | answerable | C+ R+ ✓ | C− R+  |
| T118 | answerable | C− R+  | C+ R−  |
| T119 | reference_absent | C− R−  | C+ R−  |
| T120 | answerable | C− R+  | C− R−  |

</details>
