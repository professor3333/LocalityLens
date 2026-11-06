# dev-4 scoring plan (written before dev-4 is annotated or any system runs on it)

dev-4 is a 50-group dev sample drawn on 2026-11-06 (seed `dev-4/1`, text shape version 2,
exclusion version 2), with 35 "place, offset" labels. It exists to test the place-or-offset
rules (rules-3 to rules-6) **independently**: dev-3 could not, because Claude annotated it and
also wrote the rules. The owner annotates dev-4. This plan is pushed before the annotations
exist, so the systems, inputs, questions and reporting are fixed in advance.

## Frozen inputs

| Input | Pinned |
|---|---|
| Code | the commit that adds this plan: rules-6 (`baseline/rules.py` SHA-256 `442b7501a40b…`), unchanged until dev-4 is scored |
| Release manifest | `release/manifest.json`, SHA-256 `9aeaccceb500…` |
| Sample | `eval/dev/dev-4/dev-4.json`, SHA-256 `b5ecfe3aa820…` (blank worksheet `95c264d2f9cc…`) |
| Annotations | the owner's first commit of `eval/dev/dev-4/worksheet.csv` after this plan. Its SHA-256 goes into the score report. It must pass the annotation checker with 0 errors before any system runs; the owner fixes any error first. |
| Extent store | `data/reviewed/extents.csv`, SHA-256 `85b610b3c31b…` (67 reviewed) |
| Earlier rules, for the rule question | rules-2 to rules-5 from `57b3261`, `06cacbc`, `4e56bfe`, `3b24d4e`, replayed by `scripts/replay_rules_versions.py --sample dev-4` (it reproduces dev-3's rule question byte for byte) |

## Systems, each run once

- `rules-6`
- LLM `llm-x2g2-qwen3.5-4b-q4km`: prompt `extraction-v2`, greedy decoding, completion cache on
- `hybrid-1`: rules first, the LLM only when the rules reach no gazetteer candidate

Each runs with and without the extent store. No rule, prompt, annotation or extent changes
between these runs and the report.

## Reported

- **Primary, the rule question:** on the answerable records of the `place_offset` stratum,
  correct candidates of rules-6 against the rules-2 replay, paired, with the bootstrap interval
  and the exact sign test. Every record that any two of rules-2 to rules-6 read differently is
  listed with each version's reading and whether it is correct.
  - **Support** for the place-or-offset rules: rules-6 gains more of these records than it loses.
  - **Against:** it loses more than it gains.
  - **Not shown:** neither, or no record changes. With about 25 records, a one- or two-record
    margin proves little, and the report will say so.
  - **Expectation, stated now:** no difference. On dev-3, rules-2 to rules-6 scored 6, 7, 6, 6
    and 6 of 24.
- **Systems:** correct proposal candidates of the answerable records per system, with the paired
  bootstrap and sign test (hybrid-1 and LLM, each against the rules), also without the unsure
  rows. The expectation from dev-2 and dev-3 is hybrid-1 a few records ahead of the rules and
  never behind.
- **Regions:** computed regions, precision and useful coverage with the extent store, with the
  region sizes.

## Known limits, stated now

- **One annotator,** but not the rules' author. The owner has seen the dev-3 findings, which
  describe the rules' failure kinds; dev-4's records are new to everyone.
- **Small numbers.** One record is about 3 points of the answerable records and about 4 of the
  place-offset ones.
- **dev-4 becomes read data** once scored. The locked test is not read or run here.
