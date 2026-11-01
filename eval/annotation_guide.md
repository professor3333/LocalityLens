# Annotation guide

Used for every worksheet: the [audit](audit/) and each [dev sample](dev/). One row per sampled
locality group. Annotate **before** looking at any system output for that sample.

Work from the `locality` text and the supplied `county` column only. Use maps or GNIS to
identify features, never to work out where the specimen "really" is. Mark any value you are
unsure of with `?` and explain in `notes`. A flagged label is better than a guessed one.

**Two passes.** Pass 1: every column except `acceptable_gnis_ids`, from the text alone.
Pass 2: look up GNIS IDs. Doing it second keeps search results from shaping how you read the label.

**One clause.** When a label chains several clauses, annotate the clause a curator would
georeference: the most specific one, giving the smallest area. List the other clauses in `notes`
as `multi: …`.

| Column | Fill with |
|---|---|
| `description_type` | The chosen clause's type: `named_feature` (including "N slope of X", "summit of X", "above X"), `distance_and_direction` (straight line; "air mi" counts), `distance_only`, `direction_only`, `route_relative` ("road mi", "up the road", "along the trail"), `itinerary`, `between_features`, `orthogonal_offsets`, `admin_only`, `habitat_only`, `no_locality` |
| `supported` | `yes` for named feature, distance + direction, distance only, direction only, or an ambiguous name a curator could settle. `no` otherwise. `no` means outside v1 scope, not that the record cannot be georeferenced |
| `reference_features` | The place(s) the clause is measured from, spelled as on the label (`;`-separated) |
| `acceptable_gnis_ids` | Every defensible GNIS feature ID from our snapshot (`;`-separated), `absent` if not in GNIS, blank if there is no reference |
| `distance` | As written: `2`, `1.5`, `1/2`, `20-21` (for a range, also note `range`) |
| `unit` | `mile`, `kilometre`, `metre`, `foot`, `yard`. A bare "m" (miles or metres?): leave blank and add `unit` to missing |
| `direction` | 16-point code `N` `NNE` … `NNW` ("S.E." is `SE`). Blank for "upstream", "above" and the like |
| `qualifiers` | As written, `;`-separated: about, ca., approx., near, vicinity, `?` |
| `missing_information` | From: `extent`, `which_feature`, `distance`, `unit`, `direction`, `route_geometry`, `feature_not_in_gnis`, `historical_name`, `other: …` |
| `notes` | `multi: …`, `bracketed: …` (text in square brackets was added by someone other than the collector), positions on a feature, elevation, doubts |

Elevations ("9,800 ft") are not distances. "Co." means county. "Mt.", "Cr." and "Canon" are read
as Mount, Creek and Canyon.

**Finding GNIS IDs:**

```bash
uv run localitylens gazetteer search "Mount Zenobia" --county Moffat --limit 10
uv run localitylens gazetteer search "Zenobia" --limit 10
```

Try spelling variants. If the label could mean either of two features, list both and add
`which_feature`.

**Saving:** keep the file as CSV, UTF-8, with the same name. In Excel, set `gbif_id` to Text.
**Self-consistency:** about a week later, re-annotate about 10 random records without looking at
your first answers. With one annotator, the agreement rate is what gets published.
