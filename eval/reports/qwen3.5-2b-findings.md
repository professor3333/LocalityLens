# Qwen3.5-2B against Qwen3.5-4B (dev and validation data)

This is the planned lower-resource model comparison. The setup is identical to 4B:
- prompt `extraction-v2`, grammar 2, validation 3, rules-2 for the hybrid
- greedy decoding, the same llama.cpp build
- only the model file differs

The 2B model is pinned in [`release/manifest-2b.json`](../../release/manifest-2b.json):

| | 4B (release) | 2B |
|---|---|---|
| Model | `Qwen/Qwen3.5-4B` @ `851bf6e8` | `Qwen/Qwen3.5-2B` @ `15852e8c` |
| GGUF | `unsloth/Qwen3.5-4B-GGUF` @ `e87f1764`, Q4_K_M | `unsloth/Qwen3.5-2B-GGUF` @ `f6d5376b`, Q4_K_M |
| SHA-256 | `00fe7986…` | `aaf42c8b…` |
| File size | 2,740,937,888 B | 1,280,835,840 B |

- **How the 2B checksum was pinned:** it is Hugging Face's LFS object ID, which is the
  SHA-256. The same lookup reproduces the 4B pin exactly, and the downloaded file matched it.
- **Upstream revision:** the Qwen repository head on 2026-11-04. The GGUF repository doesn't
  state which upstream revision it was converted from.

Reports are in [`qwen3.5-2b/`](qwen3.5-2b/). The locked test was not run.

## Correct proposal candidates

| Set (answerable) | rules-2 | 4B alone | **2B alone** | hybrid, 4B | **hybrid, 2B** |
|---|---|---|---|---|---|
| Audit (31) | 17 | 13 | **5** | 17 | **17** |
| dev-1 (29) | 16 | 18 | **16** | 18 | **18** |
| Validation (32) | 13 | 15 | **6** | 16 | **14** |
| **All (92)** | 46 | 46 | **27** | **51** | **49** |

**On its own, 2B is much worse:** 27 against 46 correct candidates. **As the hybrid's
fallback it costs only 2 records** (49 against 51). That is because the rules answer most
records and 2B is asked only where they reach nothing. hybrid-1 with 2B never loses a record
the rules had right (0 rules-only records on every sample).

## Why 2B fails

| Of 160 records | 4B | 2B |
|---|---|---|
| Extraction failed validation | 7 | **51** |
| … of which a quote not found in the label | 3 | **51** |
| Critical interpretation exact | 76 | 66 |
| Relation read correctly | 97 | 106 |

**2B reads the relation as well as 4B, but it misquotes.** It returns text that is not in
the label, so validation rejects the extraction before retrieval. Quote-only extraction makes
this failure visible instead of letting an invented name reach the gazetteer.

## Speed (Apple M1, 8 GB; both measured on 2026-11-04 under the same conditions)

| Per record | 4B | 2B |
|---|---|---|
| p50 | 20.4 s | **4.9 s** |
| p95 | 30.8 s | **7.9 s** |
| 160 records | 3,387 s | **845 s** |

These 4B times are slower than the locked-test run (p50 11.7 s). Memory pressure varies
between sessions, which is why both models were timed in the same session. Process memory
was not measured for 2B.

## What this means

- **Keep 4B as the release model.** On its own, 2B is not a usable extractor (51 of 160
  rejected).
- **For a machine where 4B is too slow,** hybrid-1 with 2B keeps most of the gain over the
  rules (+3 records on these 92, against +5 with 4B) at a quarter of the model time.
  Validation and retrieval guard against its errors.
- **The 2B measurements are dev and validation numbers.** A test claim needs a declared
  release.
