# test-4: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `benchmark-4/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 60 · `named_feature` 35 · `route_relative` 16 · `orthogonal_offsets` 7 · `between_features` 2

**retrieval**: `candidates_found` 85 · `feature_absent_from_index` 27 · `None` 8

**proposal**: `computed` 53 · `needs_information` 36 · `unsupported` 23 · `invalid_extraction` 8

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| Q001 | Gurley Canyon, 1.6 mi NW along Colo 145 from intersection with Specie Cr. road. | route_relative | intersection with Specie Cr. road | feature_absent_from_index |  | unsupported |
| Q002 | White River National Forest, 1 km from Baxter Peak at 28°. | distance_and_direction |  |  |  | invalid_extraction |
| Q003 | Mineral Basin, ca. 7 miles southwest of Cottonwood Lake, San Isabel National Forest. At base of Jones Mountain. | named_feature | Mineral Basin | candidates_found | Mineral Basin (Basin, Chaffee, exact_official) | needs_information |
| Q004 | Red hills SW of Raven Ridge, ca. 14 mi WNW of Rangley. | distance_and_direction | Rangley | candidates_found | Rangely (Populated Place, Rio Blanco, fuzzy_variant) | computed |
| Q005 | Chambers place, 2 miles S. of Broomfield on Wadsworth; in cat-tail swamp near underpass. | distance_and_direction | Broomfield | candidates_found | Broomfield (Populated Place, Broomfield, exact_official) | computed |
| Q006 | Rio Grande National Forest; ~11 1/2 miles SW of Platoro; Augustora Creek, ~1 mile SE of Fish Lake | named_feature | Augustora Creek | candidates_found | Augustora Creek (Stream, Conejos, exact_official) | computed |
| Q007 | Williams Fork Mountains: Arapaho National Forest: ridge N of Cottonwood Gulch, ca 4 air mi ENE of Heeney. | distance_and_direction | Heeney | candidates_found | Heeney (Populated Place, Summit, exact_official) | computed |
| Q008 | Arapaho National Forest, along Keyser Creek, 0.2 mile upstream of Simpson Creek. | route_relative | Simpson Creek | candidates_found | Simpson Creek (Stream, Grand, exact_official) | unsupported |
| Q009 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Forest Road 510, S of Salter Y, ca 9 air mi NW of Dolores. | orthogonal_offsets |  |  |  | invalid_extraction |
| Q010 | Flat Tops/White River Plateau: mesa above Deep Creek, ca 11 air mi NNE of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | computed |
| Q011 | Lost Creek Area, Tarryall Mtns., 80 km (50 mi) southwest of Denver and 80 km northwest of Colo. Springs. Goose Creek trail head. | distance_and_direction |  |  |  | invalid_extraction |
| Q012 | Upper Chicago Lake, Mt. Evans Wilderness, Arapaho National Forest, 2 miles north of Mt. Evans. | named_feature | Upper Chicago Lake | candidates_found | Chicago Lakes (Lake, Clear Creek, core_official) | computed |
| Q013 | Rocky Flats site, 7 mi S of Boulder. Southwest corner. | named_feature | Rocky Flats site | feature_absent_from_index |  | needs_information |
| Q014 | Simpson Creek, ca. 0.4 mile West of headquarter buildings, Eagle Rock Ranch, ca. 15 air m. E of Hwy. 85 & 2 m. S of WY border. | named_feature | Simpson Creek | candidates_found | Simpson Creek (Stream, Weld, exact_official) | needs_information |
| Q015 | East slope of "Clay Hill", ca. 6 mi NW of Paradox, Manti-LaSal Nat. Forest. | named_feature | "Clay Hill" | feature_absent_from_index |  | needs_information |
| Q016 | Lone Mesa State Park, 5 miles north of southern entrance at FS 514. | route_relative | FS 514 | feature_absent_from_index |  | unsupported |
| Q017 | Red Rocks Lake, 2½ miles W of Ward. | distance_and_direction | Ward | candidates_found | Ward (Populated Place, Boulder, exact_official) | computed |
| Q018 | Flat Tops/White River Plateau: Clinetop benchmark, ca 16 air mi NE of Rifle. | distance_and_direction | Rifle | candidates_found | Rifle (Populated Place, Garfield, exact_official) | computed |
| Q019 | S Fork White River, 2 mi NW of Shingle Peak. | distance_and_direction | Shingle Peak | candidates_found | Shingle Peak (Summit, Garfield, exact_official) | needs_information |
| Q020 | Central Colorado: Sawatch Range, West Slope Continental Divide: along Fall Creek Trail 2001, between Lake Constantine and Lake Hunky Dory, ca 11 air mi S of Minturn. | orthogonal_offsets | Lake Constantine | candidates_found | Lake Constantine (Lake, Eagle, exact_official) | unsupported |
| Q021 | Rio Grande National Forest; ~8 miles SE of South Fork; W of Forest Road 345 & E of Del Norte Peak | between_features | Forest Road 345 | feature_absent_from_index |  | unsupported |
| Q022 | San Juan Mts., Rio Grande National Forest, basin SE of Stony Pass, ca. 8 air miles ESE of Silverton, headwaters of Rio Grande. N summit ridge of Sheep Mt. | named_feature | San Juan Mts. | feature_absent_from_index |  | needs_information |
| Q023 | High Creek, 10 mi S of Fairplay. E of highway. | named_feature | High Creek | candidates_found | High Creek (Stream, Park, exact_official) | needs_information |
| Q024 | San Juan National Forest; ~8 miles NE of Pagosa Springs; N of Coal Creek, ~3/4 mile NE of Coal Creek TH | distance_and_direction | Pagosa Springs | candidates_found | Pagosa Springs (Populated Place, Archuleta, exact_official) | computed |
| Q025 | Gore Range: trailhead at North Rock Creek, 2.3 air mi SE of Blue River Campground and 7.3 air mi NE of Silverthorne. | distance_and_direction | Blue River Campground | feature_absent_from_index |  | needs_information |
| Q026 | Culebra Range, ca. 25 air mi. SSE of Fort Garland, NE face of Purgatorie Pk. above Johnson Creek. | distance_and_direction | Fort Garland | candidates_found | Fort Garland (Populated Place, Costilla, exact_official) | computed |
| Q027 | Fossil Ridge area; ca. 32 km (20 mi) NE of Gunnison, ca. 10 km (6mi) N of Ohio City, ca. 3 km (2mi) NW of Gold Creek Campground, Gunnison National Forest; ca. 400 m (¼ mi) S of Fossil Mtn. | distance_and_direction |  |  |  | invalid_extraction |
| Q028 | Fox Ranch, ca. ten miles NE of Kirk, and four miles N of Hwy. 36. River pasture west of County Road U. Bluff along the north side of the Arickaree River. | distance_and_direction | Kirk | candidates_found | Kirk (Populated Place, Yuma, exact_official) | computed |
| Q029 | Flat Tops / White River Plateau: Flat Tops Wilderness: Blair Mountain, ca 17 air mi NNW of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | computed |
| Q030 | "Point of Rocks"; 10 miles E of Barnesville. | named_feature | Point of Rocks | candidates_found | Point of Rocks (Summit, Weld, exact_official) | needs_information |
| Q031 | Just east of Wolf Creek, 7 mi. w. of Elk Springs. | named_feature | Wolf Creek | candidates_found | Wolf Creek (Stream, Moffat, exact_official) | computed |
| Q032 | Whisky Springs Ranch, 6 mi SW of Greystone, NE slope of Douglas Mt. | named_feature | Whisky Springs Ranch | feature_absent_from_index |  | needs_information |
| Q033 | S. end of Gunbarrel Hill, White Rocks, 10 miles n. e. of Boulder. | named_feature | Gunbarrel Hill | candidates_found | Gun Barrel Hill (Summit, Boulder, fuzzy_official) | needs_information |
| Q034 | Along South Platte river; 2.9 miles southwest of Deckers on hwy 67. | orthogonal_offsets | Deckers | candidates_found | Deckers (Populated Place, Douglas, exact_official) | unsupported |
| Q035 | N of Shire Gulch between De Beque Cutoff Road and Sunnyside Road, ca 7 air mi SSE of De Beque at the intersection of I-70 and De Beque Cutoff Road. | orthogonal_offsets | Shire Gulch | candidates_found | Shire Gulch (Valley, Mesa, exact_official) | unsupported |
| Q036 | Sawatch Range: White River National Forest: Holy Cross Wilderness: Eagle Lake Trail to Halfmoon Lake, between Eagle and Avalanche peaks, along Lime Creek, ca 18 air mi SSE of Eagle. | distance_and_direction | Eagle | candidates_found | Eagle (Populated Place, Eagle, exact_official) | computed |
| Q037 | Park Range; ca. 3 air mi NNE of Steamboat Springs, ridge between Soda and Butcherknife creeks. | distance_and_direction | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | computed |
| Q038 | Eastern San Miguel Mts.; East Fork trail, 0.6 mi. south of Colo. 145. | route_relative | Colo. 145 | feature_absent_from_index |  | unsupported |
| Q039 | Gore Range: Arapaho National Forest: vicinity of Surprise Trailhead near the end of Cataract Creek Road, ca 19 air mi NW of Silverthorne at I-70. | distance_and_direction | Silverthorne | candidates_found | Silverthorne (Populated Place, Summit, exact_official) | computed |
| Q040 | Arapaho National Forest: Front Range: Barbour Fork Soda Creek, ca 2.5 air mi SW of Idaho Springs; ca 30-31 air mi W of Denver. | distance_and_direction | Idaho Springs | candidates_found | Idaho Springs (Populated Place, Clear Creek, exact_official) | computed |
| Q041 | ON SE face of Porphyry Mountain, ½ mi. E of Jamestown. | named_feature | Porphyry Mountain | candidates_found | Porphyry Mountain (Summit, Boulder, exact_official) | needs_information |
| Q042 | Paint Mines, ca 1 mi S of Calhan, E side of Paint Mines Rd. | named_feature | Paint Mines | feature_absent_from_index |  | needs_information |
| Q043 | Along Deep Creek, approximately 1 mile upstream of confluence with Colorado River. | route_relative | confluence with Colorado River | feature_absent_from_index |  | unsupported |
| Q044 | Rocky Flats Site, 7 mi S of Boulder, on Rocky Flats Pediment. NW corner [of site or Sec3?]. | named_feature |  |  |  | invalid_extraction |
| Q045 | Flat Tops/White River Plateau: Flat Tops Wilderness: Big Marvine Peak, ca 30 air miles ESE of Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | computed |
| Q046 | Along railroad track, ½ mi. east of Ft.Collins. | route_relative | Ft.Collins | candidates_found | Fort Collins (Populated Place, Larimer, exact_official) | unsupported |
| Q047 | Along Muddy Creek, approximately 4 miles north of Kremmling on I-40. | route_relative | Kremmling | candidates_found | Kremmling (Populated Place, Grand, exact_official) | unsupported |
| Q048 | White River National Forest in the Flat Tops Wilderness Area, 1/2 mile north of Island Lake along Middle Fork Derby Creek. | route_relative | Island Lake | candidates_found | Island Lake (Lake, Garfield, exact_official) | unsupported |
| Q049 | Four Mile Mesa, 5 mi N of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| Q050 | Park Range; ca. 2 air mi N of Red Elephant Mountain. | distance_and_direction | Red Elephant Mountain | candidates_found | Red Elephant Mountain (Summit, Jackson, exact_official) | needs_information |
| Q051 | S. Fork San Miguel River, 2 mi N of Ames. | distance_and_direction | Ames | candidates_found | Ames (Populated Place, San Miguel, exact_official) | needs_information |
| Q052 | Unaweap Canyon road between Whitewater and Gateway; Nancy Hanks Gulch, 2 mi. E of divide. | between_features | Whitewater | candidates_found | Whitewater (Populated Place, Mesa, exact_official) | unsupported |
| Q053 | Morrison Creek. In shaded forest beside Morrison Creek, 2.21 km. northwest of the Kelsey Campground, 5.22 km. southwest of the Little Scraggy Trailhead. | named_feature | Morrison Creek | candidates_found | Morrison Creek (Stream, Routt, exact_official) | computed |
| Q054 | Dinosaur National Monument. Disappointment Draw, ca 1.25 mi SW of The Steps and Deerlodge Park. | distance_and_direction | The Steps and Deerlodge Park | feature_absent_from_index |  | needs_information |
| Q055 | Flat Tops/White River Plateau: Grand Hogback, ca 6 air mi NNW of Rifle. | distance_and_direction | Rifle | candidates_found | Rifle (Populated Place, Garfield, exact_official) | computed |
| Q056 | Fletcher Gulch, 3 miles S of State Highway 64. | distance_and_direction | State Highway 64 | feature_absent_from_index |  | needs_information |
| Q057 | Roadside, twelve miles west of Kenton, Oklahoma. Mesa de Maya Region. | distance_and_direction | Kenton | feature_absent_from_index |  | needs_information |
| Q058 | First high bench above McElmo Creek, 12 mi. w. of Cortez. | distance_and_direction | Cortez | candidates_found | Cortez (Populated Place, Montezuma, exact_official) | computed |
| Q059 | McElmo Canyon, 7 mi. w. of jct. with Cortez road. | named_feature |  |  |  | invalid_extraction |
| Q060 | Medicine Bow Mountains: Colorado State Forest: Kelly Lake trail crossing North Fork Canadian River, ca 18 air mi E of Walden. | distance_and_direction | Walden | candidates_found | Walden (Populated Place, Jackson, exact_official) | computed |
| Q061 | Rocky Mountain National Park. Edge of Harbison Ranch near site of old buildings, 1.5 mi N of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | computed |
| Q062 | Central Colorado: Castle Peak Area, West Slope Continental Divide: Greenhorn Mountain, ca 4 air mi NW of Gypsum. | distance_and_direction | Gypsum | candidates_found | Gypsum (Populated Place, Eagle, exact_official) | computed |
| Q063 | Muggins Gulch, ca. 5 miles SE of Estes Park. | named_feature | Muggins Gulch | candidates_found | Muggins Gulch (Valley, Larimer, exact_official) | needs_information |
| Q064 | Culebra Range, Sangre de Cristo Mts., Bar NI Ranch, ca. 30.0 air miles W of Trinidad. Upper Whiskey Creek. | named_feature | Upper Whiskey Creek | candidates_found | Whiskey Creek (Stream, Routt, core_official) | needs_information |
| Q065 | Flat Tops/White River Plateau: Flat Tops Wilderness: Lost Solar Creek, ca 24 air mi NNW of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | computed |
| Q066 | North-central Colorado: Elkhead Mountains: along South Fork Slater Creek at the forest boundary, ca 34 air mi NW of Steamboat Springs; ca 26 air mi NNE of Craig. | distance_and_direction | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | computed |
| Q067 | Cottonwood Spring adjacent to Big Duck Creek in Piceance Basin, 16 mi. SE of Rangely. | named_feature | Cottonwood Spring | candidates_found | Cottonwood Spring (Spring, Rio Blanco, exact_official) | computed |
| Q068 | San Juan National Forest; ~8 miles ENE of Chromo; Price Lakes Rd. ~1 mile N of National Forest boundary | orthogonal_offsets |  |  |  | invalid_extraction |
| Q069 | Roadside and pasture, 2 mi. E of Kiowa. | distance_and_direction | Kiowa | candidates_found | Kiowa (Populated Place, Elbert, exact_official) | computed |
| Q070 | Barr Camp, 3.5 miles from summit of Manitou Mt. incline, Pikes Peak. | route_relative | Manitou Mt. | candidates_found | Mount Manitou (Summit, El Paso, core_official) | unsupported |
| Q071 | Dinosaur National Monument. Mantle Ranch Road, ca. ¼ mi W of Dry Woman Canyon. | distance_and_direction | Dry Woman Canyon | candidates_found | Dry Woman Canyon (Valley, Moffat, exact_official) | needs_information |
| Q072 | Flat Tops/White River Plateau: Yampa Valley, ca. 2.5 air mi N of Yampa. | distance_and_direction | Yampa | candidates_found | Yampa (Populated Place, Routt, exact_official) | computed |
| Q073 | Private ranch, ca. 12 miles S of Pueblo. | distance_and_direction | Pueblo | candidates_found | Pueblo (Populated Place, Pueblo, exact_official) | computed |
| Q074 | Northwest of Mack; 4.6 km north of US Highway 6/50 on Two Road. | orthogonal_offsets | Mack | candidates_found | Mack (Populated Place, Mesa, exact_official) | unsupported |
| Q075 | White River National Forest: Hunter Creek, ca 2 air mi NE of Aspen. | distance_and_direction | Aspen | candidates_found | Aspen (Populated Place, Pitkin, exact_official) | computed |
| Q076 | Near C.S.U. Piceance Basin Intensive Study Site, 7 mi from Piceance Basin road. | named_feature | C.S.U. Piceance Basin Intensive Study Site | feature_absent_from_index |  | needs_information |
| Q077 | Park Range; 22 air mi WSW of Walden; Slide Lake, Rainbow Lake area. | distance_and_direction | Walden | candidates_found | Walden (Populated Place, Jackson, exact_official) | computed |
| Q078 | Hwy. 82, summit of Independence Pass, ¼ mi. N of parking area. | named_feature | Independence Pass | candidates_found | Independence Pass (Gap, Lake, exact_official) | needs_information |
| Q079 | Huerfano Uplands, Vigil-St. Vrain Grant. Private ranch, ca. 27 miles SE of Pueblo. | distance_and_direction | Pueblo | candidates_found | Pueblo (Populated Place, Pueblo, exact_official) | computed |
| Q080 | Black Canyon, 1/8 mi W of Blue Mesa Dam. | distance_and_direction | Blue Mesa Dam | feature_absent_from_index |  | needs_information |
| Q081 | Baca Nantional Wildlife Refuge, San Luis Valley; ca. 3.4 miles SW of Hooper, just S of County Rd. | distance_and_direction | Hooper | candidates_found | Hooper (Populated Place, Alamosa, exact_official) | computed |
| Q082 | South Plattte River at Tamarack Ranch State Wildlife Area west of Red Lion Rd., ca. 28 miles NE of Sterling. | distance_and_direction | Sterling | candidates_found | Sterling (Populated Place, Logan, exact_official) | computed |
| Q083 | San Juan National Forest, near West fork of San Juan River, ca. 13.0 miles NE of Pagosa Springs, SW og wolf Creek Pass, ca. 0.5 air mile W of US 160, CR 648A. | distance_and_direction | Pagosa Springs | candidates_found | Pagosa Springs (Populated Place, Archuleta, exact_official) | computed |
| Q084 | Peltier Creek in the Flat Tops, 6 mi. SE of Buford on County Rd. 10. | named_feature | Peltier Creek | candidates_found | Peltier Creek (Stream, Rio Blanco, exact_official) | computed |
| Q085 | Upper valley of Middle St. Vrain Creek, 0.6 miles NE of Red Deer Lake. | distance_and_direction | Red Deer Lake | candidates_found | Red Deer Lake (Lake, Boulder, exact_official) | computed |
| Q086 | East Rifle Creek at Rifle Mountain Park, 22 mi. NNE of Rifle. | named_feature | East Rifle Creek | candidates_found | East Rifle Creek (Stream, Garfield, exact_official) | computed |
| Q087 | White River National Forest in the Flat Tops; approx. 3 miles south of Elk Knob, along Dry Sweetwater Creek. | route_relative | Dry Sweetwater Creek | candidates_found | Dry Sweetwater Creek (Stream, Garfield, exact_official) | unsupported |
| Q088 | Great Sand Dunes National Monument, ¼ mi. from beginning Mosca Pass Trail. | route_relative | Mosca Pass Trail | feature_absent_from_index |  | unsupported |
| Q089 | Along the Colorado River, approximately 1 mile downstream of McPhee Gulch. | route_relative | McPhee Gulch | candidates_found | McPhee Gulch (Valley, Eagle, exact_official) | unsupported |
| Q090 | South Sand Wash north of Dry Mountain, 10 mi NE of junction with Hwy 318 on Moffat Rd 46. | orthogonal_offsets | junction with Hwy 318 on Moffat Rd 46 | feature_absent_from_index |  | unsupported |
| Q091 | Rocky Flats Environmental Technology Site, 7 miles south of Boulder on Rocky Flats Pediment. B-3 Pond revegetation area. | named_feature | Rocky Flats Environmental Technology Site | feature_absent_from_index |  | needs_information |
| Q092 | Pawnee National Grassland, 5 miles northeast of town of Nunn, above Robinson Creek. | named_feature | Pawnee National Grassland | feature_absent_from_index |  | needs_information |
| Q093 | Front Range: Arapaho National Forest: Peru Creek Road at the confluence of Warren Gulch, ca 2 air mi NE of Montezuma. | distance_and_direction | Montezuma | candidates_found | Montezuma (Populated Place, Summit, exact_official) | computed |
| Q094 | East Rifle Creek above Little Box Canyon, ca. 20 miles NE of Rifle. | named_feature | East Rifle Creek | candidates_found | East Rifle Creek (Stream, Garfield, exact_official) | computed |
| Q095 | Coal Creek, 17 mi NE of Meeker; streambank in hay meadow. | named_feature | Coal Creek | candidates_found | Coal Creek (Stream, Rio Blanco, exact_official) | computed |
| Q096 | Rifle Falls Picnic Area, 14 mi. NE of Rifle in the Grand Hogback. | distance_and_direction |  |  |  | invalid_extraction |
| Q097 | In grassland west of Ingleside formation escarpment, 30 miles N of Fort Collins. | distance_and_direction | Fort Collins | candidates_found | Fort Collins (Populated Place, Larimer, exact_official) | computed |
| Q098 | Wet Mountain Valley, Kennicott Ranch, 6 miles NW of Westcliffe. Swift Creek. | named_feature | Swift Creek | candidates_found | Swift Creek (Stream, Custer, exact_official) | computed |
| Q099 | Un-named tributary of Vaughn Creek below Beaver Lake in the Flat Tops, 6 mi. SW of Buford. | distance_and_direction | Buford | candidates_found | Buford (Populated Place, Rio Blanco, exact_official) | needs_information |
| Q100 | Radium Wildlfie Area, 5 mi E of Radium on N side of river. | named_feature | Radium Wildlfie Area | feature_absent_from_index |  | needs_information |
| Q101 | On floor of valley, about 10 miles north of Grand Lake. | distance_and_direction | Grand Lake | candidates_found | Grand Lake (Reservoir, Grand, exact_official) | computed |
| Q102 | Wigwam Campground; 3.8 miles SW of Deckers on hwy. 67. | route_relative | Deckers | candidates_found | Deckers (Populated Place, Douglas, exact_official) | unsupported |
| Q103 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Culebra Range, Vermejo Park Ranch, head of Costilla Creek, ca 14 air mi SE of San Luis. | distance_and_direction | San Luis | candidates_found | San Luis (Populated Place, Costilla, exact_official) | computed |
| Q104 | Paint Mines, ca 1 mi S of Calhan; E side of Paint Mines Rd. At bottom of main channel of Paint Mines drainage. | named_feature | Paint Mines | feature_absent_from_index |  | needs_information |
| Q105 | Less than one mile east of Canon City, ¼ mile south of Highway 50, on private land. | distance_and_direction | Canon City | candidates_found | Cañon City (Populated Place, Fremont, exact_official) | computed |
| Q106 | Arkansas River Valley; ca. 2 miles SE of Wetmore, just outside San Isabel National Forest boundary. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| Q107 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Arkansas River Valley, ca 1.5 mi W of Parkdale on the south side of U.S. Hwy 50. | route_relative | Parkdale | feature_absent_from_index |  | unsupported |
| Q108 | Sarvis Creek exiting Buffalo Park, ca. 17.0 air miles NW of Kremmling, by Forest Service Road 100 (19). | distance_and_direction | Kremmling | candidates_found | Kremmling (Populated Place, Grand, exact_official) | computed |
| Q109 | Pike National Forest, Lost Creek Wilderness Area, East Lost Park Natural Area, ca. 1.0 air miles SE of Lost Park Campground. | distance_and_direction | Lost Park Campground | feature_absent_from_index |  | needs_information |
| Q110 | Boulder Creek at White Rocks, 8 mi. NE of Boulder. | named_feature | Boulder Creek | candidates_found | Middle Boulder Creek (Stream, Boulder, exact_variant) | computed |
| Q111 | Flat Tops Wilderness Area in White River National Forest, along Bull Lake Creek, 2/3 mile downstream of Stillwaters Lakes. | route_relative | Stillwaters Lakes | candidates_found | Grand Lake (Reservoir, Grand, fuzzy_variant) | unsupported |
| Q112 | San Juan National Forest; ~13 miles E of Pagosa Springs; ~1/2 mile S of Blackhead Peak Summit | distance_and_direction | Pagosa Springs | candidates_found | Pagosa Springs (Populated Place, Archuleta, exact_official) | computed |
| Q113 | Morgan County right-of-way, about 1/2 mile east of Hwy 71 business (Colorado Ave, Brush) on Mill St. | route_relative | Hwy 71 business (Colorado Ave, Brush) | feature_absent_from_index |  | unsupported |
| Q114 | Arapaho National Forest, along Porcupine Creek, approximately 2.75 miles southwest of Loveland Pass. | distance_and_direction | Loveland Pass | candidates_found | Loveland Pass (Gap, Summit, exact_official) | needs_information |
| Q115 | San Juan National Forest; ~7 miles NNE of Chromo; E side of Little Navajo River | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| Q116 | On flat of NE-facing slope of Douglas Mtn., at Whisky Springs Ranch, 6 mi SW of Greystone. | distance_and_direction | Greystone | candidates_found | Greystone (Populated Place, Moffat, exact_official) | needs_information |
| Q117 | S-facing slopes of Coal Creek Peak, about 10 mi S of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| Q118 | San Juan National Forest; ~15 miles E/SE of Pagosa Springs; southeast of Opal Lake near western base of Flattop Mountain | named_feature | San Juan National Forest | feature_absent_from_index |  | needs_information |
| Q119 | Comanche National Grassland. Carrizo Creek: near Campground, ca. 4 mi. W. of Las Animas County line. | named_feature | Carrizo Creek | candidates_found | West Carrizo Creek (Stream, Las Animas, exact_variant) | needs_information |
| Q120 | Flat Tops/White River Plateau: Flat Tops: Miller Creek Cow Camp, ca 14 air mi SE of Meeker. | distance_and_direction | Meeker | candidates_found | Meeker (Populated Place, Rio Blanco, exact_official) | computed |
