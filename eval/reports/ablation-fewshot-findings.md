# Ablation: the few-shot examples in prompt v2

**Question:** how much of the LLM's result comes from the 11 invented examples in
`extraction-v2`?

**Method:**
- `extraction-v2-zeroshot` is v2 with the example exchanges removed. The system instructions and
  the final user turn are unchanged.
- Release manifest `release/manifest-abl-zeroshot.json`. It differs from `release/manifest.json`
  only in the prompt, the extractor ID (`llm-x2zs-qwen3.5-4b-q4km`) and the release label. The
  model, grammar, validation and decoding are the same.
- Run once on the six read samples: audit-50, dev-1 and validation (owner-annotated), and dev-2,
  dev-3 and dev-4 (Claude-annotated).
- Scored against the same annotations as the committed v2 reports, using
  `scripts/ablation_fewshot.py` (output in `ablation-fewshot.json`).
- The locked test was not used.
- This is an ablation of the frozen release. Nothing was tuned, and the zero-shot prompt is not a
  candidate for release.

## Result: removing the examples loses most correct proposals

| Correct proposal candidates (answerable) | v2 with examples | zero-shot | invalid extractions (v2 / zero-shot) |
|---|---|---|---|
| audit-50 (31) | 13 | 2 | 1 / 20 of 50 |
| dev-1 (29) | 18 | 5 | 4 / 14 of 50 |
| validation (32) | 15 | 4 | 2 / 23 of 60 |
| **Owner-annotated, pooled (92)** | **46** | **11** | 7 / 57 of 160 |
| dev-2 (36) | 17 | 5 | 6 / 22 of 50 |
| dev-3 (32) | 14 | 3 | 10 / 32 of 50 |
| dev-4 (29) | 14 | 2 | 3 / 26 of 50 |
| **Claude-annotated, pooled (97)** | **45** | **10** | 19 / 80 of 150 |

**Paired, zero-shot minus v2.** In `ablation-fewshot.json` the paired keys are named
`rules`/`llm`, for v2/zero-shot respectively.

- **Owner-annotated:** −38 points (95% bootstrap CI −49 to −27). 38 records are correct only with
  the examples, 3 only without them. Sign test p < 0.001.
- **Claude-annotated:** −36 points (CI −45 to −27). 35 against 0. Sign test p < 0.001.
- **Critical interpretation exact**, summed over the six samples: 108 with the examples, 30
  without, of 310 records.

## Why: the examples teach the output contract, not just the language

Validation failures over all 310 records:

| Validation error | v2 with examples | zero-shot |
|---|---|---|
| `quote_not_found` (a quote that is not in the label) | 11 | 101 |
| `required_component_undeclared` | 1 | 61 |
| `contradictory_missing` | 17 | 44 |
| `unparseable_distance` | 4 | 9 |
| `direction_mismatch` | 0 | 6 |

Without examples the model:

- paraphrases or normalises text where the schema asks for an exact quote;
- leaves out the observed / assumed / missing declarations;
- marks fields both present and missing.

The grammar guarantees valid JSON, but not these cross-field rules. The deterministic validator
catches them, so the cost is invalid extractions (`failed`-style results), not silently wrong
georeferences.

## Cost and latency

- The zero-shot prompt is about 960 tokens against about 1,500 for v2.
- Zero-shot model time was a median of 13–17 s per record across the six samples (Apple M1
  8 GB, warm server, cache off).
- These were not measured side by side with v2 under the same machine load, so no latency saving
  is claimed.

## What this means

- **Keep the examples.** They are where most of the 4B model's usable output comes from on this
  task. A shorter prompt is not a cheap win.
- **The rules-first hybrid depends on the LLM being right where the rules reach nothing.** The
  hybrid's gain therefore also rests on the examples.
- **Not tested:** fewer examples (between 0 and 11), different examples, or examples with
  a larger model. Each would be a new prompt version, developed on dev data.
