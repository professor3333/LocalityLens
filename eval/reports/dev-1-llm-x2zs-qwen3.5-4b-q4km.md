# dev-1: LLM extraction (`llm-x2zs-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-1/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 22 · `route_relative` 12 · `distance_and_direction` 7 · `no_locality` 6 · `orthogonal_offsets` 1 · `other` 1 · `direction_only` 1

**retrieval**: `candidates_found` 17 · `None` 14 · `feature_absent_from_index` 12 · `no_reference_feature` 7

**proposal**: `unsupported` 19 · `needs_information` 17 · `invalid_extraction` 14

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| D01 | 12 mi S and 2 mi W of Rico, San Juan Mts., NE edge of Grindstone Lake. | orthogonal_offsets | Rico, San Juan Mts. | feature_absent_from_index |  | unsupported |
| D02 | Swales along R.R. between Boulder and Marshall. | route_relative | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | unsupported |
| D03 | North slope of Hoosier Ridge, east of Hoosier Pass. | named_feature | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | needs_information |
| D04 | Black Canyon of the Gunnison National Monument. South rim at the south entrance to the park. | named_feature | Black Canyon of the Gunnison National Monument | feature_absent_from_index |  | needs_information |
| D05 | Rocky Mountain National Park, Front Range, +/- ½ mi. S of Gem L. | distance_and_direction |  |  |  | invalid_extraction |
| D06 | Eldorado Springs/Rocky Flats juction S of Boulder. | route_relative |  |  |  | invalid_extraction |
| D07 | Mineral Basin, ca. 7 miles west of Cottonwood Lake, San Isabel National Forest. Disturbed area on mining road. | named_feature |  |  |  | invalid_extraction |
| D08 | 12 miles south of Hwy. 14 on Long Draw Rd. ½ mile up Neota Creek Valley on glacial moraine. | route_relative | Hwy. 14 | feature_absent_from_index |  | unsupported |
| D09 | Rocky Mountain National Park, Trail Ridge, on N. side of Toll Pass. | named_feature |  |  |  | invalid_extraction |
| D10 | ¼ mi. N of Spitzie house site, Brown's Park. | distance_and_direction | Spitzie house site | feature_absent_from_index |  | needs_information |
| D11 | Ten Mile Range, east slope, southern part; lower slopes of Quandary Peak. | named_feature | Quandary Peak | candidates_found | Quandary Peak (Summit, Summit, exact_official) | needs_information |
| D12 | Roadside, approximately 2 miles south of the junction of Co. hwys 80 and 145, which is 4 miles east of Naturita. | distance_and_direction |  |  |  | invalid_extraction |
| D13 | Seasonal pool 1 mi. s. of Baseline Lake, s.e. of Boulder. | distance_and_direction | Baseline Lake | candidates_found | Base Line Reservoir (Reservoir, Boulder, fuzzy_variant) | needs_information |
| D14 | Along the highway east from Aspen toward Independence Pass, 11 mi. E of Aspen. | distance_and_direction |  |  |  | invalid_extraction |
| D15 | Rocky Mountain National Park, Baker Gulch, 8 mi. NNW of Grand Lake. | named_feature | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | needs_information |
| D16 | Dartmouth Ave at Sheridan Blvd., Denver. | named_feature | Dartmouth Ave | feature_absent_from_index |  | needs_information |
| D17 | Denver. Platte River. | no_locality |  | no_reference_feature |  | unsupported |
| D18 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: San Luis Valley: by radio tower, ca 2 mi on Colo Hwy 159, S of San Luis. | route_relative | San Luis | candidates_found | San Luis (Populated Place, Costilla, exact_official) | unsupported |
| D19 | Routt National Forest. Big Creek Lake; trail from the lake to Big Creek Falls. | route_relative | Big Creek Lake | candidates_found | Big Creek Lake (Lake, Routt, exact_official) | unsupported |
| D20 | Mosquito Range. Pike National Forest, near SE part of the peak NE of E Buffalo Peak. | named_feature |  |  |  | invalid_extraction |
| D21 | Silver Lake, near Boulder. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| D22 | Middle Park. South side of Elk Creek, just west of railroad crossing. | named_feature |  |  |  | invalid_extraction |
| D23 | Near Devil Creek on road to Chimney Rock. Piedra. | route_relative | Chimney Rock | candidates_found | Chimney Rock (Summit, Archuleta, exact_official) | unsupported |
| D24 | Comanche National Grassland: junction of U.S. Hwy 160 and the Villegreen Road, ca 9.5 mi WSW of Kim; 6 mi S of Villegreen. | route_relative | U.S. Hwy 160 | feature_absent_from_index |  | unsupported |
| D25 | Grand Mesa Nat. Forest. Oak brush belt east of intersection of old and new roads #65. | route_relative | intersection of old and new roads #65 | feature_absent_from_index |  | unsupported |
| D26 | North of highway, 7 mi. east of Montrose. | distance_and_direction |  |  |  | invalid_extraction |
| D27 | Pond, west side of Colorado R. near mouth of Red Creek, 9½ mi N of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | needs_information |
| D28 | 12.7 road miles east of Delta on Smith Mountain road. | route_relative | Delta | candidates_found | Delta (Populated Place, Delta, exact_official) | unsupported |
| D29 | San Isabel National Forest, Sangre de Cristo Range, North Colony Creek drainage. | other |  | no_reference_feature |  | unsupported |
| D30 | Along US 285 (South Platte Valley) just E of South Platte High School. Rotten granite cliffs along S side of road. | route_relative | South Platte High School | feature_absent_from_index |  | unsupported |
| D31 | Route 24, Woodland Park. | no_locality |  | no_reference_feature |  | unsupported |
| D32 | Wasson. San Luis Valley; at stream at the edge of the Rio Grande. | named_feature | Rio Grande | candidates_found | Rio Grande (Stream, Cameron, exact_official) | needs_information |
| D33 | Sapinero. Along Black Canyon on R. R. | route_relative | Black Canyon | candidates_found | Black Canyon (Valley, Larimer, exact_official) | unsupported |
| D34 | Near Peach Valley Road in Adobes, E of Olathe. | route_relative | Peach Valley Road | feature_absent_from_index |  | unsupported |
| D35 | Canon in mesa fronting Flagstaff Hill, Boulder. | named_feature | Flagstaff Hill | feature_absent_from_index |  | needs_information |
| D36 | Eldorado Springs State Park, South Boulder Creek at emergence from the canyon. Growing along North Canyon Creek Trail by Red Garden Wall. | named_feature | South Boulder Creek | candidates_found | South Boulder Creek (Stream, Gilpin, exact_official) | needs_information |
| D37 | Williams Peak Road. | no_locality |  | no_reference_feature |  | unsupported |
| D38 | Hartsel. | no_locality |  | no_reference_feature |  | unsupported |
| D39 | Dickson Creek. | named_feature | Dickson Creek. | candidates_found | Dickson Creek (Stream, Eagle, exact_official) | needs_information |
| D40 | La Veta Pass. | named_feature |  |  |  | invalid_extraction |
| D41 | Two Buttes. | named_feature | Two Buttes | candidates_found | Two Buttes (Populated Place, Baca, exact_official) | needs_information |
| D42 | Cardinal. | no_locality |  | no_reference_feature |  | unsupported |
| D43 | Skull Canyon. | named_feature |  |  |  | invalid_extraction |
| D44 | Poudre Canyon. | named_feature | Poudre Canyon. | feature_absent_from_index |  | needs_information |
| D45 | At Arboles. | named_feature |  |  |  | invalid_extraction |
| D46 | Rifle Gap. | named_feature | Rifle Gap | candidates_found | Rifle Gap (Gap, Garfield, exact_official) | needs_information |
| D47 | Arapaho Pass. | named_feature |  |  |  | invalid_extraction |
| D48 | North of Eads. | direction_only |  |  |  | invalid_extraction |
| D49 | North Cheyenne Canon. | named_feature | Cheyenne Canon | feature_absent_from_index |  | needs_information |
| D50 | Roadside near Florissant. | no_locality |  | no_reference_feature |  | unsupported |
