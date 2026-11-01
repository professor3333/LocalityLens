# 50-record feasibility audit

The first milestone asks one question: on real Colorado labels, does an LLM give **more correct,
useful proposals with less human effort** than a rules baseline? This folder holds the sample
and the annotation worksheet. System outputs live in [`../reports/`](../reports/).

## Order of work

1. **Annotate [`worksheet.csv`](worksheet.csv) first**, without opening any system report.
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

Work from the `locality` text and the supplied `county` column only. Use maps or GNIS to
identify features, never to work out where the specimen "really" is. Mark any value you are
unsure of with `?` and explain in `notes`. A flagged label is better than a guessed one.

**Two passes.** Pass 1: every column except `acceptable_gnis_ids`, from the text alone.
Pass 2: look up GNIS IDs. Doing it second keeps search results from shaping how you read the label.

**One clause.** When a label chains several clauses, annotate the clause a curator would
georeference: the most specific one, giving the smallest area. List the other clauses in `notes`
as `multi: …`.

| Column | Fill with |
|---|---|
| `description_type` | The chosen clause's type: `named_feature` (including "N slope of X", "summit of X", "above X"), `distance_and_direction` (straight line; "air mi" counts), `distance_only`, `direction_only`, `route_relative` ("road mi", "up the road", "along the trail"), `itinerary`, `between_features`, `orthogonal_offsets`, `admin_only`, `habitat_only`, `no_locality` |
| `supported` | `yes` for named feature, distance + direction, distance only, direction only, or an ambiguous name a curator could settle. `no` otherwise. `no` means outside v1 scope, not that the record cannot be georeferenced |
| `reference_features` | The place(s) the clause is measured from, spelled as on the label (`;`-separated) |
| `acceptable_gnis_ids` | Every defensible GNIS feature ID from our snapshot (`;`-separated), `absent` if not in GNIS, blank if there is no reference |
| `distance` | As written: `2`, `1.5`, `1/2`, `20-21` (for a range, also note `range`) |
| `unit` | `mile`, `kilometre`, `metre`, `foot`, `yard`. A bare "m" (miles or metres?): leave blank and add `unit` to missing |
| `direction` | 16-point code `N` `NNE` … `NNW` ("S.E." is `SE`). Blank for "upstream", "above" and the like |
| `qualifiers` | As written, `;`-separated: about, ca., approx., near, vicinity, `?` |
| `missing_information` | From: `extent`, `which_feature`, `distance`, `unit`, `direction`, `route_geometry`, `feature_not_in_gnis`, `historical_name`, `other: …` |
| `notes` | `multi: …`, `bracketed: …` (text in square brackets was added by someone other than the collector), positions on a feature, elevation, doubts |

Elevations ("9,800 ft") are not distances. "Co." means county. "Mt.", "Cr." and "Canon" are read
as Mount, Creek and Canyon.

**Finding GNIS IDs:**

```bash
uv run localitylens gazetteer search "Mount Zenobia" --county Moffat --limit 10
uv run localitylens gazetteer search "Zenobia" --limit 10
```

Try spelling variants. If the label could mean either of two features, list both and add
`which_feature`.

**Saving:** keep the file as CSV, UTF-8, with the same name. In Excel, set `gbif_id` to Text.
**Self-consistency:** about a week later, re-annotate about 10 random records without looking at
your first answers. With one annotator, the agreement rate is what gets published.

## Data licence and attribution

Records come from the **University of Colorado Museum of Natural History Herbarium Vascular
Plant Collection**, published under **CC BY 4.0**. Cite: *GBIF.org (01 November 2026) GBIF
Occurrence Download https://doi.org/10.15468/dl.hqxjjf*. The selection, grouping and annotation
columns are modifications made by this project. The label text itself is unchanged.
Coordinates and other georeference fields were not read and are not included.
