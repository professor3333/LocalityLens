# dev-1: LLM extraction (`llm-x2g2-qwen3.5-2b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-1/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 36 · `route_relative` 7 · `distance_and_direction` 5 · `orthogonal_offsets` 1 · `direction_only` 1

**retrieval**: `candidates_found` 23 · `feature_absent_from_index` 14 · `None` 13

**proposal**: `needs_information` 35 · `invalid_extraction` 13 · `unsupported` 2

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| D01 | 12 mi S and 2 mi W of Rico, San Juan Mts., NE edge of Grindstone Lake. | orthogonal_offsets |  |  |  | invalid_extraction |
| D02 | Swales along R.R. between Boulder and Marshall. | route_relative | R.R. | feature_absent_from_index |  | unsupported |
| D03 | North slope of Hoosier Ridge, east of Hoosier Pass. | named_feature | North slope of Hoosier Ridge | feature_absent_from_index |  | needs_information |
| D04 | Black Canyon of the Gunnison National Monument. South rim at the south entrance to the park. | named_feature | Black Canyon of the Gunnison National Monument | feature_absent_from_index |  | needs_information |
| D05 | Rocky Mountain National Park, Front Range, +/- ½ mi. S of Gem L. | distance_and_direction |  |  |  | invalid_extraction |
| D06 | Eldorado Springs/Rocky Flats juction S of Boulder. | named_feature |  |  |  | invalid_extraction |
| D07 | Mineral Basin, ca. 7 miles west of Cottonwood Lake, San Isabel National Forest. Disturbed area on mining road. | named_feature | Mineral Basin | candidates_found | Mineral Basin (Basin, Chaffee, exact_official) | needs_information |
| D08 | 12 miles south of Hwy. 14 on Long Draw Rd. ½ mile up Neota Creek Valley on glacial moraine. | route_relative |  |  |  | invalid_extraction |
| D09 | Rocky Mountain National Park, Trail Ridge, on N. side of Toll Pass. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| D10 | ¼ mi. N of Spitzie house site, Brown's Park. | distance_and_direction |  |  |  | invalid_extraction |
| D11 | Ten Mile Range, east slope, southern part; lower slopes of Quandary Peak. | named_feature | Ten Mile Range | candidates_found | Tenmile Range (Range, Summit, fuzzy_official) | needs_information |
| D12 | Roadside, approximately 2 miles south of the junction of Co. hwys 80 and 145, which is 4 miles east of Naturita. | route_relative |  |  |  | invalid_extraction |
| D13 | Seasonal pool 1 mi. s. of Baseline Lake, s.e. of Boulder. | distance_and_direction | Baseline Lake | candidates_found | Base Line Reservoir (Reservoir, Boulder, fuzzy_variant) | needs_information |
| D14 | Along the highway east from Aspen toward Independence Pass, 11 mi. E of Aspen. | route_relative | Aspen | candidates_found | Aspen (Populated Place, Pitkin, exact_official) | unsupported |
| D15 | Rocky Mountain National Park, Baker Gulch, 8 mi. NNW of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | needs_information |
| D16 | Dartmouth Ave at Sheridan Blvd., Denver. | named_feature | Dartmouth Ave | feature_absent_from_index |  | needs_information |
| D17 | Denver. Platte River. | named_feature | Denver | candidates_found | Denver (Populated Place, Denver, exact_official) | needs_information |
| D18 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: San Luis Valley: by radio tower, ca 2 mi on Colo Hwy 159, S of San Luis. | route_relative |  |  |  | invalid_extraction |
| D19 | Routt National Forest. Big Creek Lake; trail from the lake to Big Creek Falls. | named_feature | Routt National Forest | feature_absent_from_index |  | needs_information |
| D20 | Mosquito Range. Pike National Forest, near SE part of the peak NE of E Buffalo Peak. | named_feature | Mosquito Range | candidates_found | Mosquito Range (Range, Lake, exact_official) | needs_information |
| D21 | Silver Lake, near Boulder. | named_feature | Silver Lake | candidates_found | Silver Lake (Reservoir, Boulder, exact_official) | needs_information |
| D22 | Middle Park. South side of Elk Creek, just west of railroad crossing. | named_feature | Middle Park | candidates_found | Middle Park (Flat, Rio Grande, exact_official) | needs_information |
| D23 | Near Devil Creek on road to Chimney Rock. Piedra. | named_feature | Devil Creek | candidates_found | Devil Creek (Stream, Archuleta, exact_official) | needs_information |
| D24 | Comanche National Grassland: junction of U.S. Hwy 160 and the Villegreen Road, ca 9.5 mi WSW of Kim; 6 mi S of Villegreen. | route_relative |  |  |  | invalid_extraction |
| D25 | Grand Mesa Nat. Forest. Oak brush belt east of intersection of old and new roads #65. | named_feature | Grand Mesa Nat. Forest | feature_absent_from_index |  | needs_information |
| D26 | North of highway, 7 mi. east of Montrose. | distance_and_direction |  |  |  | invalid_extraction |
| D27 | Pond, west side of Colorado R. near mouth of Red Creek, 9½ mi N of Grand Lake. | named_feature | Pond | candidates_found | Middle Pond (Lake, Mesa, core_official) | needs_information |
| D28 | 12.7 road miles east of Delta on Smith Mountain road. | route_relative |  |  |  | invalid_extraction |
| D29 | San Isabel National Forest, Sangre de Cristo Range, North Colony Creek drainage. | named_feature | San Isabel National Forest | feature_absent_from_index |  | needs_information |
| D30 | Along US 285 (South Platte Valley) just E of South Platte High School. Rotten granite cliffs along S side of road. | named_feature | US 285 | feature_absent_from_index |  | needs_information |
| D31 | Route 24, Woodland Park. | named_feature | Route 24 | feature_absent_from_index |  | needs_information |
| D32 | Wasson. San Luis Valley; at stream at the edge of the Rio Grande. | named_feature |  |  |  | invalid_extraction |
| D33 | Sapinero. Along Black Canyon on R. R. | named_feature |  |  |  | invalid_extraction |
| D34 | Near Peach Valley Road in Adobes, E of Olathe. | named_feature | Peach Valley Road | feature_absent_from_index |  | needs_information |
| D35 | Canon in mesa fronting Flagstaff Hill, Boulder. | named_feature |  |  |  | invalid_extraction |
| D36 | Eldorado Springs State Park, South Boulder Creek at emergence from the canyon. Growing along North Canyon Creek Trail by Red Garden Wall. | named_feature | Eldorado Springs State Park | feature_absent_from_index |  | needs_information |
| D37 | Williams Peak Road. | named_feature | Williams Peak Road | feature_absent_from_index |  | needs_information |
| D38 | Hartsel. | named_feature | Hartsel | candidates_found | Hartsel (Populated Place, Park, exact_official) | needs_information |
| D39 | Dickson Creek. | named_feature | Dickson Creek | candidates_found | Dickson Creek (Stream, Eagle, exact_official) | needs_information |
| D40 | La Veta Pass. | named_feature | La Veta Pass | candidates_found | La Veta Pass (Populated Place, Costilla, exact_official) | needs_information |
| D41 | Two Buttes. | named_feature | Two Buttes | candidates_found | Two Buttes (Populated Place, Baca, exact_official) | needs_information |
| D42 | Cardinal. | named_feature | Cardinal | candidates_found | Cardinal (historical) (Populated Place, Boulder, exact_official) | needs_information |
| D43 | Skull Canyon. | named_feature | Skull Canyon | candidates_found | Skull Canyon (Valley, Baca, exact_official) | needs_information |
| D44 | Poudre Canyon. | named_feature | Poudre Canyon | feature_absent_from_index |  | needs_information |
| D45 | At Arboles. | named_feature | Arboles | candidates_found | Arboles (Populated Place, Archuleta, exact_official) | needs_information |
| D46 | Rifle Gap. | named_feature | Rifle Gap | candidates_found | Rifle Gap (Gap, Garfield, exact_official) | needs_information |
| D47 | Arapaho Pass. | named_feature | Arapaho Pass | candidates_found | Arapaho Pass (Gap, Boulder, exact_official) | needs_information |
| D48 | North of Eads. | direction_only | Eads | candidates_found | Eads (Populated Place, Kiowa, exact_official) | needs_information |
| D49 | North Cheyenne Canon. | named_feature | North Cheyenne Canon | candidates_found | North Cheyenne Canyon (Valley, El Paso, core_official) | needs_information |
| D50 | Roadside near Florissant. | named_feature | Florissant | candidates_found | Florissant (Populated Place, Teller, exact_official) | needs_information |
