# Static replay

`site/` is the LocalityLens review screen frozen into static HTML. GitHub Pages serves it.
It is a **replay**: the real pipeline computed every page in advance, nothing runs in the
browser except the map, and decisions and export are switched off. Every page says so.

- **Records:** the 50 audit records (`eval/audit/audit-50.json`), University of Colorado
  Herbarium via GBIF, CC BY 4.0.
  - They passed the specimen screen: none carries `informationWithheld` or
    `dataGeneralizations`.
  - They are development data, read while building the system, so the replay shows how the
    screen works. It is not evidence of accuracy. Measured results are in `docs/evaluation.md`.
  - No validation or locked-test record is published: `tests/unit/test_demo_site.py` fails if
    a page is not an audit record.
- **System:** the release system, hybrid-1. The rules (`rules-6`) run first, and the LLM
  (`llm-x2g2-qwen3.5-4b-q4km`) runs only where the rules reach no gazetteer candidate.
  - **Extents:** hand-measured ones come first. Others are derived from Census place polygons
    and USGS NHD geometry, and each such region says "derived … not curator-reviewed".
  - **Selection check:** `selection-2` (on by default from v0.1.2) holds 3 full regions for a
    question, because each label names another place that GNIS has inside the region or lacks.
    Against the owner's annotations, 2 of the 3 are drawn around the wrong reference.
  - **Result:** 14 records reach "ready for review". Some of those regions are drawn around the
    wrong reference, the system's known weakness
    ([results](../docs/results.md#regions-the-main-shortfall)).
- **No curator decisions** are included. Each record shows the pipeline's proposal awaiting
  review.

Rebuild after a change that alters the pages (needs `llama-server` on 127.0.0.1:8080 and the
gazetteer built, both as in the [user guide](../docs/guide.md)):

```bash
uv run python scripts/build_replay.py   # imports, freezes, replaces demo/site
```

The script refuses to run with uncommitted tracked changes, because each page's banner names
the commit that built it.
