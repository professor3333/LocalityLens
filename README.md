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
```

**Interpret a whole label** with the rules baseline: extraction, validation and retrieval in one
command. Every value carries its `[start, end)` span in the original text:

```console
$ uv run localitylens baseline run "Larimer Co., Colo., 2 mi NE of Longs Peak summit." --limit 2
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
| **The LLM never produces coordinates** | The extraction schema rejects unknown fields. Coordinates come only from `localitylens.geo` | ✅ |
| **Every claim cites the label** | Quotes must be found in the text and are mapped to half-open `[start, end)` spans of the *original* string | ✅ |
| **Swapped or invented details are caught** | Code re-parses quoted directions and units and rejects mismatches. A bare `m` (miles or metres?) cannot be asserted | ✅ |
| **Missing ≠ zero** | Each relation's parts must be present or explicitly declared missing. GNIS `0.0` coordinates are stored as null | ✅ |
| **Context ranks, never filters** | County, state and feature type order the candidates, and each candidate carries its evidence | ✅ |
| **Abstain rather than guess** | A bare `m` becomes "unit missing" plus a question. "Hwy 34" is not a distance. Route descriptions are labelled, not flattened. A name the gazetteer lacks is reported absent, not trimmed to a lookalike | ✅ |
| **Humans approve before export** | A single checked status machine. Only `approved` records are exportable | ✅ |
| **A point is not a place** | Feature extent and uncertainty components must be explicit, never assumed from a representative point | 🔜 |
| **Reproducible provenance** | Checksummed, immutable source snapshots. The index records which snapshot built it | ✅ |

## 🗺️ Roadmap

| Phase | Scope | Status |
|---|---|---|
| **1 · Data & feasibility** | ✅ core contract & validation · ✅ GNIS gazetteer · ✅ rules baseline · specimen snapshot · 50-record audit | 🚧 in progress |
| **2 · MVP** | LLM extraction (llama.cpp, Qwen3.5) · candidate disambiguation · footprints · map review · CSV export | 🔜 |
| **3 · Production engineering** | Persistent jobs, leases & recovery · uncertainty policy · telemetry | 🔜 |
| **4 · Evaluation** | 300-record reviewed benchmark · rules vs LLM vs GEOLocate · model-size & quantization study | 🔜 |
| **5 · Release** | Docker Compose · static replay demo · published results & model card | 🔜 |

<details>
<summary><b>What exists today, module by module</b></summary>

| Module | What it does |
|---|---|
| `extract/schema.py` | Typed extractor output (quotes only) and the validated `Interpretation` |
| `extract/validate.py` | Locates quotes, maps spans, cross-checks units and directions, enforces present-or-missing |
| `extract/quantities.py` | Label numbers: `2`, `2.5`, `.5`, `1 1/2`, `1-1/2`, `½`, `1½`, keeping their written precision |
| `ingest/normalize.py` | NFC and whitespace normalization with an exact offset map back to the original |
| `geo/` | Exact unit conversion, 16-point compass parsing, datum-aware geodesic forward/inverse |
| `domain/status.py` | Record lifecycle with a single checked transition function |
| `data/` | Snapshot manifests and the GNIS fetcher (immutable, checksummed) |
| `gazetteer/` | GNIS parsing, versioned name keys, SQLite index, ranked search with evidence |
| `baseline/rules.py` | Rules extractor: offsets, route/between/orthogonal detection, admin areas, gazetteer phrase matching |
| `resolve/retrieve.py` | Interpretation → ranked candidates, with county context from supplied fields or the label |
| `pipeline/interpret.py` | normalize → extract → validate → retrieve for any extractor (rules now, LLM next) |
| `cli.py` | `data fetch-gnis` · `gazetteer build` · `gazetteer search` · `baseline run` |

</details>

## 📚 Data & licences

| Source | Snapshot | Terms |
|---|---|---|
| **USGS GNIS**: Domestic Names (CO) + All Names (National) | [`gnis-co-2026-09-29`](data/manifests/gnis-co-2026-09-29.json): 26,429 features · 4,190 variant names | U.S. public domain. *"Acknowledgment of the U.S. Geological Survey would be appreciated for products derived from these data."* |
| **University of Colorado Herbarium** via GBIF | 🔜 pinned download with DOI | CC BY 4.0 |

Raw files are not committed. Each manifest records URLs, SHA-256 hashes, sizes and
publication dates, so a snapshot can be re-downloaded and verified byte for byte.

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
├── extract/      extraction contract, validation, quantity parsing
├── ingest/       normalization with offset maps
├── geo/          units, compass directions, geodesy
├── data/         snapshot manifests, GNIS fetcher
├── gazetteer/    GNIS parser, name keys, SQLite index + search
├── baseline/     rules extractor (the comparison system the LLM must beat)
├── resolve/      candidate retrieval with admin context
├── pipeline/     per-record orchestration
└── cli.py        command-line entry point
tests/
├── unit/         behaviour tests (synthetic GNIS fixtures, no network)
├── property/     Hypothesis invariants
└── support/      shared fixture builders
data/manifests/   committed snapshot manifests (raw data is gitignored)
scripts/          generators for the README banner and pipeline diagram
```

</details>

## 📄 Licence & acknowledgements

Code is released under the [MIT licence](LICENSE). Geographic names are courtesy of the
**U.S. Geological Survey** Geographic Names Information System. Methodology follows the
[GBIF Georeferencing Best Practices](https://docs.gbif.org/georeferencing-best-practices/1.0/en/).
[GEOLocate](https://www.geo-locate.org/) is the established tool in this space, and LocalityLens
will be benchmarked against it.
