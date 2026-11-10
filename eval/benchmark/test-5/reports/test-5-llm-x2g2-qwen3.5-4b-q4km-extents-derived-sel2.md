# test-5: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark-5/1`

> System output only. Correctness needs Codex's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 55 · `named_feature` 42 · `route_relative` 9 · `orthogonal_offsets` 9 · `itinerary` 4 · `between_features` 1

**retrieval**: `candidates_found` 70 · `feature_absent_from_index` 36 · `None` 14

**proposal**: `needs_information` 76 · `computed` 16 · `unsupported` 14 · `invalid_extraction` 14

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| S001 | Gunnison Gorge National Conservation Area, 1.3 mi east of Peach Valley Road along the Bobcat Trail access road near the intersection with but along Sidewinder Trail. | route_relative | Peach Valley Road | feature_absent_from_index |  | unsupported |
| S002 | Along road to Kossler's Lake, ca. 5 mi. W of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| S003 | Roosevelt National Forest: Front Range: Indian Peaks Wilderness: Saint Vrain Mountain Trail, ca 18 air mi NW of Boulder; ca 7 air mi NW of Ward. | distance_and_direction |  |  |  | invalid_extraction |
| S004 | Along the road to Poverty Mesa and Sheep Knob, 3.0 miles north of U.S. Highway 50, 13 air miles east of Montrose. | itinerary |  |  |  | invalid_extraction |
| S005 | On bank above road; Sunshine Canyon, ca. 2.5 mi. w. of Boulder. | named_feature | Sunshine Canyon | candidates_found | Sunshine Canyon (Valley, Boulder, exact_official) | needs_information |
| S006 | White River National Forest; along the Piney River, 2 miles downstream of Piney Lake. | route_relative | Piney Lake | candidates_found | Piney Lake (Lake, Eagle, exact_official) | unsupported |
| S007 | West Creek, 5 mi. NE of Gateway. | distance_and_direction | Gateway | candidates_found | Gateway (Populated Place, Mesa, exact_official) | needs_information |
| S008 | The Rocky Flats Site, 7 mi S of Boulder. Flats directly N of plant site. | named_feature | The Rocky Flats Site | feature_absent_from_index |  | needs_information |
| S009 | Rocky Flats Site; 7 mi S of Boulder. Ravine of northwest corner. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| S010 | San Juan Nat'l Forest, La Plata Mts., ca. 1 mi N of US hwy 160 on Madden Park rd. | route_relative | US hwy 160 | feature_absent_from_index |  | unsupported |
| S011 | Flat Tops/White River Plateau: Hanging Lake trail, ca 8 air mi ENE of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | needs_information |
| S012 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Sangre de Cristo Range: Forbes Trinchera Ranch: above Placer Creek, ca 1 mi N of Russell on U.S. Hwy 160. | route_relative | Russell | candidates_found | Russell (Populated Place, Costilla, exact_official) | unsupported |
| S013 | Northern Gunnison Basin: Forest Hill Mountain, ca 6 air mi WNW of Taylor Park Reservoir. | distance_and_direction | Taylor Park Reservoir | candidates_found | Taylor Park Reservoir (Reservoir, Gunnison, exact_official) | needs_information |
| S014 | Region of the Mesa de Maya. Long's Canyon, two miles south of western end of Mesa de Maya. | distance_and_direction | Mesa de Maya | candidates_found | Mesa de Maya (Summit, Las Animas, exact_official) | needs_information |
| S015 | Rocky Flats Site, 7 miles south of Boulder. In upper Rock Creek. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| S016 | North-central Colorado: Medicine Bow Mountains: Jack Creek and vicinity, 0.5 air mi SW of Calamity Pass, ca 6 air mi S of Gould. | distance_and_direction | Calamity Pass | candidates_found | Calamity Pass (Gap, Jackson, exact_official) | needs_information |
| S017 | Flat Tops/White River Plateau: Coulter Mesa Road, ca 15 air mi NNE of Rifle. | distance_and_direction | Rifle | candidates_found | Rifle (Populated Place, Garfield, exact_official) | computed |
| S018 | Sangre de Cristo Wilderness, Rio Grande National Forest, South Zapata Trail; ca 20 mi. NE of Alamosa; W of South Zapata Lake. | orthogonal_offsets |  |  |  | invalid_extraction |
| S019 | Gently sloping north slope of Haystack Butte, 12 mi. n.e. of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| S020 | Rocky Flats Site, 7 mi. S of Boulder on Rocky Flats pediment; in ravine in NW corner east of the farm. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| S021 | San Isabel National Forest, Sangre de Cristo Wilderness, ca. 6 mi. SW of Westcliffe. Lower Venable Creek, just north of Alvarado campground. | named_feature | Lower Venable Creek | candidates_found | Venable Creek (Stream, Custer, core_official) | computed |
| S022 | Southern Gunnison Basin: San Juan Mountains: along Brush Creek from trailhead to mouth of Canon Infierno, ca 6.9-8.4 air mi W to WNW of Lake City along Forest Trail 461. | itinerary |  |  |  | invalid_extraction |
| S023 | Miners Canyon within the Smith Hollow Hills, fifteen miles WNW of Thatcher. | distance_and_direction | Thatcher | feature_absent_from_index |  | needs_information |
| S024 | Yampa River Basin: Yampa River, 1 mi N of Hwy 40, 2.5 mi NE of Hayden. | distance_and_direction | Hwy 40 | feature_absent_from_index |  | needs_information |
| S025 | Colorado National Monument, 6 mi S of Fruita, near west rim of Park Headquarters mesa. | named_feature | Colorado National Monument | feature_absent_from_index |  | needs_information |
| S026 | Dinosaur National Monument. Conway Draw, ca 0.6 mi ENE of Lodore Ranger Station. | named_feature | Conway Draw | candidates_found | Conway Draw (Valley, Moffat, exact_official) | needs_information |
| S027 | Arapaho National Forest: Front Range: S of Lake Granby along Doe Creek, ca 6.5 air mi ENE of Grandby; ca 15.5 air mi NNW of Fraser. | distance_and_direction | Grandby | candidates_found | Granby (Populated Place, Grand, fuzzy_official) | needs_information |
| S028 | BLM, Big Dominguez Creek at Smith Point, 7 miles southeast of Unaweep Canyon on the Uncompahgre Plateau. | named_feature | Big Dominguez Creek | candidates_found | Big Dominguez Creek (Stream, Mesa, exact_official) | needs_information |
| S029 | Northern Gunnison Basin. Along Beaver Creek, ca 7 air mi WNW of Gunnison. | named_feature | Northern Gunnison Basin | feature_absent_from_index |  | needs_information |
| S030 | Sawatch Range: White River National Forest: Homestake Road, ca 13 air mi S of Dowds Junction and 6 mi W of U.S. Hwy 24. | distance_and_direction | Dowds Junction | candidates_found | Dowds Junction (Populated Place, Eagle, exact_official) | needs_information |
| S031 | Rist Canyon, near top of canyon, 20 miles nw. of Fort Collins. | named_feature | Rist Canyon | candidates_found | Rist Canyon (Valley, Larimer, exact_official) | needs_information |
| S032 | Phantom Canyon, ca. 5 mi. SE of Canyon City, one mile N of canyon mouth, on hillside W of dirt road. | named_feature | Phantom Canyon | candidates_found | Phantom Canyon (Valley, Fremont, exact_official) | needs_information |
| S033 | Arapaho National Forest; upper Bobtail Creek; 0.92 miles due west of Pettingell Peak. | distance_and_direction | Pettingell Peak | candidates_found | Pettingell Peak (Summit, Clear Creek, exact_official) | needs_information |
| S034 | San Juan National Forest; 6 miles SW of Pagosa Springs; just S of radio tower near Oak Brush Hill summit | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| S035 | San Juan Mountains, 4.5 miles NE of Slumgullion Pass. Along Mill Creek. | distance_and_direction | Slumgullion Pass | candidates_found | Slumgullion Pass (Gap, Hinsdale, exact_official) | needs_information |
| S036 | Comanche National Grassland: Holt Canyon, ca 27.5 air mi SSW of Springfield. | distance_and_direction | Springfield | candidates_found | Springfield (Populated Place, Baca, exact_official) | needs_information |
| S037 | Four-Way Ranch, Black Squirrel Creek, ca. 0.5 mi west of Elbert Road and 0.5 mi north of Latigo Blvd. | orthogonal_offsets |  |  |  | invalid_extraction |
| S038 | Summit of Cottonwood Pass; ¼ mi from roadcut. | named_feature | Cottonwood Pass | candidates_found | Cottonwood Pass (Gap, Chaffee, exact_official) | needs_information |
| S039 | Lost Creek Area, Tarryall Mtns., 80km (50mi) southwest of Denver and 80km northwest of Colo. Springs. Near stream draining Lake Park. | named_feature | Lost Creek Area | feature_absent_from_index |  | needs_information |
| S040 | Along trail to Hayden Pass; San Isabel National Forest; ca. 5 mi. s.w. of Coaldale. | itinerary |  |  |  | invalid_extraction |
| S041 | Bend of trail halfway between Shipler cabins and Lulu City, 13 mi N of Grand Lake. | between_features | Shipler cabins | feature_absent_from_index |  | unsupported |
| S042 | Near Chamber of Commerce information station, 1 mi. W of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | needs_information |
| S043 | Central Colorado: Sawatch Range, East Slope Continental Divide: at Hancock Lake at the end of Forest Road 295, north and west side of lake, ca 7 air mi S of St. Elmo. | distance_and_direction | St. Elmo | feature_absent_from_index |  | needs_information |
| S044 | Comanche National Grassland: along Purgatoire River, ca 29 air mi SSW of La Junta. | distance_and_direction | La Junta | candidates_found | Cordova Plaza (Populated Place, Las Animas, exact_variant) | needs_information |
| S045 | Wet ditch on roadside near Andrews' Nursery; 1 mi. s. of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| S046 | Lost Creek Area, Tarryall Mts., 80km (50mi.) southwest of Denver and 80km northwest of Colo. Springs. McCurdy Mountain. | named_feature | Lost Creek Area | feature_absent_from_index |  | needs_information |
| S047 | Rocky Flats Site, 7 mi. S of Boulder, on Rocky Flats Pediment. W boundary, on S-facing slope just S of road. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| S048 | Beaver Creek State Wildlife Area, ca 12 air mi NE of Canon City, W of Colo. Hwy 115. Beaver Creek. | distance_and_direction | Canon City | candidates_found | Cañon City (Populated Place, Fremont, exact_official) | computed |
| S049 | Sangre de Cristo Range, San Isabel Natl. Forest, vicinity of Hayden Creek C.G., ca. 20 air mi. NW of Westcliffe. Along S. Prong of Hayden Creek. | distance_and_direction | Westcliffe | candidates_found | Westcliffe (Populated Place, Custer, exact_official) | needs_information |
| S050 | White River National Forest: near the headwaters of Willow Creek, 2 mi N of Spruce Mountain and ca 22 air mi S of New Castle. | distance_and_direction | Spruce Mountain | candidates_found | Spruce Mountain (Summit, Delta, exact_official) | needs_information |
| S051 | Geneva Iron Fen Natural Area, approx. 15 miles SW of Georgetown off FS Rd. 119 near Geneva and Josephine creeks; south side of Josephine Creek Iron Fen; | named_feature | Geneva Iron Fen Natural Area | feature_absent_from_index |  | needs_information |
| S052 | Upper part of Phantom Canyon, about 6 miles south of Victor. | distance_and_direction | Victor | candidates_found | Victor (Populated Place, Teller, exact_official) | computed |
| S053 | NNW of Twin Lakes, 1 mi. SE of Conundrum Pass; saddle ridge area. | orthogonal_offsets |  |  |  | invalid_extraction |
| S054 | White River National Forest, Holy Cross Wilderness, along West Cross Creek, 1/3 mile upstream of confluence with Cross Creek. | route_relative | confluence with Cross Creek | feature_absent_from_index |  | unsupported |
| S055 | Arapaho National Forest: Front Range: westside of ridge between Cub and Maxwell creeks off Black Mountain Drive, ca 5.5-6 air mi SW of Evergreen. | distance_and_direction |  |  |  | invalid_extraction |
| S056 | Along Tarryall Creek, 13.8 miles northwest of U.S. 24 on Colo. 77. | route_relative | U.S. 24 | feature_absent_from_index |  | unsupported |
| S057 | Upper Dolores River Drainage and Adjacent Areas: upper east end of Disappointment Valley, County Road D.00, Warden Draw, ca 26 air mi. N of Dolores. | orthogonal_offsets | Dolores | candidates_found | Dolores (Populated Place, Montezuma, exact_official) | unsupported |
| S058 | Gulch above north side of San Juan River opposite Four Corners, ca 22 mi SW of Towaoc. | distance_and_direction | Towaoc | candidates_found | Towaoc (Populated Place, Montezuma, exact_official) | needs_information |
| S059 | Southern Gunnison Basin: west side of Wolf Creek, ca 2 air mi NW of summit of Nine Mile Hill; ca 4.2 air mi SSW of Blaine Rock; ca 11.5 air mi SE of Sapinero. | distance_and_direction | summit of Nine Mile Hill | feature_absent_from_index |  | needs_information |
| S060 | Dinosaur National Monument. Head of Little Joe Draw, ca 0.2 mi SW of Zenobia Peak. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| S061 | Along south shore of Baseline Lake, 3 miles east of Boulder. | named_feature | Baseline Lake | candidates_found | Base Line Reservoir (Reservoir, Boulder, fuzzy_variant) | computed |
| S062 | Breaks of North Fork, Tabeguache Creek, 1½ mi W of Smokehouse Campground. Uncompahgre Plateau. | distance_and_direction | Smokehouse Campground | feature_absent_from_index |  | needs_information |
| S063 | Top of Langridge Dyke, 1 mi. E of Gross Reservoir. | distance_and_direction | Gross Reservoir | candidates_found | Gross Reservoir (Reservoir, Boulder, exact_official) | computed |
| S064 | North branch of Spring Brook, 1 mile south of Eldorado Springs. Outer foothills of the Front Range. | named_feature | North branch of Spring Brook | feature_absent_from_index |  | needs_information |
| S065 | Escalante Canyon at Cottonwood Spgs, ca 12 mi W of Hwy 50. | named_feature | Escalante Canyon | feature_absent_from_index |  | needs_information |
| S066 | San Juan National Forest; Stony Pass, ca 7 mi NE of Silverton. | named_feature | Stony Pass | candidates_found | Stony Pass (Gap, San Juan, exact_official) | needs_information |
| S067 | Colorado School of Mines Survey Field. Southernmost edge of the Survey Field, adjacent to Stonebridge HOA lands, high plains at the base of the Rocky Mountain Front Range, 3.26 km. south of the GNIS location of Golden. | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| S068 | Douglas Mountain, 45 mi NW of Maybell, Dutch Oven Spring just below Whisky Springs Ranch. | named_feature | Douglas Mountain | candidates_found | Douglas Mountain (Summit, Jefferson, exact_official) | needs_information |
| S069 | San Juan National Forest; ~2 miles N of Chromo; NW slope of Confar Hill, ~3/4 mile W of U.S. Route 84 | orthogonal_offsets |  |  |  | invalid_extraction |
| S070 | Roosevelt National Forest, Comanche Peak Wilderness, 1.5 miles northeast of Big South Trailhead. Un-named ponds in wide level basin. | distance_and_direction | Big South Trailhead | feature_absent_from_index |  | needs_information |
| S071 | Sand Arroyo, 2 miles s. of Walsh. | distance_and_direction | Walsh | candidates_found | Walsh (Populated Place, Baca, exact_official) | computed |
| S072 | Central Colorado: Sawatch Range, East Slope Continental Divide: Mount Massive and North Halfmoon Lakes Trail junction, ca 13 air mi SE of Leadville. | distance_and_direction | Leadville | candidates_found | Leadville (Populated Place, Lake, exact_official) | computed |
| S073 | Northern Gunnison Basin: West Elk Wilderness: The Castles, ca 11.5 air mi SSW of Kebler Pass. | distance_and_direction | Kebler Pass | candidates_found | Kebler Pass (Gap, Gunnison, exact_official) | needs_information |
| S074 | Culebra Range, 30 air miles west of Trinidad, Bar NI Ranch. Abbot Creek drainage, ca. 4.0 miles above ranch hdqtrs. | distance_and_direction | Trinidad | candidates_found | Trinidad (Populated Place, Las Animas, exact_official) | needs_information |
| S075 | Private ranch near Trujillo, ca. 16 miles S of Pagosa Springs, on uplands above Montezuma Creek. | named_feature | Trujillo | candidates_found | Trujillo (Populated Place, Archuleta, exact_official) | needs_information |
| S076 | Lippincott Property. Northernmost Jefferson County, parcel jointly owned by City of Boulder and Jefferson County Open Space, approximate centroid of parcel, 22 km. north northwest of the GNIS location of Golden. | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| S077 | Buckhorn Canyon northwest of Loveland; 1.4 miles north of the cattle-guard marking the south edge of Roosevelt National Forest. | named_feature | Buckhorn Canyon | feature_absent_from_index |  | needs_information |
| S078 | Colorado River Valley: mesas on either side of Little Horsethief Creek, S of Sunnyside Road, ca 3 air mi NW of Horsethief Mountain and ca 2 air mi SE of De Beque. | orthogonal_offsets |  |  |  | invalid_extraction |
| S079 | Northern Gunnison Basin: Taylor River, ca 0.5 air mi E of Almont. | distance_and_direction | Almont | candidates_found | Almont (Populated Place, Gunnison, exact_official) | needs_information |
| S080 | Northern Gunnison Basin: southeast side of Mount Baldy, ca 3.5 air mi NW of Gothic. | distance_and_direction | Gothic | candidates_found | Gothic (Populated Place, Gunnison, exact_official) | needs_information |
| S081 | Flat Tops/ White River Plateau: slopes of Colorado River Canyon, ca 15 air mi NNW of Eagle, 1.5 road mi SW of Burns. | orthogonal_offsets |  |  |  | invalid_extraction |
| S082 | Gunnison Basin; Lower Quartz Creek, 7 miles N of Parlin. | named_feature | Lower Quartz Creek | candidates_found | Quartz Creek (Stream, Gunnison, core_official) | needs_information |
| S083 | Wet Mountains. Rattlesnake Gulch, ca. 1½ mi. NE of McKenzie Junction, N side of Highway 96. | named_feature | Rattlesnake Gulch | candidates_found | Rattlesnake Gulch (Valley, Custer, exact_official) | needs_information |
| S084 | Dinosaur National Monument. N side of meander of Yampa River, 0.75 mi NW of Katy's Nipple. | orthogonal_offsets | Katy's Nipple | candidates_found | Katys Nipple (Cliff, Moffat, exact_official) | unsupported |
| S085 | Arikaree River, 11 miles northwest of Idalia on west side of DD Rd. East side of drainage; | named_feature | Arikaree River | candidates_found | Arikaree River (Stream, Dundy, exact_official) | needs_information |
| S086 | Unaweap Canyon, 1 mi E of Narrows on West Cr, and in First Canyon (Costo Draw) E of Gateway. | named_feature | Unaweap Canyon | candidates_found | Unaweep Canyon (Valley, Mesa, fuzzy_official) | needs_information |
| S087 | Pike N. F.; Hoosier Ridge, about 2 mi E of Hoosier Pass; on talus below black basalt outcrop on S side of ridge above headwaters of Beaver Creek. | named_feature | Pike N. F. | feature_absent_from_index |  | needs_information |
| S088 | Western State College, 1/4 mile on dirt road back of girls' dorms. | route_relative | Western State College | feature_absent_from_index |  | unsupported |
| S089 | San Isabel National Forest, Sangre de Cristo Wilderness, ca. 6 mi. SW of Westcliffe. Lower Venable Creek north of Alvarado campground. | named_feature | Lower Venable Creek | candidates_found | Venable Creek (Stream, Custer, core_official) | computed |
| S090 | Central Colorado: Mosquito Range, East Slope Continental Divide: from Kite Lake to summit of Mt. Democrat, ca 13 air mi NE of Leadville. | itinerary | Kite Lake | candidates_found | Kite Lake (Lake, Park, exact_official) | unsupported |
| S091 | South-facing canyon wall of Clear Creek Canyon, 1 mi. E. of junction of Central City road. | distance_and_direction | junction of Central City road | feature_absent_from_index |  | needs_information |
| S092 | Sangre de Cristo Range, Rio Grande National Forest, Dorsey Creek Rd, ca 3 mi E of Hwy 285. | distance_and_direction | Hwy 285 | feature_absent_from_index |  | needs_information |
| S093 | Romley, an old station on Colo & Southern RR, 3 mi SW of St. Elmo. San Isabel National Forest. Below old mine buildings and tailing dump. | named_feature | Romley | candidates_found | Romley (historical) (Populated Place, Chaffee, exact_official) | needs_information |
| S094 | Vicinity of Timberline Van, Niwot Ridge, ca. 8 miles north of Nederland. Institute of Arctic and Alpine Research. | distance_and_direction | Nederland | candidates_found | Nederland (Populated Place, Boulder, exact_official) | needs_information |
| S095 | Taylor Mountain, ca. 3.5 miles north of Garfield, San Isabel National Forest. Northeast flank of Taylor Mountain. | named_feature | Taylor Mountain | candidates_found | Taylor Mountain (Summit, Chaffee, exact_official) | needs_information |
| S096 | Rocky Mountain National Park. Grand Lake Entrance, 1 mi N of Grand Lake. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| S097 | Wagon Wheel Gap, 2.0 mi WNW of the village of Wagon Wheel Gap. | named_feature | Wagon Wheel Gap | candidates_found | Wagon Wheel Gap (Gap, Mineral, exact_official) | needs_information |
| S098 | Road to Eldora, 2.1 miles west of Peak-to-Peak Highway. | route_relative | Peak-to-Peak Highway | feature_absent_from_index |  | unsupported |
| S099 | Access road to Pine Creek Visitors Center, ca. 0.5 mi from US Hwy 50. | distance_and_direction |  |  |  | invalid_extraction |
| S100 | Unaweep Canyon, 7 mi of Gateway. | distance_and_direction | Gateway | candidates_found | Gateway (Populated Place, Mesa, exact_official) | needs_information |
| S101 | Ravine of Sugar Creek, 1-2 mi E of the Platte River, Pike National Forest. | named_feature | Sugar Creek | candidates_found | Sugar Creek (Stream, Douglas, exact_official) | needs_information |
| S102 | Fairview Peak Basin, ca. 5.6 miles southwest of intersect of Halls Gulch road and Cumberland Pass road, Gunnison National Forest. | distance_and_direction | intersect of Halls Gulch road and Cumberland Pass road | feature_absent_from_index |  | needs_information |
| S103 | At base of Mount Garfield, 5 mi N of Clifton. In gullies between the hills. | named_feature | Mount Garfield | candidates_found | Mount Garfield (Summit, Mesa, exact_official) | needs_information |
| S104 | Pike National Forest, Lost Creek Wilderness Area, East Lost Park Natural Area, ca. 1.25 miles along trail SE of Lost Park Camprground. | route_relative | Lost Park Camprground | feature_absent_from_index |  | unsupported |
| S105 | SE slope of Lead Mountain, below Turquoise Tarn, 14 mi. N of Grand Lake. | named_feature | Lead Mountain | candidates_found | Lead Mountain (Summit, Grand, exact_official) | needs_information |
| S106 | Deadman Gulch. Along Deadman Gulch (Kinney Run), between US Highway 6 and Eagle Ridge Drive, collected at the edge of the concrete of the retention pond dam, 3.18 km. south of the GNIS location of Golden. | named_feature | Deadman Gulch | candidates_found | Deadman Gulch (Valley, Jefferson, exact_official) | needs_information |
| S107 | Northern Gunnison Basin: southeast side of Snodgrass Mountain, ca. 4 air miles N of Crested Butte. | distance_and_direction | Crested Butte | candidates_found | Crested Butte (Summit, Gunnison, exact_official) | needs_information |
| S108 | Bear Creek Canyon, about 0.50 miles NW of intersection with Gold Camp Road.; 38.81453 -104.89954 | distance_and_direction | intersection with Gold Camp Road | feature_absent_from_index |  | needs_information |
| S109 | Kinney Run. West side of Kinney Run nearing the houses of Stonebridge HOA, between Deadman Gulch and Tripp Ranch, 2.42 km. south of the GNIS location of Golden. | named_feature | Kinney Run | feature_absent_from_index |  | needs_information |
| S110 | Independence Mountain, 8.5 air miles NW of Cowdrey. | distance_and_direction | Cowdrey | candidates_found | Cowdrey (Populated Place, Jackson, exact_official) | needs_information |
| S111 | Ute Creek, 4 mi from Ft. Garland. | distance_and_direction |  |  |  | invalid_extraction |
| S112 | Northern Gunnison Basin: Matchless Mountain, ca 2.5 air mi W of Taylor Park Reservoir. | distance_and_direction | Taylor Park Reservoir | candidates_found | Taylor Park Reservoir (Reservoir, Gunnison, exact_official) | needs_information |
| S113 | Red Top Ranch, approx. 25 miles SE of City of Pueblo, approx. 3 miles S of Red Top Road. | distance_and_direction | City of Pueblo | candidates_found | City of Pueblo (Civil, Pueblo, exact_official) | computed |
| S114 | Wet Mountains, San Isabel National Forest. Squirrel Creek Trail, ca. 12 mi. S of Wetmore. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| S115 | Barrow, 5 miles W of Gunnison. | distance_and_direction | Gunnison | candidates_found | Gunnison (Populated Place, Gunnison, exact_official) | computed |
| S116 | Grape Creek near Temple Canyon City Park, approx. 6 miles SW of Canon City. | named_feature | Grape Creek | candidates_found | Grape Creek (Stream, Fremont, exact_official) | computed |
| S117 | Rio Grande National Forest; ~12 miles E of Chromo; NE face of Chama Peak | named_feature | Chama Peak | candidates_found | Chama Peak (Summit, Archuleta, exact_official) | needs_information |
| S118 | Park Range, Routt National Forest; kettle lake between Shafer and Goose creeks, 0.25 mi N of Frying Pan Trail. | orthogonal_offsets | Frying Pan Trail | feature_absent_from_index |  | unsupported |
| S119 | Flat Tops/White River Plateau: Flat Tops Wilderness: Mirror Lake Trail, ca 30 air mi E of Meeker; ca 6 air mi NW of Trappers Lake.; 40.0484963 -107.3256534 | distance_and_direction |  |  |  | invalid_extraction |
| S120 | High Creek Fen, east edge, 10 mi S of Fairplay, South Park. | distance_and_direction | Fairplay | candidates_found | Fairplay (Populated Place, Park, exact_official) | computed |
