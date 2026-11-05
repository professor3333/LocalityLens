# Dev samples

Records for developing prompts and rules. Everything here has been or will be read during
development, so it is **dev data forever**.

## Exclusions

Every dev sample excludes the groups already viewed and, since the benchmark was drawn, every
group reserved by [`../splits.lock.json`](../splits.lock.json) (the held-out components).

A group is one wording in one supplied county, so the same label text under another county is
another group. dev-2's E40 ("Hoosier Pass.") repeated validation's V021 this way. Since dev-3,
**exclusion version 2** also drops every group whose wording (by name key, county ignored)
matches a viewed or reserved group. On `gbif-cu-2026-11-01` that removes 28 more groups, 19 of
them repeating a held-out group's text. Group keys did not change (`GROUPING_VERSION` 1), so the
registry, the lock and the worksheets keep theirs. dev-1 and dev-2 reproduce with
`--shape-version 1 --exclusion-version 1` (dev-1 also with `--lock /nonexistent`; its
`excluded_viewed_groups` now reads 100, not 50, because dev-2 is registered too: same groups).

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

## dev-2

Drawn after rules-3 to check it on unread labels; scored once by its
[scoring plan](dev-2/scoring-plan.md). Same strata as dev-1, prefix `E`, seed `dev-2/1`. Only 3 of
its labels put a place right before an offset, so it did not test rules-3 or rules-4
([findings](../reports/dev-2-findings.md)).

## dev-3

Drawn to test rules-3 and rules-4 (the place-or-offset decision) on unread labels.

```bash
uv run localitylens dev sample --name dev-3 --seed dev-3/1 --prefix F --out eval/dev/dev-3 \
  --quota place_offset=35 --quota offset=5 --quota bare=5 --quota other=5
```

| Step | Rule | Groups |
|---|---|---|
| Pool | eligible groups of `gbif-cu-2026-11-01` | 40,444 |
| Exclude | viewed (audit, dev-1, dev-2: 150) and reserved (1,942) groups, by key | −2,092 |
| Exclude (exclusion version 2) | groups repeating the wording of an excluded group | −28 |
| Stratify (`SHAPE_VERSION` 2) | adds `place_offset`, carved out of `offset`: a clause with letters and no digits, then `,` or `;`, then an offset "N unit … of/from X" opening its clause. Unviewed pool: place_offset 6,095, offset 10,658, bare 2,753, other 18,818 | |
| Sample | place_offset 35, offset 5, bare 5, other 5, interleaved | 50 |

The shape is text only: no gazetteer and no rule decides it, so the stratum also holds labels
the rules do not treat as "place, offset", and broad places (forests, parks, rivers) that
rules-4 keeps the offset for. The other 15 rows keep the annotator from knowing every row's
shape. **The worksheet is blank: no system runs on dev-3 until
the owner has annotated it.** Then a scoring plan is pushed before any system runs, as for dev-2.

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
