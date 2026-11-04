# rules-2 and validation 3: air miles, spelled-out numbers, bare "ca"

The audit findings listed label numbers that neither system read. Three were fixed, all in
shared, versioned code:

| Change | Where | Example |
|---|---|---|
| `air mi`, `air miles` read as a distance and unit | rules-2 | "ca 6 air mi NE of Almont" was read as direction only |
| Spelled-out whole numbers and "half", **only directly before a unit** | rules-2 and the shared quantity parser (validation 3) | "Nine miles north of Hotchkiss" |
| `ca` without a dot, before a number, read as "approximately" | rules-2 | "ca 6 air mi" |

- **Number words never count inside a name.** "Two Buttes", "Ten Mile Range" and "Hiway
  Nine" stay names.
- **A spelled-out number takes the precision of the same number in digits.** "Nine miles"
  has a precision of 1 mile, like "9 mi". This is a project convention, because Best
  Practices does not treat words separately.
- **Ranges ("20-21 air mi") and compound words ("twenty-five") are still not parsed.** They
  give a validation issue instead of a guessed value.

Because the quantity parser is shared, the LLM's quotes are checked with it too
(`VALIDATION_VERSION` 3). Its completions did not change: they came from the completion cache,
identical to the committed run.

## Results (correct proposal candidates)

| Set | rules-1 → rules-2 | LLM v2 (validation 2 → 3) | hybrid-1 |
|---|---|---|---|
| Audit (31) | 14 → **17** | 12 → 13 | 14 → **17** |
| dev-1 (29) | 16 → 16 | 18 → 18 | 18 → 18 |
| Validation (32) | 13 → 13 | 15 → 15 | 16 → 16 |

- **Nothing got worse.** No record lost a correct candidate or a correct critical
  interpretation in any system.
- **The audit gains are in-sample.** The fixes target A03, A13 and A25, which the audit
  findings named, so the audit can't show they generalize.
  - rules: A03, A13, A25
  - LLM: A25, whose "Nine" now parses
- **dev-1 has no such labels**, so it shows no effect.
- **Validation** gains one critical interpretation (V004, "Half mile E of Hiway Nine, …").
  Its reference is absent from GNIS, so no correct candidate changes.
- **The locked test was not scored.** Releases 1 and 2 used rules-1 and validation 2. Any
  test number for rules-2 needs a new declaration.

The previous reports are kept as `*-pre-rules-2.*`.
