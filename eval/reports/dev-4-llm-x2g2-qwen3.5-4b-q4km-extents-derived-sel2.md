# dev-4: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-4/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 22 · `named_feature` 16 · `orthogonal_offsets` 4 · `other` 2 · `route_relative` 2 · `between_features` 2 · `distance_only` 1 · `itinerary` 1

**retrieval**: `candidates_found` 29 · `feature_absent_from_index` 16 · `None` 3 · `no_reference_feature` 2

**proposal**: `needs_information` 29 · `computed` 9 · `unsupported` 9 · `invalid_extraction` 3

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| G01 | Enchanted Mesa above the National Bureau of Standards. | named_feature | the National Bureau of Standards | feature_absent_from_index |  | needs_information |
| G02 | Side of Moly Mtn. near Climax. | named_feature | Moly Mtn. | candidates_found | Owl Mountain (Summit, Jackson, fuzzy_official) | needs_information |
| G03 | Entrance to Colorado National Monument. | named_feature | Colorado National Monument | feature_absent_from_index |  | needs_information |
| G04 | Northern Gunnison Basin: south-facing slope of Mt. Axtel. | named_feature | Mt. Axtel | candidates_found | Mount Axtell (Summit, Gunnison, fuzzy_official) | needs_information |
| G05 | East of Tolland, five miles west of Rollinsville. | distance_and_direction | Rollinsville | candidates_found | Rollinsville (Populated Place, Gilpin, exact_official) | computed |
| G06 | Colorado National Monument, Grand Junction entrance highway. | other |  | no_reference_feature |  | unsupported |
| G07 | 25 mi below Manitou. | distance_only | Manitou | candidates_found | Manitou Springs (Populated Place, El Paso, exact_variant) | computed |
| G08 | Uncompahgre National Forest, along Divide Road, 6.7 miles SSW of Colorado Hwy. 141 at Taylor Ranch, junction about 15 miles from U.S. Hwy. 50 at Whitewater, on the edge and in a large meadow 0.5 mile south of the northern boundary of the Forest. | orthogonal_offsets | Colorado Hwy. 141 | feature_absent_from_index |  | unsupported |
| G09 | Plains Conservation Center, West Bijou Creek property, 5760 acres in the Denver Basin along West Bijou Creek, 38 miles SE of downtown Denver and 12 miles S of Strasburg. Approx. 3/4 mile E of W Bijou Creek. | named_feature | Plains Conservation Center | feature_absent_from_index |  | needs_information |
| G10 | Vermejo Park Ranch: in Long Canyon 0.65 air miles north of mouth of Joe Baker Canyon; 1.1 air miles north of New Mexico and 15 air miles southwest of Raton. | distance_and_direction | mouth of Joe Baker Canyon | feature_absent_from_index |  | needs_information |
| G11 | Near Trinidad. W of Trinidad on 12 ca. 10 miles then N on Burro Canyon Rd 1.3 miles. W of road. | itinerary | Trinidad | candidates_found | Trinidad (Populated Place, Las Animas, exact_official) | unsupported |
| G12 | Northern Gunnison Basin: ca. 2 air mi. S of Paonia Reservoir. | distance_and_direction | Paonia Reservoir | candidates_found | Paonia Reservoir (Reservoir, Gunnison, exact_official) | needs_information |
| G13 | South Park, Mile Creek road at crossing of culvert, 0.7 mi from Jct. Hwy 8. | route_relative | Jct. Hwy 8 | feature_absent_from_index |  | unsupported |
| G14 | White Rocks Area Conservation Easement, along north bank of Boulder Creek, 8 mi NE of Boulder. East entrance area. | named_feature | White Rocks Area Conservation Easement | feature_absent_from_index |  | needs_information |
| G15 | Beneath NW escarpment, Colorado National Monument, 3 mi. S of Fruita, W of hwy approach to Monument. | orthogonal_offsets |  |  |  | invalid_extraction |
| G16 | Slope of Caribou Hill, ca. six miles west of Nederland. | distance_and_direction | Nederland | candidates_found | Nederland (Populated Place, Boulder, exact_official) | needs_information |
| G17 | Southern Gunnison Basin: Curecanti National Recreation Area: ca 1.2 air mi N of Sapinero Mesa, just W of Fourmile Gulch Bay, ca 18.8 air mi WSW of Gunnison. | orthogonal_offsets | Sapinero Mesa | candidates_found | Sapinero Mesa (Summit, Gunnison, exact_official) | unsupported |
| G18 | Cathedral Creek in Piceance Basin, 18 mi NE of Douglas Pass. | named_feature | Cathedral Creek | candidates_found | Cathedral Creek (Stream, Rio Blanco, exact_official) | needs_information |
| G19 | Little South Fork of Elk River, 2 mi S of Seedhouse G.S., Routt National Forest, ca 29 mi N of Steamboat Springs. | distance_and_direction | Seedhouse G.S. | feature_absent_from_index |  | needs_information |
| G20 | U.S. Air Force Academy, ca. 30 ft. from Deadman's Lake and ca. 10 ft. from walking path. | named_feature | U.S. Air Force Academy | feature_absent_from_index |  | needs_information |
| G21 | Cedaredge, 0.2 miles east of Highway 65 on SE Deer Trail Ave. | distance_and_direction | Highway 65 | feature_absent_from_index |  | needs_information |
| G22 | Comanche National Grassland: near base of Shale Hills, ca 16.5 air mi S of La Junta. | distance_and_direction | La Junta | candidates_found | La Junta (Populated Place, Otero, exact_official) | computed |
| G23 | Mesa de Maya, 5 miles south of Kim. | distance_and_direction | Kim | candidates_found | Kim (Populated Place, Las Animas, exact_official) | computed |
| G24 | Between Rollinsville and Black Hawk, eight miles from Black Hawk. | between_features | Black Hawk | candidates_found | Black Hawk (Populated Place, Gilpin, exact_official) | unsupported |
| G25 | Central Colorado: Sawatch Range, East Slope Continental Divide: at lake at top of Porcupine Gulch, pond crossed on W by Continental Divide/Colorado Trail, ca 10 air mi NW of Leadville. | distance_and_direction | Leadville | candidates_found | Leadville (Populated Place, Lake, exact_official) | computed |
| G26 | Silver Lake. | named_feature | Silver Lake | candidates_found | Silver Lake (Reservoir, Boulder, exact_official) | computed |
| G27 | Flat Tops/ White River Plateau: Flat Tops Wilderness: Sheep Mountain, ca 28 air mi NNE of Glenwood Springs. Also SEC 34. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | needs_information |
| G28 | E Side of Black Forest, Latigo Blvd, 0.7 mi E of Elbert Rd. | named_feature | Black Forest | candidates_found | Black Forest (Area, El Paso, exact_official) | needs_information |
| G29 | Banner Peak. | named_feature | Banner Peak | candidates_found | Banner Peak (Summit, Jefferson, exact_official) | needs_information |
| G30 | North-central Colorado: Elkhead Mountains: near the head of Elkhead Creek at the north end of California Park, ca 1.5 air mi E of Saddle Mountain; ca 22.5 air mi NE of Hayden. | distance_and_direction | Saddle Mountain | candidates_found | Saddle Mountain (Summit, Routt, exact_official) | needs_information |
| G31 | Rio Grande National Forest. On forest service road, CA. 13.6 MI NW of Colorado 17. | route_relative | Rio Grande National Forest | feature_absent_from_index |  | unsupported |
| G32 | Colorado Mtns. | other |  | no_reference_feature |  | unsupported |
| G33 | Wet Mountains, Wet Mountain Valley, Sangre de Cristo Range, and Vicinity. Wet Mountains, Game Ridge, SE of Westcliffe, ca 0.8 mi E of Rosita on County Road 328. | distance_and_direction | Rosita | candidates_found | Rosita (Populated Place, Custer, exact_official) | needs_information |
| G34 | West slope of Steamboat Mt., 1 mile northwest of Lyons. | named_feature | Steamboat Mt. | candidates_found | Steamboat Mountain (Summit, Boulder, core_official) | needs_information |
| G35 | Pole Canyon, Boulder. | named_feature | Pole Canyon | candidates_found | Pole Canyon (Valley, Garfield, exact_official) | needs_information |
| G36 | Sarvis Creek wetlands adjacent to Buffalo Park, ca. 17.0 air miles NW of Kremmling, by Forest Service Road 100 (19). | between_features | Buffalo Park | candidates_found | Buffalo Park (Flat, Grand, exact_official) | unsupported |
| G37 | Front Range: Arapaho National Forest: Georgia Pass to the eastern slopes of Mount Guyot, ca 6-7 air mi ESE of Breckenridge. | distance_and_direction |  |  |  | invalid_extraction |
| G38 | Rocky Flats Site, 7 mi S of Boulder. North of Lindsay farm. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| G39 | Rio Grande National Forest; ~5 miles SW of Platoro; W slope of ridge NW of Conejos Peak summit | orthogonal_offsets |  |  |  | invalid_extraction |
| G40 | Small butte on s. side of Hwy. 96; Arkansas River Valley, 1 mile e. of Livsey. | distance_and_direction | Livsey | feature_absent_from_index |  | needs_information |
| G41 | Kremmling. | named_feature | Kremmling | candidates_found | Kremmling (Populated Place, Grand, exact_official) | computed |
| G42 | Temporary pool, filled in early summer by overflow from Baseline Lake, W of Cherryvale Road and the Lake, 4 mi E of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | needs_information |
| G43 | Burch's Lake, 4 mi E of Lyons. | distance_and_direction | Lyons | candidates_found | Lyons (Populated Place, Boulder, exact_official) | needs_information |
| G44 | Roadbed, falls and vicinity, 0.5 miles south of South Mineral Campground. | distance_and_direction | South Mineral Campground | feature_absent_from_index |  | needs_information |
| G45 | Park creek above Leon Creek Cow Camp in Grand Mesa National Forest, 4 mi. south of Vega Reservoir. | distance_and_direction | Vega Reservoir | candidates_found | Vega Reservoir (Reservoir, Mesa, exact_official) | computed |
| G46 | Central Colorado: Sawatch Range, West Slope Continental Divide: along Mt. Holy Cross Trail, ca 10 air mi SW of Redcliff. | distance_and_direction | Redcliff | candidates_found | Red Cliff (Populated Place, Eagle, exact_variant) | computed |
| G47 | Rocky Mountain National Park. Neversummer Range. Lulu Mountain, 16 mi N of Grand Lake. | named_feature | Lulu Mountain | candidates_found | Lulu Mountain (Summit, Grand, exact_official) | needs_information |
| G48 | Dinosaur National Monument. Schoonover Buttes, ca 1.2 mi NW of confluence of Pothole & Johnson Canyons. | distance_and_direction | confluence of Pothole & Johnson Canyons | feature_absent_from_index |  | needs_information |
| G49 | Flat Tops/White River Plateau: Rifle Mountain Park: East Rifle Creek, Sawmill Gulch, 0.3 air mi. SE of Community Building; ca. 15 air mi. SE of Community Building; ca. 15 air mi. NNE of Rifle. | distance_and_direction | Community Building | feature_absent_from_index |  | needs_information |
| G50 | Along road to Stone Cellar R.S. and Saguache Park, near junction of main highway, 4 mi. w. of Cochetopa Pass. | distance_and_direction | Cochetopa Pass | candidates_found | Cochetopa Pass (Gap, Saguache, exact_official) | needs_information |
