# rules-6: "or" also joins a distance range

rules-5 treated "-", "–" and "to" as range separators, but not "or". "2 or 3 mi NE of X" was
still read as exactly 3 mi, with no warning, so the [rules-5 findings](rules-5-findings.md)
claimed too much with "no more silent ranges". rules-6 adds "or": the distance is declared
missing and an open question names the range, as for "20-21". A road number before it
("Hwy 1 or 2 mi N") is still no range.

## Effect

- **Read samples (audit, dev-1, validation, dev-2):** no extraction changes. All 28 rules, hybrid
  and score reports are identical to the rules-5 ones apart from the version label (kept as
  `*-pre-rules-6`).
- **Unread groups (counts only):** 0 of 38,272 change.

So no label outside dev-3 and the reserved held-out groups is written this way. The gap was
raised after dev-3 had been annotated, so a dev-3 label may be where it came from. The dev-3
scoring plan therefore reports, separately and as in-sample, every dev-3 record that rules-5
and rules-6 read differently.
