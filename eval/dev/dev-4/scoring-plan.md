# dev-4 scoring plan (written before dev-4 is annotated or any system runs on it)

dev-4 is a 50-group dev sample drawn on 2026-11-06 (seed `dev-4/1`, text shape version 2,
exclusion version 2), with 35 "place, offset" labels. It was drawn to test the place-or-offset
rules (rules-3 to rules-6) independently of their author. **It no longer can.** On 2026-11-06 the
owner decided that Claude annotates dev-4, and Claude also wrote those rules. It is therefore a
second result of the same weak kind as dev-3, not an independent check.

The first version of this plan named the owner as annotator. This revision is pushed with the
annotations and before any system runs on dev-4, so the systems, inputs, questions and reporting
are still fixed in advance. The clause choices were fixed from the label text before any GNIS
lookup, and no system output on these records had been seen.

## Frozen inputs

| Input | Pinned |
|---|---|
| Code | `main` at `c8069be`: rules-6 (`baseline/rules.py` SHA-256 `442b7501a40b…`), unchanged until dev-4 is scored. This revision changes only which annotator the reports name. |
| Release manifest | `release/manifest.json`, SHA-256 `9aeaccceb500…` |
| Sample | `eval/dev/dev-4/dev-4.json`, SHA-256 `b5ecfe3aa820…` (blank worksheet `95c264d2f9cc…`) |
| Annotations | `eval/dev/dev-4/worksheet.csv`, annotated by Claude, SHA-256 `614472125609…`, 0 checker problems: 8 rows with an unsure mark. Committed unchanged with this revision. |
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
  - **Sensitivity:** the same comparison without G19 and G38, whose wording nearly repeats read
    records.
- **Systems:** correct proposal candidates of the answerable records per system, with the paired
  bootstrap and sign test (hybrid-1 and LLM, each against the rules), also without the unsure
  rows. The expectation from dev-2 and dev-3 is hybrid-1 a few records ahead of the rules and
  never behind.
- **Regions:** computed regions, precision and useful coverage with the extent store, with the
  region sizes.

## Known limits, stated now

- **The annotator also wrote the rules.** So this is not an independent check of rules-3 to
  rules-6. An independent check needs the owner's own annotation of a sample, or the locked test in
  a declared release.
- **Near repeats.** The sample excludes identical wording only. G19 nearly repeats dev-3's F36
  (28 mi there, 29 here), and G38 is close to read records A15 and V029. So not every dev-4 label
  is new to the annotator. Others may exist; they were found by reading, not by a search.
- **Small numbers.** One record is about 3 points of the answerable records and about 4 of the
  place-offset ones.
- **dev-4 becomes read data** once scored. The locked test is not read or run here.
