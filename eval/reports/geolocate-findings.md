# GEOLocate comparison: results

The method was pinned in [the plan](geolocate-plan.md) before any query was sent. Queries went
out on 2026-11-06 (from 14:55 UTC), for 310 read-sample labels and no locked-test labels. The full
numbers are in [`geolocate-comparison.json`](geolocate-comparison.json).

**One technical fix after the plan.** For 17 labels, GEOLocate answers HTTP 200 with an empty
body. A nonsense string gets the same reply, so an empty body means "no match". The first run
counted these as failures. The script now records them as no result (marked `empty_body`). No
metric changed.

## Points within 5 km (headline) and 1 km of the defensible position

| Annotations | Records | GEOLocate | rules-6 | LLM v2 | hybrid-1 |
|---|---|---|---|---|---|
| Owner (audit, dev-1, validation) | 85 | **58** / 44 | 54 / 51 | 59 / 53 | **61** / 58 |
| Claude (dev-2, dev-3, dev-4) | 91 | **63** / 44 | 54 / 47 | 51 / 47 | **62** / 54 |

Coverage, the number of records each system gave a point for:

| Annotations | GEOLocate | rules-6 | LLM v2 | hybrid-1 |
|---|---|---|---|---|
| Owner (85) | 82 | 63 | 65 | 71 |
| Claude (91) | 89 | 71 | 62 | 79 |

Median error of the points given: GEOLocate 536 m (owner) and 1,038 m (Claude). Ours is 0 m,
because our correct picks land on the GNIS point itself (the bias stated in the plan).

**GEOLocate's uncertainty radius:**
- Its top result gives a numeric radius in 113 of 293 answered queries; the other 180 say
  "Unavailable" or found nothing.
- Where a radius exists and the record has a defensible position, it contains that position in
  23 of 33 (owner) and 27 of 32 (Claude) records.
- When it contains the position, the median radius is 8.2 km and 10.2 km.

## Reading

- **At 5 km, GEOLocate and hybrid-1 are level** (58 vs 61, and 63 vs 62), and both are ahead of
  the rules alone.
- **GEOLocate almost always gives a point** (82 of 85), but a third of those points are more than
  5 km off. Ours give fewer points, and most of them are right. Ours abstain where GEOLocate
  guesses.
- **The 1 km gap in our favour (58 vs 44) is mostly the stated GNIS bias**, not evidence of
  better geography.
- **This compares point placement only.** GEOLocate ran with default settings and no curator,
  and our systems are partly tuned on these samples. No locked-test comparison was made.
