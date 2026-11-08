# test-2: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark-2/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the system's ranking, not a reviewed choice, and no extent was supplied.

**relation**: `named_feature` 55 · `distance_and_direction` 27 · `itinerary` 9 · `route_relative` 7 · `between_features` 6 · `orthogonal_offsets` 5 · `other` 4 · `direction_only` 3 · `no_locality` 3 · `distance_only` 1

**retrieval**: `candidates_found` 69 · `feature_absent_from_index` 32 · `None` 12 · `no_reference_feature` 7

**proposal**: `needs_information` 80 · `unsupported` 27 · `invalid_extraction` 12 · `computed` 1

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| H002 | Rio Grande National Forest; ~4 miles NW of Platoro; E ridge of Lookout Mountain | named_feature | Rio Grande National Forest | feature_absent_from_index |  | needs_information |
| H003 | Along Hwy 160 between Mancos and Cortez, west of Mesa Verde Nat. Park exit and ca. 1 mi. W of hwy rest area. | itinerary | Hwy 160 | feature_absent_from_index |  | unsupported |
| H004 | Roadside cut, ca 24.5 road-km up Forest Service Rd 369 from junct with Forest Service Rd 360, Wet Mountains, San Isabel National Forest, ca 11 air-km W of Rye, CO. NW-facing roadcut, E side of rd. | itinerary |  |  |  | invalid_extraction |
| H005 | Colorado National Monument. Between Glade Park road and rim of No Thoroughfare canyon. | between_features | No Thoroughfare canyon | candidates_found | No Thoroughfare Canyon (Valley, Mesa, exact_official) | unsupported |
| H006 | Clear Creek Valley 1 mile east of Georgetown. | distance_and_direction | Georgetown | candidates_found | Georgetown (Populated Place, Clear Creek, exact_official) | needs_information |
| H007 | 8 miles southwest of Sedalia. | distance_and_direction | Sedalia | candidates_found | Sedalia (Populated Place, Douglas, exact_official) | needs_information |
| H008 | Range beyond Windy Gulch. | other | Windy Gulch | candidates_found | Windy Gulch (Valley, Larimer, exact_official) | unsupported |
| H009 | River bench 2 mi. w. of Florence. | distance_and_direction | Florence | candidates_found | Florence (Populated Place, Fremont, exact_official) | needs_information |
| H010 | Wild Basin; Ouzel Burn. Rocky Mountain National Park. | named_feature | Wild Basin | candidates_found | Wild Basin (Basin, Boulder, exact_official) | needs_information |
| H012 | Rocky Flats Site, 7 mi S of Boulder. West Entrance road by Woman Creek. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| H013 | Gunnison Gorge, N of the Black Canyon. | named_feature | Black Canyon | candidates_found | Black Canyon (Valley, Larimer, exact_official) | needs_information |
| H014 | Black Canyon of the Gunnison National Park. Sunset Overlook; west end of South Rim road. GPS waypoint: AB21. | named_feature | Sunset Overlook | feature_absent_from_index |  | needs_information |
| H015 | Fox Ranch, ca. ten miles NE of Kirk, and six miles N of Hwy. 36. East of County Road P. North bank of the Arickaree River. | orthogonal_offsets |  |  |  | invalid_extraction |
| H016 | Independence Pass, top of Continental Divide. | named_feature | Independence Pass | candidates_found | Independence Pass (Gap, Lake, exact_official) | needs_information |
| H017 | Near Windy Point, s.e. slope of Pike's Peak. | named_feature | Windy Point | candidates_found | Windy Point (Cliff, El Paso, exact_official) | needs_information |
| H018 | Limon, 5 mi. N, 0.5 mi. E. S-facing slope of Foncanyon Hill. | orthogonal_offsets | Foncanyon Hill | candidates_found | Long Canyon Hill (Slope, Las Animas, fuzzy_official) | unsupported |
| H019 | In Conway Draw along Ladore Road, 17.45 mi. from Greystone. | route_relative | Greystone | candidates_found | Greystone (Populated Place, Moffat, exact_official) | unsupported |
| H020 | Approx. 1.2 mi. W of Horsetooth Res. | distance_and_direction | Horsetooth Res. | candidates_found | Horsetooth Reservoir (Reservoir, Larimer, exact_official) | needs_information |
| H022 | Along Cherry Creek, Denver. | named_feature | Cherry Creek | candidates_found | Cherry Creek (Stream, Denver, exact_official) | needs_information |
| H023 | Trail to Queens Basin, n.e. of Gothic. | route_relative | Queens Basin | candidates_found | Queen Basin (Basin, Gunnison, fuzzy_official) | unsupported |
| H024 | Arapahoe National Wildlife Refuge, ca. 10 mi. S of Walden. | distance_and_direction | Walden | candidates_found | Walden (Populated Place, Jackson, exact_official) | needs_information |
| H025 | 5 miles SW Cortez. | distance_and_direction | Cortez | candidates_found | Cortez (Populated Place, Montezuma, exact_official) | needs_information |
| H026 | Upper Dolores River Drainage and Adjacent Areas: Goodman Point at Hovenweep National Monument, ca 18 air mi NW of Cortez, County Road P, between County roads 17 and 18. | itinerary | Hovenweep National Monument | feature_absent_from_index |  | unsupported |
| H027 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Sangre de Cristo Range, Rainbow Trail between Alvarado and Hiltman creeks, ca 2.8 air mi NE of Horn Peak, ca 6.5 air mi SW of Westcliffe. | itinerary | Horn Peak | candidates_found | Horn Peak (Summit, Custer, exact_official) | unsupported |
| H028 | Mesa de Maya Region of southeastern Colorado, Pine Canyon Quad., growing at the far western end of the Mesa de Maya. | named_feature | Mesa de Maya | candidates_found | Mesa de Maya (Summit, Las Animas, exact_official) | needs_information |
| H029 | Park Range; Mad Creek Drainage, ca. 7 air mi NNW of Steamboat Springs; gravel bars of Mad Creek. | distance_and_direction | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | needs_information |
| H030 | White River Plateau above Broken Rib Creek. | named_feature | Broken Rib Creek | candidates_found | Broken Rib Creek (Stream, Garfield, exact_official) | needs_information |
| H031 | Just west of Far Veiw Ruin, Mesa Verde National Park. | direction_only | Far Veiw Ruin | feature_absent_from_index |  | needs_information |
| H032 | Eldorado Springs State Park, South Boulder Creek at emergence from the canyon. North side of road near gate at the park entrance. | named_feature | Eldorado Springs State Park | feature_absent_from_index |  | needs_information |
| H033 | Rocky Flats Site. 7 miles south of Boulder on Rocky Flats Pediment, north of TR08, south of power poles. | named_feature | Rocky Flats Pediment | feature_absent_from_index |  | needs_information |
| H034 | Eldorado Springs State Park, South Boulder Creek at emergence from the canyon. Sunny hillside 200 ft. above north side of the creek by Red Garden Wall. | named_feature | Eldorado Springs State Park | feature_absent_from_index |  | needs_information |
| H035 | Mosquito Range. Pike National Forest. 1/8 mile SW of Weston Pass on S-facing slope. | distance_and_direction | Weston Pass | candidates_found | Weston Pass (Gap, Lake, exact_official) | needs_information |
| H036 | North Park, sagebrush flats northwest of Cowdrey. | distance_and_direction | Cowdrey | candidates_found | Cowdrey (Populated Place, Jackson, exact_official) | needs_information |
| H038 | Along road to Bowie Mine. | named_feature | Bowie Mine | feature_absent_from_index |  | needs_information |
| H041 | Trail from Slavonia to Gilpin Lake, ca. 30 mi. n. of Steamboat Springs. | itinerary | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | unsupported |
| H042 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Black Hawk State Trust Lands off County Road 312, ca 10 air mi S of Walsenberg. | distance_and_direction | Walsenberg | candidates_found | Walsenburg (Populated Place, Huerfano, fuzzy_official) | needs_information |
| H043 | Head of Navajo Canyon. Mesa Verde National Park. | named_feature | Navajo Canyon | candidates_found | Navajo Canyon (Valley, Montezuma, exact_official) | needs_information |
| H044 | South Park, about 1 mile E of HW 285 on Lost Park Road, NE of Jefferson. | orthogonal_offsets | HW 285 | feature_absent_from_index |  | unsupported |
| H045 | North Cheyenne Creek. | named_feature | North Cheyenne Creek | candidates_found | North Cheyenne Creek (Stream, El Paso, exact_official) | needs_information |
| H046 | Along Jasper Rd 2 mi W of Erie. | route_relative | Erie | candidates_found | Erie (Populated Place, Boulder, exact_official) | unsupported |
| H047 | Golden; Tin Cup Ridge. Along the top of “Tin Cup Ridge,” the northward extension of Dinosaur Ridge into Golden, 5.2 km. south of the GNIS location of Golden.; 39.71099831 -105.2037943 | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | needs_information |
| H048 | North-central Colorado: Elkhead Mountains: Sand Point above the head of Fourmile Creek, ca 7.5 air mi E of Fortification; ca 22.5 air mi NNE of Craig. | distance_and_direction | Fortification | feature_absent_from_index |  | needs_information |
| H049 | At Ferndale Ranch on Baggs-Great Divide Road; about 20 mi. sw. of Baggs. | named_feature | Ferndale Ranch | feature_absent_from_index |  | needs_information |
| H052 | 3.8 mi. W of Sapinero Bridge above Curecanti Reservoir just W of Dry Gulch and W of Lake City Turnoff. | distance_and_direction | Sapinero Bridge | feature_absent_from_index |  | needs_information |
| H053 | Top of Red Mountain Pass. | named_feature | Red Mountain Pass | candidates_found | Red Mountain Pass (Gap, Ouray, exact_official) | needs_information |
| H054 | On North side of Four mile canyon road (118) about 1/2 miles Southeast of Salina. | orthogonal_offsets | Four mile canyon road (118) | feature_absent_from_index |  | unsupported |
| H055 | Dinosaur National Monument; east of Snow Cabin Harper's Corner. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| H056 | Fork of Poudre and Big South. | between_features |  | no_reference_feature |  | unsupported |
| H058 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Culebra Range: southwestern ridge of Trinchera Peak, SE of Fort Garland. | distance_and_direction |  |  |  | invalid_extraction |
| H059 | Grand Mesa Nat. Forest. Lily Lake. Above lake. | named_feature | Lily Lake | candidates_found | Lily Lake (Reservoir, Mesa, exact_official) | needs_information |
| H060 | John Rideo Hill, 1 mi. E. of Hwy 109. | distance_and_direction | Hwy 109 | feature_absent_from_index |  | needs_information |
| H062 | Spenser Mt., Eldora. | named_feature | Spenser Mt. | feature_absent_from_index |  | needs_information |
| H064 | Neota Wilderness. 7 miles south of Hwy. 14 on Long draw Rd. 1 mile west of road in wilderness. | itinerary | Neota Wilderness | feature_absent_from_index |  | unsupported |
| H065 | Dry flood channel of Conejos river; Spectacle Lake campground. | named_feature | Spectacle Lake | candidates_found | Spectacle Lake (Lake, Conejos, exact_official) | needs_information |
| H066 | San Juan Mts. | named_feature | San Juan Mts. | feature_absent_from_index |  | needs_information |
| H067 | Just north of Colorado-New Mexico state line above Lake Maloya. | named_feature | Lake Maloya | feature_absent_from_index |  | needs_information |
| H068 | Northern Gunnison Basin: West Elk Wilderness: Middle Baldy and Middle Baldy Mountain, ca 13.5 air mi N of Blue Mesa Reservoir. | distance_and_direction | Blue Mesa Reservoir | candidates_found | Blue Mesa Reservoir (Reservoir, Gunnison, exact_official) | needs_information |
| H069 | Overlooking Hwy 64 ca. 5 mi E of Rangely. | distance_and_direction |  |  |  | invalid_extraction |
| H070 | Cement Creek Hot Springs. SE of Crested Butte. | named_feature | Cement Creek Hot Springs | candidates_found | Cement Creek Hot Spring (Spring, Gunnison, fuzzy_official) | computed |
| H071 | Just west of Marshall Lake, along Boulder-Golden Highway. | named_feature | Marshall Lake | candidates_found | Marshall Lake (Reservoir, Boulder, exact_official) | needs_information |
| H073 | Along Hwy. 78. | no_locality |  | no_reference_feature |  | unsupported |
| H074 | Mosquito Range. San Isabel National Forest. Buffalo Peaks Wilderness Area. Just SE and below of South Peak. | named_feature | Mosquito Range | candidates_found | Mosquito Range (Range, Lake, exact_official) | needs_information |
| H075 | I-76 frontage road between Roggen and Keensburg. | between_features | Roggen | candidates_found | Roggen (Populated Place, Weld, exact_official) | unsupported |
| H076 | Grand Mesa, Bull Basin. | named_feature | Grand Mesa | candidates_found | Grand Mesa (Area, Mesa, exact_official) | needs_information |
| H077 | 1 mile southwest of Eldorado Springs; along railroad tracks at head of Rattlesnake Gulch, just east of tunnel. | distance_and_direction | Eldorado Springs | candidates_found | Eldorado Springs (Populated Place, Boulder, exact_official) | needs_information |
| H078 | Near Albion Lake. | named_feature | Albion Lake | candidates_found | Albion Lake (Reservoir, Boulder, exact_official) | needs_information |
| H079 | Rocky Mountain National Park. Glacier Basin, Boulder Brook, ~.5 mi. above Sprague Lake. | named_feature | Glacier Basin, Boulder Brook | feature_absent_from_index |  | needs_information |
| H080 | Taylor Peak, above the Iron Mine Road. | named_feature | Taylor Peak | candidates_found | Taylor Peak (Summit, Pitkin, exact_official) | needs_information |
| H081 | Along Horse Creek -South Platte tributary; directly southeast of Deckers on Hwy. 67. | route_relative | Deckers | candidates_found | Deckers (Populated Place, Douglas, exact_official) | unsupported |
| H082 | Watson's Gulch at Florence Picnic grounds. | named_feature | Watson's Gulch | candidates_found | Watson Gulch (Valley, Custer, fuzzy_official) | needs_information |
| H083 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: ca 2.5 air mi E of Rico, along the Colorado Trail at Black Hawk Basin. | itinerary |  |  |  | invalid_extraction |
| H084 | La Plata Mts., Tomahawk Basin. Slope down toward Little Kate from saddle to 1/2 way down. Diorite Peak. | named_feature | Diorite Peak | candidates_found | Diorite Peak (Summit, La Plata, exact_official) | needs_information |
| H085 | Pike National Forest near Indian Creek Campground. | named_feature | Indian Creek Campground | feature_absent_from_index |  | needs_information |
| H086 | Rocky Mtountain Flora. 39°-41° | no_locality |  | no_reference_feature |  | unsupported |
| H088 | Near the junction of McElmo and Yellow Jacket Canyons (G Rd). SW-facing slopes just E of the Ismay Trading Post. | between_features | the junction of McElmo and Yellow Jacket Canyons | feature_absent_from_index |  | unsupported |
| H090 | 9 mi. n.e. of Nucla, on road to Columbine Pass, Uncompahgre Plateau. | distance_and_direction | Nucla | candidates_found | Nucla (Populated Place, Montrose, exact_official) | needs_information |
| H091 | Luning Arroyo, approx. 20 miles ESE of Earl and 2 miles west of Purgatoire Canyon. South side of arroyo. | distance_and_direction | Earl | candidates_found | Earl (Populated Place, Las Animas, exact_official) | needs_information |
| H092 | Start of Stone City Road (road 111), between Pueblo and Penrose 1-2 mi. north of Hwy 50. | itinerary |  |  |  | invalid_extraction |
| H093 | Vicinity of Aspen. Along forest trail 1994, about one city block east of trailhead on rockfall on south side of trail. (Woody Creek Road.). | itinerary |  |  |  | invalid_extraction |
| H094 | 5 mi. n. of Rifle along Government Creek.; 39.6055368 -107.803777 | distance_and_direction | Rifle | candidates_found | Rifle (Populated Place, Garfield, exact_official) | needs_information |
| H095 | Boulder quad: 13TDQ 751 306. Silver Lake ditch at 2839, 3rd, Boulder. | no_locality |  | no_reference_feature |  | unsupported |
| H096 | Shore of Cowdrey Reservoir, 3½ mi. E of Marshall. | distance_and_direction | Cowdrey Reservoir | candidates_found | Cowdrey Reservoir (historical) (Reservoir, Boulder, exact_official) | needs_information |
| H097 | Hagerman Pass, ca. 10.5 miles northwest of Turquoise Lake, San Isabel National Forest. | named_feature | Hagerman Pass | candidates_found | Hagerman Pass (Gap, Pitkin, exact_official) | needs_information |
| H098 | Ridge E of Cumberland Pass. Gunnison National Forest. | direction_only | Cumberland Pass | candidates_found | Cumberland Pass (Gap, Gunnison, exact_official) | needs_information |
| H099 | Mesa Verde National Park and vicinity. Gravel pits, S end of Chapin Mesa. | named_feature | Chapin Mesa | candidates_found | Chapin Mesa (Summit, Montezuma, exact_official) | needs_information |
| H100 | Boulder Creeek Road. Willow Lakes Quadrangle. | other |  | no_reference_feature |  | unsupported |
| H101 | Inlet to north end of Lake John. | named_feature | Lake John | candidates_found | Lake John (Lake, Jackson, exact_official) | needs_information |
| H103 | Pastures along Mud Creek, south and west of Mancos. | named_feature | Mud Creek | candidates_found | Mud Creek (Stream, Montezuma, exact_official) | needs_information |
| H105 | Capitol Hill. | named_feature | Capitol Hill | feature_absent_from_index |  | needs_information |
| H106 | Black Canyon of the Gunnison National Park. Gunnison River, at base of " Warner Route". GPS waypoint: AB29. | named_feature | Black Canyon of the Gunnison National Park | feature_absent_from_index |  | needs_information |
| H107 | Uncompahgre. | other |  | no_reference_feature |  | unsupported |
| H108 | South Park, Twelve Mile Club, up Sheep Creek along salt flat. | route_relative | Sheep Creek | candidates_found | Sheep Creek (Stream, Park, exact_official) | unsupported |
| H109 | On hill above Junc. of Dolores River. | named_feature | Junc. of Dolores River | feature_absent_from_index |  | needs_information |
| H110 | Near Ellicott. | named_feature | Ellicott | candidates_found | Ellicott (Populated Place, El Paso, exact_official) | needs_information |
| H111 | Fraser Experimental Forest. Bottle Pass treeline. | other |  | no_reference_feature |  | unsupported |
| H113 | E. Thomasville - Fryingpan Creek. | between_features | E. Thomasville | candidates_found | Thomasville (Populated Place, Pitkin, fuzzy_official) | unsupported |
| H114 | Northern Gunnison Basin: Raggeds Wilderness: Dark Canyon, ca 8.5 air mi NW of Kebler Pass. | distance_and_direction | Kebler Pass | candidates_found | Kebler Pass (Gap, Gunnison, exact_official) | needs_information |
| H115 | 2.2 mi S, 17.2 mi W DeBeque. (Take X.50/222 Road [to Wild Horse Area] 11.5 roadmi E from junction with 204/45 Road, then O.90 Road 6.5 roadmi SE. Site on N side of O.90 Road.) Just E Corcoran Peak. | orthogonal_offsets |  |  |  | invalid_extraction |
| H116 | Material from near Chimney Rock. | named_feature | Chimney Rock | candidates_found | Chimney Rock (Summit, Archuleta, exact_official) | needs_information |
| H117 | Paonia. | named_feature | Paonia | candidates_found | Paonia (Populated Place, Delta, exact_official) | needs_information |
| H118 | Needle Creek. | named_feature | Needle Creek | candidates_found | Needle Creek (Stream, La Plata, exact_official) | needs_information |
| H119 | Castlewood Canyon State Park, 4.5 miles southeast of Castle Rock. | named_feature | Castlewood Canyon State Park | feature_absent_from_index |  | needs_information |
| H120 | Lost Man Creek, west of Indepdence Pass. | named_feature |  |  |  | invalid_extraction |
| H121 | West Mesa County, near Loma. | named_feature | Loma | candidates_found | Loma (Populated Place, Mesa, exact_official) | needs_information |
| H123 | Northeast of John Martin Reservoir; along two-track service road. | direction_only | John Martin Reservoir | candidates_found | John Martin Reservoir (Reservoir, Bent, exact_official) | needs_information |
| H124 | Pike-San Isabel National Forest, Pikes Peak, Boemer Creek headwaters, Windy Point, ca. 0.75 SW of Sachett Mt. Below saddle between uppermost knob and knob 11848 at head of 1st ridge W of Windy Point ridge below cog railway. | distance_and_direction | Sachett Mt. | candidates_found | Sachett Mountain (Summit, El Paso, core_official) | needs_information |
| H125 | Rocky Mountain National Park. 1.5 mi W of Grand Lake Village. | distance_and_direction | Grand Lake Village | feature_absent_from_index |  | needs_information |
| H126 | Fraser Experimental Forest: upper basin of St. Louis Lake trail. | route_relative | St. Louis Lake | candidates_found | Saint Louis Lake (Lake, Grand, fuzzy_official) | unsupported |
| H127 | Gore Range, Eagles Nest Wilderness Area, central Colorado. Alpine basin west of Booth Lake. | named_feature | Booth Lake | candidates_found | Booth Lake (Lake, Eagle, exact_official) | needs_information |
| H128 | One half mile south of Willow Creek Pass, along small drainage on east side of highway. | distance_and_direction |  |  |  | invalid_extraction |
| H129 | One-half mile above Gothic. | distance_only |  |  |  | invalid_extraction |
| H130 | Between Buford and Trappers Lake. | between_features |  |  |  | invalid_extraction |
| H132 | Gunnison National Forest. Saddle S of Italian Mtn. | named_feature | Gunnison National Forest | feature_absent_from_index |  | needs_information |
| H133 | Adventive along right-of-way of Boulder-Denver Toll Road just east of Superior. | route_relative | Superior | candidates_found | Superior (Populated Place, Boulder, exact_official) | unsupported |
| H134 | Tin Cup Ridge. East base of the hogback locally called Tin Cup Rudge, the northward extension of Dinosaur Rudge into Golden, 6.4 km. south southeast of the GNIS location of Golden. | named_feature | Tin Cup Ridge | feature_absent_from_index |  | needs_information |
| H135 | Upper part of Wheeler Basin. | named_feature | Wheeler Basin | candidates_found | Wheeler Basin (Basin, Grand, exact_official) | needs_information |
| H136 | 9 miles E of Rand, North Park; drainage gully on hillside below road. | distance_and_direction | Rand | candidates_found | Rand (Populated Place, Jackson, exact_official) | needs_information |
| H137 | Rist Canyon, 5 miles W of Bellevue, 10 miles N of Fort Collins. | named_feature | Rist Canyon | candidates_found | Rist Canyon (Valley, Larimer, exact_official) | needs_information |
| H139 | Apex Park. East-central Apex Park, part-way up the initial Rocky Mountain Front Range scarp, along a social trail in a small canyon, 5.21 km. south of the GNIS location of Golden. | named_feature | Apex Park | feature_absent_from_index |  | needs_information |
| H140 | Turkey Creek side canyon. Geneva Glen Camp. | named_feature | Turkey Creek | candidates_found | Turkey Creek (Stream, Jefferson, exact_official) | needs_information |
