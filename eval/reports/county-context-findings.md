# Supplied county context (`COUNTY_CONTEXT_VERSION` 1)

Retrieval ranks candidates by the record's supplied county, ahead of a county named in the
label. Some supplied values are not one county, and before this change they were used as
written.

## How often (all 105,544 eligible records of `gbif-cu-2026-11-01`)

| Supplied value | Records | Before | Now |
|---|---|---|---|
| One known Colorado county | 102,616 | used | used |
| Placeholder: `Unknown` 718, `Unknown-E` 504, `Unknown-W` 83 | 1,305 | matched no feature, and hid the label's county | missing: the label's county is used |
| Empty | 218 | missing | missing |
| Two counties: `Gunnison/Pitkin` 389, `Chaffee/Gunnison` 182 … and 16 written with "or" | 1,395 | matched no feature | a candidate in either county matches |
| Not a county in the gazetteer: `Giplin` 4, `Sedgewick` 2, `Rio Blanca`, `Sevier`, `Fergus`, `Morrison` | 10 | matched no feature | missing |

County context still only ranks candidates. It never removes one, because current county
lines are not proof for an old label.

## Effect on the samples

Rules, LLM v2 (re-scored from cached completions, identical to the committed run) and
hybrid-1 were run again on audit, dev-1 and validation.

**No result changed.** Every score and every candidate list is identical to the committed
reports. Only 5 of the 160 records carry an affected value (`Unknown`, `Unknown-E`,
`Costilla/Huerfano`, `Park/Summit`, `Lake/Park`), and their candidate lists came out
unchanged.

The change is kept because it is correct for the 2.7% of eligible records it touches, and
the samples show it costs nothing. It is not counted as a measured improvement.
