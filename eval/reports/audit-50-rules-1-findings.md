# 50-record audit, rules baseline `rules-1`: developer findings

Observations about how the system behaved on the audit sample. These are not correctness
scores: correctness needs the owner's annotations (see [`../audit/README.md`](../audit/README.md)).
Record IDs refer to [`audit-50-rules-1.md`](audit-50-rules-1.md).

**Outcome counts:** proposal `needs_information` 46 · `unsupported` 3 · `computed` 1.
Retrieval `candidates_found` 33 · `feature_absent_from_index` 14 · `no_reference_feature` 3.

## What blocks proposals

1. **Unknown feature extent blocks almost everything.** Most references are towns, summits
   and streams. GNIS gives each one a point and no extent, so the policy asks for an extent
   instead of drawing a falsely small circle. A reviewed-extent store, or cited extent rules per
   feature class, is the critical path to any `computed` proposal.
2. **The one `computed` proposal rests on a fuzzy match.** A42 "Five Springs" matched GNIS
   "Five Spring" (Spring class, whose published default extent is 3 m). A fuzzy match should not
   produce a ready proposal without a selection-confidence gate, which is the review policy (not
   built yet).

## Rules extraction gaps

3. **Unit forms:** "air mi" (A03, A13, A23), spelled-out numbers ("Nine miles", A25) and ranges
   ("20-21 air mi", A23) are not parsed. The offset then degrades to `direction_only`.
4. **Road designations taken as the reference feature:** "Hwy" (A14), "National Forest Road"
   (A20), "County Rd" (A32), "Rte" (A40).
5. **Leading words absorbed into names:** "Above Rainbow Lake" (A10), "Near Deer Creek" (A21).
   In A21 the "near" qualifier is lost as well.
6. **Multi-clause labels:** many labels chain several places and offsets (A04, A15, A19, A32,
   A34, A37). The rules take one clause, and not always the most specific one (A19 picks "Green
   Ridge Trail" over "ca 37 air mi W of Fort Collins").
7. **Unknown bare names are not detected at all**, so they show up as `no_reference_feature`
   rather than `feature_absent_from_index`.

## Retrieval and ranking

8. **Head-word typing:** A37 "16 miles N of Grand Lake". "Lake" implies a lake-type feature,
   so the Reservoir outranks the Populated Place of the same name. Without a type hint the town
   ranks first. The label alone does not say which is meant.
9. **Names absent from GNIS Domestic Names:** national monuments and state parks (A01, A45),
   mines (A31), informal regions (A17), and older spellings such as "Canon" (A27).
10. **Supplied county values that are not counties:** across the eligible records, 102,616
    supplied counties match a GNIS county, 218 are empty and 2,710 do not match. The non-matches
    are mostly placeholders (`Unknown` 718, `Unknown-E` 504, `Unknown-W` 83) or two counties for
    a boundary locality (`Gunnison/Pitkin` 389, `Chaffee/Gunnison` 182 …). Splitting the
    two-county values, and treating placeholders as missing, would let them rank candidates.

## Not yet measurable

The LLM side of the comparison does not exist yet, and nothing here says whether a proposal is
*correct*. Both need the annotated worksheet.
