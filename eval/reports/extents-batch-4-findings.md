# Extents batch 4: dev-2's references, and regions on unseen labels

dev-2's first score left only 2 full regions, because its references had no measured extent
([dev-2 findings](dev-2-findings.md)). This batch measures the references that block a
**correct** dev-2 candidate, then reruns every read sample with the new store. No rule, prompt or
annotation changed. The LLM came from the completion cache (210 hits, 0 misses). The locked test
was not run.

dev-2's plan-pinned reports (store `5a98f0c2…`, 2 regions) are kept as
`dev-2-*-extents-plan.{json,md}`. The `dev-2-*-extents` reports are the rerun with this store
(`a3ee12cb…`).

## What was measured

21 features block a correct dev-2 candidate. Two (Bear Draw, Moffat) are references of
direction-only labels, which still lack a distance, and Almont was already pending. That leaves
18, of which 12 are measured and 6 stay pending.

| Feature | Class | Extent | How |
|---|---|---|---|
| Craig | town | 4,700 m | farthest vertex of its USGS `govunits` incorporated-place polygon |
| Boulder | town | 12,000 m | same; the far point is the end of a narrow NE arm of the city limit |
| Bayfield | town | 3,000 m | same |
| Somerset | town | 1,700 m | census-designated place polygon (no incorporated limit) |
| Dolores | town | 2,100 m | incorporated-place polygon |
| South Fork | town | 4,400 m | incorporated-place polygon |
| Oak Creek (Rio Blanco) | stream | 37,000 m | farthest vertex of the NHD flowlines carrying its GNIS ID |
| Beaver Creek (Routt, 169843) | stream | 2,800 m | same |
| Arapaho Glacier | glacier | 430 m | farthest vertex of the NHD ice-mass polygon carrying its GNIS ID |
| Rosalie Peak | summit | 3,400 m | QRG §2.1.2 summit rule; edges located with 3DEP profiles |
| Milner Pass | gap | 1,800 m | project gap rule; SW approach to the Beaver Creek floor (3DEP and NHD agree) |
| San Francisco Pass | gap | 3,000 m | project gap rule; NW approach to the San Francisco Creek floor |

Every polygon, line and far point was drawn on the USGS Topo basemap to check that it matches
the mapped feature. Values are the geodesic (GRS80) readout, rounded up to the next
two-significant-figure step. Each row says which boundary it used.

**What is new in the method.** Earlier town rows were measured with the viewer's Distance tool
and checked against the `govunits` polygon. Here the polygon's farthest vertex *is* the reading,
checked on the basemap. Streams and the glacier use the NHD features that carry the row's GNIS
ID, so the name decides the reach, not the eye. Summit and gap edges are still terrain
judgments. As before, they are rough.

