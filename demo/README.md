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
  (`llm-x2g2-qwen3.5-4b-q4km`) runs only where the rules reach no gazetteer candidate. The
  reviewed-extent store is used as committed.
- **No curator decisions** are included. Each record shows the pipeline's proposal awaiting
  review.

Rebuild after a change that alters the pages (needs `llama-server` on 127.0.0.1:8080 and the
gazetteer built, both as in the main README):

```bash
uv run python scripts/build_replay.py   # imports, freezes, replaces demo/site
```

The script refuses to run with uncommitted tracked changes, because each page's banner names
the commit that built it.
