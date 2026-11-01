<p align="center">
  <img src="docs/assets/banner.svg" alt="LocalityLens: turn historical specimen descriptions into reviewable, uncertainty-aware geographic records" width="100%">
</p>

<p align="center">
  <a href="https://github.com/professor3333/LocalityLens/actions/workflows/ci.yml"><img src="https://github.com/professor3333/LocalityLens/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python 3.12+">
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <img src="https://img.shields.io/badge/types-mypy%20strict-2A6DB2" alt="mypy strict">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-3DA639" alt="MIT licence"></a>
  <br>
  <img src="https://img.shields.io/badge/status-phase%201%20%C2%B7%20data%20%26%20feasibility-F4B860" alt="Status: Phase 1">
  <img src="https://img.shields.io/badge/gazetteer-USGS%20GNIS%202026--09--29-5FD3B5" alt="Gazetteer: USGS GNIS 2026-09-29">
  <img src="https://img.shields.io/badge/inference-local%20only-103A34" alt="Local inference only">
</p>

<p align="center">
  <a href="#-how-it-works">How it works</a> ·
  <a href="#-try-it">Try it</a> ·
  <a href="#-design-guarantees">Design guarantees</a> ·
  <a href="#-roadmap">Roadmap</a> ·
  <a href="#-data--licences">Data</a> ·
  <a href="#-development">Development</a>
</p>

---

Natural history museums hold millions of specimens whose collecting locality exists only as prose
written by the collector, often a century ago:

> *Larimer Co., Colo., 2 mi NE of Longs Peak summit.*

Before ecologists can use such a record, someone has to read the abbreviations, find the right
reference place among many with similar names, apply the offset, and decide **how uncertain** the
result is. **LocalityLens** is a review workbench for that job. A small, local language model
*reads* the description. Ordinary, tested code finds the places and does the geometry. A
curator approves, corrects, or defers every result before it is exported as Darwin Core.

> [!NOTE]
> **Early development: Phase 1 (data & feasibility).** This README separates what exists
> (✅) from what is planned (🔜). Measured results will be published only once the evaluation
> benchmark is frozen.

## 🧭 How it works

<p align="center">
  <img src="docs/assets/pipeline.svg" alt="Pipeline: locality text, extraction, validation, retrieval, disambiguation, geometry, review and export, each marked built, partly built or planned" width="100%">
</p>

The split between the stages is the core idea:

| The language model does | Deterministic code does |
|---|---|
| Read abbreviations and varied phrasing (`Colo.`, `Pk.`, `nr.`) | Look up places in a pinned gazetteer snapshot |
| Pull out relations: *what* is offset from *where*, by how much, in which direction | Parse every number and unit, and convert units exactly |
| Separate what the label **says** from what is **missing** | Compute coordinates and geodesic offsets on the source datum |
| Say which ambiguity a curator needs to resolve | Validate, track provenance, enforce statuses, export |

A **rules baseline** (regular expressions plus gazetteer name matching) fills the same contract.
It is the comparison system the LLM has to beat, and it runs through the identical validator
and retrieval, so any measured difference comes from language interpretation alone.

**The model never produces a coordinate, an ID, or a character offset.** It returns exact quotes.
Code locates those quotes in the original text, so every highlighted phrase in the review UI is
correct by construction, and an invented quote fails validation.

## ⚡ Try it

```bash
git clone https://github.com/professor3333/LocalityLens.git && cd LocalityLens
uv sync
uv run localitylens data fetch-gnis                        # ~23 MB from USGS, checksummed
uv run localitylens gazetteer build --snapshot data/raw/gnis/2026-09-29
# optional, needs a free GBIF account (GBIF_USER, GBIF_PWD, GBIF_EMAIL in .env):
uv run localitylens data fetch-gbif                        # ~165 MB Darwin Core Archive + DOI
```

**Interpret a whole label** with the rules baseline: extraction, validation and retrieval in one
command. Every value carries its `[start, end)` span in the original text:

