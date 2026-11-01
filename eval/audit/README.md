# 50-record feasibility audit

The first milestone asks one question: on real Colorado labels, does an LLM give **more correct,
useful proposals with less human effort** than a rules baseline? This folder holds the sample
and the annotation worksheet. System outputs live in [`../reports/`](../reports/).

## Order of work

1. **Annotate [`worksheet.csv`](worksheet.csv) first** (done), without opening any system report.
2. Then compare against the rules report ([`audit-50-rules-1.md`](../reports/audit-50-rules-1.md))
   and, once it exists, the LLM report.

These 50 records, and every record in their locality groups, belong to the **dev** split. They
have been read during development, so they can never be part of the locked test set.

## How the sample was drawn

Reproduce it with `uv run localitylens audit sample` (defaults: snapshot
`data/raw/gbif/2026-11-01`, `--n 50`, `--seed audit-50/1`).

| Step | Rule | Records |
|---|---|---|
| Snapshot | `gbif-cu-2026-11-01`, DOI [10.15468/dl.hqxjjf](https://doi.org/10.15468/dl.hqxjjf) | 311,988 |
| Screen (`SCREEN_VERSION` 1) | Colorado, United States, not withheld, real locality text | 105,544 eligible |
| Group (`GROUPING_VERSION` 1) | same wording (name key) in the same supplied county | 40,444 groups |
| Sample | the 50 groups first in `sha256(seed \| group_key)` order; each shown by its lowest gbifID | 50 |

Sampling is per **group**, not per specimen. A curator georeferences each distinct locality once,
so "Boulder." on hundreds of sheets counts once.

<details>
<summary><b>Exclusions, with reasons (every record is accounted for)</b></summary>

| Reason | Records | Rule |
|---|---|---|
| `outside_colorado` | 148,265 | `stateProvince` is another state or country |
| `no_state` | 55,912 | `stateProvince` empty. Not inferred from coordinates, since that would use the answer |
| `sensitive_withheld` | 1,745 | `informationWithheld` or `dataGeneralizations` present (invariant 11) |
| `no_locality_on_label` | 325 | Whole-string placeholders: `[No locality data provided on the label.]`, `Unknown.` |
| `no_locality_text` | 134 | `locality` empty |
| `cultivated_note_only` | 60 | Only a bracketed note such as `[Cultivated specimen.]` |
| `state_uncertain` | 3 | `Colorado?`, `Colorado/Wyoming` |
| `not_united_states` | 0 | Colorado record with a non-US country |

Reproduce with `uv run localitylens ingest scan`.

</details>

## How to annotate

Follow the shared [annotation guide](../annotation_guide.md).

## Data licence and attribution

Records come from the **University of Colorado Museum of Natural History Herbarium Vascular
Plant Collection**, published under **CC BY 4.0**. Cite: *GBIF.org (01 November 2026) GBIF
Occurrence Download https://doi.org/10.15468/dl.hqxjjf*. The selection, grouping and annotation
columns are modifications made by this project. The label text itself is unchanged.
Coordinates and other georeference fields were not read and are not included.
