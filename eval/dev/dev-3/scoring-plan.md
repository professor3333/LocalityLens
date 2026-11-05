# dev-3 scoring plan (written before any system runs on dev-3)

dev-3 is a 50-group dev sample drawn on 2026-11-05 (seed `dev-3/1`, text shape version 2,
exclusion version 2), with 35 "place, offset" labels: the labels where rules-3 to rules-6
decide between a named place and an offset. This plan is committed and pushed before any system
runs on dev-3, so the systems, inputs and reporting are fixed in advance.

## Frozen inputs

| Input | Pinned |
|---|---|
| Code | `main` at `c848b4a` (rules-6; `baseline/rules.py` SHA-256 `442b7501a40b…`) |
| Release manifest | `release/manifest.json`, SHA-256 `9aeaccceb500…` |
| Sample | `eval/dev/dev-3/dev-3.json`, SHA-256 `edad3e73b879…` |
| Annotations | `eval/dev/dev-3/worksheet.csv`, SHA-256 `4036658ab468…` (commit `46367fe`), 0 checker problems: 32 answerable, 10 reference absent, 8 unsupported, 11 rows with an unsure mark |
| Extent store | `data/reviewed/extents.csv`, SHA-256 `85b610b3c31b…` (67 reviewed) |
| Earlier rules, for the rule question only | `baseline/rules.py` from `57b3261` (rules-2), `06cacbc` (rules-3), `4e56bfe` (rules-4), `3b24d4e` (rules-5), each replayed through the code above. The rules-2 replay reproduces the committed rules-2 audit report on 50 of 50 records. |

## Systems, each run once

- `rules-6`
- LLM `llm-x2g2-qwen3.5-4b-q4km`: prompt `extraction-v2`, greedy decoding, completion cache on
- `hybrid-1`: rules first, the LLM only when the rules reach no gazetteer candidate

Each runs with and without the extent store. No rule, prompt, annotation or extent changes
between these runs and the report.

## Reported

- **Main metric:** correct proposal candidates of the answerable records per system, with the
  existing paired bootstrap and exact sign test (hybrid-1 and LLM, each against the rules). Also
  without the unsure rows.
- **The rule question (rules-3 to rules-6):** on the answerable records of the `place_offset`
  stratum, correct candidates of rules-6 against the rules-2 replay, paired, with the bootstrap
  interval and the sign test. Every record where any two of rules-2 to rules-6 read differently
  is listed with each version's reading and whether it is correct, so each change can be
  attributed to the version that made it.
  - **Support** for the place-or-offset rules: rules-6 gains more of these records than it loses
    against rules-2.
  - **Against:** it loses more than it gains.
  - **Not shown:** neither, or no record changes. With about 24 records, a one-record margin
    proves little, and the report will say so.
- **Regions:** computed regions, their precision and useful coverage with the extent store,
  with the region sizes, because precision ignores size.
- **rules-6 separately:** every dev-3 record that rules-5 and rules-6 read differently. The
  "2 or 3 mi" gap was raised after dev-3 was annotated, and no other read or unread label is
  written that way, so such a record is in-sample for rules-6.

## Known limits, stated before scoring

- **The annotator also wrote the rules.** Claude annotated dev-3, at the owner's request, before
  any system ran, and Claude also wrote the rules being tested. dev-3 is therefore weaker
  evidence than an owner-annotated set, and it is not an independent check of rules-3 to
  rules-6. An independent check needs the owner's annotation of these records, or the locked
  test in a declared release.
- **Small numbers.** One record is about 3 points of the 32 answerable records, and about 4 of
  the place-offset ones.
- **dev-3 becomes read data** once scored. A claim about unseen labels still needs a declared
  test release, which needs the owner's authorisation. The locked test is not read or run here.
