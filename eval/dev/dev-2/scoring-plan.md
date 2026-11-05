# dev-2 scoring plan (written before any system runs on dev-2)

dev-2 is a fresh 50-group dev sample, drawn on 2026-11-05 (seed `dev-2/1`) to check rules-3
and rules-4 on labels nobody had read while writing them. This plan is committed and pushed
before scoring, so the systems, inputs and reporting are fixed in advance.

## Frozen inputs

| Input | Pinned |
|---|---|
| Code | `main` at `2bfc227` (rules-4) |
| Release manifest | `release/manifest.json`, SHA-256 `96594916…` |
| Sample | `eval/dev/dev-2/dev-2.json`, SHA-256 `7f016d3e…` |
| Annotations | `eval/dev/dev-2/worksheet.csv`, SHA-256 `ee210198…` (commit `12ebc31`, 0 checker problems) |
| Extent store | `data/reviewed/extents.csv`, SHA-256 `5a98f0c2…` (56 reviewed) |

## Systems, each run once

- `rules-4`
- LLM `llm-x2g2-qwen3.5-4b-q4km`: prompt `extraction-v2`, greedy decoding
- `hybrid-1`: rules first, the LLM only when the rules reach no gazetteer candidate

Each system runs with and without the extent store. No rule, prompt or annotation changes
between these runs and the report.

## Reported

- **Main metric:** correct proposal candidates (of answerable records) per system. Paired
  comparisons use the existing bootstrap and exact sign test.
- **Regions:** computed regions, their precision and useful coverage with the extent store,
  together with the region sizes, because precision ignores size.
- **Rule-sensitive records, separately:** every record where a named place stands right before
  an offset. These are the records where rules-3 or rules-4 decide between the place and the
  offset. They are listed by the rules' own output, not chosen by looking at the annotations.

## Known limits, stated before scoring

- **The annotations are not independent of rules-4.** The owner wrote rules-4 (broad features
  keep the offset) and then annotated dev-2. rules-3's collecting-place rule came from the
  read samples. dev-2 is unseen by both rules, but on the rule-sensitive records the annotator
  knew the rule's logic. Those records are reported apart, and a blind second annotation of
  them would make that part independent.
- **50 groups give wide intervals.** One record is 2 to 3 percentage points of the answerable
  records.
- **dev-2 is dev data.** Once scored it is read. A claim about unseen labels still needs a
  declared test release, which needs the owner's authorisation.
