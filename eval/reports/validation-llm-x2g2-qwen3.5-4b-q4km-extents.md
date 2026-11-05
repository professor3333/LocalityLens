# validation: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `named_feature` 24 · `distance_and_direction` 20 · `route_relative` 6 · `other` 3 · `orthogonal_offsets` 2 · `itinerary` 2 · `between_features` 2 · `no_locality` 1

**retrieval**: `candidates_found` 35 · `feature_absent_from_index` 19 · `no_reference_feature` 4 · `None` 2

**proposal**: `needs_information` 30 · `unsupported` 15 · `computed` 13 · `invalid_extraction` 2

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| V001 | 13T 0520450/ 449820; T12N R64W SEC20 E. central part | no_locality |  | no_reference_feature |  | unsupported |
| V002 | Genessee Mountain. | named_feature | Genessee Mountain | candidates_found | Genesee Mountain (Summit, Jefferson, fuzzy_official) | computed |
| V003 | 19th and Alpine Street. | other |  | no_reference_feature |  | unsupported |
| V004 | Half mile E of Hiway Nine, 3 mi. S of LaFayette. | orthogonal_offsets |  |  |  | invalid_extraction |
| V005 | 3 miles east of Roggen on the Painter Hereford Ranch. | distance_and_direction | Roggen | candidates_found | Roggen (Populated Place, Weld, exact_official) | needs_information |
| V006 | Vernal Mesa, 15 mi. east of Montrose. | distance_and_direction | Montrose | candidates_found | Montrose (Populated Place, Montrose, exact_official) | computed |
| V007 | Fishers Peak State Park, Raton Mesa and vicinity; east side of I-25 approx. 6 miles south of the town of Trinidad and just north of New Mexico; steep southwest facing slope of Fishers Peak Mesa. | named_feature | Fishers Peak State Park | feature_absent_from_index |  | needs_information |
| V008 | Lutz Reservoir, NW of Barr Lake. | distance_and_direction |  |  |  | invalid_extraction |
| V009 | Wet Mountains; Grape Creek drainage, Bear Gulch tributary; ~1.5 miles NW of Yorkville, ~1.5 mile SW of Curley Peak | distance_and_direction | Yorkville | candidates_found | Yorkville (Populated Place, Fremont, exact_official) | needs_information |
| V010 | Wallace Gulch Road going N from Rainbow gas sta., Bayfield & following Pine River short way; in irrigation field 1 mile from station. | itinerary | Rainbow gas sta. | feature_absent_from_index |  | unsupported |
| V011 | West Rim of Uncompahgre Plateau, near road between Columbine Pass and Uncompahgre Butte, along road to Love Mesa. | route_relative | Uncompahgre Plateau | candidates_found | Uncompahgre Plateau (Plain, Montrose, exact_official) | unsupported |
| V012 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Wet Mountains, drainage N of North Peak. | named_feature | North Peak | candidates_found | North Peak (Summit, Pueblo, exact_official) | needs_information |
| V013 | S. slope Mt. Shavano, 10 mi. n. w. Salida. | named_feature | Mt. Shavano | candidates_found | Mount Shavano (Summit, Chaffee, exact_official) | computed |
| V014 | Northeast-facing slope of Douglas Mt., 3/5 mi. SW of Greystone. | distance_and_direction | Greystone | candidates_found | Greystone (Populated Place, Moffat, exact_official) | needs_information |
| V015 | Moun tains about the head waters of Clear Creek. In the valley near Empire. | named_feature | Clear Creek | candidates_found | Clear Creek (Stream, Jackson, exact_official) | needs_information |
| V016 | Gravelly slope of Table Mesa, 3 mi. s. of Lyons. | distance_and_direction | Lyons | candidates_found | Lyons (Populated Place, Boulder, exact_official) | needs_information |
| V017 | Sandstone hill ¼ mile west of Gem Village on north side US 160. | distance_and_direction | Gem Village | candidates_found | Gem Village (Populated Place, La Plata, exact_official) | needs_information |
| V018 | BLM. Samjbrito Wetalnds.State Hwy 140 to County Road 136. On 136 ca. 4 mi. to County Road 134 | itinerary | County Road 134 | feature_absent_from_index |  | unsupported |
| V019 | Along U.S. 36 near Idalia. | named_feature | Idalia | candidates_found | Idalia (Populated Place, Yuma, exact_official) | needs_information |
| V020 | Lone Mesa State Park, 7.5 miles north of southern entrance at FR 514. | route_relative | southern entrance at FR 514 | feature_absent_from_index |  | unsupported |
| V021 | Hoosier Pass. | named_feature | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | computed |
| V022 | Edge of pond on the north side of the Arkansas River. | named_feature | Arkansas River | candidates_found | Arkansas River (Stream, Desha, exact_official) | computed |
| V023 | Boulder Mt. Parks, NBS Mesa. Along the Enchanted Mesa cutoff trails just S of the gully. | other |  | no_reference_feature |  | unsupported |
| V024 | Roosevelt National Forest: Medicine Bow Mountains: Rawah Wilderness: Link Trail from Link/McIntyre Trailhead on Old Glendevey Road (County Road 80C), ca 46 air mi NW of Fort Collins. | distance_and_direction | Fort Collins | candidates_found | Fort Collins (Populated Place, Larimer, exact_official) | needs_information |
| V025 | Ca. 0.25 mi N of Weston Pass summit. | distance_and_direction | Weston Pass summit | candidates_found | Weston Pass (Gap, Lake, core_official) | computed |
| V026 | Castleton Ranch, along Carbon Creek, just east of County Road 730, near jct. with CR 737. | named_feature | Castleton Ranch | feature_absent_from_index |  | needs_information |
| V027 | Dinosaur National Monument. E. Fork Sand Canyon, W of the Billiard Table. | named_feature | E. Fork Sand Canyon | feature_absent_from_index |  | needs_information |
| V028 | Bull Domingo Hills at east edge of Wet Mountain Valley about 1 mile north of Westcliffe. | distance_and_direction | Westcliffe | candidates_found | Westcliffe (Populated Place, Custer, exact_official) | computed |
| V029 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment. Rock Creek. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| V030 | Along the trail up Sawtooth Peak (Buchanan Pass). Just E of the summit of the pass. | named_feature | Sawtooth Peak | candidates_found | Sawtooth Peak (Summit, Pueblo, exact_official) | needs_information |
| V031 | San Juan National Forest: Tenmile Basin. Animas River drainage ca. 18 mi. S.E. of Silverton. Meadow NE and above Balsam Lake. | named_feature | Tenmile Basin | feature_absent_from_index |  | needs_information |
| V032 | Summit of Rountop Mountain, Fire Lookout. Dinosaur National Monument. East-facing slope between lookout and brink of Hell Canyon. | named_feature | Rountop Mountain | candidates_found | Round Top Mountain (Summit, Moffat, fuzzy_official) | needs_information |
| V033 | National Park Service. Yucca House National Monument, near spring. | other |  | no_reference_feature |  | unsupported |
| V034 | Slope along Sand Creek Canyon 25 mi. south of Pritchett. | distance_and_direction | Pritchett | candidates_found | Pritchett (Populated Place, Baca, exact_official) | needs_information |
| V035 | Junction of Hagues Creek and Paudre [sic] River. | between_features | Hagues Creek and Paudre [sic] River | feature_absent_from_index |  | unsupported |
| V036 | Hwy I-70 at Beavertail Bridge along Colorado River east of Grand Junction. | route_relative | Grand Junction | candidates_found | Grand Junction (Populated Place, Mesa, exact_official) | unsupported |
| V037 | Boulder, 28th Street north of Arapahoe St., along irrigation ditch. | route_relative | Arapahoe St. | feature_absent_from_index |  | unsupported |
| V038 | Skyland Ranch, 6 1/2 miles n. east of Estes Park. | distance_and_direction | Estes Park | candidates_found | Estes Park (Flat, Larimer, exact_official) | needs_information |
| V039 | Cultivated. S.E. Corner of Uinta and Hancock. | between_features | Uinta and Hancock | feature_absent_from_index |  | unsupported |
| V040 | Along County Road 27, ~2 mi. N of US 34. | route_relative | US 34 | feature_absent_from_index |  | unsupported |
| V041 | Yucca House National Monument, west Ishmay property, ¼ mile south of gravel pit. | orthogonal_offsets | gravel pit | feature_absent_from_index |  | unsupported |
| V042 | Ranch at the Roaring Fork. On the floodplain of the Roaring Fork River. | named_feature | Roaring Fork | candidates_found | Roaring Fork River (Stream, Garfield, exact_variant) | computed |
| V043 | 4 miles northwest of Canyon City. | distance_and_direction | Canyon City | candidates_found | Cañon City (Populated Place, Fremont, exact_variant) | computed |
| V044 | Found 5 mi. up Jacob's Ladder Road. | route_relative | Jacob's Ladder Road | feature_absent_from_index |  | unsupported |
| V045 | Cirque of the Peck Glacier and base of the west slopes of Lone Eagle Peak. | named_feature | Peck Glacier | candidates_found | Peck Glacier (Glacier, Grand, exact_official) | needs_information |
| V046 | Approx. 12 miles northwest of Idalia, along the Arikaree River. | distance_and_direction | Idalia | candidates_found | Idalia (Populated Place, Yuma, exact_official) | computed |
| V047 | Eldorado Canyon State Park, Upper Big Bluestem Trail. | named_feature | Eldorado Canyon State Park | feature_absent_from_index |  | needs_information |
| V048 | Along Conejos River, Near Antonito. | named_feature | Conejos River | candidates_found | Conejos River (Stream, Conejos, exact_official) | needs_information |
| V049 | Along Maroon Creek near Aspen. | named_feature | Maroon Creek | candidates_found | Maroon Creek (Stream, Pitkin, exact_official) | needs_information |
| V050 | 5.5 mi. s.e. of Gothic. | distance_and_direction | Gothic | candidates_found | Gothic (Populated Place, Gunnison, exact_official) | needs_information |
| V051 | Fraser Experimental Forest, near Fool Creek gaging station. | named_feature | Fool Creek gaging station | feature_absent_from_index |  | needs_information |
| V052 | Intersect of dirt roads along Alimosita Creek. | named_feature | Alimosita Creek | candidates_found | Alamosito Creek (Stream, Costilla, fuzzy_official) | needs_information |
| V053 | One mile below summit Pennock Pass. | distance_and_direction | Pennock Pass | feature_absent_from_index |  | needs_information |
| V054 | 13 mi SW of Westcliffe on Hermit road. | distance_and_direction | Westcliffe | candidates_found | Westcliffe (Populated Place, Custer, exact_official) | computed |
| V055 | Roosevelt National Forest: Front Range: West Whilte Pine Mountain on Forest Road 100 off Pennock Pass Road (County Road 44H), ca 18 air mi W of Fort Collins. | distance_and_direction | Fort Collins | candidates_found | Fort Collins (Populated Place, Larimer, exact_official) | needs_information |
| V056 | Allenspark. | named_feature | Allenspark | candidates_found | Allenspark (Populated Place, Boulder, exact_official) | computed |
| V057 | Sand hills 12 mi N of Wray of East-trending side road that ends just W of Laird. | distance_and_direction | Wray | candidates_found | Wray (Populated Place, Yuma, exact_official) | computed |
| V058 | Rollins Pass, 0.3 mi. N. of Needle Eye Tunnel. | distance_and_direction | Needle Eye Tunnel | feature_absent_from_index |  | needs_information |
| V059 | Boulder Mountain Parks. West side of Bear Pk. & S. Boulder Pk, in rich ravine below the W. ridge of Bear Pk. | named_feature | Boulder Mountain Parks | feature_absent_from_index |  | needs_information |
| V060 | Bluebell Canyon, south edge of Boulder. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
