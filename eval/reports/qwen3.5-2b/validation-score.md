# validation: scores against the owner's annotations

rules `rules-2` · llm `llm-x2g2-qwen3.5-2b-q4km` · specimens `gbif-cu-2026-11-01`

Annotated records: 60. Categories: answerable 32 · reference_absent 24 · unsupported 4. Annotated types: named_feature 36 · distance_and_direction 13 · direction_only 5 · distance_only 2 · between_features 2 · admin_only 1 · route_relative 1.

> A **correct proposal candidate** is an answerable record whose critical interpretation (relation, distance, unit, direction, qualifiers) matches the annotation and whose top-ranked reference is an acceptable GNIS ID. It becomes a correct proposal once the feature extent is supplied. One annotator; 60 records; wide intervals.

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 32/60 (53%) | 37/60 (62%) |
| Extraction passed validation | 60/60 (100%) | 40/60 (67%) |
| Critical interpretation exact | 26/60 (43%) | 21/60 (35%) |
| Reference top-1 acceptable (answerable) | 15/32 (47%) | 7/32 (22%) |
| Reference in top 5 (answerable) | 15/32 (47%) | 8/32 (25%) |
| **Correct proposal candidates** (answerable) | 13/32 (41%) | 6/32 (19%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 3/4 (75%) | 2/4 (50%) |
| References absent from GNIS reported absent | 13/24 (54%) | 15/24 (62%) |
| Place names read as no locality | 0 | 1 |
| Mean fields to correct per record | 1.85 | 2.6 |

**Paired, correct proposal candidates (LLM − rules):** -22% (95% bootstrap CI -44% to +0%); LLM-only 3, rules-only 10, exact sign test p = 0.0923.

**Paired, critical exact match (LLM − rules):** -8% (95% bootstrap CI -25% to +8%); LLM-only 11, rules-only 16, exact sign test p = 0.4421.

<details><summary><b>Sensitivity: excluding 11 rows with an unsure (?) annotation</b></summary>

| Metric | rules | llm |
|---|---|---|
| Relation read correctly | 30/49 (61%) | 34/49 (69%) |
| Extraction passed validation | 49/49 (100%) | 31/49 (63%) |
| Critical interpretation exact | 24/49 (49%) | 19/49 (39%) |
| Reference top-1 acceptable (answerable) | 15/32 (47%) | 7/32 (22%) |
| Reference in top 5 (answerable) | 15/32 (47%) | 8/32 (25%) |
| **Correct proposal candidates** (answerable) | 13/32 (41%) | 6/32 (19%) |
| Computed proposals that are correct | 0/0 | 0/0 |
| Unsupported records flagged unsupported | 2/2 (100%) | 1/2 (50%) |
| References absent from GNIS reported absent | 9/15 (60%) | 10/15 (67%) |

Paired correct proposal candidates: -22% (CI -44% to +0%), p = 0.0923.

</details>

<details><summary><b>Correct proposal candidates by annotated type</b></summary>

| Type | rules | llm |
|---|---|---|
| admin_only | 0/0 | 0/0 |
| between_features | 0/0 | 0/0 |
| direction_only | 1/3 (33%) | 0/3 (0%) |
| distance_and_direction | 7/8 (88%) | 0/8 (0%) |
| distance_only | 0/0 | 0/0 |
| named_feature | 5/21 (24%) | 6/21 (29%) |
| route_relative | 0/0 | 0/0 |

</details>

<details><summary><b>Per record</b> (C = critical interpretation, R = top-1 reference, ✓ correct candidate)</summary>

| id | category | rules | llm |
|---|---|---|---|
| V001 | unsupported | C+ R−  | C− R−  |
| V002 | answerable | C− R−  | C+ R+ ✓ |
| V003 | reference_absent | C+ R−  | C+ R−  |
| V004 | reference_absent | C+ R−  | C− R−  |
| V005 | reference_absent | C− R−  | C− R−  |
| V006 | answerable | C− R−  | C− R−  |
| V007 | answerable | C− R−  | C− R−  |
| V008 | answerable | C− R−  | C+ R+ ✓ |
| V009 | answerable | C− R−  | C− R−  |
| V010 | reference_absent | C− R−  | C− R−  |
| V011 | unsupported | C+ R−  | C− R−  |
| V012 | answerable | C+ R+ ✓ | C− R−  |
| V013 | answerable | C− R+  | C− R−  |
| V014 | answerable | C− R−  | C− R−  |
| V015 | answerable | C− R+  | C− R−  |
| V016 | answerable | C− R−  | C− R−  |
| V017 | answerable | C+ R+ ✓ | C− R−  |
| V018 | reference_absent | C− R−  | C− R−  |
| V019 | reference_absent | C− R−  | C+ R−  |
| V020 | reference_absent | C− R−  | C− R−  |
| V021 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| V022 | answerable | C+ R+ ✓ | C+ R−  |
| V023 | reference_absent | C− R−  | C− R−  |
| V024 | reference_absent | C− R−  | C− R−  |
| V025 | answerable | C+ R+ ✓ | C− R−  |
| V026 | reference_absent | C− R−  | C− R−  |
| V027 | reference_absent | C− R−  | C+ R−  |
| V028 | answerable | C+ R+ ✓ | C− R−  |
| V029 | answerable | C− R−  | C+ R−  |
| V030 | answerable | C− R−  | C+ R−  |
| V031 | answerable | C− R−  | C− R−  |
| V032 | unsupported | C− R−  | C− R−  |
| V033 | reference_absent | C+ R−  | C− R−  |
| V034 | reference_absent | C− R−  | C− R−  |
| V035 | answerable | C− R−  | C+ R−  |
| V036 | reference_absent | C− R−  | C+ R−  |
| V037 | reference_absent | C+ R−  | C− R−  |
| V038 | reference_absent | C− R−  | C− R−  |
| V039 | reference_absent | C+ R−  | C+ R−  |
| V040 | reference_absent | C− R−  | C− R−  |
| V041 | reference_absent | C− R−  | C− R−  |
| V042 | answerable | C+ R+ ✓ | C− R−  |
| V043 | answerable | C+ R+ ✓ | C− R−  |
| V044 | unsupported | C− R−  | C+ R−  |
| V045 | answerable | C+ R−  | C+ R−  |
| V046 | answerable | C+ R+ ✓ | C− R−  |
| V047 | reference_absent | C+ R−  | C+ R−  |
| V048 | answerable | C− R−  | C− R+  |
| V049 | answerable | C− R−  | C+ R+ ✓ |
| V050 | answerable | C+ R+ ✓ | C− R−  |
| V051 | reference_absent | C+ R−  | C− R−  |
| V052 | reference_absent | C− R−  | C+ R−  |
| V053 | reference_absent | C− R−  | C− R−  |
| V054 | answerable | C+ R+ ✓ | C− R−  |
| V055 | answerable | C− R−  | C− R−  |
| V056 | answerable | C+ R+ ✓ | C+ R+ ✓ |
| V057 | answerable | C+ R−  | C− R−  |
| V058 | reference_absent | C+ R−  | C+ R−  |
| V059 | answerable | C+ R−  | C+ R−  |
| V060 | answerable | C+ R+ ✓ | C+ R+ ✓ |

</details>
