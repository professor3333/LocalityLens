# Deploy verification sample

`sample.csv` holds two records for the deploy check (`scripts/deploy_verify.py`, run by the
release workflow). They are records of the committed audit sample, development data that is
already published in the static replay:

- **gbif:2573441754** "Northern Gunnison Basin: ca 5 air mi SSW of Paonia." The rules reach it,
  and selection-2 holds its region with a question; the check approves it.
- **gbif:2573332102** "Above Rainbow Lake." The rules reach no candidate, so hybrid-1 calls the
  LLM. This exercises the model server.

Specimen data: University of Colorado Museum of Natural History Herbarium, via GBIF.org
(01 November 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.hqxjjf, CC BY 4.0. Only
identifiers and locality and admin columns are included; no georeference fields.
