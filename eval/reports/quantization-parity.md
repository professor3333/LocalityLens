# Quantization parity: Q4_K_M fails the declared 1-point gate

The first run of the release workflow ([run 43214807200](https://github.com/professor3333/LocalityLens/actions/runs/43214807200),
[evidence](quantization-parity.json)):
- **What ran:** the v0.1.2 pipeline, re-evaluated from scratch on the six dev and validation
  samples (310 records, no held-out test).
- **Where:** GitHub-hosted x86 CPU runners with the pinned llama.cpp image.
- **Models:** the shipped Q4_K_M and the Q8_0 reference quant of the same upstream and GGUF
  revisions ([`release/manifest-q8.json`](../../release/manifest-q8.json)).

## The gates ([`release/regression.json`](../../release/regression.json))

| Gate | Result |
|---|---|
| Rules identical to the committed reports | pass: identical in all six samples |
| LLM and hybrid-1 within 3 records (pooled) | pass: LLM valid 292 vs 284, critical 151 vs 150, correct candidates 93 vs 91; hybrid-1 critical 163 vs 164, correct candidates 102 vs 101, ready correct 57 vs 57 |
| Abstention within 3 records | pass: unsupported flagged 10 vs 10, absent reported 39 vs 40 |
| selection-2 holds back ≥ 2× wrong as correct, precision not lower | pass: 20 wrong / 5 correct, 55.3% → 66.7% |
| **Q4_K_M loses ≤ 1 point to Q8_0 on critical exact match** | **fail: 48.7% vs 51.0%, a 2.3-point loss** |

- **Hardware drift:** the committed reports were made on Metal (Apple M1). On x86 CPU the
  LLM's greedy output differs for a few records. Here that went slightly in its favour.

## Q4_K_M against Q8_0, record by record ([script](../../scripts/quant_parity.py))

| Pooled, 310 records (189 answerable) | Q4_K_M (shipped) | Q8_0 (reference) | Only Q8_0 right / only Q4_K_M right | Sign test p |
|---|---|---|---|---|
| LLM alone: critical exact match | 151 | 158 | 20 / 13 | 0.30 |
| LLM alone: correct proposal candidates | 93 | 92 | 5 / 6 | 1.0 |
| hybrid-1: correct proposal candidates | 102 | 103 | 3 / 2 | 1.0 |
| hybrid-1: ready regions correct | 57 of 103 | 59 of 108 | | |
| LLM alone: valid extractions | 292 | 297 | | |
| Model seconds per record, p50 / p95 | 23.8 / 41.2 | 41.6 / 54.6 | | |
| Model file | 2.74 GB | 4.48 GB | | |

- **The loss is in the reading, not in the result.**
  - Q8_0 reads the critical fields correctly on 7 more records, but the record-by-record
    difference is not significant.
  - Correct proposals are the same within one record, for the LLM alone and for hybrid-1.
- **Q8_0 costs:**
  - **Size:** its model file is 1.6 times larger.
  - **Speed:** it ran 1.75 times slower here.
  - **Memory:** not measured reliably. The release check's `docker stats` figure doesn't
    consistently count the memory-mapped model, so it is not used: it said 5.4 GiB here and
    0.9 GiB on the next run.
  - **On the 8 GB development machine:** not measured.

## Second run: the v0.1.3 tag ([run 43353616244](https://github.com/professor3333/LocalityLens/actions/runs/43353616244))

- **The same gate fails again,** by more: Q4_K_M 48.7% against Q8_0 51.9%, a 3.2-point loss.
  The other gates pass, and so does the Linux deploy check.
- **Repeated runs on x86 CPU differ by a few records.**
  - **Q8_0:** 161 critical exact matches here, against 158 in the first run.
  - **LLM alone:** 289 valid extractions here, against 292.
  - **Why:** the runners may get different CPUs, so greedy decoding can differ for a few
    records. The parity gap itself moves by about a point between runs.
- **Model time per call:** p50 28.6 / 39.5 s and p95 44.6 / 53.2 s (Q4_K_M / Q8_0).

## Decision

The owner kept Q4_K_M as the shipped quant (2026-11-12) and chose to record the failure rather
than change the gate after seeing the result.
- **The release check stays red on this gate** until the quant or the spec changes.
- **No image is pushed while it is red,** because only a tag that passes every gate pushes one.
