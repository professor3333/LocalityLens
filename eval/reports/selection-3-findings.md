# selection-3: holding same-name ties (`candidates_unresolved`)

**Question.** Retrieval ranks candidates on evidence: match tier, then feature-type, state and
county agreement, then name similarity. When two candidates are level on all of that, only the
stable-order tie-breakers choose: official over variant name, then the lower GNIS ID. The design
calls this case `candidates_unresolved` and says it must not pass as a confident choice. How
often does it happen, and what does holding it do?

**The rule** ([`resolve/selection.py`](../../src/localitylens/resolve/selection.py),
`same_name_ties`). selection-3 is selection-2 plus one more hold:
- **Tie:** another retrieved candidate has the same evidence key
  (`gazetteer.index.evidence_key`) as the chosen one.
- **Distance:** a tie counts only when its point lies farther from the chosen feature's point
  than the proposed radius, so the region drawn from it would be centred outside this one. A
  town and the spring it is named after, 300 m apart, do not count.
- **Effect:** a computed region with a tie goes to `needs_information`. It keeps its region and
  asks "Which one does the label mean?", naming each feature with its class, county, GNIS ID and
  distance. Approving the record confirms the chosen feature; an edit can choose another.
- **No tuning:** the rule was written from the design and measured once. Nothing in it was
  chosen from these records.

**Data.** The six read samples (in-sample, not a test):
- **Owner-annotated:** audit-50, dev-1, validation.
- **Claude-annotated:** dev-2 to dev-4.
- **Systems:** hybrid-1 with reviewed and derived extents. The LLM ran from the warm cache.
- **Check:** selection-2 regenerated alongside, with readings, proposals and scores identical to
  the committed reports (only timings differ).

## Result

| Ready regions (hybrid-1) | selection-2 | selection-3 | Held by the tie check |
|---|---|---|---|
| Owner-annotated (150 records) | 43, 30 correct (70%) | 41, 29 correct (71%) | 2: 1 correct, 1 wrong |
| Claude-annotated (150 records) | 35, 22 correct (63%) | 34, 21 correct (62%) | 1: correct |
| **All** | **78, 52 correct (67%)** | **75, 50 correct (67%)** | **3: 2 correct, 1 wrong** |

The three held records:
- **A38, Fall River** (Larimer): wrong. The annotation calls the label unsupported. It ties with
  Fall Creek, 38 km away, which GNIS also lists as "Fall River".
- **D40, La Veta Pass** (Costilla): correct. It ties with Veta Pass, 12 km away. In GNIS each
  pass lists the other's name as a variant. The official-name tie-breaker picked the annotated
  one.
- **E40, Hoosier Pass** (Summit County): correct. The record has no county context, and
  another Hoosier Pass lies in Teller County, 104 km away. The lower GNIS ID picked the annotated
  one.

## What it shows

- **Ties are rare:** 3 of 78 ready regions on 300 read records.
- **Holding them doesn't raise precision.** It held 2 correct regions and 1 wrong one, the
  opposite of selection-2's adoption rule (held wrong ≥ 2 × held correct).
- **The two correct ones were right by a tie-breaker,** not by evidence: official over variant
  name, and the lower GNIS ID. So the hold is honest; it just has no measured benefit.
- **A declared check can't settle it:** at about 1 tie per 100 records, a 120-record sample would
  hold one or two regions.
- **Decision:** selection-3 is available (`--selection-3` on `audit rules`/`audit llm`,
  `review import`/`review work`; `selection-3` in a manifest's `selection_version`). The
  release default stays `selection-2`. Making it the default is the owner's choice on design
  grounds: it is abstention only, and the property test shows it never moves a region.
- **Limits:** read data, three events, half of it Claude-annotated.

Counts: [`selection-3-findings.json`](selection-3-findings.json). Reports:
`<sample>-*-extents-derived-sel3.{md,json}`.
