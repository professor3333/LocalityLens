# test-3 diagnosis: where the wrong ready regions go wrong

**This is a diagnosis of a used set, not an evaluation.** test-3 was scored once
([result](test-3.md)). Nothing here changes that result, and no rule may be tuned on it and then
claimed as tested.

- **Method:** a script sorted every hybrid-1 ready region into one stage, from the score
  judgements and the system's reference name compared with the annotated reference (name key or
  core key).
- **Published here:** counts only. No label, name or record output was read. The rows to review
  are listed by ID only, in `eval/benchmark/test-3/diagnosis/`.
- **Annotations:** by Codex, labelled "Codex-annotated; agreement with the owner 54/60
  (category), 55/60 (GNIS IDs)". Those figures describe consistency with the owner on other
  records. They don't establish accuracy on test-3.

## Stages

| hybrid-1 ready regions | Without the check | With `selection-2` | Held back |
|---|---|---|---|
| Correct | 7 | 5 | 2 |
| **Clause choice, annotated place in GNIS:** the system used another place | 20 | 6 | 14 |
| **Clause choice, annotated place absent from GNIS:** the system used another place, usually the offset's town | 21 | 17 | 4 |
| Annotated unsupported (route, itinerary…) | 5 | 1 | 4 |
| Same name, other GNIS feature | 0 | 0 | 0 |
| Reading error (distance, direction, unit, qualifiers) with the right reference | 0 | 0 | 0 |
| **Total** | 53 | 29 | 24 |

- **Almost every wrong region is a clause choice:** 41 of 46. No ready region failed on GNIS
  identity or on reading the offset.
- **selection-2 catches most of the clear errors.** Where the annotated place is in GNIS, it held
  back 14 of 20.
- **It catches few of the absent-place cases:** 4 of 21. These make up most of what it leaves
  ready (17 of 24 wrong).
- **Region construction can't be judged here.** The scorer counts a region correct when the
  reading and the reference pick are right. It has no containment truth, so construction errors
  (extent, radius) are not measured.

## An open convention, not only a system error

The guide says to annotate "the clause a curator would georeference: the most specific one". It
does not say what happens when that place is **absent from GNIS**.

- **Codex chose the specific place in all 21 cases,** so each is scored "reference absent", and
  any region the system computes counts as wrong.
- **A curator might instead georeference the offset** when the specific place can't be found.
  Then some of these 21 regions would be acceptable, if they contain the place.
- **These totals can't decide which reading is right.** Settling the convention is the owner's
  call, and needs a guide change before any future sample is annotated.
- **Under either convention, 20 of the 46 wrong regions** pick another place when the annotated
  one is in GNIS.

## Rows for independent review

`eval/benchmark/test-3/diagnosis/dispute-candidates.txt` lists, by ID only, the ready-region rows
where:
- the system's reference has the same name as an annotated one; or
- the annotation carries an "unsure" marker.

There are 5 without the check and 4 with it. The 41 clause-choice rows (without the check) are listed in `clause-choice.txt` there. The listed
rows and a sample of the clause-choice rows are the ones an annotator other than Codex should
check.

Reproduce: `uv run python scripts/diagnose_regions.py` with the test-3 sample, worksheet, hybrid
report and score report (the script prints counts only).
