# Definition of Done: audit at v0.1.2

Checked on 2026-11-12, on a **fresh clone from GitHub** (`main` at 82db428, the v0.1.2 pipeline).
The clone followed only the README, on the development machine (Apple M1, 8 GB, macOS). The
Linux host is the release workflow's deploy check. Each item is the project's own Definition of
Done, with the evidence for it.

## The eleven items

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | A fresh installation processes supported user-supplied records end to end | **done** | See [1](#1-fresh-install) |
| 2 | Original text stays preserved and linked to every interpretation | **done** | See [2](#2-original-text) |
| 3 | Coordinates come from retrieved geographic evidence and explicit calculations | **done** | See [3](#3-coordinates) |
| 4 | Uncertainty assumptions are visible; unknown uncertainty is never silently zero | **done** | See [4](#4-uncertainty) |
| 5 | Ambiguous and unsupported descriptions get actionable statuses | **done, opt-in for same-name ties** (`selection-3`) | See [5](#5-statuses) |
| 6 | Review decisions persist in the local application and can be audited | **done** | See [6](#6-decisions) |
| 7 | Approved exports include Darwin Core geography and provenance fields | **done** | See [7](#7-export) |
| 8 | Benchmark, baselines, ablations and measured results are reproducible | **done, with a caveat** | See [8](#8-reproducibility) |
| 9 | Injection, malformed-output, interruption and recovery tests pass | **done** | See [9](#9-tests) |
| 10 | The deployed demo says whether it is live inference or a replay | **done** | See [10](#10-demo) |
| 11 | Docs cover setup, licences, supported cases, limitations and measured resources | **done after one fix; two small gaps** | See [11](#11-docs) |

### 1. Fresh install

- **Setup:** clone, `uv sync`, then the pinned GNIS and specimen snapshots (from the project's
  data releases, checksums matched), then `gazetteer build`. 42 s.
- **The review flow:**
  - `review import` of the audit sample: 38 need information, 9 ready, 3 unsupported, as the
    README shows.
  - Then approve, `review export`, `review backup`, a later rejection, and
    `review restore --replace`. The approval is back and the rejection is gone.
- **The bundled CSV** (`deploy/sample.csv`) through `review import --csv --system hybrid`: both
  records were processed, one through the LLM.
- **On Linux:** the Compose stack with llama-server took the same CSV from upload to export
  ([deployment](deployment.md#releasing)).

### 2. Original text

- **Storage:** the review store keeps original fields, interpretations, candidates, proposals and
  decisions in separate tables, and a proposal never overwrites a record.
- **Spans:** every extracted value carries a `[start, end)` span checked against the original
  text, and a property test checks that spans index the original string. The review screen marks
  each value at its span.

### 3. Coordinates

- **The model has nowhere to put them:** its output schema has no coordinate field, and a test
  shows this.
- **Coordinates it writes anyway are refused:** in open questions, including pairs with few
  decimals.
- **Feature IDs:** only retrieved candidate IDs are accepted.
- **Geometry** is `pyproj` code from GNIS points (`geo/`).
- **Adversarial tests** cover a model that obeys an injected request for coordinates.

### 4. Uncertainty

- **Each component is listed with its rule and citation** (policy `gbif-bp-2020/1`). The
  components are shown on the record page and written to `georeferenceRemarks`.
- **An unknown extent** gives `needs_information` with a lower bound, and a test checks that it
  is never zero. A property test checks that more imprecision never shrinks the region.

### 5. Statuses

Unresolved records carry the question that blocks them, for example:
- "the extent is unknown";
- the selection-2 question "the label also names … Is 'X' the reference?".

Unsupported relations carry a reason and the evidence that would make them supportable. A
reference GNIS lacks gets `feature_absent_from_index`.

**Same-name ambiguity (`candidates_unresolved`): built after the audit, opt-in.** The design
asks for several candidates the evidence can't tell apart (two "Bear Lake"s in different
counties and no county context) to be flagged, not proposed as a confident choice.
- **The audit found it missing:** the pipeline proposed the top-ranked candidate, and a module
  docstring wrongly claimed the case was handled. The docstring was corrected.
- **Now:** `selection-3` (selection-2 plus a tie check) holds a computed region when another
  candidate ranks level with the chosen one on every piece of evidence (match tier, type, state,
  county, name similarity) and lies outside the region. The record goes to `needs_information`
  and asks which feature the label means; approving confirms the chosen one.
  It is available with `--selection-3` or a manifest's `selection_version`.
- **Why it isn't the default:** on 300 read records it held 3 of 78 ready regions, 2 of them
  correct ([findings](../eval/reports/selection-3-findings.md)). The release default stays
  selection-2. Without it, the record page still says "N other candidate(s) share the name: the
  text must decide."

### 6. Decisions

- **What is recorded:** reviewer, time, rationale and edits.
- **Retries:** a retried decision with the same key returns the same decision (tested, and
  checked on Linux).
- **Restarts:** decisions survive a restart (checked on Linux).
- **Backup and restore:** rehearsed in the clone (item 1) and earlier across a schema change.

### 7. Export

The approved CSV row has:
- **Geography:** `decimalLatitude`, `decimalLongitude`, `geodeticDatum` (EPSG code),
  `coordinateUncertaintyInMeters`, `footprintWKT`, `footprintSRS`.
- **Georeference terms:** `georeferencedBy`, `georeferencedDate`, `georeferenceProtocol`,
  `georeferenceSources` (GNIS IDs and snapshot), `georeferenceRemarks`,
  `georeferenceVerificationStatus`.
- **Provenance:** release, extractor, proposal, decision and trace IDs, and human edits.

GeoJSON (WGS 84, 4 m datum allowance) and the unresolved report are written alongside.

### 8. Reproducibility

- **The model results reproduce exactly.**
  - **What was rerun:** the three owner-annotated read samples (audit-50, dev-1, validation:
    160 records), from scratch in the fresh clone with the LLM cache off (rules-6,
    llm-x2g2-qwen3.5-4b-q4km, hybrid-1, scores, with reviewed and derived extents).
  - **Result:** they match the committed reports record for record, apart from timings.
- **On x86 CPU** (the release workflow): the rules are identical, and the LLM differs on a few
  records, within the declared tolerance.
- **Samples:** `audit sample --seed audit-50/1` from the archived specimen snapshot redraws the
  committed audit sample byte for byte.
- **Derived extents:** `data fetch-geometry` and `extents derive` rebuild
  `data/extents/derived.csv` byte for byte (SHA-256 215df866…, 11,993 extents).
- **Test runs:** every locked-test run has its declaration and totals committed. They are not
  rerun here, by design: each test is scored only under a declaration.
- **Caveat, resolved 2026-11-13:** the derived extents came from USGS NHD (1.05 GB) and Census
  TIGER (2.8 MB) at their agency URLs, checked by SHA-256 but not mirrored. GNIS and the specimen
  archive were already mirrored, after USGS republished GNIS once and broke the pinned fetch.
  - **The fix:** both files are now mirrored unchanged in data releases
    (`data-nhd-co-2023-12-27`, `data-tiger-place-co-2025`).
  - **Order:** `data fetch-geometry` tries the mirror first, and keeps a file only if its
    checksum matches.

### 9. Tests

In the clone, all 693 tests pass without a network. They include:
- 22 adversarial behaviour tests: swapped directions, missing units, repeated names,
  conflicting counties, injected instructions, unknown landmarks, withheld records, malformed
  output, a crash after the model call, cancelled batches, oversized input;
- the job-queue recovery tests (lease expiry, retries, cancellation);
- the Hypothesis properties.

CI adds a llama.cpp smoke test and the browser test of the review flow.

### 10. Demo

Every page of the [static replay](https://professor3333.github.io/LocalityLens/) opens with
"Replay, not live inference", checked on the live site.

### 11. Docs

- **What exists:**
  - the README and the [user guide](guide.md) cover setup, usage with verified output, data
    sources and licences (code MIT; specimen data CC BY 4.0; GNIS public domain), limitations,
    deployment and results;
  - [evaluation](evaluation.md) gives the correctness definition;
  - the model card, dataset card, evaluation, results and deployment pages are current.
- **Verified here:** the 9 README console examples that run offline match their real output
  in the clone. The other 18 need a model server, Docker or stored state, and were checked in
  the steps above or when they were written.
- **Fixed in this audit:** the README's development install was `uv sync`, after which
  `uv run mypy src/` fails on the optional OpenTelemetry exporter. CI installs every extra; the
  README now says `uv sync --all-extras`.
- **Gaps:**
  - The user guide's CSV-import example uses a test file that is not in the repository. It
    contains a withheld record, which must not be published, so it stays an illustration.
  - Qwen3.5-2B's process memory has not been measured.

## Against the acceptance targets

The Definition of Done says the system works and is honest about itself. It doesn't say the
targets are met. Most quality targets are not:

| Target | Measured | Met? |
|---|---|---|
| ≥ 95% of ready proposals correct | 55–66% on read samples; 32% on test-5 ("place, offset" labels) | no |
| Ready proposals for ≥ 70% of answerable records | about 30% on read samples; 7–11% on test-5 | no |
| LLM contribution ≥ 10 points over the rules | +10.7 points on the locked test (releases 2 and 3), the smallest margin that clears it | yes, narrowly |
| Candidate recall@5 ≥ 95% where the feature is in the index | 61% (34 of 56, locked test, hybrid-1) | no |
| Evidence integrity | spans always resolve (validated); ≥ 95% audited interpretations supported: not separately measured | partly |
| Spatial usefulness ≥ 95% containment, with region size | not measured | — |
| Reviewer time ≥ 25% lower | not measured: needs curators | — |
| Warm latency p50 ≤ 30 s, p95 ≤ 90 s | p50 9.9 s, p95 16.4 s (M1, Metal, locked test); 23.8 / 41.2 s on a 4-vCPU x86 runner | yes |
| ≥ 99% of valid jobs reach a terminal state over 300 jobs | no 300-job queue run. The release workflow's 620 model calls had 0 technical failures, as did the declared test runs | not as specified |
| No paid inference; publish hosting cost per record | no paid inference; hosting cost not published | partly |

## What remains

The code item found by the audit, `candidates_unresolved` (item 5), is built as the opt-in
`selection-3`. Making it the default is a decision: a declared check would see one or two ties.

The rest need people or decisions, not code:
- **A reviewer-time pilot** with a few curators: the only way to measure the review-effort target.
- **Owner-annotated fresh labels:** all post-release evidence on selection-2 is Claude- or
  Codex-annotated.
- **Containment and region size on the locked test:** needs test-feature extents measured by the
  owner, and a declaration.
- **The quantization-parity gate** fails for the shipped Q4_K_M, so no release image is pushed
  until the quant or the spec changes ([parity](../eval/reports/quantization-parity.md)).
