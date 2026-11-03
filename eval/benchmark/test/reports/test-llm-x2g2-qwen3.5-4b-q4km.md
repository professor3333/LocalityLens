# test: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 52 · `distance_and_direction` 25 · `route_relative` 13 · `between_features` 10 · `orthogonal_offsets` 8 · `other` 5 · `itinerary` 3 · `direction_only` 2 · `no_locality` 2

**retrieval**: `candidates_found` 61 · `feature_absent_from_index` 37 · `None` 15 · `no_reference_feature` 7

**proposal**: `needs_information` 72 · `unsupported` 33 · `invalid_extraction` 15

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| T001 | Sapinero, also Cimarron. | named_feature | Sapinero, also Cimarron | feature_absent_from_index |  | needs_information |
| T002 | Coal Canyon. | named_feature | Coal Canyon | candidates_found | Coal Canyon (Valley, Mesa, exact_official) | needs_information |
| T003 | Near Austin. | named_feature | Austin | candidates_found | Austin (Populated Place, Delta, exact_official) | needs_information |
| T004 | Mt. Evans Highway at timberline. | named_feature | Mt. Evans Highway | feature_absent_from_index |  | needs_information |
| T005 | Private ranch, off private road -- continuation of County Road 5E. | route_relative | County Road 5E | feature_absent_from_index |  | unsupported |
| T006 | Northeast of Limon along CR 36. | route_relative | Limon | candidates_found | Limon (Populated Place, Lincoln, exact_official) | unsupported |
| T007 | White River National Forest, along Two Elk Creek, approx. 2/5 mile upstream of confluence with Eagle River. | route_relative | confluence with Eagle River | feature_absent_from_index |  | unsupported |
| T008 | North-central Colorado: Never Summer Mountains: Never Summer Wilderness: Baker Pass NW to peak "11740". | between_features |  |  |  | invalid_extraction |
| T009 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. San Isabel National Forest, up Stultz Gulch from Stultz Trailhead on County Road 143, ca 8 air mi S of Canon City. | distance_and_direction | Canon City | candidates_found | Cañon City (Populated Place, Fremont, exact_official) | needs_information |
| T010 | Wolf Creek Pass - 10 mi w. on Continental Divide Trail. | route_relative | Wolf Creek Pass | candidates_found | Wolf Creek Pass (Gap, Mineral, exact_official) | unsupported |
| T011 | South San Juans, E. side of Lake Anne. | named_feature | Lake Anne | candidates_found | Lake Ann (Lake, Archuleta, fuzzy_official) | needs_information |
| T012 | Below Santa Fe Peak. | named_feature | Santa Fe Peak | candidates_found | Santa Fe Peak (Summit, Summit, exact_official) | needs_information |
| T013 | Wetland E side of C470. | named_feature | C470 | feature_absent_from_index |  | needs_information |
| T014 | Mouth of Sunshine Canyon near picnic shelter, NW edge of Boulder. | named_feature | Sunshine Canyon | candidates_found | Sunshine Canyon (Valley, Boulder, exact_official) | needs_information |
| T015 | South of Silverton, near road to Kendall Gulch. | direction_only | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| T016 | 17.9 mi. S on Grand Cty. Rd. 3 (aka. USFS Rd. 138) fr. junction with US Hwy. 40 to rd. fork, cont. left SSE on Rd. 138 (aka. Grand Cty. Rd. 30) to USFS Rd. 141 (Kinney Cr. Rd.), 2.5 mi. ENE on Rd. 141 to rivulet drainage, S-side of rd., few hundred m up. | itinerary | rivulet drainage | feature_absent_from_index |  | unsupported |
| T017 | Owl Canyon, north of La Porte. | named_feature | Owl Canyon | candidates_found | Owl Canyon (Valley, Larimer, exact_official) | needs_information |
| T018 | North 1 mile on flat from junction of Mine road and Redfern road. Douglas Mountain. | orthogonal_offsets | junction of Mine road and Redfern road | feature_absent_from_index |  | unsupported |
| T019 | Cuchara Valley. Blue Lake, near the 1 lake. | named_feature | Blue Lake | candidates_found | Blue Lake (Lake, Jackson, exact_official) | needs_information |
| T020 | Conn Creek, 1/3 mile upstream from confluence of Cascade Creek. | route_relative | confluence of Cascade Creek | feature_absent_from_index |  | unsupported |
| T021 | Round Butte Ranch, ca. 20 air mi. of Fort Collins. Sand Creek. | named_feature | Sand Creek | candidates_found | Sand Creek (Stream, Larimer, exact_official) | needs_information |
| T022 | Two miles west of Burlington on north side of Highway 24. | distance_and_direction |  |  |  | invalid_extraction |
| T023 | East of Cheyenne, Wyoming. | direction_only | Cheyenne | candidates_found | Cheyenne Mountain (Summit, El Paso, core_official) | needs_information |
| T024 | Windy Saddle Park. Southeast corner of Windy Saddle Park, about 375 m northeast of, and downslope from the Buffalo Bill Museu and 3.36 Km soutwest of the GNIS location of Golden. | named_feature | Windy Saddle Park | feature_absent_from_index |  | needs_information |
| T025 | Private land; slopes NW of Yucca House National Monument. | named_feature | Yucca House National Monument | feature_absent_from_index |  | needs_information |
| T026 | 12.4 road miles along CO Hwy 134 E of its junction with CO Hwy 131 in Toponas. | route_relative | CO Hwy 131 | feature_absent_from_index |  | unsupported |
| T027 | Longs Peak. East face. | named_feature | Longs Peak | candidates_found | Longs Peak (Summit, Boulder, exact_official) | needs_information |
| T028 | Central Colorado: Sawatch Range, East Slope Continental Divide: off County Road 321, ca 3.5 air mi W of Nathrop. | distance_and_direction | Nathrop | candidates_found | Nathrop (historical) (Populated Place, Chaffee, exact_official) | needs_information |
| T029 | 2 mi. south of Crested Butte, turn left onto Co. Rd. 738 from Rt. 135. Second rd. on right after crossing the East River, across from farm house. | itinerary | Crested Butte | candidates_found | Crested Butte (Summit, Gunnison, exact_official) | unsupported |
| T030 | Pike National Forest, Lost Creek drainage between Tarryall and Kenosha Mts., along forest trail 609, 1.0 air mile SE of Lost Park Campground. | orthogonal_offsets | Lost Park Campground | feature_absent_from_index |  | unsupported |
| T031 | North Park. Coalmont. | no_locality |  | no_reference_feature |  | unsupported |
| T032 | Near junction with Navajo Canyon, Mesa Verde National Park. Canyon floor, Spruce Canyon. | between_features | Navajo Canyon | candidates_found | Navajo Canyon (Valley, Montezuma, exact_official) | unsupported |
| T033 | Colorado National Monument, Fruita entrance. | other |  | no_reference_feature |  | unsupported |
| T034 | Along Jenny creek, near Ladora. | named_feature | Jenny creek | candidates_found | Jenny Creek (Stream, Gilpin, exact_official) | needs_information |
| T035 | Loveland, NE side of town on SW side of Westerdoll Lake. Disturbed, open ground along roads and in pastures near intersection of Monroe Avenue and E 38th Street. | between_features | Westerdoll Lake | candidates_found | Westerdoll Lake (Lake, Larimer, exact_official) | unsupported |
| T036 | La Foret, Black Forest; meadow vic. Ponderosa Lodge. | named_feature | Ponderosa Lodge | feature_absent_from_index |  | needs_information |
| T037 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Culebra Range: on a small tributary of Trinchera Creek, ca 2 mi before Beccerro Basin, SE of Fort Garland. | distance_and_direction |  |  |  | invalid_extraction |
| T038 | Headwaters of Clear Creek, west of U.S. Forest Service ski lodge near Loveland Pass. | named_feature | Clear Creek | candidates_found | Clear Creek (Stream, Jackson, exact_official) | needs_information |
| T039 | La Sal Cr., 3 mi above confluence with Dolores River, SW of Bedrock. | distance_and_direction | Bedrock | candidates_found | Bedrock (Populated Place, Montrose, exact_official) | needs_information |
| T040 | Alamosa River Canyon just below Alamosa Campground. | named_feature | Alamosa River Canyon | feature_absent_from_index |  | needs_information |
| T041 | Mesa de Maya, in gap between east and west sections, on Willard Louden Ranch (20,000 acres) NW of Branson. | named_feature | Mesa de Maya | candidates_found | Mesa de Maya (Summit, Las Animas, exact_official) | needs_information |
| T042 | Boulder Mtn. Parks W of the National Bureau of Standards. In a swale between NBS Mesa and Enchanted Mesa. | between_features | NBS Mesa | feature_absent_from_index |  | unsupported |
| T043 | Near Platte River. | route_relative | Platte River | candidates_found | Slate River (Stream, Gunnison, fuzzy_official) | unsupported |
| T044 | Baca National Wildlife Refuge, San Luis Valley. Ca. 4 air miles WSW of Crestone. Ca. ¼ mile S of County Road T, just E of two-track to Cattle HQ. ON N. Crestone Ditch. | orthogonal_offsets |  |  |  | invalid_extraction |
| T045 | Dinosaur National Monument; at Canyon Overlook Picnic Ground between Harper's Corner and Echo Park road. | between_features | Harper's Corner | candidates_found | Harpers Corner (Cape, Moffat, exact_official) | unsupported |
| T046 | Rocky Mountain National Park, Front Range, Horseshoe Park alluvial fan at mouth of Roaring R. on deep gravel floodplain deposited by Lawn L. flood in July 1982. E of Roaring R., S of Fall R. rd, N of Fall R. | orthogonal_offsets | Roaring R. | candidates_found | Roaring Fork (Stream, Larimer, fuzzy_official) | unsupported |
| T047 | Curecanti National Recreation Area. Cimarron. Mesa Creek trail just below Morrow Point Dam. GPS waypoint: AC9. | named_feature | Mesa Creek trail | feature_absent_from_index |  | needs_information |
| T048 | Rocky Mountain National Park; valley near junct. of E. & W. forks of Hague Creek; in Hague Creek subalpine fens. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| T049 | Alpine saddle between summit of Mount Evans and Mount Epaulet. | between_features |  |  |  | invalid_extraction |
| T050 | Near Lower Cataract Lake. | named_feature | Lower Cataract Lake | candidates_found | Lower Cataract Lake (Lake, Summit, exact_official) | needs_information |
| T051 | Ranch near Cortez. | named_feature | Cortez | candidates_found | Cortez (Populated Place, Montezuma, exact_official) | needs_information |
| T052 | 4 wheel drive road to Coney Flats from Beaver Reservoir, ca 1.7 air mi WNW of Beaver Reservoir. | itinerary | Beaver Reservoir | candidates_found | Beaver Reservoir (Reservoir, Boulder, exact_official) | unsupported |
| T053 | Near entrance to Black Canyon National Monument. | route_relative | Black Canyon National Monument | feature_absent_from_index |  | unsupported |
| T054 | Lost Creek Area, Tarryall Mtns., 80 km (50 mi) southwest of Denver and 80km northwest of Colorado Springs. Near Site #60. | named_feature | Lost Creek Area | feature_absent_from_index |  | needs_information |
| T055 | Rocky Mountain National Park, Longs Peak Valley. | other |  | no_reference_feature |  | unsupported |
| T056 | Boulder. Eben Fine Park at mouth of Boulder Canyon. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| T057 | Baca National Wildlife Refuge, San Luis Valley. Ca. 1.5 air miles southwest of Crestone, less than a mile south of Co. Rd. T. where refuge road to headquarters crosses Crestone Creek. | distance_and_direction | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| T058 | Hwy 40, E of Jct. 131, S of Steamboat Springs. | route_relative | Jct. 131 | feature_absent_from_index |  | unsupported |
| T059 | At top of Nipple Mountain Road. | route_relative | Nipple Mountain Road | candidates_found | Nipple Mountain (Summit, Archuleta, fuzzy_official) | unsupported |
| T060 | Stony Basin, ca. 7 miles northeast of Silverton, San Juan National Forest. On east-facing ridge on Green Mountain. | named_feature | Stony Basin | candidates_found | Stone Basin (Basin, Montrose, fuzzy_official) | needs_information |
| T061 | La Foret, Black Forest. | other |  | no_reference_feature |  | unsupported |
| T062 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: on County Road 120, ca 1 mi W of the junction of County Road 120 and U.S. Hwy 50; W of Pueblo. | distance_and_direction | the junction of County Road 120 and U.S. Hwy 50 | feature_absent_from_index |  | needs_information |
| T063 | Niobrara shale formation where it crosses Carter Lake Road, 7 mi SW of Loveland. | distance_and_direction | Loveland | candidates_found | Loveland (Populated Place, Larimer, exact_official) | needs_information |
| T064 | ¼ mi. N of Vallecito Reservoir. | distance_and_direction | Vallecito Reservoir | candidates_found | Vallecito Reservoir (Reservoir, La Plata, exact_official) | needs_information |
| T065 | Boulder; near Boulder Creek south of university baseball park. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| T066 | Southern Gunnison Basin: San Juan Mountains: Uncompahgre National Forest: on Trail 232 along Big Blue Creek, ca 1.6-2.1 air mi ENE of Fall Creek Falls; ca 1-2.6 air mi S of northern Uncompahgre Wilderness Boundary. | distance_and_direction |  |  |  | invalid_extraction |
| T067 | Upper Roaring Fork Valley. City of Aspen Open Space. Aspen Mass. Just off of US Hwy. 82 north of the Brush Creek turn off. | named_feature | Upper Roaring Fork Valley | feature_absent_from_index |  | needs_information |
| T068 | Pike-San Isabel National Forest, Pikes Peak, Boemer Creek headwaters SW. of Windy Point and cog railway, at head of ridge between E. and main forks of Boemer Cr. on flay lying saddle. | named_feature |  |  |  | invalid_extraction |
| T069 | West end of St. Sophia Ridge. | named_feature | St. Sophia Ridge | candidates_found | Saint Sophia Ridge (Ridge, Ouray, fuzzy_official) | needs_information |
| T070 | Central Colorado: Sawatch Range, West Slope Continental Divide: along Trail 1917 at Henderson Park, ca 7 air mi E of Thomasville. | distance_and_direction | Thomasville | candidates_found | Thomasville (Populated Place, Pitkin, exact_official) | needs_information |
| T071 | South side of hwy. 94. | named_feature | hwy. 94 | feature_absent_from_index |  | needs_information |
| T072 | Sand Wash, 10 miles east of junction of Dry Mountain road and Hwy. 318. | distance_and_direction | junction of Dry Mountain road and Hwy. 318 | feature_absent_from_index |  | needs_information |
| T073 | Head of East Brush Creek. | named_feature | East Brush Creek | candidates_found | East Brush Creek (Stream, Gunnison, exact_official) | needs_information |
| T074 | On west bank of Devil Creek east of Pargin house. Piedra. | named_feature | Devil Creek | candidates_found | Devil Creek (Stream, Archuleta, exact_official) | needs_information |
| T075 | 2.5 mi SE of Marble. East side of Whitehouse Mountain. | distance_and_direction | Marble | candidates_found | Marble (Populated Place, Gunnison, exact_official) | needs_information |
| T076 | Northwestern Colorado. 9 miles E. Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | needs_information |
| T077 | Whitby Canyon, Comanche National Grassland. | named_feature | Whitby Canyon | candidates_found | Whitby Canyon (Valley, Baca, exact_official) | needs_information |
| T078 | North end of South Park, Michigan Creek Drainage Area near Jefferson. Moist meadow along Michigan Creek above campground. | named_feature | South Park | candidates_found | South Park (Flat, San Juan, exact_official) | needs_information |
| T079 | White River National Forest, along Fall Creek, 1/10 mile upstream of confluence with Notch Mountain Creek, 5 miles northeast of Holy Cross Mountain. | route_relative | confluence with Notch Mountain Creek | feature_absent_from_index |  | unsupported |
| T080 | Ca. 5 mi W of Delta, 3/4 mi S of Hwy 50, bench above Gunnison River. | distance_and_direction | Delta | candidates_found | Delta (Populated Place, Delta, exact_official) | needs_information |
| T081 | South side Hwy 94. | named_feature | Hwy 94 | feature_absent_from_index |  | needs_information |
| T082 | Gateway Palisade Natural Area N of Gateway between CO hwy 141 (West Creek) & Dolores R.; minor drainages E of Mesa Co road 4.2 on W side of the Palisade. | between_features | Gateway | candidates_found | Gateway (Populated Place, Mesa, exact_official) | unsupported |
| T083 | Foothills just southeast of Buena Vista. | distance_and_direction | Buena Vista | candidates_found | Buena Vista (Populated Place, Chaffee, exact_official) | needs_information |
| T084 | Ca. 5 mi W on Red Feather Lakes Rd. from its intersection with US Hwy 287. | route_relative | US Hwy 287 | feature_absent_from_index |  | unsupported |
| T085 | Approx. 13 miles southeast of Las Aniumas, east side of Road 16. Near stones of old homestead. | distance_and_direction | Las Aniumas | candidates_found | Las Animas (Populated Place, Bent, fuzzy_official) | needs_information |
| T086 | At head of Browns Park; just northeast of Gates of Lodore above Vermilion drainage. | named_feature | Browns Park | candidates_found | Browns Park (Flat, Moffat, exact_official) | needs_information |
| T087 | La Plata Mountains. | other |  | no_reference_feature |  | unsupported |
| T088 | Breaks of East Carrizo Creek 5 mi. s.w. of Kirkwell. | distance_and_direction | Kirkwell | candidates_found | Kirkwell (Populated Place, Baca, exact_official) | needs_information |
| T089 | Banks of Willow Creek near junction with Denver Creek, few miles south of Willow Creek Pass. | between_features | Willow Creek | candidates_found | Willow Creek (Stream, Grand, exact_official) | unsupported |
| T090 | Upper valley of Middle St. Vrain Creek, ca. 2½ miles west of Highway 72. Small meadow along trail, north side of creek, ca. 1½ miles west of Camp Dick Campground. | distance_and_direction | Highway 72 | feature_absent_from_index |  | needs_information |
| T091 | Central Colorado: Gore Range, West Slope Continental Divide: off Forest Road 701, NW of Horse Pond, ca 7 air mi N of Edwards. | orthogonal_offsets |  |  |  | invalid_extraction |
| T092 | Mt. Vernon Country Club, Lookout Mountain. | named_feature | Mt. Vernon Country Club | feature_absent_from_index |  | needs_information |
| T093 | Below Bald Mountain, head of Alta Basin, north of Ophir. | named_feature | Bald Mountain | candidates_found | Bald Mountain (Summit, San Miguel, exact_official) | needs_information |
| T094 | Dinosaur Nat. Mon. East of Snow cabin. Harper's Corner. | named_feature | Dinosaur Nat. Mon. | feature_absent_from_index |  | needs_information |
| T095 | Clear Creek Canyon at Dumont. | named_feature | Clear Creek Canyon | candidates_found | Clear Creek Canyon (Valley, Jefferson, exact_official) | needs_information |
| T096 | 612 Rico Way, Grand Junction. Also found in flower beds at Mesa College. | named_feature | 612 Rico Way | feature_absent_from_index |  | needs_information |
| T097 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. S of Colorado City on Road 670 just N of Huerfano County line. | distance_and_direction |  |  |  | invalid_extraction |
| T098 | Colo. R. half way between Phantom Valley Ranch & Shipler Cabins. 11½ mi. N of Grand Lake. | orthogonal_offsets |  |  |  | invalid_extraction |
| T099 | Mesa Verde National Park. Wetherill Mesa, on backfill below Long House. | named_feature | Wetherill Mesa | candidates_found | Wetherill Mesa (Summit, Montezuma, exact_official) | needs_information |
| T100 | Rabbit Ears' Pass at Jct. w. Muddy Pass. | between_features | Muddy Pass | candidates_found | Muddy Pass (Gap, Jackson, exact_official) | unsupported |
| T101 | Baca National Wildlife Refuge, San Luis Valley. Ca. 6.5 air miles WSW of Crestone. Ca. 3/4 mile S of County Road T on Lexam Rd. In Crestone Creek. | named_feature | Baca National Wildlife Refuge | feature_absent_from_index |  | needs_information |
| T102 | South of Hwy 50, west of Turkey Creek. | between_features |  |  |  | invalid_extraction |
| T103 | Open roadside to Niwot Ridge; above Science Lodge Mountain Research Station, southwest of Ward. | orthogonal_offsets |  |  |  | invalid_extraction |
| T104 | Chicago Basin. San Juan Mts., at Columbine Pass. | named_feature | Chicago Basin | candidates_found | Chicago Basin (Basin, La Plata, exact_official) | needs_information |
| T105 | From seed, NIST, Boulder. | no_locality |  | no_reference_feature |  | unsupported |
| T106 | Outside Crested Butte. Cement Creek Rd., near summit of Italian mt. | named_feature | Italian mt. | candidates_found | Italian Mountain (Summit, Gunnison, core_official) | needs_information |
| T107 | Shores of Crown Hill cemetery lake at 26th & Kipling St. | named_feature | Crown Hill cemetery lake | feature_absent_from_index |  | needs_information |
| T108 | 9 mi. north of Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | needs_information |
| T109 | T6S R46W SEC28. | other |  | no_reference_feature |  | unsupported |
| T110 | Northern Gunnison Basin: Fossil Ridge Wilderness: Summerville Creek, ca 7 air mi SW of Taylor Reservoir. | distance_and_direction | Taylor Reservoir | candidates_found | Taylor Park Reservoir (Reservoir, Gunnison, exact_variant) | needs_information |
| T111 | North of Crestone. At gates of spillway on Crestone Creek. | named_feature | Crestone Creek | candidates_found | Crestone Creek (Stream, Saguache, exact_official) | needs_information |
| T112 | San Juan National Forest; South Fork of Mineral Creek. Trail to Ice Lake Basin. | named_feature | South Fork of Mineral Creek | candidates_found | South Fork Mineral Creek (Stream, San Juan, fuzzy_official) | needs_information |
| T113 | Gothic. Rocky Mountain Biological Laboratory. Gothic Earthflow, flow area below slump block in less steep areas IV and V of Langenheim (1956). In lower, SE section of flow. | named_feature | Gothic Earthflow | feature_absent_from_index |  | needs_information |
| T114 | Above small lakes on Silver Mesa near trail 0.75 miles up from Lake Marie (Durango Reservoir #2). About 1.25 miles south of Trimble Pass. | orthogonal_offsets |  |  |  | invalid_extraction |
| T115 | Denver Mountain Park near Golden. | named_feature | Denver Mountain Park | feature_absent_from_index |  | needs_information |
| T116 | Two miles above Arboles. | distance_and_direction |  |  |  | invalid_extraction |
| T117 | North of Stratton, along County Road 32. | route_relative | Stratton | candidates_found | Stratton (Populated Place, Kit Carson, exact_official) | unsupported |
| T118 | 3.7 miles SE of junction of Greasewood Gulch and Piceance Creek. | distance_and_direction | junction of Greasewood Gulch and Piceance Creek | feature_absent_from_index |  | needs_information |
| T119 | Uncompahgre Plateau. Smokehouse Camprground, 3 mi. NW of Columbine Pass. | named_feature | Smokehouse Camprground | feature_absent_from_index |  | needs_information |
| T120 | Three miles north of Ignacio. | distance_and_direction |  |  |  | invalid_extraction |
