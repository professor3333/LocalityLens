# 50-record audit: LLM extraction (`llm-x1-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `audit-50/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `distance_and_direction` 19 · `named_feature` 13 · `no_locality` 7 · `route_relative` 5 · `None` 5 · `itinerary` 1

**retrieval**: `candidates_found` 19 · `None` 14 · `feature_absent_from_index` 10 · `no_reference_feature` 7

**proposal**: `needs_information` 23 · `unsupported` 12 · `invalid_extraction` 9 · `failed:malformed_model_output` 5 · `computed` 1

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| A01 | Colorado National Monument, S of E entrance. | named_feature |  |  |  | invalid_extraction |
| A02 | 5 mi. E. of Eaton towards Cornish. | distance_and_direction | Eaton | candidates_found | Eaton (Populated Place, Weld, exact_official) | needs_information |
| A03 | Northern Gunnison Basin: ca 6 air mi NE of Almont. | distance_and_direction | Almont | candidates_found | Almont (Populated Place, Gunnison, exact_official) | needs_information |
| A04 | San Juan Nat. Forest: Chicago Basin. Animas River drainage ca. 18 mi. S.E. of Silverton. Near the top of Eolus. | distance_and_direction | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| A05 | Collegiate Peaks Overlook, Arkansas Headwaters State Recreation Area, approx. 1 mile east of Johnson Village on CR 34 off of Highway 285. | route_relative | Johnson Village | candidates_found | Johnson Village (Populated Place, Chaffee, exact_official) | unsupported |
| A06 | Grand Mesa National Forest. Old road on N slope of plateau E of Mesa Creek. | distance_and_direction |  |  |  | invalid_extraction |
| A07 | Head of canon on east slope of Flagstaff Mountain, Boulder. | named_feature | Flagstaff Mountain | candidates_found | Flagstaff Mountain (Summit, Boulder, exact_official) | needs_information |
| A08 | Shale 15 miles east of Pueblo. | distance_and_direction | Pueblo | candidates_found | Pueblo (Populated Place, Pueblo, exact_official) | needs_information |
| A09 | Trail from Soda Tipoff to Mancos River, south rim of Mesa Verde. | itinerary | Mancos River | candidates_found | Mancos River (Stream, San Juan, exact_official) | unsupported |
| A10 | Above Rainbow Lake. | named_feature | Rainbow Lake | candidates_found | Rainbow Lake (Lake, Jackson, exact_official) | needs_information |
| A11 | Lone Cone. | named_feature | Lone Cone | candidates_found | Lone Cone (Summit, Dolores, exact_official) | needs_information |
| A12 | Silt Mesa (right-of-way). | no_locality |  | no_reference_feature |  | unsupported |
| A13 | Northern Gunnison Basin: ca 5 air mi SSW of Paonia. | None |  |  |  | failed:malformed_model_output |
| A14 | White River Plateau. Coffee Pot Road, 8 mi W of Hwy 301. | distance_and_direction | Hwy 301 | feature_absent_from_index |  | needs_information |
| A15 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment. Along a 2-track road next to Woman Creek bypass north of C-2 pond. | None |  |  |  | failed:malformed_model_output |
| A16 | South Park area. | no_locality |  | no_reference_feature |  | unsupported |
| A17 | Mesa de Maya Region of southeastern CO. Gotera Canyon. | no_locality |  | no_reference_feature |  | unsupported |
| A18 | Rico Mts.; northern ridge of Sockrider Mt. | named_feature | Sockrider Mt. | feature_absent_from_index |  | needs_information |
| A19 | Roosevelt National Forest: Front Range: E of Green Ridge Trail or Forest Road 177, just N of Laramie Lake, ca 37 air mi W of Fort Collins. | None |  |  |  | failed:malformed_model_output |
| A20 | Morrison Creek. Buffalo Creek Recreation Area, along Morrison Creek and former National Forest Road 547, 2.69 km. south of National Forest Road 550, 63.3 km. south of the GNIS location of Golden. | distance_and_direction | National Forest Road 550 | feature_absent_from_index |  | needs_information |
| A21 | Near Deer Creek, Chatfield Arboretum site, Denver Botanic Gardens, located at junction of Highway 75 and Deer Creek Rd. | named_feature | Deer Creek | candidates_found | Deer Creek (Stream, Jefferson, exact_official) | needs_information |
| A22 | Lost Man Campground, upper Roaring Fork Valley east of Aspen. | named_feature | Aspen | candidates_found | Aspen (Populated Place, Pitkin, exact_official) | needs_information |
| A23 | North-central Colorado: Elkhead Mountains: rim of Black Mountain, ca 20-21 air mi NE of Craig. | distance_and_direction |  |  |  | invalid_extraction |
| A24 | Tolland. James Peak. | named_feature | James Peak | candidates_found | James Peak (Summit, Gilpin, exact_official) | needs_information |
| A25 | Nine miles north of Hotchkiss on Oak Mesa. | distance_and_direction |  |  |  | invalid_extraction |
| A26 | S slope of Mt. Zenobia. | named_feature | Mt. Zenobia | feature_absent_from_index |  | needs_information |
| A27 | Gunnison Canon. | no_locality |  | no_reference_feature |  | unsupported |
| A28 | 2 mi. W of Hesperus. | distance_and_direction | Hesperus | candidates_found | Hesperus (Populated Place, La Plata, exact_official) | needs_information |
| A29 | Wet Mountain Range. Roadside along State Hwy. 96, approx. 5 miles SW of Wetmore. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| A30 | Pitkin. | no_locality |  | no_reference_feature |  | unsupported |
| A31 | Eastern San Miguel Mts. Seep 0.2 mi. southeast from Graysill Mine. By FR 578. | distance_and_direction | Graysill Mine | feature_absent_from_index |  | needs_information |
| A32 | Baca National Wildlife Refuge, San Luis Valley. Ca. 2 air miles WSW of Crestone. Ca. ½ mile S of County Rd. T; ¼ mile E of Ranch HQ. Near jct. of N. Crestone and S. Crestone creeks. | distance_and_direction | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| A33 | Gravelly bench along highway below Fremont Pass. | named_feature | Fremont Pass | candidates_found | Fremont Pass (Gap, Lake, exact_official) | needs_information |
| A34 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Sangre de Cristo Range: San Isabel National Forest: ca 3.4 road mi on Forest 101 from U.S. Hwy 50. | route_relative | U.S. Hwy 50 | feature_absent_from_index |  | unsupported |
| A35 | Gore Range, Eagles Nest Wilderness Area, central Colorado. 1km west of Lower Piney Lake. | distance_and_direction | Lower Piney Lake | candidates_found | Lone Pine Lake (Reservoir, Larimer, fuzzy_official) | needs_information |
| A36 | Chico Basin Ranch, ca. 28 miles SE of Colorado Springs. Dry uplands above Black Squirrel Creek. | None |  |  |  | failed:malformed_model_output |
| A37 | Rocky Mountain National Park. Neversummer Range. About halfway up south slope of Thunder Mt., 16 miles N of Grand Lake. | distance_and_direction |  |  |  | invalid_extraction |
| A38 | Rocky Mountain National Park, along Old Fall River Rd., ca. 6 mi. from Fall River entrance to Park. | route_relative |  |  |  | invalid_extraction |
| A39 | Dry Creek drainage. | no_locality |  | no_reference_feature |  | unsupported |
| A40 | Mosquito Range, San Isabel National Forest, Weston Pass Rd (FS Rd 7), E from Rte 24, about 1 mi. past USFS boundary, along Big Union Creek. | route_relative | Rte 24 | feature_absent_from_index |  | unsupported |
| A41 | 1.9 miles up Pool Table Road approx. 1/8 mile west of road. | route_relative | Pool Table Road | feature_absent_from_index |  | unsupported |
| A42 | Dinosaur National Monument. Douglas Mtn Boulevard, ca. 3 mi. WSW of Five Springs. | distance_and_direction | Five Springs | candidates_found | Five Spring (Spring, Moffat, fuzzy_official) | computed |
| A43 | Great Sand Dunes Natl. Mon. Morris Gulch just below horse trap. | named_feature |  |  |  | invalid_extraction |
| A44 | West of Hesperus. West slope of La Plata Mts. | None |  |  |  | failed:malformed_model_output |
| A45 | Lone Mesa State Park, 3.5 miles west of entrance at FR 526; west-facing slope. | distance_and_direction |  |  |  | invalid_extraction |
| A46 | Co Rd PP ca 3.2 mi W jct Co Rd 5. Immediately E of dry tributary of Two Buttes Creek. | distance_and_direction |  |  |  | invalid_extraction |
| A47 | Medano Ranch, east part of valley. | named_feature | Medano Ranch | feature_absent_from_index |  | needs_information |
| A48 | Chokecherry Draw, NW part of Moffat County. | no_locality |  | no_reference_feature |  | unsupported |
| A49 | 1.5 mi N of CO24 off tranquil Acres Rd along Rule Cr. | distance_and_direction | CO24 | feature_absent_from_index |  | needs_information |
| A50 | "Hattie Sammon's Pasture", Powderhorn. | named_feature | Powderhorn | candidates_found | Powderhorn (Populated Place, Gunnison, exact_official) | needs_information |
