# test: rules first, LLM fallback (`hybrid-1`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark/1`

> Rules first; the LLM's result is used only where the rules reach no gazetteer candidate and the LLM does. Built from the two component reports (both deterministic). The top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**source**: `rules` 107 · `llm` 13

**llm_call**: `made` 47 · `skipped` 73

**relation**: `named_feature` 54 · `direction_only` 35 · `distance_and_direction` 15 · `other` 6 · `route_relative` 6 · `between_features` 4

**retrieval**: `candidates_found` 86 · `feature_absent_from_index` 20 · `no_reference_feature` 14

**proposal**: `needs_information` 104 · `unsupported` 16

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| T001 | Sapinero, also Cimarron. | named_feature | Sapinero | candidates_found | Sapinero (Populated Place, Gunnison, exact_official) | needs_information |
| T002 | Coal Canyon. | named_feature | Coal Canyon | candidates_found | Coal Canyon (Valley, Mesa, exact_official) | needs_information |
| T003 | Near Austin. | named_feature | Austin | candidates_found | Austin (Populated Place, Delta, exact_official) | needs_information |
| T004 | Mt. Evans Highway at timberline. | named_feature | Mt. Evans Highway | feature_absent_from_index |  | needs_information |
| T005 | Private ranch, off private road -- continuation of County Road 5E. | other |  | no_reference_feature |  | unsupported |
| T006 | Northeast of Limon along CR 36. | direction_only | Limon | candidates_found | Limon (Populated Place, Lincoln, exact_official) | needs_information |
| T007 | White River National Forest, along Two Elk Creek, approx. 2/5 mile upstream of confluence with Eagle River. | named_feature | White River National Forest | feature_absent_from_index |  | needs_information |
| T008 | North-central Colorado: Never Summer Mountains: Never Summer Wilderness: Baker Pass NW to peak "11740". | named_feature | Never Summer Mountains | candidates_found | Never Summer Mountains (Range, Jackson, exact_official) | needs_information |
| T009 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. San Isabel National Forest, up Stultz Gulch from Stultz Trailhead on County Road 143, ca 8 air mi S of Canon City. | direction_only | Canon City | candidates_found | Cañon City (Populated Place, Fremont, exact_official) | needs_information |
| T010 | Wolf Creek Pass - 10 mi w. on Continental Divide Trail. | route_relative | Wolf Creek Pass | candidates_found | Wolf Creek Pass (Gap, Mineral, exact_official) | unsupported |
| T011 | South San Juans, E. side of Lake Anne. | named_feature | Lake Anne | candidates_found | Lake Ann (Lake, Archuleta, fuzzy_official) | needs_information |
| T012 | Below Santa Fe Peak. | named_feature | Santa Fe Peak | candidates_found | Santa Fe Peak (Summit, Summit, exact_official) | needs_information |
| T013 | Wetland E side of C470. | other |  | no_reference_feature |  | unsupported |
| T014 | Mouth of Sunshine Canyon near picnic shelter, NW edge of Boulder. | named_feature | Sunshine Canyon | candidates_found | Sunshine Canyon (Valley, Boulder, exact_official) | needs_information |
| T015 | South of Silverton, near road to Kendall Gulch. | direction_only | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| T016 | 17.9 mi. S on Grand Cty. Rd. 3 (aka. USFS Rd. 138) fr. junction with US Hwy. 40 to rd. fork, cont. left SSE on Rd. 138 (aka. Grand Cty. Rd. 30) to USFS Rd. 141 (Kinney Cr. Rd.), 2.5 mi. ENE on Rd. 141 to rivulet drainage, S-side of rd., few hundred m up. | route_relative |  | no_reference_feature |  | unsupported |
| T017 | Owl Canyon, north of La Porte. | direction_only | La Porte | candidates_found | Laporte (Populated Place, Larimer, exact_variant) | needs_information |
| T018 | North 1 mile on flat from junction of Mine road and Redfern road. Douglas Mountain. | route_relative |  | no_reference_feature |  | unsupported |
| T019 | Cuchara Valley. Blue Lake, near the 1 lake. | named_feature | Cuchara Valley | candidates_found | Cucharas Reservoir (Reservoir, Huerfano, fuzzy_variant) | needs_information |
| T020 | Conn Creek, 1/3 mile upstream from confluence of Cascade Creek. | named_feature | Conn Creek | candidates_found | Conn Creek (Stream, Garfield, exact_official) | needs_information |
| T021 | Round Butte Ranch, ca. 20 air mi. of Fort Collins. Sand Creek. | named_feature | Sand Creek | candidates_found | Sand Creek (Stream, Larimer, exact_official) | needs_information |
| T022 | Two miles west of Burlington on north side of Highway 24. | direction_only | Burlington | candidates_found | Burlington (Populated Place, Kit Carson, exact_official) | needs_information |
| T023 | East of Cheyenne, Wyoming. | direction_only | Cheyenne | candidates_found | Cheyenne Mountain (Summit, El Paso, core_official) | needs_information |
| T024 | Windy Saddle Park. Southeast corner of Windy Saddle Park, about 375 m northeast of, and downslope from the Buffalo Bill Museu and 3.36 Km soutwest of the GNIS location of Golden. | named_feature | Windy Saddle Park | feature_absent_from_index |  | needs_information |
| T025 | Private land; slopes NW of Yucca House National Monument. | direction_only | Yucca House National Monument | feature_absent_from_index |  | needs_information |
| T026 | 12.4 road miles along CO Hwy 134 E of its junction with CO Hwy 131 in Toponas. | route_relative |  | no_reference_feature |  | unsupported |
| T027 | Longs Peak. East face. | named_feature | Longs Peak | candidates_found | Longs Peak (Summit, Boulder, exact_official) | needs_information |
| T028 | Central Colorado: Sawatch Range, East Slope Continental Divide: off County Road 321, ca 3.5 air mi W of Nathrop. | direction_only | Nathrop | candidates_found | Nathrop (historical) (Populated Place, Chaffee, exact_official) | needs_information |
| T029 | 2 mi. south of Crested Butte, turn left onto Co. Rd. 738 from Rt. 135. Second rd. on right after crossing the East River, across from farm house. | distance_and_direction | Crested Butte | candidates_found | Crested Butte (Summit, Gunnison, exact_official) | needs_information |
| T030 | Pike National Forest, Lost Creek drainage between Tarryall and Kenosha Mts., along forest trail 609, 1.0 air mile SE of Lost Park Campground. | between_features |  | no_reference_feature |  | unsupported |
| T031 | North Park. Coalmont. | named_feature | North Park | candidates_found | North Park (Flat, Jackson, exact_official) | needs_information |
| T032 | Near junction with Navajo Canyon, Mesa Verde National Park. Canyon floor, Spruce Canyon. | named_feature | Navajo Canyon | candidates_found | Navajo Canyon (Valley, Montezuma, exact_official) | needs_information |
| T033 | Colorado National Monument, Fruita entrance. | named_feature | Colorado National Monument | feature_absent_from_index |  | needs_information |
| T034 | Along Jenny creek, near Ladora. | named_feature | Jenny creek | candidates_found | Jenny Creek (Stream, Gilpin, exact_official) | needs_information |
| T035 | Loveland, NE side of town on SW side of Westerdoll Lake. Disturbed, open ground along roads and in pastures near intersection of Monroe Avenue and E 38th Street. | named_feature | Loveland | candidates_found | Loveland (Populated Place, Larimer, exact_official) | needs_information |
| T036 | La Foret, Black Forest; meadow vic. Ponderosa Lodge. | named_feature | La Foret | candidates_found | La Foret (Populated Place, El Paso, exact_official) | needs_information |
| T037 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Culebra Range: on a small tributary of Trinchera Creek, ca 2 mi before Beccerro Basin, SE of Fort Garland. | direction_only | Fort Garland | candidates_found | Fort Garland (Populated Place, Costilla, exact_official) | needs_information |
| T038 | Headwaters of Clear Creek, west of U.S. Forest Service ski lodge near Loveland Pass. | named_feature | Clear Creek | candidates_found | Clear Creek (Stream, Jackson, exact_official) | needs_information |
| T039 | La Sal Cr., 3 mi above confluence with Dolores River, SW of Bedrock. | direction_only | Bedrock | candidates_found | Bedrock (Populated Place, Montrose, exact_official) | needs_information |
| T040 | Alamosa River Canyon just below Alamosa Campground. | named_feature | Alamosa River Canyon | feature_absent_from_index |  | needs_information |
| T041 | Mesa de Maya, in gap between east and west sections, on Willard Louden Ranch (20,000 acres) NW of Branson. | direction_only | Branson | candidates_found | Branson (Populated Place, Las Animas, exact_official) | needs_information |
| T042 | Boulder Mtn. Parks W of the National Bureau of Standards. In a swale between NBS Mesa and Enchanted Mesa. | between_features |  | no_reference_feature |  | unsupported |
| T043 | Near Platte River. | named_feature | Platte River | candidates_found | Slate River (Stream, Gunnison, fuzzy_official) | needs_information |
| T044 | Baca National Wildlife Refuge, San Luis Valley. Ca. 4 air miles WSW of Crestone. Ca. ¼ mile S of County Road T, just E of two-track to Cattle HQ. ON N. Crestone Ditch. | distance_and_direction | County Road T | feature_absent_from_index |  | needs_information |
| T045 | Dinosaur National Monument; at Canyon Overlook Picnic Ground between Harper's Corner and Echo Park road. | between_features | Harper's Corner | candidates_found | Harpers Corner (Cape, Moffat, exact_official) | unsupported |
| T046 | Rocky Mountain National Park, Front Range, Horseshoe Park alluvial fan at mouth of Roaring R. on deep gravel floodplain deposited by Lawn L. flood in July 1982. E of Roaring R., S of Fall R. rd, N of Fall R. | direction_only | Roaring R | candidates_found | Roaring Fork (Stream, Larimer, fuzzy_official) | needs_information |
| T047 | Curecanti National Recreation Area. Cimarron. Mesa Creek trail just below Morrow Point Dam. GPS waypoint: AC9. | named_feature | Curecanti National Recreation Area | feature_absent_from_index |  | needs_information |
| T048 | Rocky Mountain National Park; valley near junct. of E. & W. forks of Hague Creek; in Hague Creek subalpine fens. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| T049 | Alpine saddle between summit of Mount Evans and Mount Epaulet. | named_feature | Alpine | candidates_found | Alpine (Populated Place, Rio Grande, exact_official) | needs_information |
| T050 | Near Lower Cataract Lake. | named_feature | Near Lower Cataract Lake | candidates_found | Lower Cataract Lake (Lake, Summit, fuzzy_official) | needs_information |
| T051 | Ranch near Cortez. | named_feature | Cortez | candidates_found | Cortez (Populated Place, Montezuma, exact_official) | needs_information |
| T052 | 4 wheel drive road to Coney Flats from Beaver Reservoir, ca 1.7 air mi WNW of Beaver Reservoir. | direction_only | Beaver Reservoir | candidates_found | Beaver Reservoir (Reservoir, Boulder, exact_official) | needs_information |
| T053 | Near entrance to Black Canyon National Monument. | named_feature | Black Canyon National Monument | feature_absent_from_index |  | needs_information |
| T054 | Lost Creek Area, Tarryall Mtns., 80 km (50 mi) southwest of Denver and 80km northwest of Colorado Springs. Near Site #60. | direction_only | Denver | candidates_found | Denver (Populated Place, Denver, exact_official) | needs_information |
| T055 | Rocky Mountain National Park, Longs Peak Valley. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| T056 | Boulder. Eben Fine Park at mouth of Boulder Canyon. | named_feature | Boulder Canyon | candidates_found | Butler Canyon (Valley, Douglas, fuzzy_official) | needs_information |
| T057 | Baca National Wildlife Refuge, San Luis Valley. Ca. 1.5 air miles southwest of Crestone, less than a mile south of Co. Rd. T. where refuge road to headquarters crosses Crestone Creek. | direction_only | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| T058 | Hwy 40, E of Jct. 131, S of Steamboat Springs. | direction_only | Jct. | feature_absent_from_index |  | needs_information |
| T059 | At top of Nipple Mountain Road. | named_feature | Nipple Mountain Road | candidates_found | Nipple Mountain (Summit, Archuleta, fuzzy_official) | needs_information |
| T060 | Stony Basin, ca. 7 miles northeast of Silverton, San Juan National Forest. On east-facing ridge on Green Mountain. | distance_and_direction | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| T061 | La Foret, Black Forest. | named_feature | La Foret | candidates_found | La Foret (Populated Place, El Paso, exact_official) | needs_information |
| T062 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: on County Road 120, ca 1 mi W of the junction of County Road 120 and U.S. Hwy 50; W of Pueblo. | direction_only | Pueblo | candidates_found | Pueblo (Populated Place, Pueblo, exact_official) | needs_information |
| T063 | Niobrara shale formation where it crosses Carter Lake Road, 7 mi SW of Loveland. | distance_and_direction | Loveland | candidates_found | Loveland (Populated Place, Larimer, exact_official) | needs_information |
| T064 | ¼ mi. N of Vallecito Reservoir. | distance_and_direction | Vallecito Reservoir | candidates_found | Vallecito Reservoir (Reservoir, La Plata, exact_official) | needs_information |
| T065 | Boulder; near Boulder Creek south of university baseball park. | named_feature | Boulder Creek | candidates_found | Middle Boulder Creek (Stream, Boulder, exact_variant) | needs_information |
| T066 | Southern Gunnison Basin: San Juan Mountains: Uncompahgre National Forest: on Trail 232 along Big Blue Creek, ca 1.6-2.1 air mi ENE of Fall Creek Falls; ca 1-2.6 air mi S of northern Uncompahgre Wilderness Boundary. | direction_only | Fall Creek Falls | feature_absent_from_index |  | needs_information |
| T067 | Upper Roaring Fork Valley. City of Aspen Open Space. Aspen Mass. Just off of US Hwy. 82 north of the Brush Creek turn off. | direction_only | Brush Creek | candidates_found | Brush Creek (Stream, Pitkin, exact_official) | needs_information |
| T068 | Pike-San Isabel National Forest, Pikes Peak, Boemer Creek headwaters SW. of Windy Point and cog railway, at head of ridge between E. and main forks of Boemer Cr. on flay lying saddle. | named_feature | Pikes Peak | candidates_found | Pikes Peak (Summit, El Paso, exact_official) | needs_information |
| T069 | West end of St. Sophia Ridge. | named_feature | St. Sophia Ridge | candidates_found | Saint Sophia Ridge (Ridge, Ouray, fuzzy_official) | needs_information |
| T070 | Central Colorado: Sawatch Range, West Slope Continental Divide: along Trail 1917 at Henderson Park, ca 7 air mi E of Thomasville. | direction_only | Thomasville | candidates_found | Thomasville (Populated Place, Pitkin, exact_official) | needs_information |
| T071 | South side of hwy. 94. | other |  | no_reference_feature |  | unsupported |
| T072 | Sand Wash, 10 miles east of junction of Dry Mountain road and Hwy. 318. | named_feature | Sand Wash | candidates_found | Sand Wash (Stream, Moffat, exact_official) | needs_information |
| T073 | Head of East Brush Creek. | named_feature | East Brush Creek | candidates_found | East Brush Creek (Stream, Gunnison, exact_official) | needs_information |
| T074 | On west bank of Devil Creek east of Pargin house. Piedra. | direction_only | Pargin | candidates_found | Pargin Mountain (Summit, Archuleta, core_official) | needs_information |
| T075 | 2.5 mi SE of Marble. East side of Whitehouse Mountain. | distance_and_direction | Marble | candidates_found | Marble (Populated Place, Gunnison, exact_official) | needs_information |
| T076 | Northwestern Colorado. 9 miles E. Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | needs_information |
| T077 | Whitby Canyon, Comanche National Grassland. | named_feature | Whitby Canyon | candidates_found | Whitby Canyon (Valley, Baca, exact_official) | needs_information |
| T078 | North end of South Park, Michigan Creek Drainage Area near Jefferson. Moist meadow along Michigan Creek above campground. | named_feature | Jefferson | candidates_found | Jefferson (Populated Place, Park, exact_official) | needs_information |
| T079 | White River National Forest, along Fall Creek, 1/10 mile upstream of confluence with Notch Mountain Creek, 5 miles northeast of Holy Cross Mountain. | distance_and_direction | Holy Cross Mountain | feature_absent_from_index |  | needs_information |
| T080 | Ca. 5 mi W of Delta, 3/4 mi S of Hwy 50, bench above Gunnison River. | distance_and_direction | Delta | candidates_found | Delta (Populated Place, Delta, exact_official) | needs_information |
| T081 | South side Hwy 94. | other |  | no_reference_feature |  | unsupported |
| T082 | Gateway Palisade Natural Area N of Gateway between CO hwy 141 (West Creek) & Dolores R.; minor drainages E of Mesa Co road 4.2 on W side of the Palisade. | direction_only | Gateway | candidates_found | Gateway (Populated Place, Mesa, exact_official) | needs_information |
| T083 | Foothills just southeast of Buena Vista. | direction_only | Buena Vista | candidates_found | Buena Vista (Populated Place, Chaffee, exact_official) | needs_information |
| T084 | Ca. 5 mi W on Red Feather Lakes Rd. from its intersection with US Hwy 287. | route_relative |  | no_reference_feature |  | unsupported |
| T085 | Approx. 13 miles southeast of Las Aniumas, east side of Road 16. Near stones of old homestead. | distance_and_direction | Las Aniumas | candidates_found | Las Animas (Populated Place, Bent, fuzzy_official) | needs_information |
| T086 | At head of Browns Park; just northeast of Gates of Lodore above Vermilion drainage. | direction_only | Gates of Lodore | candidates_found | Gates of Lodore (Gap, Moffat, exact_official) | needs_information |
| T087 | La Plata Mountains. | named_feature | La Plata Mountains | candidates_found | La Plata Mountains (Range, Montezuma, exact_official) | needs_information |
| T088 | Breaks of East Carrizo Creek 5 mi. s.w. of Kirkwell. | distance_and_direction | Kirkwell | candidates_found | Kirkwell (Populated Place, Baca, exact_official) | needs_information |
| T089 | Banks of Willow Creek near junction with Denver Creek, few miles south of Willow Creek Pass. | direction_only | Willow Creek Pass | candidates_found | Willow Creek Pass (Gap, Grand, exact_official) | needs_information |
| T090 | Upper valley of Middle St. Vrain Creek, ca. 2½ miles west of Highway 72. Small meadow along trail, north side of creek, ca. 1½ miles west of Camp Dick Campground. | distance_and_direction | Highway | feature_absent_from_index |  | needs_information |
| T091 | Central Colorado: Gore Range, West Slope Continental Divide: off Forest Road 701, NW of Horse Pond, ca 7 air mi N of Edwards. | direction_only | Horse Pond | candidates_found | Horse Pond (Lake, Eagle, exact_official) | needs_information |
| T092 | Mt. Vernon Country Club, Lookout Mountain. | named_feature | Mt. Vernon Country Club | feature_absent_from_index |  | needs_information |
| T093 | Below Bald Mountain, head of Alta Basin, north of Ophir. | direction_only | Ophir | candidates_found | Ophir (Populated Place, San Miguel, exact_official) | needs_information |
| T094 | Dinosaur Nat. Mon. East of Snow cabin. Harper's Corner. | direction_only | Snow | feature_absent_from_index |  | needs_information |
| T095 | Clear Creek Canyon at Dumont. | named_feature | Dumont | candidates_found | Dumont (Populated Place, Clear Creek, exact_official) | needs_information |
| T096 | 612 Rico Way, Grand Junction. Also found in flower beds at Mesa College. | named_feature | Mesa College | feature_absent_from_index |  | needs_information |
| T097 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. S of Colorado City on Road 670 just N of Huerfano County line. | direction_only | Colorado City | candidates_found | Colorado City (Populated Place, Pueblo, exact_official) | needs_information |
| T098 | Colo. R. half way between Phantom Valley Ranch & Shipler Cabins. 11½ mi. N of Grand Lake. | between_features |  | no_reference_feature |  | unsupported |
| T099 | Mesa Verde National Park. Wetherill Mesa, on backfill below Long House. | named_feature | Wetherill Mesa | candidates_found | Wetherill Mesa (Summit, Montezuma, exact_official) | needs_information |
| T100 | Rabbit Ears' Pass at Jct. w. Muddy Pass. | named_feature | Muddy Pass | candidates_found | Muddy Pass (Gap, Jackson, exact_official) | needs_information |
| T101 | Baca National Wildlife Refuge, San Luis Valley. Ca. 6.5 air miles WSW of Crestone. Ca. 3/4 mile S of County Road T on Lexam Rd. In Crestone Creek. | distance_and_direction | County Road T | feature_absent_from_index |  | needs_information |
| T102 | South of Hwy 50, west of Turkey Creek. | direction_only | Hwy | feature_absent_from_index |  | needs_information |
| T103 | Open roadside to Niwot Ridge; above Science Lodge Mountain Research Station, southwest of Ward. | direction_only | Ward | candidates_found | Ward (Populated Place, Boulder, exact_official) | needs_information |
| T104 | Chicago Basin. San Juan Mts., at Columbine Pass. | named_feature | Columbine Pass | candidates_found | Columbine Pass (Gap, La Plata, exact_official) | needs_information |
| T105 | From seed, NIST, Boulder. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| T106 | Outside Crested Butte. Cement Creek Rd., near summit of Italian mt. | named_feature | Outside Crested Butte | candidates_found | Mount Crested Butte (Populated Place, Gunnison, fuzzy_official) | needs_information |
| T107 | Shores of Crown Hill cemetery lake at 26th & Kipling St. | other |  | no_reference_feature |  | unsupported |
| T108 | 9 mi. north of Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | needs_information |
| T109 | T6S R46W SEC28. | other |  | no_reference_feature |  | unsupported |
| T110 | Northern Gunnison Basin: Fossil Ridge Wilderness: Summerville Creek, ca 7 air mi SW of Taylor Reservoir. | direction_only | Taylor Reservoir | candidates_found | Taylor Park Reservoir (Reservoir, Gunnison, exact_variant) | needs_information |
| T111 | North of Crestone. At gates of spillway on Crestone Creek. | direction_only | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| T112 | San Juan National Forest; South Fork of Mineral Creek. Trail to Ice Lake Basin. | named_feature | South Fork of Mineral Creek | candidates_found | South Fork Mineral Creek (Stream, San Juan, fuzzy_official) | needs_information |
| T113 | Gothic. Rocky Mountain Biological Laboratory. Gothic Earthflow, flow area below slump block in less steep areas IV and V of Langenheim (1956). In lower, SE section of flow. | named_feature | Gothic | candidates_found | Gothic (Populated Place, Gunnison, exact_official) | needs_information |
| T114 | Above small lakes on Silver Mesa near trail 0.75 miles up from Lake Marie (Durango Reservoir #2). About 1.25 miles south of Trimble Pass. | route_relative |  | no_reference_feature |  | unsupported |
| T115 | Denver Mountain Park near Golden. | named_feature | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | needs_information |
| T116 | Two miles above Arboles. | named_feature | Arboles | candidates_found | Arboles (Populated Place, Archuleta, exact_official) | needs_information |
| T117 | North of Stratton, along County Road 32. | direction_only | Stratton | candidates_found | Stratton (Populated Place, Kit Carson, exact_official) | needs_information |
| T118 | 3.7 miles SE of junction of Greasewood Gulch and Piceance Creek. | named_feature | Greasewood Gulch | candidates_found | Greasewood Gulch (Valley, Rio Blanco, exact_official) | needs_information |
| T119 | Uncompahgre Plateau. Smokehouse Camprground, 3 mi. NW of Columbine Pass. | distance_and_direction | Columbine Pass | candidates_found | Columbine Pass (Gap, Montrose, exact_official) | needs_information |
| T120 | Three miles north of Ignacio. | direction_only | Ignacio | candidates_found | Ignacio (Populated Place, La Plata, exact_official) | needs_information |
