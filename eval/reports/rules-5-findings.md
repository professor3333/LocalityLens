# rules-5: a distance range is asked about, never read as one number

## The bug

Extents batch 4 turned A23 ("rim of Black Mountain, ca 20-21 air mi NE of Craig") into a
computed, wrong region of 15 km around a point 21 mi NE of Craig. The rules had read the range
"20-21" as exactly 21 mi, with no warning: the number pattern could start right after a hyphen,
so the range's second number looked like a plain distance. The
[rules-2 findings](rules-2-findings.md) said ranges "give a validation issue instead of a
guessed value". That was true of the LLM's quotes, not of the rules. Found from an audit
record, so the A23 change below is in-sample.

## The rule

- A number never starts right after a hyphen or dash.
- A range ("20-21", "4–5", "2 to 3", "½-1", "9½-10") before a unit is read as a range. The
  relation, reference and direction are kept, the distance is declared **missing**, and an open
  question names the range ("The distance is a range (20-21 mi): which distance should the
  region use?"). The record goes to `needs_information`, not to a precise-looking circle.
- "1-1/2 mi" is still the mixed number 1.5: a slash fraction is never a range's second number.
- A "range" whose first number is a road number ("Hwy 133 - 3 mi S of X") or is not below the
  second ("12 - 3 mi") is not a range. The search resumes at the second number.
- For the collecting-place rule (rules-3), a range's shorter end decides whether an opening
  offset is at least a mile.

The release manifests now pin `rules_version` `rules-5` (contract test).

## Read samples (audit, dev-1, validation, dev-2)

One reading changes: **A23**. With the range no longer misread, the offset now starts right
after "rim of Black Mountain," and the rules-3 collecting-place rule reads Black Mountain, the
annotated reference.

| Correct candidates | rules-4 → rules-5 | hybrid-1 |
|---|---|---|
| Audit (31 answerable) | 17 → 18 | 17 → 18 |
| dev-1, validation, dev-2 | unchanged | unchanged |
| Read samples (audit, dev-1, validation: 92) | 50 → 51 | 55 → 56 |

With the extent store, A23's wrong region disappears (Black Mountain has no measured extent, so
it asks): hybrid-1 on the read samples computes 36 regions, 33 correct (92%, was 89%); rules 33,
30 correct (91%). dev-2 is unchanged (hybrid-1 11 regions, 10 correct). The gain is in-sample.

The rules-4 hybrid and score reports are kept as `*-pre-rules-5`.

## Unread groups (counts only, no label read)

38,272 groups outside the viewed registry (including dev-3), the reserved held-out components
and their repeated wordings. rules-5 reads 258 of them differently from rules-4:

| Change | Groups |
|---|---|
| A range that was read as one number now asks for the distance | 217 |
| A collecting place before a range offset is now chosen (rules-3 applies, as on A23) | 16 |
| Same reading, the relation quote now includes the range | 9 |
| A range newly recognised where the rules read only a place | 3 |
| A number after a letter and hyphen ("I-70" shape) is no longer a distance | 7 |
| A slash-fraction range ("1/4-1/2 mi" shape): now direction-only, no distance | 3 |
| Odd layouts ("12-2 mi", "Rt 9 -2 mi" shapes): now direction-only | 3 |

These were classified by structure (letters and digits masked), not by reading the labels. The
last two rows lose a number. Of the 7 "I-70" shapes, 3 now read another offset in the same
label and 4 fall back to direction-only. No other change sets a distance.

## What this means

- **Fewer silent ranges.** About 220 unread labels per 38,000 had a range read as one number,
  a false precision of up to the range's width. *Correction: "or" ranges ("2 or 3 mi") were
  still read as one number until [rules-6](rules-6-findings.md).*
- **dev-3 will test rules-5** together with rules-3 and rules-4. Nothing in this change was
  designed on dev-3, which has not been read.
