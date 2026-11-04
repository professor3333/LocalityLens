# 50-record audit: LLM extraction (`llm-x2g2-qwen3.5-2b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `audit-50/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 27 · `distance_and_direction` 11 · `route_relative` 9 · `direction_only` 2 · `no_locality` 1

**retrieval**: `feature_absent_from_index` 20 · `None` 18 · `candidates_found` 11 · `no_reference_feature` 1

**proposal**: `needs_information` 27 · `invalid_extraction` 18 · `unsupported` 5

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| A01 | Colorado National Monument, S of E entrance. | named_feature | Colorado National Monument | feature_absent_from_index |  | needs_information |
| A02 | 5 mi. E. of Eaton towards Cornish. | distance_and_direction | Eaton | candidates_found | Eaton (Populated Place, Weld, exact_official) | needs_information |
| A03 | Northern Gunnison Basin: ca 6 air mi NE of Almont. | distance_and_direction |  |  |  | invalid_extraction |
| A04 | San Juan Nat. Forest: Chicago Basin. Animas River drainage ca. 18 mi. S.E. of Silverton. Near the top of Eolus. | named_feature | San Juan Nat. Forest | feature_absent_from_index |  | needs_information |
| A05 | Collegiate Peaks Overlook, Arkansas Headwaters State Recreation Area, approx. 1 mile east of Johnson Village on CR 34 off of Highway 285. | route_relative |  |  |  | invalid_extraction |
| A06 | Grand Mesa National Forest. Old road on N slope of plateau E of Mesa Creek. | named_feature | Grand Mesa National Forest | feature_absent_from_index |  | needs_information |
| A07 | Head of canon on east slope of Flagstaff Mountain, Boulder. | named_feature | Flagstaff Mountain | candidates_found | Flagstaff Mountain (Summit, Boulder, exact_official) | needs_information |
| A08 | Shale 15 miles east of Pueblo. | distance_and_direction |  |  |  | invalid_extraction |
| A09 | Trail from Soda Tipoff to Mancos River, south rim of Mesa Verde. | route_relative | Mancos River | candidates_found | Mancos River (Stream, San Juan, exact_official) | unsupported |
| A10 | Above Rainbow Lake. | direction_only |  |  |  | invalid_extraction |
| A11 | Lone Cone. | named_feature |  |  |  | invalid_extraction |
| A12 | Silt Mesa (right-of-way). | named_feature | Silt Mesa | feature_absent_from_index |  | needs_information |
| A13 | Northern Gunnison Basin: ca 5 air mi SSW of Paonia. | distance_and_direction |  |  |  | invalid_extraction |
| A14 | White River Plateau. Coffee Pot Road, 8 mi W of Hwy 301. | route_relative |  |  |  | invalid_extraction |
| A15 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment. Along a 2-track road next to Woman Creek bypass north of C-2 pond. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| A16 | South Park area. | no_locality |  | no_reference_feature |  | unsupported |
| A17 | Mesa de Maya Region of southeastern CO. Gotera Canyon. | named_feature | Mesa de Maya Region of southeastern CO. | feature_absent_from_index |  | needs_information |
| A18 | Rico Mts.; northern ridge of Sockrider Mt. | named_feature | Rico Mts. | feature_absent_from_index |  | needs_information |
| A19 | Roosevelt National Forest: Front Range: E of Green Ridge Trail or Forest Road 177, just N of Laramie Lake, ca 37 air mi W of Fort Collins. | named_feature | Roosevelt National Forest | feature_absent_from_index |  | needs_information |
| A20 | Morrison Creek. Buffalo Creek Recreation Area, along Morrison Creek and former National Forest Road 547, 2.69 km. south of National Forest Road 550, 63.3 km. south of the GNIS location of Golden. | route_relative | National Forest Road 550 | feature_absent_from_index |  | unsupported |
| A21 | Near Deer Creek, Chatfield Arboretum site, Denver Botanic Gardens, located at junction of Highway 75 and Deer Creek Rd. | named_feature | Deer Creek | candidates_found | Deer Creek (Stream, Jefferson, exact_official) | needs_information |
| A22 | Lost Man Campground, upper Roaring Fork Valley east of Aspen. | named_feature | Lost Man Campground | feature_absent_from_index |  | needs_information |
| A23 | North-central Colorado: Elkhead Mountains: rim of Black Mountain, ca 20-21 air mi NE of Craig. | distance_and_direction |  |  |  | invalid_extraction |
| A24 | Tolland. James Peak. | named_feature | Tolland | candidates_found | Tolland (Populated Place, Gilpin, exact_official) | needs_information |
| A25 | Nine miles north of Hotchkiss on Oak Mesa. | distance_and_direction |  |  |  | invalid_extraction |
| A26 | S slope of Mt. Zenobia. | named_feature |  |  |  | invalid_extraction |
| A27 | Gunnison Canon. | named_feature |  |  |  | invalid_extraction |
| A28 | 2 mi. W of Hesperus. | distance_and_direction | Hesperus | candidates_found | Hesperus (Populated Place, La Plata, exact_official) | needs_information |
| A29 | Wet Mountain Range. Roadside along State Hwy. 96, approx. 5 miles SW of Wetmore. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| A30 | Pitkin. | named_feature |  |  |  | invalid_extraction |
| A31 | Eastern San Miguel Mts. Seep 0.2 mi. southeast from Graysill Mine. By FR 578. | named_feature | Eastern San Miguel Mts. | feature_absent_from_index |  | needs_information |
| A32 | Baca National Wildlife Refuge, San Luis Valley. Ca. 2 air miles WSW of Crestone. Ca. ½ mile S of County Rd. T; ¼ mile E of Ranch HQ. Near jct. of N. Crestone and S. Crestone creeks. | route_relative |  |  |  | invalid_extraction |
| A33 | Gravelly bench along highway below Fremont Pass. | named_feature | Gravelly bench | feature_absent_from_index |  | needs_information |
| A34 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Sangre de Cristo Range: San Isabel National Forest: ca 3.4 road mi on Forest 101 from U.S. Hwy 50. | route_relative |  |  |  | invalid_extraction |
| A35 | Gore Range, Eagles Nest Wilderness Area, central Colorado. 1km west of Lower Piney Lake. | named_feature | Gore Range | candidates_found | Gore Range (Range, Summit, exact_official) | needs_information |
| A36 | Chico Basin Ranch, ca. 28 miles SE of Colorado Springs. Dry uplands above Black Squirrel Creek. | named_feature | Chico Basin Ranch | feature_absent_from_index |  | needs_information |
| A37 | Rocky Mountain National Park. Neversummer Range. About halfway up south slope of Thunder Mt., 16 miles N of Grand Lake. | distance_and_direction |  |  |  | invalid_extraction |
| A38 | Rocky Mountain National Park, along Old Fall River Rd., ca. 6 mi. from Fall River entrance to Park. | route_relative | Rocky Mountain National Park | feature_absent_from_index |  | unsupported |
| A39 | Dry Creek drainage. | named_feature | Dry Creek drainage | feature_absent_from_index |  | needs_information |
| A40 | Mosquito Range, San Isabel National Forest, Weston Pass Rd (FS Rd 7), E from Rte 24, about 1 mi. past USFS boundary, along Big Union Creek. | route_relative | Mosquito Range | candidates_found | Mosquito Range (Range, Lake, exact_official) | unsupported |
| A41 | 1.9 miles up Pool Table Road approx. 1/8 mile west of road. | route_relative |  |  |  | invalid_extraction |
| A42 | Dinosaur National Monument. Douglas Mtn Boulevard, ca. 3 mi. WSW of Five Springs. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| A43 | Great Sand Dunes Natl. Mon. Morris Gulch just below horse trap. | named_feature | Great Sand Dunes Natl. Mon. | feature_absent_from_index |  | needs_information |
| A44 | West of Hesperus. West slope of La Plata Mts. | direction_only | Hesperus | candidates_found | Hesperus (Populated Place, La Plata, exact_official) | needs_information |
| A45 | Lone Mesa State Park, 3.5 miles west of entrance at FR 526; west-facing slope. | named_feature | Lone Mesa State Park | feature_absent_from_index |  | needs_information |
| A46 | Co Rd PP ca 3.2 mi W jct Co Rd 5. Immediately E of dry tributary of Two Buttes Creek. | distance_and_direction |  |  |  | invalid_extraction |
| A47 | Medano Ranch, east part of valley. | named_feature | Medano Ranch | feature_absent_from_index |  | needs_information |
| A48 | Chokecherry Draw, NW part of Moffat County. | named_feature | Chokecherry Draw | candidates_found | Chokecherry Draw (Valley, Moffat, exact_official) | needs_information |
| A49 | 1.5 mi N of CO24 off tranquil Acres Rd along Rule Cr. | distance_and_direction |  |  |  | invalid_extraction |
| A50 | "Hattie Sammon's Pasture", Powderhorn. | named_feature | "Hattie Sammon's Pasture" | feature_absent_from_index |  | needs_information |
