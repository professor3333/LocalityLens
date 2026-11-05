# Dataset card

What LocalityLens is built and evaluated on: where the data comes from, how it was filtered,
sampled, split and annotated, and what that means for the results.

## Sources

| Source | Snapshot | Pinned by | Licence |
|---|---|---|---|
| University of Colorado Museum of Natural History Herbarium, vascular plants (GBIF dataset `7c5e863f-3f70-4933-b05d-fc57c66dd3f3`) | `gbif-cu-2026-11-01`: GBIF download `0020715-261023074918325`, DOI [10.15468/dl.hqxjjf](https://doi.org/10.15468/dl.hqxjjf), 311,988 records, the whole dataset as a Darwin Core Archive | [manifest](../data/manifests/gbif-cu-2026-11-01.json): zip SHA-256 `089633a5b80aed48…`, 164,985,562 bytes | CC BY 4.0 |
| USGS GNIS: Domestic Names (Colorado) and All Names (National) | `gnis-co-2026-09-29`: 26,429 features, 4,190 variant names | [manifest](../data/manifests/gnis-co-2026-09-29.json): SHA-256 of both zips | U.S. public domain |

**Citations:**
- *GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf*
- *U.S. Geological Survey, Geographic Names Information System (GNIS) Domestic Names for CO
  (published 2026-09-29) and All Names (National).* USGS asks for acknowledgment in derived
  products.

**Snapshot handling:**
- Raw files are never committed. Each manifest holds URLs, hashes, sizes and dates, so a
  snapshot can be downloaded again and checked byte for byte.
- GBIF may erase the archive after 2027-05-01. The DOI stays resolvable, and the manifest
  stores the exact query so it can be reissued.
- GNIS coordinates are NAD83 (GRS80 ellipsoid), as stated in its metadata.

## Filtering: every record accounted for

The model reads the specimen's `locality` text from `verbatim.txt`. `verbatimLocality` is
empty for every Colorado record. Screening (`SCREEN_VERSION` 1, `uv run localitylens ingest
scan`) gives each excluded record the first reason that applies:

| Reason | Records |
|---|---|
| `outside_colorado` | 148,265 |
| `no_state`: not inferred from coordinates, since that would use the answer | 55,912 |
| `sensitive_withheld`: `informationWithheld` or `dataGeneralizations` present | 1,745 |
| `no_locality_on_label` | 325 |
| `no_locality_text` | 134 |
| `cultivated_note_only` | 60 |
| `state_uncertain` | 3 |
| `not_united_states` | 0 |
| **Eligible** | **105,544** |

Eligible records are grouped by wording (name key) within their supplied county
(`GROUPING_VERSION` 1), giving **40,444 locality groups**. A curator georeferences each distinct
wording once, so every sample counts groups, not specimens.

**Sensitive records** are excluded at screening and never sampled. Nothing in the project tries
to recover a location a publisher withheld or generalized.

## Samples and splits

| Set | Records | Drawn by | Role |
|---|---|---|---|
| Audit | 50 | seed `audit-50/1`, uniform over groups | Dev data: first comparison, then development |
| dev-1 | 50 | seed `dev-1/1`, stratified by label shape: 15 bare names, 15 offsets, 20 other | Dev data: prompt v2 was written on it |
| Validation | 60 | seed `benchmark/1`, uniform | Held out, then read when scored with frozen systems |
| Locked test | 120 | seed `benchmark/1`, uniform | Scored only under declared releases. Per-record outputs are never read |

**Leakage controls:**
- **Collecting events.** Groups that share a collector and an exact date are joined into
  leakage components (`EVENT_GROUPING_VERSION` 1: 15,955 components). Validation and test take
  at most one group per component.
- **Viewed groups.** Every group read during development is listed in
  [`eval/viewed-groups.json`](../eval/viewed-groups.json). Its components (93, holding 3,550
  groups) are excluded from both held-out splits.
- **Reserved groups.** All 1,942 groups of held-out components are reserved in the write-once
  [`eval/splits.lock.json`](../eval/splits.lock.json), and dev samples exclude them.
- **Model inputs** come from an allowlist: locality, state, county, country. Coordinates,
  uncertainty and georeference fields never reach a prompt.

## Annotation

One annotator (the project owner) annotated every set **before seeing any system output for
it**, following [`eval/annotation_guide.md`](../eval/annotation_guide.md):

- **What each record gets:** description type, supported or not, reference features, every
  acceptable GNIS ID (or `absent`), distance, unit, direction, qualifiers, missing information
  and notes.
- **Unsure values** are marked with `?` and reported as a sensitivity analysis.
- **Checks:** `audit score` refuses a worksheet with errors (inventories, GNIS IDs that exist,
  internal consistency).

| Set | Answerable | Reference absent from GNIS | Unsupported | Rows with an unsure mark |
|---|---|---|---|---|
| Audit | 31 | 15 | 4 | 10 |
| dev-1 | 29 | 17 | 4 | 9 |
| Validation | 32 | 24 | 4 | 11 |
| Locked test | 56 | 48 | 16 | 23 |

An **answerable** record is supported and has at least one acceptable GNIS ID. In 104 of the
280 records, the reference is absent from GNIS. GNIS Domestic Names has no mine or locale
classes, so cultural features such as mines and ranches cannot be matched. The counts by
feature kind were not tallied.

### Reviewed feature extents

[`data/reviewed/extents.csv`](../data/reviewed/) holds measured extents for the references of
the dev and validation annotations: one row per GNIS feature, 115 rows (68 measured). Each measurement is the
radial from the GNIS representative point to the farthest point of the feature (Best Practices
§3.4.1). Each row records its method, source, who measured it and the date, and is checked
against the snapshot. Rows with no measurement stay pending. The README there gives the
current count. Summit and gap edges are terrain judgments, not mapped limits, so they are
rougher than town limits. Gaps follow a rule of this project, because the Quick Reference Guide
has none for passes.

## Licence layering

- **Specimen data:** CC BY 4.0. Sample files keep label text unchanged and include no
  georeference fields. Selection and annotation columns are modifications by this project and
  are marked as such.
- **GNIS:** U.S. public domain, with acknowledgment requested.
- **Measured extents:** each row names its map source, so the terms of that source apply to
  how the measurement may be reused.
- **Code:** MIT ([LICENSE](../LICENSE)).

## Known biases and limitations

- **One herbarium, one state, English labels.** Nothing here measures other collections,
  regions or languages.
- **One annotator.** No second reviewer yet, and no repeat-annotation self-consistency check
  yet.
- **Small sets.** 56 answerable test records give wide intervals: one record is 1.8 points.
- **Grouping is not independence.** Grouping removes identical wordings and known shared
  events, but different wordings of one place by different collectors can still fall in
  different splits.
- **GNIS is current, labels are historical.** Old names, vanished settlements and changed
  county lines may be missing or misleading. GNIS lists one primary county per feature.
- **GNIS gives points, not shapes.** Feature extent is unknown until measured.
- **Existing specimen coordinates are not ground truth** and are not used.
