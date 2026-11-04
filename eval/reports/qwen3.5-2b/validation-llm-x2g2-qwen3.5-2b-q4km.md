# validation: LLM extraction (`llm-x2g2-qwen3.5-2b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 33 · `distance_and_direction` 20 · `route_relative` 5 · `no_locality` 1 · `direction_only` 1

**retrieval**: `feature_absent_from_index` 23 · `None` 20 · `candidates_found` 16 · `no_reference_feature` 1

**proposal**: `needs_information` 36 · `invalid_extraction` 20 · `unsupported` 4

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| V001 | 13T 0520450/ 449820; T12N R64W SEC20 E. central part | no_locality |  | no_reference_feature |  | unsupported |
| V002 | Genessee Mountain. | named_feature | Genessee Mountain | candidates_found | Genesee Mountain (Summit, Jefferson, fuzzy_official) | needs_information |
| V003 | 19th and Alpine Street. | named_feature | 19th and Alpine Street | feature_absent_from_index |  | needs_information |
| V004 | Half mile E of Hiway Nine, 3 mi. S of LaFayette. | distance_and_direction |  |  |  | invalid_extraction |
| V005 | 3 miles east of Roggen on the Painter Hereford Ranch. | distance_and_direction |  |  |  | invalid_extraction |
| V006 | Vernal Mesa, 15 mi. east of Montrose. | distance_and_direction | Montrose | candidates_found | Montrose (Populated Place, Montrose, exact_official) | needs_information |
| V007 | Fishers Peak State Park, Raton Mesa and vicinity; east side of I-25 approx. 6 miles south of the town of Trinidad and just north of New Mexico; steep southwest facing slope of Fishers Peak Mesa. | named_feature | Fishers Peak State Park | feature_absent_from_index |  | needs_information |
| V008 | Lutz Reservoir, NW of Barr Lake. | named_feature | Lutz Reservoir | candidates_found | Lutz Reservoir (historical) (Reservoir, Adams, exact_official) | needs_information |
| V009 | Wet Mountains; Grape Creek drainage, Bear Gulch tributary; ~1.5 miles NW of Yorkville, ~1.5 mile SW of Curley Peak | distance_and_direction |  |  |  | invalid_extraction |
| V010 | Wallace Gulch Road going N from Rainbow gas sta., Bayfield & following Pine River short way; in irrigation field 1 mile from station. | route_relative |  |  |  | invalid_extraction |
| V011 | West Rim of Uncompahgre Plateau, near road between Columbine Pass and Uncompahgre Butte, along road to Love Mesa. | named_feature | Uncompahgre Plateau | candidates_found | Uncompahgre Plateau (Plain, Montrose, exact_official) | needs_information |
| V012 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Wet Mountains, drainage N of North Peak. | named_feature | Wet Mountains | candidates_found | Wet Mountains (Range, Custer, exact_official) | needs_information |
| V013 | S. slope Mt. Shavano, 10 mi. n. w. Salida. | distance_and_direction |  |  |  | invalid_extraction |
| V014 | Northeast-facing slope of Douglas Mt., 3/5 mi. SW of Greystone. | distance_and_direction | Douglas Mt. | candidates_found | Douglas Mountain (Summit, Jefferson, core_official) | needs_information |
| V015 | Moun tains about the head waters of Clear Creek. In the valley near Empire. | named_feature |  |  |  | invalid_extraction |
| V016 | Gravelly slope of Table Mesa, 3 mi. s. of Lyons. | distance_and_direction |  |  |  | invalid_extraction |
| V017 | Sandstone hill ¼ mile west of Gem Village on north side US 160. | distance_and_direction |  |  |  | invalid_extraction |
| V018 | BLM. Samjbrito Wetalnds.State Hwy 140 to County Road 136. On 136 ca. 4 mi. to County Road 134 | route_relative | County Road 136 | feature_absent_from_index |  | unsupported |
| V019 | Along U.S. 36 near Idalia. | named_feature | U.S. 36 | feature_absent_from_index |  | needs_information |
| V020 | Lone Mesa State Park, 7.5 miles north of southern entrance at FR 514. | named_feature | Lone Mesa State Park | feature_absent_from_index |  | needs_information |
| V021 | Hoosier Pass. | named_feature | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | needs_information |
| V022 | Edge of pond on the north side of the Arkansas River. | named_feature | Edge of pond | feature_absent_from_index |  | needs_information |
| V023 | Boulder Mt. Parks, NBS Mesa. Along the Enchanted Mesa cutoff trails just S of the gully. | named_feature | Boulder Mt. Parks | feature_absent_from_index |  | needs_information |
| V024 | Roosevelt National Forest: Medicine Bow Mountains: Rawah Wilderness: Link Trail from Link/McIntyre Trailhead on Old Glendevey Road (County Road 80C), ca 46 air mi NW of Fort Collins. | route_relative |  |  |  | invalid_extraction |
| V025 | Ca. 0.25 mi N of Weston Pass summit. | distance_and_direction |  |  |  | invalid_extraction |
| V026 | Castleton Ranch, along Carbon Creek, just east of County Road 730, near jct. with CR 737. | named_feature | Castleton Ranch | feature_absent_from_index |  | needs_information |
| V027 | Dinosaur National Monument. E. Fork Sand Canyon, W of the Billiard Table. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| V028 | Bull Domingo Hills at east edge of Wet Mountain Valley about 1 mile north of Westcliffe. | distance_and_direction |  |  |  | invalid_extraction |
| V029 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment. Rock Creek. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| V030 | Along the trail up Sawtooth Peak (Buchanan Pass). Just E of the summit of the pass. | direction_only | Sawtooth Peak | candidates_found | Sawtooth Peak (Summit, Pueblo, exact_official) | needs_information |
| V031 | San Juan National Forest: Tenmile Basin. Animas River drainage ca. 18 mi. S.E. of Silverton. Meadow NE and above Balsam Lake. | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| V032 | Summit of Rountop Mountain, Fire Lookout. Dinosaur National Monument. East-facing slope between lookout and brink of Hell Canyon. | named_feature | Rountop Mountain | candidates_found | Round Top Mountain (Summit, Moffat, fuzzy_official) | needs_information |
| V033 | National Park Service. Yucca House National Monument, near spring. | named_feature | Yucca House National Monument | feature_absent_from_index |  | needs_information |
| V034 | Slope along Sand Creek Canyon 25 mi. south of Pritchett. | distance_and_direction | Sand Creek Canyon | candidates_found | Sage Creek Canyon (Valley, Routt, fuzzy_official) | needs_information |
| V035 | Junction of Hagues Creek and Paudre [sic] River. | named_feature | Junction of Hagues Creek and Paudre [sic] River | feature_absent_from_index |  | needs_information |
| V036 | Hwy I-70 at Beavertail Bridge along Colorado River east of Grand Junction. | named_feature | Hwy I-70 | feature_absent_from_index |  | needs_information |
| V037 | Boulder, 28th Street north of Arapahoe St., along irrigation ditch. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| V038 | Skyland Ranch, 6 1/2 miles n. east of Estes Park. | distance_and_direction |  |  |  | invalid_extraction |
| V039 | Cultivated. S.E. Corner of Uinta and Hancock. | named_feature | S.E. Corner of Uinta and Hancock | feature_absent_from_index |  | needs_information |
| V040 | Along County Road 27, ~2 mi. N of US 34. | route_relative | County Road 27 | feature_absent_from_index |  | unsupported |
| V041 | Yucca House National Monument, west Ishmay property, ¼ mile south of gravel pit. | named_feature | Yucca House National Monument | feature_absent_from_index |  | needs_information |
| V042 | Ranch at the Roaring Fork. On the floodplain of the Roaring Fork River. | named_feature |  |  |  | invalid_extraction |
| V043 | 4 miles northwest of Canyon City. | distance_and_direction |  |  |  | invalid_extraction |
| V044 | Found 5 mi. up Jacob's Ladder Road. | route_relative | Jacob's Ladder Road | feature_absent_from_index |  | unsupported |
| V045 | Cirque of the Peck Glacier and base of the west slopes of Lone Eagle Peak. | named_feature | Cirque of the Peck Glacier | feature_absent_from_index |  | needs_information |
| V046 | Approx. 12 miles northwest of Idalia, along the Arikaree River. | distance_and_direction |  |  |  | invalid_extraction |
| V047 | Eldorado Canyon State Park, Upper Big Bluestem Trail. | named_feature | Eldorado Canyon State Park | feature_absent_from_index |  | needs_information |
| V048 | Along Conejos River, Near Antonito. | named_feature | Conejos River | candidates_found | Conejos River (Stream, Conejos, exact_official) | needs_information |
| V049 | Along Maroon Creek near Aspen. | named_feature | Maroon Creek | candidates_found | Maroon Creek (Stream, Pitkin, exact_official) | needs_information |
| V050 | 5.5 mi. s.e. of Gothic. | distance_and_direction |  |  |  | invalid_extraction |
| V051 | Fraser Experimental Forest, near Fool Creek gaging station. | named_feature | Fraser Experimental Forest | feature_absent_from_index |  | needs_information |
| V052 | Intersect of dirt roads along Alimosita Creek. | named_feature | Alimosita Creek | candidates_found | Alamosito Creek (Stream, Costilla, fuzzy_official) | needs_information |
| V053 | One mile below summit Pennock Pass. | distance_and_direction |  |  |  | invalid_extraction |
| V054 | 13 mi SW of Westcliffe on Hermit road. | distance_and_direction |  |  |  | invalid_extraction |
| V055 | Roosevelt National Forest: Front Range: West Whilte Pine Mountain on Forest Road 100 off Pennock Pass Road (County Road 44H), ca 18 air mi W of Fort Collins. | distance_and_direction |  |  |  | invalid_extraction |
| V056 | Allenspark. | named_feature | Allenspark | candidates_found | Allenspark (Populated Place, Boulder, exact_official) | needs_information |
| V057 | Sand hills 12 mi N of Wray of East-trending side road that ends just W of Laird. | distance_and_direction |  |  |  | invalid_extraction |
| V058 | Rollins Pass, 0.3 mi. N. of Needle Eye Tunnel. | distance_and_direction | Needle Eye Tunnel | feature_absent_from_index |  | needs_information |
| V059 | Boulder Mountain Parks. West side of Bear Pk. & S. Boulder Pk, in rich ravine below the W. ridge of Bear Pk. | named_feature | Boulder Mountain Parks | feature_absent_from_index |  | needs_information |
| V060 | Bluebell Canyon, south edge of Boulder. | named_feature | Bluebell Canyon | candidates_found | Bluebell Canyon (Valley, Boulder, exact_official) | needs_information |