```console
$ uv run localitylens baseline run --limit 2 \
      "Larimer Co., Colo., 2 mi NE of Longs Peak summit."
extractor   rules-1
relation    distance_and_direction
quote       "2 mi NE of Longs Peak summit" [20:48]
feature     Longs Peak [31:41] type=summit
distance    2 mile [20:21]
direction   NE [25:27]
admin       county "Larimer Co." · state "Colo."
missing     none
retrieval   candidates_found (county context: Larimer Co., from text)
  1.  204979  Longs Peak         Summit   Boulder   exact_official  type=y county=n
  2.  186722  Youngs Peak        Summit   Delta     fuzzy_official  type=y county=n
```

**Add a point-radius proposal** with `--propose`. Every uncertainty component is listed with
its rule. GNIS gives only a representative point for Longs Peak, so the extent is **unknown**,
not zero. The tool reports a lower bound and asks for the extent instead of drawing a falsely
small circle:

```console
$ uv run localitylens baseline run --limit 1 --propose \
      "Larimer Co., Colo., 2 mi NE of Longs Peak summit."
proposal    needs_information  [point-radius, policy gbif-bp-2020/1]
  point     40.27536, -105.58948 (NAD83)   feature 204979
  radius    unknown   (at least 1,657 m without extent)
    extent                   unknown  unknown
    datum                        0 m  recorded (NAD83), not transformed
    coordinate_source            0 m  gazetteer coordinate, no map measurement
    distance_precision         805 m  1-digit integer: precision 1 mile, half of it
    coordinate_precision        39 m  GNIS coordinates to the nearest second
    heading                  1,256 m  ±22.5° at 3,219 m (alone; combined geometrically)
  assume    'NE' read as bearing 45° ± 22.5° from true north (BP §3.4.5 Table 4; …)
  ask       What is the extent of Longs Peak (Summit)? GNIS gives only a representative …
```

With a reviewed extent (`--extent-m 500 --extent-note "…"`) the same record becomes
`computed` with a 2,018 m radius, and the extent's source and rationale are recorded.

**When the label is ambiguous, it asks instead of guessing.** A bare `m` might be miles or metres:

```console
$ uv run localitylens baseline run "3 m E of Estes Park" --limit 2
relation    distance_and_direction
distance    3 (unit missing) [0:1]
direction   E [4:5]
missing     distance_unit
question    Does 'm' mean miles or metres?
retrieval   candidates_found
  1.  177636  Estes Park         Flat              Larimer   exact_official
  2.  204674  Estes Park         Populated Place   Larimer   exact_official
```

**Route descriptions are flagged, not flattened** into a straight-line offset:

```console
$ uv run localitylens baseline run "5 mi up Big Thompson Canyon from Loveland"
relation    route_relative
quote       "5 mi up Big Thompson Canyon from Loveland" [0:41]
missing     route_geometry
```

### Run the local LLM

The model runs on your machine through llama.cpp. No API, no network at inference time. The
model, its quantisation, the prompt and the generation settings are pinned with checksums in
[`release/manifest.json`](release/manifest.json):

```bash
brew install llama.cpp                                     # or build llama.cpp from source
uv run localitylens model fetch                            # 2.74 GB GGUF, sha256-verified
llama-server -m models/Qwen3.5-4B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8080 -c 4096 -np 1 --no-context-shift
uv run localitylens model check                            # server matches the manifest
```

The same label, read by Qwen3.5-4B instead of the rules. The output is checked the same way:
every quote is located in the text, every number is parsed by code, and there is no field in
which a coordinate could be returned:

```console
$ uv run localitylens interpret "Larimer Co., Colo., 2 mi NE of Longs Peak summit." --limit 2
extractor   llm-x1g2-qwen3.5-4b-q4km
relation    distance_and_direction
quote       "2 mi NE of Longs Peak summit" [20:48]
feature     Longs Peak [31:41] type=summit
distance    2 mile [20:21]
direction   NE [25:27]
admin       county "Larimer Co." · state "Colo."
missing     none
retrieval   candidates_found (county context: Larimer Co., from text)
  1.  204979  Longs Peak       Summit   Boulder   exact_official   type=y county=n
  2.  186722  Youngs Peak      Summit   Delta     fuzzy_official   type=y county=n
```

