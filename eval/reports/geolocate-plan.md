# GEOLocate comparison: plan (pinned before any query)

GEOLocate is the existing tool in this domain. This plan fixes what is sent, what is measured
and how it is reported **before** any label text goes to its web service. The result is published
whatever it is.

## What is sent

- **Records:** the six read samples only: audit-50, dev-1 and validation (owner-annotated), and
  dev-2, dev-3 and dev-4 (Claude-annotated). That is 310 records. The locked test is never sent.
- **Per record:** the original locality text unchanged, `country=USA`, `state=Colorado`, and the
  supplied county. The county is left out when it is empty, starts with "Unknown", or names two
  counties ("A/B", "A or B"), as `COUNTY_CONTEXT_VERSION` 1 treats it.
- **Settings** (glcwrap, `geolocatesvcv2`): `hwyX=false`, `enableH2O=false`, `doUncert=true`,
  `doPoly=false`, `displacePoly=false`, `languageKey=0`, `fmt=geojson`. These are GEOLocate's
  defaults as used by other clients, with no tuning.
- **One request at a time**, a 1 s pause between requests, at most 4 attempts with backoff.
  Raw responses are cached in `eval/.cache/geolocate/` and are not committed.
- **Code:** `scripts/geolocate_compare.py` (`COMPARE_VERSION` geolocate-compare-1).

## What is measured

Only **answerable** records with a **defensible position** are scored:

- **Named feature:** the GNIS primary point of each acceptable GNIS ID.
- **Distance and direction** (annotated distance, unit and direction): the geodesic offset from
  that point, at the direction's nominal bearing.
- **Other relations** (direction only, distance only and the rest) defend no point. They are
  counted and not scored.

Each system gives at most one point:

- **GEOLocate:** its highest-scoring result.
- **Ours** (rules-6, LLM v2 and hybrid-1, from the committed reports): the top candidate's GNIS
  point, offset by the system's own reading when it has a distance, unit and direction.

Distances are geodesics on GRS80. GEOLocate's WGS84 and GNIS's NAD83 differ by about 1–2 m here,
and are not transformed. With several acceptable IDs, the nearest one counts.

**Reported, per sample and pooled by annotator:**

1. Records with a point (coverage).
2. **Points within 5 km** of the defensible position (headline), and within 1 km. Records with
   no point count as misses.
3. Median error of the points given.
4. **GEOLocate containment:** how often its own uncertainty radius contains the defensible
   position, with the median radius when it does. Our systems compute regions only where a
   reviewed extent exists, so our containment is the computed-region figure already published
   in [extents-findings.md](extents-findings.md), not a like-for-like comparison.

No significance test or target is set. This is a descriptive comparison on read data.

## Known biases, stated in advance

- **The positions come from GNIS, which our systems use natively.** When our system picks an
  acceptable ID its error is 0 m, while GEOLocate may place the same feature from another
  gazetteer, a few hundred metres away. The 1 km figure favours us. The 5 km headline is less
  sensitive to this.
- **The positions are reference points, not collecting sites.** A town's point is not where the
  specimen was collected. This measures whether each tool finds the place the label names.
- **All six samples have been read in development**, and our systems were tuned on some of them,
  so our numbers are partly in-sample. GEOLocate's are not.
- **Our systems' figures were computed once in a dry run of the script before this plan was
  written**, with no GEOLocate responses present. GEOLocate's figures have not been seen.
- **GEOLocate's service may change over time.** The query date is recorded with the results.
