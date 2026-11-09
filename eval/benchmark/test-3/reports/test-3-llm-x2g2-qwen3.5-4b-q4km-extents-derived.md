# test-3: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark-3/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 69 · `named_feature` 28 · `route_relative` 10 · `itinerary` 7 · `between_features` 3 · `orthogonal_offsets` 3

**retrieval**: `candidates_found` 76 · `feature_absent_from_index` 37 · `None` 7

**proposal**: `needs_information` 50 · `computed` 43 · `unsupported` 20 · `invalid_extraction` 7

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| P001 | Vermejo Park Ranch: in Colorow Canyon from the Colorado state line NE to mouth of Bear Canyon; 14 air mi SW of Trinidad. | itinerary |  |  |  | invalid_extraction |
| P002 | Golden; Colorado School of Mines Survey Field: Base of the Rocky Mountain Front Range, northeast-facing slope, above an unnamed stream in the south end of the Survey Field, 2.51 km. south of the GNIS location of Golden. | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| P003 | North Italian Peak; ca. 10 mi. n.e. of Crested Butte. | distance_and_direction | Crested Butte | candidates_found | Crested Butte (Summit, Gunnison, exact_official) | needs_information |
| P004 | Flat Tops Wilderness, White River National Forest, along Middle Ford Derby Creek, 2 miles upstream of McMillan Lake. | route_relative | McMillan Lake | candidates_found | McMillan Lake (Lake, Garfield, exact_official) | unsupported |
| P005 | Dinosaur National Monument. Bower Draw, ca ½ mi N of Yampa River. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| P006 | Golden; Colorado School of Mines Survey Field. High plains at the base of the Rocky Mountain Front Range, 2.4 km. south southwest of the GNIS location of Golden | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| P007 | Northern Gunnison Basin: Collegiate Peaks Wilderness: on ridge heading toward Continental Divide, ca 9 air mi N of Taylor Park Reservoir. | distance_and_direction | Taylor Park Reservoir | candidates_found | Taylor Park Reservoir (Reservoir, Gunnison, exact_official) | computed |
| P008 | Arapaho National Forest, along Snake River, 1 mile upstream of confluence with Deer Creek. | route_relative | confluence with Deer Creek | feature_absent_from_index |  | unsupported |
| P009 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity: Sangre de Cristo Range: Porters Gulch, ca 1 air mi upstream from confluence with Howard Creek. | route_relative | confluence with Howard Creek | feature_absent_from_index |  | unsupported |
| P010 | Chambers place, 2 miles S. of Broomfield on Wadsworth. On hillside above southernmost bend of creek. | distance_and_direction | Broomfield | candidates_found | Broomfield (Populated Place, Broomfield, exact_official) | computed |
| P011 | Fraser Creek in Flat Tops Wilderness, 2.5 mi. SE of Trappers Lake. | named_feature | Fraser Creek | candidates_found | Fraser Creek (Stream, Garfield, exact_official) | computed |
| P012 | North side of Cortez, 1.3 mi N of Jct. Hwys 160 and 145, then 0.4 mi W on Alamosa St. | itinerary |  |  |  | invalid_extraction |
| P013 | Catamount Ranch, ¼ mi. up drainage SE of easternmost pond. | route_relative | easternmost pond | feature_absent_from_index |  | unsupported |
| P014 | Golden; North Table Mountain Park. Southern portion of North Table Mountain just above a break in slope above an unnamed canyon draining into Clear Creek, 1.85 km. north northeast of the GNIS location of Golden.; 39.7716 -105.215 | named_feature |  |  |  | invalid_extraction |
| P015 | San Juan National Forest; ~12 miles SE of Pagosa Springs; NE side of Buckles Lake; away from margins of lake | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| P016 | Dinosaur National Monument. Upper end, Sand Canyon, ca 0.5 mi SW of Pearl Park. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| P017 | San Isabel National Forest; ~17 miles SW of La Veta, ~1/3 mile S of Trinchera Peak; E side of Continental Divide. | distance_and_direction | La Veta | candidates_found | La Veta (Populated Place, Huerfano, exact_official) | computed |
| P018 | Park Range; ca 14.5 air mi S of Steamboat Springs, along Service Creek, ca 1.5 air mi above the Yampa River. | itinerary | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | unsupported |
| P019 | Rocky Mountain National Park. Pasture south of Sun Valley Ranch, 2.5 mi NW of Grand Lake. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
| P020 | Baseline Lake, 3 mi. e. of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| P021 | Vicinity Castle Rock; Middle Boulder Creek Canyon; 1.5 miles northeast of Tungsten. | distance_and_direction | Tungsten | candidates_found | Tungsten (historical) (Populated Place, Boulder, exact_official) | needs_information |
| P022 | Ridge between Farris Creek and East River, 4 mi SE of Crested Butte-Gunnison highway. | between_features | Farris Creek | candidates_found | Farris Creek (Stream, Gunnison, exact_official) | unsupported |
| P023 | Lone Mesa State Park, 6 miles north of southern entrance at FR 514. | route_relative | southern entrance | feature_absent_from_index |  | unsupported |
| P024 | Shellhammer Ridge, 0.9 mi NNE of La Boca. | distance_and_direction | La Boca | candidates_found | La Boca (Populated Place, La Plata, exact_official) | needs_information |
| P025 | Swale along Tomichi Creek, 7 mi E of Gunnison. | distance_and_direction | Gunnison | candidates_found | Gunnison (Populated Place, Gunnison, exact_official) | computed |
| P026 | Tundra slopes, east face of Cameron Mountain, Medicine Bow Range, 2.5 mi. N.W. of Chambers Lake. | distance_and_direction | Chambers Lake | candidates_found | Chambers Lake (Reservoir, Larimer, exact_official) | computed |
| P027 | Beside road from Branson to Trinchera, 2.9 mi. (by road) east of Trinchera. | distance_and_direction | Trinchera | candidates_found | Trinchera (Populated Place, Las Animas, exact_official) | needs_information |
| P028 | San Juan National Forest; ~4 miles NW of Chromo; ~2 miles NW of Mesa Cortado | distance_and_direction | Chromo | candidates_found | Chromo (Populated Place, Archuleta, exact_official) | needs_information |
| P029 | Shoulder of peak; 0.5 miles southwest of Cottonwood Pass. | distance_and_direction | Cottonwood Pass | candidates_found | Cottonwood Pass (Gap, Chaffee, exact_official) | needs_information |
| P030 | Moist meadow just N of Grand Lake entrance station, 1 mi. N of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | computed |
| P031 | North-central Colorado: Park Range: head of Harrison Creek, ca 2 air mi E of Walton Peak, ca 3 air mi SW of Rabbit Ears Pass; ca 13 air mi SE of Steamboat Springs. | distance_and_direction | Walton Peak | candidates_found | Walton Peak (Summit, Routt, exact_official) | needs_information |
| P032 | Dolores River, 11 mi N of Dove Cr. pumping station, NE of Dove Creek. | named_feature | Dolores River | candidates_found | Dolores River (Stream, Grand, exact_official) | needs_information |
| P033 | Flat Tops/White River Plateau: Flat Tops Wilderness: Marvine Creek, ca 27 air mi E of Meeker. Also SEC7. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | computed |
| P034 | Junction of Sand and Gallinas Canyons, trib. to Cimarron River, 27 mi. s. of Pritchett. | between_features | Junction of Sand and Gallinas Canyons | feature_absent_from_index |  | unsupported |
| P035 | Flat Tops/White River Plateau: between Killarny Reservoir and old Jeep trail on Little Flat Tops, ca 45 air mi ENE of Meeker; ca 9.5 air mi W of Yampa. | orthogonal_offsets | Killarny Reservoir | candidates_found | Killarney Reservoir (Reservoir, Rio Blanco, fuzzy_official) | unsupported |
| P036 | Southern Gunnison Basin: between Stubbs Gulch and Gold Basin Creek just N of Saguache County, ca 8.3 air mi SSE of Gunnison. | between_features | Stubbs Gulch | candidates_found | Stubbs Gulch (Valley, Gunnison, exact_official) | unsupported |
| P037 | North Halfmoon Trail, 2.8 mi NW of the Mt Elbert/Massive trailhead at Elbert Creek campground. | distance_and_direction | Mt Elbert/Massive trailhead at Elbert Creek campground | feature_absent_from_index |  | needs_information |
| P038 | Pinto Ranch, approximately 7 air miles northwest of Kremmling. | distance_and_direction | Kremmling | candidates_found | Kremmling (Populated Place, Grand, exact_official) | computed |
| P039 | Eagle Rock Ranch, approx. 1.5 miles S of the Wyoming State Line, near Simpson Creek in the Chalk Bluffs. Bluffs south of Geary Creek. | named_feature | Eagle Rock Ranch | feature_absent_from_index |  | needs_information |
| P040 | In Sacramento Gulch, 8 miles west of Fairplay, along Sacramento Creek. | named_feature | Sacramento Gulch | feature_absent_from_index |  | needs_information |
| P041 | San Juan National Forest: Chicago Basin. Animas River drainage, ca 18 mi SE of Silverton. West of Twin Thumbs Pass. | distance_and_direction | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | computed |
| P042 | Punkin Center, 14 mi S along CO 71. Shortgrass prairie on E side of hwy and along County Rd K. | route_relative | CO 71 | feature_absent_from_index |  | unsupported |
| P043 | Comanche National Grassland; Rourke Rd.; 0.8 mi. N. of David Canyon Rd. | distance_and_direction | David Canyon Rd. | feature_absent_from_index |  | needs_information |
| P044 | White Rocks. Boulder Creek, 8 mi. NE of Boulder. | named_feature | White Rocks | candidates_found | White Rock (Cliff, Rio Blanco, fuzzy_official) | needs_information |
| P045 | Lippincott Ranch. Southwestern corner of the ranch, at base of railroad embankment, 22.3 km. north northwest of the GNIS location of Golden. | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| P046 | Hinman Park Campground, Routt Nat. For., 27 mi. n.e. of Steamboat Springs. | distance_and_direction | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | computed |
| P047 | Jackson Gulch, 1 mi SW of Jackson Reservoir. Wetland along Mesa Verde Park water line. | distance_and_direction | Jackson Reservoir | candidates_found | Jackson Reservoir (Reservoir, Jackson, exact_official) | computed |
| P048 | Flat Tops/ White River Plateau: Derby Mesa, ca 18 air mi NNW of Eagle. | distance_and_direction | Eagle | candidates_found | Eagle (Populated Place, Eagle, exact_official) | computed |
| P049 | Turkey Creek Canyon, about 4 miles southwest of Morrison. | distance_and_direction | Morrison | candidates_found | Morrison (Populated Place, Jefferson, exact_official) | computed |
| P050 | Along road 368, above Hardscrabble Creek, ca. 10 mi. SE of Wetmore, 2 mi. above intersection of Rd. 387. | itinerary | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | unsupported |
| P051 | Rocky Flats Site, 7 miles south of Boulder. Church Ditch W of plant site. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| P052 | Orchard Mesa, 1 mi S of Clifton. | distance_and_direction | Clifton | candidates_found | Clifton (Populated Place, Mesa, exact_official) | computed |
| P053 | Flat Tops/White River Plateau: Grand Hogback, ca 9 air mi SSW of Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | computed |
| P054 | Upper Arkansas River Valley. San Isabel Land Protection Trust private ranch, ca. 6.87 air miles southwest of Florence. About a ½ mile south of Chandler Road (Co. Rd 78). Along creek behind buildings. | distance_and_direction | Florence | candidates_found | Florence (Populated Place, Fremont, exact_official) | computed |
| P055 | Bottom of North St. Charles Canyon, ca. 4 mi. ESE of Beulah. | distance_and_direction | Beulah | candidates_found | Beulah (Populated Place, Pueblo, exact_official) | needs_information |
| P056 | County Road 31, along Willow Creek, about 1/4 mi S of its junction with County Road 61, about 1/2 mi S of Site 1.; 38.44241 -107.057956 | itinerary | County Road 31 | feature_absent_from_index |  | unsupported |
| P057 | NE slope of Douglas Mountain; Whisky Springs Ranch, 6 mi NW of Greystone. | named_feature | Douglas Mountain | candidates_found | Douglas Mountain (Summit, Jefferson, exact_official) | needs_information |
| P058 | Rimrock of Blue Mesa, 6 mi SW of Sapinero on old Lake City 'cut-off' road. | route_relative | Sapinero | candidates_found | Sapinero (Populated Place, Gunnison, exact_official) | unsupported |
| P059 | Abundant on border of pond near Mont Alto, 3 miles west of Gold Hill. | distance_and_direction | Gold Hill | candidates_found | Gold Hill (Populated Place, Boulder, exact_official) | computed |
| P060 | Rocky Flats Plant, 7 mi S of Boulder on Hwy 93, just NE of old land fill, N of industrial area. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| P061 | Cedar Mesas, 25 mi S of La Junta. | distance_and_direction | La Junta | candidates_found | La Junta (Populated Place, Otero, exact_official) | computed |
| P062 | Phantom Canyon Preserve, ca. 25 mi N of Ft. Collins along US Hwy 287; along W side of N. Fork of Cache La Poudre River. Preserve "Reach 1". | named_feature | Phantom Canyon Preserve | feature_absent_from_index |  | needs_information |
| P063 | Battlement Mesa: White River National Forest: creek below Bull Basin between waterfall and USFS boundary, ca 1-2 air mi NNW of Housetop Mountain and ca 7 air mi S of Parachute. | distance_and_direction |  |  |  | invalid_extraction |
| P064 | Northern Gunnison Basin: along Middle Quartz Creek, ca 2 air mi E of Pitkin. | distance_and_direction | Pitkin | candidates_found | Pitkin (Populated Place, Gunnison, exact_official) | computed |
| P065 | Valley below S side of Mt. Sneffels, 10 mi. SW of Ouray. | distance_and_direction | Ouray | candidates_found | Ouray (Populated Place, Ouray, exact_official) | computed |
| P066 | Vermejo Park Ranch: Culebra Range: southwest slope of Upper Glacier Lake; 0.6 air mi E of summit of State Line Peak. | distance_and_direction | State Line Peak | candidates_found | State Line Peak (Summit, Costilla, exact_official) | needs_information |
| P067 | Flat Tops/White River Plateau: Flat Tops Wilderness: slopes above Sheriff Reservoir, ca 13 air mi W of Yampa. | distance_and_direction | Yampa | candidates_found | Yampa (Populated Place, Routt, exact_official) | computed |
| P068 | Sugarloaf Mountain, ca. ten miles west of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| P069 | White River National Forest, 4.5 miles west-northwest of Sweetwater Lake, on Dry Sweetwater Creek near junction of Sweetwater Creek. | named_feature | White River National Forest | feature_absent_from_index |  | needs_information |
| P070 | Lower John Brown Canyon; 3.6 mi. S. of Colo. 141, by CR 4.4. | distance_and_direction | Colo. 141 | feature_absent_from_index |  | needs_information |
| P071 | Pond margin, Tomkey fish farm, Northeast pond, 3 miles east of Weldona. | distance_and_direction | Weldona | candidates_found | Weldona (Populated Place, Morgan, exact_official) | computed |
| P072 | Phantom Canyon Preserve, ca. 25 mi N of Ft. Collins along US Hwy 287; along an un-named stream ca. 0.5 mi from preserve gate at highway. | named_feature | Phantom Canyon Preserve | feature_absent_from_index |  | needs_information |
| P073 | Platte Gulch to Wheeler Lake, ca. 5 mi. NW of Alma. | distance_and_direction | Alma | candidates_found | Alma (Populated Place, Park, exact_official) | computed |
| P074 | Lower Roaring Fork Valley; 1-2 mi E of Aspen. | named_feature | Lower Roaring Fork Valley | feature_absent_from_index |  | needs_information |
| P075 | Lime Rd, ca 1 mile NE of intersection with I-25. | route_relative | intersection with I-25 | feature_absent_from_index |  | unsupported |
| P076 | Beech Open Space, 6 mi N of Boulder. Just south of Neva Road, north of the picnic shelter. | named_feature | Beech Open Space | feature_absent_from_index |  | needs_information |
| P077 | Rio Grande National Forest; ~14 miles ENE of Platoro; just N of Forest Road 271 | distance_and_direction | Platoro | candidates_found | Platoro (Populated Place, Conejos, exact_official) | needs_information |
| P078 | In San Luis Valley; 1.0 mile northwest of San Luis on north side of hwy. 142. | orthogonal_offsets | San Luis | candidates_found | San Luis (Populated Place, Costilla, exact_official) | unsupported |
| P079 | Heil Valley Ranch, Geer Canyon, Geer Canyon Drive, ~1.6 miles W of caretakers house; | named_feature | Heil Valley Ranch | feature_absent_from_index |  | needs_information |
| P080 | San Isabel National Forest, Mt. Champion Basin, ca. 17 mi SW of Leadville on Half Moon Road. | route_relative | Leadville | candidates_found | Leadville (Populated Place, Lake, exact_official) | unsupported |
| P081 | Arapaho National Forest: Front Range: St. Louis Campground along St. Louis Creek, ca 3 air mi SW of Fraser. | distance_and_direction | Fraser | candidates_found | Fraser (Populated Place, Grand, exact_official) | computed |
| P082 | Ice Lake Basin, San Juan Mts., 10 mi from Silverton. | distance_and_direction |  |  |  | invalid_extraction |
| P083 | Mosquito Range; ca. 9.5 miles SW of Breckenridge; E slope of Mt. Lincoln, 1/8 mile NE of "Russia Mine" | named_feature | Mosquito Range | candidates_found | Mosquito Range (Range, Lake, exact_official) | needs_information |
| P084 | Hills above McElmo creek, ca. 21 mi. WW of Cortez. | distance_and_direction | Cortez | candidates_found | Cortez (Populated Place, Montezuma, exact_official) | computed |
| P085 | Whisky Springs Ranch, Douglas Mountain, 6 mi. SW of Greystone. | named_feature | Whisky Springs Ranch | feature_absent_from_index |  | needs_information |
| P086 | Stony Basin, ca. 7 miles northeast of Silverton. San Juan National Forest. Fellfield on east-facing ridge of Green Mountain. | named_feature | Stony Basin | candidates_found | Stone Basin (Basin, Montrose, fuzzy_official) | needs_information |
| P087 | Northern Gunnison Basin; near W Fork of Terror Creek, ca. 7 air mi. NNW of Paonia. | named_feature | Northern Gunnison Basin | feature_absent_from_index |  | needs_information |
| P088 | Boulder Creek flats, 1 mile w. of Frederick. | distance_and_direction | Frederick | candidates_found | Frederick (Populated Place, Weld, exact_official) | computed |
| P089 | Yampa Canyon, 4 mi. from Youghal. | distance_and_direction |  |  |  | invalid_extraction |
| P090 | Piceance Creek Road, 3.4 miles S of junction with State Highway 64. | distance_and_direction | junction with State Highway 64 | feature_absent_from_index |  | needs_information |
| P091 | West Fork of Parachute Creek, 13 miles N of Grand Valley. | distance_and_direction | Grand Valley | candidates_found | Grand Valley (Valley, Grand, exact_official) | needs_information |
| P092 | Dinosaur National Monument. Echo Park, NW base of Jenny Lind Rock, ¼ mile E of Steamboat Rock. | distance_and_direction | Steamboat Rock | candidates_found | Steamboat Rock (Cape, Moffat, exact_official) | needs_information |
| P093 | Rio Grande National Forest; ~10 miles ENE of Platoro; N of Alamosa River at Alamosa CG | distance_and_direction | Platoro | candidates_found | Platoro (Populated Place, Conejos, exact_official) | needs_information |
| P094 | Upper Mill Creek, Arapaho National Forest, 3.5 miles SSW of James Peak. | named_feature | Upper Mill Creek | candidates_found | Mill Creek (Stream, Clear Creek, core_official) | computed |
| P095 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Morrison trail, 9.8 air mi. NE of Mancos. | distance_and_direction | Mancos | candidates_found | Mancos (Populated Place, Montezuma, exact_official) | computed |
| P096 | Central Colorado: Sawatch Range, West Slope Continental Divide: off Forest Road 714, just below Sheep Mountain, ca 6 air mi NE of Tennessee Pass. | distance_and_direction | Tennessee Pass | candidates_found | Tennessee Pass (Gap, Eagle, exact_official) | needs_information |
| P097 | White River at Beefsteak Gulch, 12 mi. west of Meeker on State Hwy. 64. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | computed |
| P098 | Barrens, ca 1 mi N of north entrance to Red Top Ranch, along county road. | distance_and_direction | Red Top Ranch | feature_absent_from_index |  | needs_information |
| P099 | Upper Dolores River Drainage and adjacent areas: San Juan National Forest: Lizard Head Wilderness Area: Lizard Head Peak, ca. 10 air mi N of Rico. | distance_and_direction | Rico | candidates_found | Rico (Populated Place, Dolores, exact_official) | computed |
| P100 | San Juan National Forest; ~16 miles NE of Pagosa Springs; S side of Fall Creek, N side of Fall Creek Road | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| P101 | Pond just S of outlet of Red Gulch, 9½ mi. N of Grand Lake. | orthogonal_offsets | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | unsupported |
| P102 | Golden; North Table Mountain Park. Lower north slopes of North Table Mountain, along the Tablerock Trail, 1.0 km. south of the Mesa Spur trailhead on W. 58th Avenue, 4.2 km. north northwest of the GNIS location of Golden. | distance_and_direction | Mesa Spur trailhead | feature_absent_from_index |  | needs_information |
| P103 | Rocky Flats, 7 mi S of Boulder, on Rocky Flats Pediment, N of Lindsay Farm. | named_feature | Rocky Flats | candidates_found | Rocky Flats (Lake, Jefferson, exact_official) | computed |
| P104 | Rocky Mountain National Park, Timber Creek, ½ mile southeast of Highway 34 and Timber Campground. | distance_and_direction | Highway 34 and Timber Campground | feature_absent_from_index |  | needs_information |
| P105 | Chambers place, 2 miles S. of Broomfield on Wadsworth. Backyard. | route_relative | Broomfield | candidates_found | Broomfield (Populated Place, Broomfield, exact_official) | unsupported |
| P106 | Meadows Campground, Routt National Forest, 15 miles southeast of Steamboat Springs on US Highway 40. Open meadow below beaver ponds, a little west of campground. | named_feature | Meadows Campground | feature_absent_from_index |  | needs_information |
| P107 | North-central Colorado: Park Range: Hinman Lake and vicinity to Hinman Creek, ca 1.5 air mi N of Elk River, ca 6.5 air mi NE of Clark; ca 20 air mi N of Steamboat Springs. | distance_and_direction | Elk River | candidates_found | Elk River (Stream, Routt, exact_official) | computed |
| P108 | Rocky Flats Site, 7 mi S of Boulder on Rocky Flats Pediment. Near crossing of W boundary of site and Woman Ck. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| P109 | Northern Gunnison Basin: along Elk Creek, ca 13.5 air mi WSW of Gunnison. | distance_and_direction | Gunnison | candidates_found | Gunnison (Populated Place, Gunnison, exact_official) | computed |
| P110 | Golden; Little Scraggy Peak: Buffalo Creek Recreation Area, northeast slopes of Little Scraggy Peak, 1.05 km. southwest of the intersection of County Roads 126 and 550, 46.5 km. south of the GNIS location of Golden. | distance_and_direction | the intersection of County Roads 126 and 550 | feature_absent_from_index |  | needs_information |
| P111 | Dinosaur National Monument. Limestone Ridge, ca. 0.9 mi WNW of Limestone Springs, 3/4 mi E of Green River. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| P112 | Arapaho National Forest: Front Range: Simpson Creek, ca 6 air mi NW of Byers Peak; ca 11.5 air mi SE of Hot Sulphur Springs. | distance_and_direction | Byers Peak | candidates_found | Byers Peak (Summit, Grand, exact_official) | needs_information |
| P113 | Deer Park Gulch, ca. 24 km N of DeBeque. | distance_and_direction | DeBeque | candidates_found | De Beque (Populated Place, Mesa, fuzzy_official) | computed |
| P114 | City of Boulder Mountain Park, Homestead Mesa, ca. 0.5 mi. NW of South Mesa Trailhead. | distance_and_direction | South Mesa Trailhead | feature_absent_from_index |  | needs_information |
| P115 | North-central Colorado: Park Range: along Forest Spur Road 471.1 from Forest Road 471 to upper Long Draw, NE of Mount Candy, ca 2.5 air mi SE of Clark; ca 14 air mi N of Steamboat Springs. | itinerary | Forest Spur Road 471.1 | feature_absent_from_index |  | unsupported |
| P116 | Flat Tops/White River Plateau: Fowler Creek Trail to Hill Creek Campground from top to midpoint, ca 8-9 air mi SE of Buford. | itinerary |  |  |  | invalid_extraction |
| P117 | Vermejo Park Ranch: Culebra Range: in alpine basin at headwaters of East Fork Costilla Creek, 3.88 air mi NE of State Line Peak. | distance_and_direction | State Line Peak | candidates_found | State Line Peak (Summit, Costilla, exact_official) | needs_information |
| P118 | Upper Dolores River Drainage and Adjacent Area: Slick Rock Canyon, ca 19 air mi WNW of Naturita in Dolores River Canyon, N of La Sal Creek confluence. | distance_and_direction | Naturita | candidates_found | Naturita (Populated Place, Montrose, exact_official) | computed |
| P119 | Yellow Creek drainage, 22 miles and 79° from Rangely. | distance_and_direction | Rangely | candidates_found | Rangely (Populated Place, Rio Blanco, exact_official) | computed |
| P120 | Vaughn Creek in White River National Forest, 6 mi. south of Buford. | distance_and_direction | Buford | candidates_found | Buford (Populated Place, Rio Blanco, exact_official) | needs_information |