<sub>Measured on an Apple M1 with 8 GB: llama-server's own footprint is 629 MB on top of the 2.74 GB
memory-mapped model file. The prompt is 1,500 tokens of the 4,096-token budget.</sub>

### Gazetteer search

**Abbreviated name, county from the label.** The right peak is found. GNIS files Longs Peak
under *Boulder* County, so the county disagreement is **shown as evidence, not used to discard
the match**:

```console
$ uv run localitylens gazetteer search "Long's Pk." --county "Larimer Co." --limit 2
  204979  Longs Peak      Summit  Boulder      exact_official  sim=100.0  county=n
  186722  Youngs Peak     Summit  Delta        fuzzy_official  sim= 85.7  county=n
```

**A former name on an old label.** Mount Evans was renamed Mount Blue Sky in 2023, and a
*different* peak in Park County is still officially "Mount Evans". Former names compete
equally with current ones, and context decides:

```console
$ uv run localitylens gazetteer search "Mt. Evans" --county "Clear Creek" --limit 2
  204716  Mount Blue Sky  Summit  Clear Creek  exact_variant   sim=100.0  county=y
  179941  Mount Evans     Summit  Park         exact_official  sim=100.0  county=n
```

**A place the gazetteer doesn't hold** is reported as absent. It is never guessed:

```console
$ uv run localitylens gazetteer search "Gold Hill Mine"
feature_absent_from_index
```

<sub>Some outputs are trimmed in width and length. The full output also shows state/type flags and the GNIS representative point (NAD83), which is evidence, not a georeference.</sub>

## 🛡️ Design guarantees

