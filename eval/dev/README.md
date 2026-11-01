# Dev samples

Records for developing prompts and rules. Everything here has been or will be read during
development, so it is **dev data forever**.

## Exclusions

Every dev sample excludes the groups already viewed and, since the benchmark was drawn, every
group reserved by [`../splits.lock.json`](../splits.lock.json) (the held-out components).

## The viewed-groups registry

[`../viewed-groups.json`](../viewed-groups.json) lists every locality group sampled for viewing
and the sample it came from. Every later sample, including the locked test split, must exclude
these groups. The audit and dev samples register themselves automatically
(`localitylens dev register`, `localitylens dev sample`).

## dev-1

Built to develop extraction prompt v2 after the [audit](../audit/) showed where prompt v1 fails.

```bash
uv run localitylens dev sample --name dev-1 --seed dev-1/1 \
  --quota bare=15 --quota offset=15 --quota other=20 --out eval/dev/dev-1 \
  --lock /nonexistent   # dev-1 predates the split lock; later samples use the lock
```

| Step | Rule | Groups |
|---|---|---|
| Pool | eligible groups of `gbif-cu-2026-11-01` (same screening and grouping as the audit) | 40,444 |
| Exclude | groups already viewed (the 50 audit groups) | −50 |
| Stratify (`SHAPE_VERSION` 1) | label text shape: `bare` (≤ 3 words, no digits), `offset` (a number followed by a distance unit), `other` | |
| Sample | per shape, the first groups in `sha256(seed \| group_key)` order: bare 15, offset 15, other 20, then interleaved | 50 |

The strata over-represent the label shapes where prompt v1 failed: bare place names (read as
"no locality"), offsets, and multi-clause labels. They use only the label text, never answer
fields, and they are **not** representative of the collection. Use the audit for rates.

## Order of work

1. Annotate [`dev-1/worksheet.csv`](dev-1/worksheet.csv) with the
   [annotation guide](../annotation_guide.md), before any system runs on these records.
2. Then develop `extraction-v2` against dev-1 only: prompt changes, examples and rules.
3. Freeze v2, then re-run it on the audit. This is a check on records v2 was not built from,
   not an unbiased test: the audit's findings shaped dev-1. Unbiased numbers come only from the
   locked test split, drawn later from unviewed groups.

## Data licence

Same as the audit: University of Colorado Museum of Natural History Herbarium Vascular Plant
Collection, CC BY 4.0. Cite: *GBIF.org (01 November 2026) GBIF Occurrence Download
https://doi.org/10.15468/dl.hqxjjf*. Selection and annotation columns are modifications by this
project. Label text is unchanged, and no georeference fields are included.
