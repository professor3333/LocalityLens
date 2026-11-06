# hybrid-2: an idea estimated, not built (kept as unvalidated)

dev-3 and dev-4 showed rules-first hybrid-1 skipping the LLM whenever the rules reach any
candidate, and the LLM reading "place, offset" labels better on those samples. **hybrid-2**
would use the LLM's reading on labels of the `place_offset` shape (text shape version 2)
whenever it reaches a gazetteer candidate, and behave like hybrid-1 otherwise.

It was estimated from the committed reports (both systems are deterministic, so combining
reports equals a live run). No code was written and nothing was tuned.

| Annotated by | Answerable | rules | LLM | hybrid-1 | hybrid-2 |
|---|---|---|---|---|---|
| Owner: audit, dev-1, validation | 92 | 51 | 46 | **56** | 53 |
| Claude: dev-2, dev-3, dev-4 | 97 | 39 | 45 | 45 | **53** |

- **On Claude-annotated samples** hybrid-2 gains 8 records and loses none (E11; F12, F44;
  G18, G23, G30, G47, G50).
- **On owner-annotated samples** it loses 3 (D07, V006, V016), but those are the labels rules-3
  was written from, so the rules win them in-sample.
- **So the read data cannot decide it.** One side favours the rules in-sample. On the other,
  the annotator is Claude and agreement with the owner has not been measured (the owner judged
  such a check unnecessary).
- **The locked test cannot decide it either:** about 10–15% of labels have this shape
  (validation: 4 of 32 answerable), so hybrid-1 and hybrid-2 would differ on a handful of test
  records at most.

**Decision (2026-11-06): not pursued.** Extraction stays frozen at hybrid-1 with rules-6, the
system line that release 2 tested. hybrid-2 stays an open idea for a time when owner-annotated
place-offset labels exist.