| Guarantee | How it is enforced today | |
|---|---|:-:|
| **The LLM never produces coordinates** | The output schema has no coordinate field and rejects unknown ones, free-text questions are scanned for coordinates, and the model server is loopback-only with no tools. Coordinates come only from `localitylens.geo` | ✅ |
| **Every claim cites the label** | Quotes must be found in the text and are mapped to half-open `[start, end)` spans of the *original* string | ✅ |
| **Swapped or invented details are caught** | Code re-parses quoted directions and units and rejects mismatches. A bare `m` (miles or metres?) cannot be asserted | ✅ |
| **Missing ≠ zero** | Each relation's parts must be present or explicitly declared missing. GNIS `0.0` coordinates are stored as null | ✅ |
| **Context ranks, never filters** | County, state and feature type order the candidates, and each candidate carries its evidence | ✅ |
| **Abstain rather than guess** | A bare `m` becomes "unit missing" plus a question. "Hwy 34" is not a distance. Route descriptions are labelled, not flattened. A name the gazetteer lacks is reported absent, not trimmed to a lookalike | ✅ |
| **Humans approve before export** | A single checked status machine. Only `approved` records are exportable | ✅ |
| **A point is not a place** | Without a reviewed extent (or a published default such as a spring's 3 m), the radius stays unknown. The proposal reports a lower bound and asks for the extent | ✅ |
| **Every uncertainty number is cited** | Each component carries its rule and its source: GBIF Best Practices, the Quick Reference Guide, or the Georeferencing Calculator's reference code | ✅ |
| **Reproducible provenance** | Checksummed, immutable source snapshots. The index records which snapshot built it | ✅ |
| **No answer leakage** | Coordinate and georeference columns are never read from the archive. A model sees only an allowlist: label text, state, county, country | ✅ |

<details>
<summary><b>Uncertainty policy <code>gbif-bp-2020/1</code>: rules and sources</b></summary>

| Component | Rule | Source |
|---|---|---|
| Heading | N/E/S/W ±45° · NE/SE/SW/NW ±22.5° · NNE-type ±11.25°, true north | Best Practices §3.4.5 Table 4 |
| Distance precision | Fractions: half of 1/denominator. Decimals: exact halves, quarters or eighths, else tenths or hundredths. Integers: half of 10^max(0, digits−2) | Best Practices §3.4.6; every row of Table 5 is a test |
| Distance + heading | `√((d+dp−d·cos α)² + (d·sin α)²) + coordinate precision`, where `dp` sums datum, extent and distance precision | Georeferencing Calculator `calculateMaxErrorDistance` |
| Named place, distance only | Linear sum of components (plus the offset, for distance only) | Georeferencing Calculator |
| Coordinate precision | GNIS is recorded to the nearest second: precision × √(lat m/° ² + lon m/° ²) | Georeferencing Calculator `getCoordPrecisionError` |
| Datum | Recorded (NAD83) and not transformed → 0. Unknown → 5,359 m | Best Practices §3.4.4 |
| Extent | Reviewed value, or a published default (spring 3 m). Otherwise **unknown** | Best Practices §3.4.1 · Quick Reference Guide Table 1 |
| "about", "ca." | No effect on coordinates or uncertainty | Best Practices §2.2 |
| "near", "vicinity" | No defensible default, so the record needs information | Quick Reference Guide §2.1.3.8 |
| Heading without distance | Unbounded, so the record needs information | Quick Reference Guide §2.2.2 |

Tests reproduce the published examples exactly: 10 km NE → 3.90 km (§3.4.5), a ¼° grid cell at
the equator → 39,226 m (Quick Reference Guide Table 1), and all 14 rows of Table 5.

</details>

## 🔬 Feasibility audit

The first milestone is decided on real labels, not synthetic ones. Every record in the snapshot
is accounted for:

```text
311,988  GBIF records (CU Herbarium, DOI 10.15468/dl.hqxjjf)
206,444    excluded, each with a reason (other state, no state, withheld, ...)
105,544  eligible: Colorado, not withheld, real locality text
 40,444  distinct locality groups (same wording, same county)
     50  audit sample: seeded, one record per group → eval/audit/
```

Both systems have run on the sample: the rules baseline
([report](eval/reports/audit-50-rules-1.md), [findings](eval/reports/audit-50-rules-1-findings.md))
and Qwen3.5-4B ([report](eval/reports/audit-50-llm-x1g2-qwen3.5-4b-q4km.md),
[findings](eval/reports/audit-50-llm-x1g2-qwen3.5-4b-q4km-findings.md)). These are **system
outcomes, not accuracy**: correctness waits for blind annotation of the
[worksheet](eval/audit/worksheet.csv).

| On 50 real labels | Rules `rules-1` | LLM `llm-x1g2` (Qwen3.5-4B Q4_K_M) |
|---|---|---|
| Relation read | named feature 22 · distance + direction 14 · direction only 10 · other 2 · distance only 1 · route 1 | distance + direction 24 · named feature 13 · no locality 7 · route 5 · itinerary 1 |
| Rejected by validation | 0 | 9 (inexact quotes, contradictions, unparseable numbers) |
| Retrieval | candidates found 33 · absent from GNIS 14 · no reference 3 | candidates found 22 · absent from GNIS 12 · no reference 7 |
| Proposal | needs information 46 · unsupported 3 · computed 1 | needs information 27 · unsupported 13 · computed 1 |
| Time per record | milliseconds | p50 10.2 s · p95 14.7 s (Apple M1, 8 GB) |

<details>
<summary><b>What the audit already shows</b></summary>

- **Real labels are multi-clause.** Many chain a forest, a range, a road and an offset in one
  string. The rules read one clause, and not always the most specific one.
- **Unknown extent is the main blocker.** Most references are towns, summits and streams with a
  single GNIS point, so honest proposals ask for an extent. A reviewed-extent store is on the
  critical path.
- **Rules gaps with names:** "air mi", spelled-out numbers, ranges, road designations read as
  places, and leading words ("Above", "Near") absorbed into names.
- **The LLM reads what the rules miss, and makes its own errors:** it handles "air mi",
  separates "Above"/"Near" from names and flags more route descriptions. It also called 7 labels
  that name a place "no locality", and 9 of its outputs were rejected by validation (as designed).
- **A grammar lesson:** the first LLM run failed 5 times because the decoding grammar allowed
  combinations that validation rejects, and greedy retries repeat themselves. The grammar now
  admits only valid combinations. The failed run is [kept](eval/reports/audit-50-llm-x1-qwen3.5-4b-q4km.md).
- **Supplied counties are not always counties:** 2,710 eligible records carry `Unknown`,
  `Unknown-E` or two counties (`Gunnison/Pitkin`).

</details>

## 🗺️ Roadmap

| Phase | Scope | Status |
|---|---|---|
| **1 · Data & feasibility** | ✅ core contract & validation · ✅ GNIS gazetteer · ✅ rules baseline · ✅ uncertainty policy · ✅ specimen snapshot (DOI) · ✅ ingest & screening · 🚧 50-record audit (rules and LLM run; scoring waits for annotation) | 🚧 in progress |
| **2 · MVP** | ✅ LLM extraction (llama.cpp, Qwen3.5-4B, pinned) · candidate disambiguation · footprints · map review · CSV export | 🚧 started |
| **3 · Production engineering** | Persistent jobs, leases & recovery · provenance store · telemetry | 🔜 |
| **4 · Evaluation** | 300-record reviewed benchmark · rules vs LLM vs GEOLocate · model-size & quantization study | 🔜 |
| **5 · Release** | Docker Compose · static replay demo · published results & model card | 🔜 |

<details>
<summary><b>What exists today, module by module</b></summary>

| Module | What it does |
|---|---|
| `extract/schema.py` | Typed extractor output (quotes only) and the validated `Interpretation` |
| `extract/validate.py` | Locates quotes, maps spans, cross-checks units and directions, enforces present-or-missing |
| `extract/prompt.py` · `extract/prompts/` | Versioned prompt files, label text fenced as data, SHA-256 pinned in the release manifest |
| `extract/llm_client.py` | The single model interface: llama-server on loopback, exact token count before each call, JSON-schema output |
| `extract/llm.py` | LLM extractor: one bounded retry, categorized failures (`malformed_model_output`, `model_supplied_coordinates`, `context_budget_exceeded` …) |
| `release.py` | Release manifest: model and GGUF checksums, llama.cpp build, generation settings, prompt, schema, policy and snapshot versions |
| `extract/quantities.py` | Label numbers: `2`, `2.5`, `.5`, `1 1/2`, `1-1/2`, `½`, `1½`, keeping their written precision |
| `ingest/normalize.py` | NFC and whitespace normalization with an exact offset map back to the original |
| `ingest/dwca.py` | Darwin Core Archive reader that streams from the zip, driven by `meta.xml`, with strict header and field counts |
| `ingest/specimens.py` | Screening with exclusion reasons, model-input allowlist, duplicate-locality groups |
| `evaluation/audit.py` | Seeded per-group audit sample, blind annotation worksheet, rules-baseline report |
| `geo/` | Exact unit conversion, 16-point compass parsing, datum-aware geodesic forward/inverse |
| `geo/uncertainty.py` | Uncertainty policy `gbif-bp-2020/1`: heading, distance precision, coordinate precision, datum, extent defaults, each cited |
| `geo/georeference.py` | Point-radius proposals: offset point, combined radius, lower bound, assumptions, blocking questions |
| `domain/status.py` | Record lifecycle with a single checked transition function |
| `data/` | Snapshot manifests, the GNIS fetcher and the GBIF download client (DOI, immutable, checksummed) |
| `gazetteer/` | GNIS parsing, versioned name keys, SQLite index, ranked search with evidence |
| `baseline/rules.py` | Rules extractor: offsets, route/between/orthogonal detection, admin areas, gazetteer phrase matching |
| `resolve/retrieve.py` | Interpretation → ranked candidates, with county context from supplied fields or the label |
| `pipeline/interpret.py` | normalize → extract → validate → retrieve for any extractor (rules now, LLM next) |
| `cli.py` | `data fetch-gnis` · `data fetch-gbif` · `model fetch` · `model check` · `ingest scan` · `audit sample` · `audit rules` · `audit llm` · `gazetteer build` · `gazetteer search` · `baseline run` · `interpret` |

</details>

## 📚 Data & licences

| Source | Snapshot | Terms |
|---|---|---|
| **USGS GNIS**: Domestic Names (CO) + All Names (National) | [`gnis-co-2026-09-29`](data/manifests/gnis-co-2026-09-29.json): 26,429 features · 4,190 variant names | U.S. public domain. *"Acknowledgment of the U.S. Geological Survey would be appreciated for products derived from these data."* |
| **University of Colorado Herbarium** vascular plants via GBIF | [`gbif-cu-2026-11-01`](data/manifests/gbif-cu-2026-11-01.json): 311,988 records, the whole dataset as a Darwin Core Archive · DOI [10.15468/dl.hqxjjf](https://doi.org/10.15468/dl.hqxjjf) · 105,544 eligible after screening | CC BY 4.0. Cite as *GBIF.org (01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf* |
| **Qwen3.5-4B** (Qwen), GGUF by unsloth | [`release/manifest.json`](release/manifest.json): `Qwen3.5-4B-Q4_K_M.gguf` at revision `e87f1764`, sha256 `00fe7986…` | Apache-2.0. Weights are downloaded, never committed |

Raw files are not committed. Each manifest records URLs, SHA-256 hashes, sizes and
publication dates, so a snapshot can be re-downloaded and verified byte for byte. The GBIF
manifest also stores the DOI and the exact download query. The whole dataset is requested on
purpose: filtering to Colorado and to usable locality text runs locally (`ingest scan`), so every
excluded record keeps a stated reason instead of vanishing inside a server-side filter.

<details>
<summary><b>Known gazetteer limitations</b></summary>

- **Primary county only.** Each GNIS feature lists one county, so features on county lines (like
  Longs Peak) disagree with many labels.
- **Representative points.** A feature is one point. For streams it is the mouth: "Grand River"
  resolves to the Colorado River, whose point is in Mexico. Such a point is never a collecting locality.
- **Missing source coordinates** are written as `0.0` in GNIS and stored as null.
- **Cultural features are largely absent.** Mines, ranches and post offices ("locales") are not
  in Domestic Names, so labels that cite them return `feature_absent_from_index`.
- **Current names and boundaries.** Historical names appear only where GNIS records a variant.

</details>

## 🛠️ Development

```bash
uv sync                                                     # install (Python 3.12+)
uv run pytest                                               # all tests, no network needed
uv run ruff check . && uv run ruff format --check .         # lint + format
uv run mypy src/                                            # strict type check
HYPOTHESIS_PROFILE=thorough uv run pytest tests/property    # 5,000 examples per property
```

CI runs lint, format, strict mypy and the full test suite on every push and pull request.
`main` is protected and only accepts commits that passed CI.

<details>
<summary><b>Project structure</b></summary>

```text
src/localitylens/
├── domain/       record lifecycle (status machine)
├── extract/      extraction contract, validation, quantities, LLM client, prompts/
├── ingest/       normalization, Darwin Core Archive reader, specimen screening
├── geo/          units, directions, geodesy, uncertainty policy, point-radius proposals
├── data/         snapshot manifests, GNIS + GBIF fetchers, model download
├── gazetteer/    GNIS parser, name keys, SQLite index + search
├── baseline/     rules extractor (the comparison system the LLM must beat)
├── resolve/      candidate retrieval with admin context
├── pipeline/     per-record orchestration
├── evaluation/   feasibility audit: sampling, worksheet, reports
└── cli.py        command-line entry point
tests/
├── unit/         behaviour tests (synthetic GNIS + DwC-A fixtures, no network)
├── property/     Hypothesis invariants
└── support/      shared fixture builders
data/manifests/   committed snapshot manifests (raw data is gitignored)
release/          release manifest: model, prompt, settings and versions, all pinned
eval/audit/       50-record audit sample + annotation worksheet (CC BY 4.0 records)
eval/reports/     system reports, kept even when results are poor
scripts/          generators for the README banner and pipeline diagram
```

</details>

## 📄 Licence & acknowledgements

Code is released under the [MIT licence](LICENSE). Geographic names are courtesy of the
**U.S. Geological Survey** Geographic Names Information System. Methodology follows the
[GBIF Georeferencing Best Practices](https://docs.gbif.org/georeferencing-best-practices/1.0/en/).
[GEOLocate](https://www.geo-locate.org/) is the established tool in this space, and LocalityLens
will be benchmarked against it.
