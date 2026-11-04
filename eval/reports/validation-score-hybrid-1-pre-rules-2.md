# validation: scores against the owner's annotations

rules `rules-1` · llm `llm-x2g2-qwen3.5-4b-q4km` · hybrid `hybrid-1` · specimens `gbif-cu-2026-11-01`

Annotated records: 60. Categories: answerable 32 · reference_absent 24 · unsupported 4. Annotated types: named_feature 36 · distance_and_direction 13 · direction_only 5 · distance_only 2 · between_features 2 · admin_only 1 · route_relative 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 60 records; wide intervals.

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 32/60 (53%) | 30/60 (50%) | 33/60 (55%) |
| Extraction passed validation | 60/60 (100%) | 57/60 (95%) | 60/60 (100%) |
| Critical interpretation exact | 25/60 (42%) | 23/60 (38%) | 26/60 (43%) |
| Reference top-1 acceptable (answerable) | 15/32 (47%) | 18/32 (56%) | 19/32 (59%) |
| Reference in top 5 (answerable) | 15/32 (47%) | 18/32 (56%) | 19/32 (59%) |
| **Correct proposal candidates** (answerable) | 13/32 (41%) | 15/32 (47%) | 16/32 (50%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| References absent from GNIS reported absent | 12/24 (50%) | 12/24 (50%) | 11/24 (46%) |
| Place names read as no locality | 0 | 1 | 0 |
| Mean fields to correct per record | 1.78 | 1.75 | 1.72 |

**Paired, correct proposal candidates (LLM − rules):** +6% (95% bootstrap CI -9% to +22%); LLM-only 4, rules-only 2, exact sign test p = 0.6875.

**Paired, critical exact match (LLM − rules):** -3% (95% bootstrap CI -15% to +8%); LLM-only 6, rules-only 8, exact sign test p = 0.7905.

**Paired, correct proposal candidates (hybrid − rules):** +9% (95% bootstrap CI +0% to +22%); hybrid-only 3, rules-only 0, exact sign test p = 0.25.

**Paired, critical exact match (hybrid − rules):** +2% (95% bootstrap CI -3% to +8%); hybrid-only 2, rules-only 1, exact sign test p = 1.0.

<details><summary><b>Sensitivity: excluding 11 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm | hybrid |
|---|---|---|---|
| Relation read correctly | 30/49 (61%) | 28/49 (57%) | 30/49 (61%) |
| Extraction passed validation | 49/49 (100%) | 47/49 (96%) | 49/49 (100%) |
| Critical interpretation exact | 23/49 (47%) | 21/49 (43%) | 23/49 (47%) |
| Reference top-1 acceptable (answerable) | 15/32 (47%) | 18/32 (56%) | 19/32 (59%) |
| Reference in top 5 (answerable) | 15/32 (47%) | 18/32 (56%) | 19/32 (59%) |
| **Correct proposal candidates** (answerable) | 13/32 (41%) | 15/32 (47%) | 16/32 (50%) |
| Computed proposals that are correct | 0/0 | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) |
| References absent from GNIS reported absent | 8/15 (53%) | 8/15 (53%) | 7/15 (47%) |

Paired correct proposal candidates: +6% (CI -9% to +22%), p = 0.6875.

Paired correct proposal candidates (hybrid − rules): +9% (CI +0% to +22%), p = 0.25.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm | hybrid |
|---|---|---|---|
| admin_only | 0/0 | 0/0 | 0/0 |
| between_features | 0/0 | 0/0 | 0/0 |
| direction_only | 1/3 (33%) | 0/3 (0%) | 1/3 (33%) |
| distance_and_direction | 7/8 (88%) | 8/8 (100%) | 8/8 (100%) |
| distance_only | 0/0 | 0/0 | 0/0 |
| named_feature | 5/21 (24%) | 7/21 (33%) | 7/21 (33%) |
| route_relative | 0/0 | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm | hybrid |
|---|---|---|---|---|
| V001 | unsupported | C+ R−  | C− R−  | C+ R−  |
| V002 | answerable | C− R−  | C+ R+ ✓ | C+ R+ ✓ |
| V003 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| V004 | reference_absent | C− R−  | C− R−  | C− R−  |
| V005 | reference_absent | C− R−  | C− R−  | C− R−  |
| V006 | answerable | C− R−  | C− R−  | C− R−  |
| V007 | answerable | C− R−  | C− R−  | C− R−  |
| V008 | answerable | C− R−  | C− R−  | C− R−  |
| V009 | answerable | C− R−  | C− R−  | C− R−  |
| V010 | reference_absent | C− R−  | C− R−  | C− R−  |
| V011 | unsupported | C+ R−  | C− R−  | C− R−  |
| V012 | answerable | C+ R+ ✓ | C− R+  | C+ R+ ✓ |
| V013 | answerable | C− R+  | C+ R+ ✓ | C− R+  |
| V014 | answerable | C− R−  | C− R−  | C− R−  |
| V015 | answerable | C− R+  | C− R−  | C− R+  |
| V016 | answerable | C− R−  | C− R−  | C− R−  |
| V017 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V018 | reference_absent | C− R−  | C− R−  | C− R−  |
| V019 | reference_absent | C− R−  | C− R−  | C− R−  |
| V020 | reference_absent | C− R−  | C− R−  | C− R−  |
| V021 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V022 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V023 | reference_absent | C− R−  | C− R−  | C− R−  |
| V024 | reference_absent | C− R−  | C− R−  | C− R−  |
| V025 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V026 | reference_absent | C− R−  | C− R−  | C− R−  |
| V027 | reference_absent | C− R−  | C+ R−  | C− R−  |
| V028 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V029 | answerable | C− R−  | C+ R−  | C− R−  |
| V030 | answerable | C− R−  | C− R−  | C− R−  |
| V031 | answerable | C− R−  | C− R−  | C− R−  |
| V032 | unsupported | C− R−  | C− R−  | C− R−  |
| V033 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| V034 | reference_absent | C− R−  | C− R−  | C− R−  |
| V035 | answerable | C− R−  | C− R−  | C− R−  |
| V036 | reference_absent | C− R−  | C− R−  | C− R−  |
| V037 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| V038 | reference_absent | C− R−  | C− R−  | C− R−  |
| V039 | reference_absent | C+ R−  | C− R−  | C+ R−  |
| V040 | reference_absent | C− R−  | C− R−  | C− R−  |
| V041 | reference_absent | C− R−  | C− R−  | C− R−  |
| V042 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V043 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V044 | unsupported | C− R−  | C+ R−  | C− R−  |
| V045 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| V046 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V047 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| V048 | answerable | C− R−  | C− R+  | C− R+  |
| V049 | answerable | C− R−  | C− R+  | C− R−  |
| V050 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V051 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| V052 | reference_absent | C− R−  | C+ R−  | C+ R−  |
| V053 | reference_absent | C− R−  | C− R−  | C− R−  |
| V054 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V055 | answerable | C− R−  | C− R−  | C− R−  |
| V056 | answerable | C+ R+ ✓ | C+ R+ ✓ | C+ R+ ✓ |
| V057 | answerable | C+ R−  | C+ R+ ✓ | C+ R+ ✓ |
| V058 | reference_absent | C+ R−  | C+ R−  | C+ R−  |
| V059 | answerable | C+ R−  | C+ R−  | C+ R−  |
| V060 | answerable | C+ R+ ✓ | C− R−  | C+ R+ ✓ |

</details>
