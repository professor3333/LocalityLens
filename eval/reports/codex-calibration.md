# Codex calibration: accepted as a second annotator

The [plan](../calibration/README.md) and its thresholds were pushed before Codex annotated
anything. Codex filled the 60-record calibration set (the owner's validation records, renumbered
and blank), and the worksheet was committed unchanged (5e067b7) before this comparison. The
comparison was run once. Numbers are in [`codex-calibration.json`](codex-calibration.json).

| Field | Codex agrees with the owner | Needed |
|---|---|---|
| **Record category** (answerable / absent from GNIS / unsupported) | **54 of 60** | ≥ 51 |
| **Acceptable GNIS IDs** | **55 of 60** | ≥ 48 |
| Description type | 51 | |
| Supported | 56 | |
| Distance / unit / direction | 57 / 57 / 56 | |
| Qualifiers | 55 | |
| Every field | 47 (78%) | |

**Decision: accepted as a second annotator,** by the rule stated in advance.

- **Category counts:** Codex marks 34 records answerable, 20 absent from GNIS and 6
  unsupported. The owner marks 32, 24 and 4. Like Claude, Codex finds a GNIS feature somewhat
  more often than the owner does, but far less so.
- **Against Claude:** on test-2's 20 repeats, Claude and the owner agreed on category and GNIS
  IDs for 16 of 20, and on every field for 12 (60%).
- **Blindness cannot be verified.** Codex worked in the repository, where the owner's
  annotations and reports for these records exist. It was told not to open them.
  - **A copying diagnostic finds no sign of it:** Codex's notes match the owner's word for word
    in 0 of 56 rows, and are far shorter (71 characters on average, against 300).
  - **The fields that do match** come from a fixed vocabulary (`missing_information`) or are
    copied from the label (`reference_features`).

**What it allows.** Codex's annotations of fresh samples can be used as **secondary** evidence,
always labelled "Codex-annotated; agreement with the owner 54/60 (category), 55/60 (GNIS IDs)".
Owner-annotated results stay the independent evidence.