**Left pending, with reasons:**
- **Cahone, Minnehaha:** no limit of their own in `govunits` (Minnehaha lies inside Manitou
  Springs' polygon).
- **Mount Audubon:** its east shoulder falls steadily for 5 km between Coney and Mitchell
  creeks toward Brainard Lake, with no edge.
- **Niwot Ridge:** the named ridge runs ESE into the foothills near CO 72 with no clear end.
- **Douglas Pass:** both approaches descend canyons at about 500–700 ft per km, with no valley
  floor where an approach ends (like Fremont Pass).
- **Boulder Falls:** the map shows only a point, and the policy has no default for falls.

The store now holds 68 reviewed rows and 47 pending (`extents check`: 0 problems).

## Results

Correct candidates are unchanged. Only full regions (`computed`) move.

| | Rules `rules-4` | LLM | **Hybrid `hybrid-1`** |
|---|---|---|---|
| **dev-2, unseen labels (36 answerable)** | | | |
| Regions computed | 10 | 8 | **11** |
| … correct (precision) | 9 (90%) | 7 (88%) | **10 (91%)** |
| Useful coverage | 9 (25%) | 7 (19%) | **10 (28%)** |
| *dev-2 with the plan's store* | *2 / 2* | *2 / 1* | *2 / 2* |
| **Read samples: audit, dev-1, validation (92 answerable)** | | | |
| Regions computed | 34 (was 31) | 34 (was 33) | **37 (was 34)** |
| … correct (precision) | 30 (88%, was 97%) | 29 (85%, was 88%) | **33 (89%, was 97%)** |
| Useful coverage | 30 (33%) | 29 (32%) | **33 (36%)** |

**dev-2's regions** (hybrid-1). The median correct radius is 3,239 m:

| Record | Reference | Relation | Radius | Correct |
|---|---|---|---|---|
| E07 | Bayfield (town) | named | 3,039 m | yes |
| E13 | Boulder (town) | named | 12,039 m | **no** |
| E15 | Dolores (town) | offset | 11,029 m | yes |
| E19 | Rosalie Peak | named | 3,439 m | yes |
| E20 | Oak Creek (stream) | offset | 38,814 m | yes |
| E24 | Swede Spring | named | 42 m | yes |
| E28 | Craig (town) | offset | 39,427 m | yes |
| E32 | Boulder (town) | named | 12,039 m | yes |
| E39 | Milner Pass | named | 1,839 m | yes |
| E40 | Hoosier Pass | named | 2,239 m | yes |
| E49 | Somerset | named | 1,739 m | yes |

E20 is correct because the annotation accepts both Oak Creek the stream and Oak Creek the town.
Measured from the stream's mouth, its region is 39 km. **Precision ignores size:** a correct
39 km circle counts the same as a correct 42 m one.

## The new incorrect regions

Every new incorrect region was already a wrong reading. The extent only lets it reach `computed`:

| Record | Label (shortened) | System reading | Annotation |
|---|---|---|---|
| A15, V029 | "Rocky Flats Site. 7 miles south of Boulder …" | offset from Boulder | the place named later (Woman Creek bypass: absent; Rock Creek) |
| A23 | "rim of Black Mountain, ca 20-21 air mi NE of Craig" | 21 mi NE of Craig | Black Mountain |
| V060 (LLM) | "Bluebell Canyon, south edge of Boulder." | Boulder | Bluebell Canyon |
| E13 | "Campus of University, Boulder." | Boulder | absent from GNIS |

- **More extents expose reading errors.** Before this batch, these readings stopped at
  `needs_information` because the reference had no extent. That hid the error from the region
  numbers. As more extents arrive, the region precision will fall toward the rate at which the
  interpretation and the reference are right.
- **A23 also shows a range bug.** The rules read "20-21 air mi" as exactly 21 mi. The number
  pattern starts a match right after a hyphen, so the range's upper bound looks like a plain
  distance. The [rules-2 findings](rules-2-findings.md) say ranges "give a validation issue
  instead of a guessed value". That holds for the LLM's quotes, not for the rules, which drop
  the lower bound without a warning. It is false precision, and fixing it is a rules change
  (a new rules version), not made here. *Update: fixed in [rules-5](rules-5-findings.md); A23
  now reads Black Mountain and its wrong region is gone (read samples: hybrid-1 36 regions, 33
  correct, 92%).*
- **E13's region would contain the campus.** The scorer counts it as incorrect because the
  annotated reference is absent from GNIS. Region containment would judge it differently.

## What this means

- **On unseen labels, regions behave like the read samples.** hybrid-1 gives 10 correct regions
  of 11 (91%) on dev-2, against 33 of 37 (89%) on the read samples. Both are below the 95%
  target, and both are small counts.
- **Coverage is still far from 70%.** dev-2 reaches 28%. Most remaining correct candidates wait
  on extents with no defensible edge, or on direction-only labels with no distance.
- **The precision target needs better readings, not more extents.** The new errors come from
  choosing the wrong clause (Rocky Flats, Bluebell Canyon) and from the range bug.
