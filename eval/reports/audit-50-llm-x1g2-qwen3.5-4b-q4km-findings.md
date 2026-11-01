# 50-record audit, LLM extraction `llm-x1g2-qwen3.5-4b-q4km`: developer findings

Observations about system behaviour, not correctness scores. Correctness needs the owner's
annotations (see [`../audit/README.md`](../audit/README.md)). Record IDs refer to
[`audit-50-llm-x1g2-qwen3.5-4b-q4km.md`](audit-50-llm-x1g2-qwen3.5-4b-q4km.md).

**Configuration:** Qwen3.5-4B Q4_K_M (sha256 `00fe7986…`), llama.cpp b11960-8642541b2,
prompt `extraction-v1`, grammar v2, greedy (temperature 0, top_k 1, seed 20261101), thinking
off. Everything is pinned in [`release/manifest.json`](../../release/manifest.json).

## Two runs, one prompt

| Run | Grammar | Hard failures | Retries | Record latency p50 / p95 / max | Total |
|---|---|---|---|---|---|
| [`llm-x1`](audit-50-llm-x1-qwen3.5-4b-q4km.md) (kept as a failed experiment) | 1 | 5 | 5 | 12.4 / 25.3 / 31.4 s | 11 min 38 s |
| `llm-x1g2` | 2 | 0 | 0 | 10.2 / 14.7 / 15.2 s | 8 min 46 s |

Latency was measured on an Apple M1 with 8 GB, with a warm server and prompt-prefix caching.
Every prompt was 1,496–1,550 tokens.

**Why run 1 failed.** "A feature type comes with its quote" (and the same for a unit) was
enforced only by Pydantic, which a JSON-schema grammar cannot express. The grammar therefore
allowed `"feature_type": "trail", "feature_type_quote": null`, Pydantic rejected it, and **the
retry repeated the same output, because decoding is greedy**. Grammar v2 encodes each pair as
two alternatives, so the grammar admits only what validation accepts. The prompt did not change.

**A second guard came out of this.** With the pair forced, the model sometimes quoted the place
name itself as the "type word" ("Paonia" → `trail`). Validation now checks every asserted type
against a shared type-word table and drops an unsupported type with a warning, the same way units
and directions are re-parsed. The rules baseline is unaffected: its report regenerates
byte-identical.

## Outcome counts (run 2)

Proposal `needs_information` 27 · `unsupported` 13 · `invalid_extraction` 9 · `computed` 1.
Retrieval `candidates_found` 22 · `feature_absent_from_index` 12 · `no_reference_feature` 7 ·
not reached 9.

## Behaviour worth knowing before scoring

1. **Bare place names read as `no_locality`:** 7 labels that name a place were classified as
   having no locality (A12, A16, A17, A27, A30, A39, A48), including a single town name (A30,
   "Pitkin."). This is the largest systematic error visible without annotations.
2. **Inexact quotes:** 4 records quote text that is not in the label (A19, A23, A37, A43). The
   validator rejects them, so they cannot produce a proposal. That is the intended behaviour.
3. **Component contradictions:** for "West of Hesperus" (A44) the model declared
   `distance_and_direction`, gave no distance and did not declare it missing, and listed
   `reference_feature` as missing while also supplying one. Similar component errors appear in
   A01, A06 and A46. A re-run reproduced A44's output exactly, as expected with greedy decoding.
4. **Spelled-out numbers and ranges** ("Nine miles", "20-21 air mi") fail in the shared quantity
   parser (A23, A25). This is a code limitation that affects the rules too.
5. **Differences from the rules that annotation should judge:**
   - "air mi" is read as a distance (A03, A13)
   - leading words are separated from names ("Above Rainbow Lake" → Rainbow Lake, A10;
     "Near Deer Creek" → Deer Creek, A21)
   - more labels are called route-relative (A05, A34, A38, A40, A41)
   - a different clause is chosen in several multi-clause labels (A24: James Peak rather than
     Tolland)
6. **The single `computed` proposal is the same fuzzy match as in the rules run** (A42 "Five
   Springs" → "Five Spring"), which again shows the need for a selection-confidence gate.

## Not yet measurable

Whether either system is *right* on any record. That needs the annotated worksheet. The prompt
has deliberately not been changed in response to these observations. Any prompt change becomes
`extraction-v2`, is developed on dev records outside the audit, and is then re-run here.
