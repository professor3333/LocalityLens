# 50-record audit: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `audit-50/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 23 · `distance_and_direction` 14 · `route_relative` 5 · `other` 3 · `itinerary` 2 · `orthogonal_offsets` 1 · `no_locality` 1 · `direction_only` 1

**retrieval**: `candidates_found` 26 · `feature_absent_from_index` 19 · `no_reference_feature` 4 · `None` 1

**proposal**: `needs_information` 37 · `unsupported` 12 · `invalid_extraction` 1

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| A01 | Colorado National Monument, S of E entrance. | route_relative | E entrance | feature_absent_from_index |  | unsupported |
| A02 | 5 mi. E. of Eaton towards Cornish. | distance_and_direction | Eaton | candidates_found | Eaton (Populated Place, Weld, exact_official) | needs_information |
| A03 | Northern Gunnison Basin: ca 6 air mi NE of Almont. | distance_and_direction | Almont | candidates_found | Almont (Populated Place, Gunnison, exact_official) | needs_information |
| A04 | San Juan Nat. Forest: Chicago Basin. Animas River drainage ca. 18 mi. S.E. of Silverton. Near the top of Eolus. | named_feature | Chicago Basin | candidates_found | Chicago Basin (Basin, La Plata, exact_official) | needs_information |
| A05 | Collegiate Peaks Overlook, Arkansas Headwaters State Recreation Area, approx. 1 mile east of Johnson Village on CR 34 off of Highway 285. | route_relative | Johnson Village | candidates_found | Johnson Village (Populated Place, Chaffee, exact_official) | unsupported |
| A06 | Grand Mesa National Forest. Old road on N slope of plateau E of Mesa Creek. | named_feature | Grand Mesa National Forest | feature_absent_from_index |  | needs_information |
| A07 | Head of canon on east slope of Flagstaff Mountain, Boulder. | named_feature | Flagstaff Mountain | candidates_found | Flagstaff Mountain (Summit, Boulder, exact_official) | needs_information |
| A08 | Shale 15 miles east of Pueblo. | distance_and_direction | Pueblo | candidates_found | Pueblo (Populated Place, Pueblo, exact_official) | needs_information |
| A09 | Trail from Soda Tipoff to Mancos River, south rim of Mesa Verde. | itinerary | Mancos River | candidates_found | Mancos River (Stream, San Juan, exact_official) | unsupported |
| A10 | Above Rainbow Lake. | named_feature | Rainbow Lake | candidates_found | Rainbow Lake (Lake, Jackson, exact_official) | needs_information |
| A11 | Lone Cone. | named_feature | Lone Cone | candidates_found | Lone Cone (Summit, Dolores, exact_official) | needs_information |
| A12 | Silt Mesa (right-of-way). | named_feature | Silt Mesa | feature_absent_from_index |  | needs_information |
| A13 | Northern Gunnison Basin: ca 5 air mi SSW of Paonia. | distance_and_direction | Paonia | candidates_found | Paonia (Populated Place, Delta, exact_official) | needs_information |
| A14 | White River Plateau. Coffee Pot Road, 8 mi W of Hwy 301. | named_feature | White River Plateau | candidates_found | White River Plateau (Summit, Garfield, exact_official) | needs_information |
| A15 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment. Along a 2-track road next to Woman Creek bypass north of C-2 pond. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| A16 | South Park area. | other |  | no_reference_feature |  | unsupported |
| A17 | Mesa de Maya Region of southeastern CO. Gotera Canyon. | other |  | no_reference_feature |  | unsupported |
| A18 | Rico Mts.; northern ridge of Sockrider Mt. | named_feature | Rico Mts. | feature_absent_from_index |  | needs_information |
| A19 | Roosevelt National Forest: Front Range: E of Green Ridge Trail or Forest Road 177, just N of Laramie Lake, ca 37 air mi W of Fort Collins. | orthogonal_offsets | Fort Collins | candidates_found | Fort Collins (Populated Place, Larimer, exact_official) | unsupported |
| A20 | Morrison Creek. Buffalo Creek Recreation Area, along Morrison Creek and former National Forest Road 547, 2.69 km. south of National Forest Road 550, 63.3 km. south of the GNIS location of Golden. | named_feature | Morrison Creek | candidates_found | Morrison Creek (Stream, Jefferson, exact_official) | needs_information |
| A21 | Near Deer Creek, Chatfield Arboretum site, Denver Botanic Gardens, located at junction of Highway 75 and Deer Creek Rd. | named_feature | Deer Creek | candidates_found | Deer Creek (Stream, Jefferson, exact_official) | needs_information |
| A22 | Lost Man Campground, upper Roaring Fork Valley east of Aspen. | named_feature | Lost Man Campground | feature_absent_from_index |  | needs_information |
| A23 | North-central Colorado: Elkhead Mountains: rim of Black Mountain, ca 20-21 air mi NE of Craig. | distance_and_direction |  |  |  | invalid_extraction |
| A24 | Tolland. James Peak. | named_feature | James Peak | candidates_found | James Peak (Summit, Gilpin, exact_official) | needs_information |
| A25 | Nine miles north of Hotchkiss on Oak Mesa. | distance_and_direction | Hotchkiss | candidates_found | Hotchkiss (Populated Place, Delta, exact_official) | needs_information |
| A26 | S slope of Mt. Zenobia. | named_feature | Mt. Zenobia | candidates_found | Zenobia Peak (Summit, Moffat, core_official) | needs_information |
| A27 | Gunnison Canon. | named_feature | Gunnison Canon | feature_absent_from_index |  | needs_information |
| A28 | 2 mi. W of Hesperus. | distance_and_direction | Hesperus | candidates_found | Hesperus (Populated Place, La Plata, exact_official) | needs_information |
| A29 | Wet Mountain Range. Roadside along State Hwy. 96, approx. 5 miles SW of Wetmore. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| A30 | Pitkin. | no_locality |  | no_reference_feature |  | unsupported |
| A31 | Eastern San Miguel Mts. Seep 0.2 mi. southeast from Graysill Mine. By FR 578. | distance_and_direction | Graysill Mine | feature_absent_from_index |  | needs_information |
| A32 | Baca National Wildlife Refuge, San Luis Valley. Ca. 2 air miles WSW of Crestone. Ca. ½ mile S of County Rd. T; ¼ mile E of Ranch HQ. Near jct. of N. Crestone and S. Crestone creeks. | distance_and_direction | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| A33 | Gravelly bench along highway below Fremont Pass. | named_feature | Fremont Pass | candidates_found | Fremont Pass (Gap, Lake, exact_official) | needs_information |
| A34 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Sangre de Cristo Range: San Isabel National Forest: ca 3.4 road mi on Forest 101 from U.S. Hwy 50. | route_relative | U.S. Hwy 50 | feature_absent_from_index |  | unsupported |
| A35 | Gore Range, Eagles Nest Wilderness Area, central Colorado. 1km west of Lower Piney Lake. | distance_and_direction | Lower Piney Lake | candidates_found | Piney Lake (Lake, Eagle, core_official) | needs_information |
| A36 | Chico Basin Ranch, ca. 28 miles SE of Colorado Springs. Dry uplands above Black Squirrel Creek. | named_feature | Chico Basin Ranch | feature_absent_from_index |  | needs_information |
| A37 | Rocky Mountain National Park. Neversummer Range. About halfway up south slope of Thunder Mt., 16 miles N of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | needs_information |
| A38 | Rocky Mountain National Park, along Old Fall River Rd., ca. 6 mi. from Fall River entrance to Park. | route_relative | Fall River entrance to Park | feature_absent_from_index |  | unsupported |
| A39 | Dry Creek drainage. | other |  | no_reference_feature |  | unsupported |
| A40 | Mosquito Range, San Isabel National Forest, Weston Pass Rd (FS Rd 7), E from Rte 24, about 1 mi. past USFS boundary, along Big Union Creek. | itinerary | USFS boundary | feature_absent_from_index |  | unsupported |
| A41 | 1.9 miles up Pool Table Road approx. 1/8 mile west of road. | route_relative | Pool Table Road | feature_absent_from_index |  | unsupported |
| A42 | Dinosaur National Monument. Douglas Mtn Boulevard, ca. 3 mi. WSW of Five Springs. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| A43 | Great Sand Dunes Natl. Mon. Morris Gulch just below horse trap. | named_feature | Morris Gulch | candidates_found | Morris Gulch (Valley, Alamosa, exact_official) | needs_information |
| A44 | West of Hesperus. West slope of La Plata Mts. | direction_only | Hesperus | candidates_found | Hesperus (Populated Place, La Plata, exact_official) | needs_information |
| A45 | Lone Mesa State Park, 3.5 miles west of entrance at FR 526; west-facing slope. | named_feature | Lone Mesa State Park | feature_absent_from_index |  | needs_information |
| A46 | Co Rd PP ca 3.2 mi W jct Co Rd 5. Immediately E of dry tributary of Two Buttes Creek. | distance_and_direction | dry tributary of Two Buttes Creek | feature_absent_from_index |  | needs_information |
| A47 | Medano Ranch, east part of valley. | named_feature | Medano Ranch | feature_absent_from_index |  | needs_information |
| A48 | Chokecherry Draw, NW part of Moffat County. | named_feature | Chokecherry Draw | candidates_found | Chokecherry Draw (Valley, Moffat, exact_official) | needs_information |
| A49 | 1.5 mi N of CO24 off tranquil Acres Rd along Rule Cr. | distance_and_direction | CO24 | feature_absent_from_index |  | needs_information |
| A50 | "Hattie Sammon's Pasture", Powderhorn. | named_feature | "Hattie Sammon's Pasture" | feature_absent_from_index |  | needs_information |
