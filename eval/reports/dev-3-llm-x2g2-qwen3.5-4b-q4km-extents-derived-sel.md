# dev-3: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-3/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 21 · `named_feature` 15 · `orthogonal_offsets` 5 · `itinerary` 4 · `route_relative` 3 · `between_features` 2

**retrieval**: `candidates_found` 28 · `feature_absent_from_index` 12 · `None` 10

**proposal**: `needs_information` 26 · `invalid_extraction` 10 · `computed` 8 · `unsupported` 6

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| F01 | Between Yampa and Toponas. | between_features |  |  |  | invalid_extraction |
| F02 | Several miles north of the town of Jefferson via county roads 35 & 37 to Deadman Gulch SE to east of Jefferson Hill. | itinerary | Jefferson Hill | candidates_found | Jefferson Hill (Summit, Park, exact_official) | unsupported |
| F03 | Roadside rangeland between I-76 & railroad. | between_features |  |  |  | invalid_extraction |
| F04 | Top of range near Ivanhoe. | named_feature |  |  |  | invalid_extraction |
| F05 | Near Teller Lake. | named_feature | Teller Lake | candidates_found | Teller Lake (Reservoir, Gilpin, exact_official) | needs_information |
| F06 | About 5 miles NW of Rangely on Colorado Hwy 64. | distance_and_direction | Rangely | candidates_found | Rangely (Populated Place, Rio Blanco, exact_official) | computed |
| F07 | San Juan Nat. Forest: Tenmile Basin, Animas River drainage ca. 18 mi. S.E. of Silverton; alpine meadow west of Lake 12260', on shelf on the south side of the valley. | named_feature | Tenmile Basin | feature_absent_from_index |  | needs_information |
| F08 | Steep talus along Hwy. 40, 4 mi e. of Gunnison Co. line and 7 mi. e. of Parlin. | distance_and_direction | Gunnison Co. line | feature_absent_from_index |  | needs_information |
| F09 | State Route 131, 12.7 km (7.9 mi) north of Wolcott (measured from the Eagle River bridge). | route_relative | Wolcott | candidates_found | Wolcott (Populated Place, Eagle, exact_official) | unsupported |
| F10 | SE Pueblo County. Vigil & St. Vrain Grant. On Pipeline Road 10 mi S of jct with Hwy 10. | distance_and_direction |  |  |  | invalid_extraction |
| F11 | Spring Creek Mesa. [Neuguets Ranche.] [sp.?] | named_feature | Spring Creek Mesa | candidates_found | Spring Creek Mesa (Summit, Montrose, exact_official) | needs_information |
| F12 | White River National Forest; ~6 miles S of Minturn; N of Half Moon Pass | distance_and_direction | Minturn | candidates_found | Minturn (Populated Place, Eagle, exact_official) | needs_information |
| F13 | Bank of Boulder Creek at bridge on west end of White Rocks, 8 mi NE of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| F14 | Empire Pass. | named_feature | Empire Pass | candidates_found | Empire Pass (Gap, Clear Creek, exact_official) | needs_information |
| F15 | Black Canyon of the Gunnison National Monument, South rim, 1.2 mi. S of Visitior Center. | distance_and_direction | Visitior Center | feature_absent_from_index |  | needs_information |
| F16 | Devil's Creek. | named_feature | Devil's Creek | candidates_found | Devils Creek (Stream, Hinsdale, exact_official) | computed |
| F17 | San Juan National Forest: No-Name Basin, Animas River drainage, ca. 18 mi SE of Silverton. On the north side of Monitor. | named_feature | No-Name Basin | feature_absent_from_index |  | needs_information |
| F18 | Arapaho National Forest. Engelmann Peak, 3 miles north of Bakerville. | named_feature | Engelmann Peak | candidates_found | Engelmann Peak (Summit, Clear Creek, exact_official) | needs_information |
| F19 | Rocky Mountain National Park, Glacier Gorge Trail, 1 Mile SE of Bear Lake. | distance_and_direction | Bear Lake | candidates_found | Bear Lake (Lake, Larimer, exact_official) | computed |
| F20 | Specimen Mountain. | named_feature | Specimen Mountain | candidates_found | Specimen Mountain (Summit, Larimer, exact_official) | needs_information |
| F21 | Flat Tops/White River Plateau: meadows above Deep Creek, ca 15 air miles NE of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | needs_information |
| F22 | Cross Mountain Gorge. | named_feature | Cross Mountain Gorge | feature_absent_from_index |  | needs_information |
| F23 | Comanche National Grassland: Picture Canyon near restroom, 27.5 air mi SSW of Springfield. | distance_and_direction | Springfield | candidates_found | Springfield (Populated Place, Baca, exact_official) | needs_information |
| F24 | Upper Dolores River Drainage and Adjacent Areas: Paradox Valley area, ca 16 air mi W of Nucla on Davis Mesa along County Road DD16. | itinerary |  |  |  | invalid_extraction |
| F25 | Lippincott Property. Northernmost Jefferson County, parcel jointly owned by Jefferson County Open Space and City of Boulder OSMP, southwest segment of parcel, nearly up to the railroad tracks, 22.6 km. north northwest of the GNIS location of Golden. | distance_and_direction | Golden | candidates_found | Golden (Populated Place, Jefferson, exact_official) | computed |
| F26 | Southern Gunnison Basin: Sawatch Range: along Agate Creek near the Agate Creek Campground, ca 3 air mi NE of Sargents; ca 7.2 air mi W of Chipeta Mountain. | distance_and_direction | Sargents | candidates_found | Sargents (Populated Place, Saguache, exact_official) | needs_information |
| F27 | Rio Grande National Forest; ~9 miles WNW of Platoro; N of Crater Lake Trail | named_feature | Rio Grande National Forest | feature_absent_from_index |  | needs_information |
| F28 | Central Colorado: Gore Range, West Slope Continental Divide: Shrine Ridge Trail just NW of Shrine Pass, ca 12 air mi SE of Vail | distance_and_direction | Vail | candidates_found | Vail (Populated Place, Eagle, exact_official) | needs_information |
| F29 | Comanche National Grassland: N of David Canyon Road, ca 16 air mi S of La Junta. | distance_and_direction | La Junta | candidates_found | La Junta (Populated Place, Otero, exact_official) | computed |
| F30 | Colorado National Monument, north end, ca. 3 mi south of Fruita, above Coke Ovens Overlook. | orthogonal_offsets |  |  |  | invalid_extraction |
| F31 | Rocky Cliffs, 1 mile southwest of Cathedral. | distance_and_direction | Cathedral | candidates_found | Cathedral (Populated Place, Hinsdale, exact_official) | computed |
| F32 | Rio Grande National Forest; ~17 miles SSE of Platoro; "First Meadows" of Elk Creek | named_feature | Elk Creek | candidates_found | Elk Creek (Stream, Conejos, exact_official) | computed |
| F33 | Baca National Wildlife Refuge, San Luis Valley; ca. 1.8 miles southwest of Crestone. South of Crestone Creek near old cattle shelter. | named_feature | Baca National Wildlife Refuge | feature_absent_from_index |  | needs_information |
| F34 | Region of the Mesa de Maya. Side of Carrizo Mt., about 15 miles SE of Kim. | distance_and_direction | Kim | candidates_found | Kim (Populated Place, Las Animas, exact_official) | needs_information |
| F35 | West fork of Fawn Creek in White River National Forest, 6.5 mi. north of Buford. | distance_and_direction | Buford | candidates_found | Buford (Populated Place, Rio Blanco, exact_official) | needs_information |
| F36 | Little South Fork of Elk River, 2 mi S of Seedhouse G.S., Routt National Forest, ca 28 mi N of Steamboat Springs. | distance_and_direction | Seedhouse G.S. | feature_absent_from_index |  | needs_information |
| F37 | White River Plateau, ½ mile N of Crane Park. | distance_and_direction | Crane Park | candidates_found | Crane Park (Flat, Garfield, exact_official) | needs_information |
| F38 | Ranson/Edwards Homestead Open Space Park. High plains above Rocky Flats, 19.4 km. NNW of the GNIS location of Golden, 1.6 mi. west on CO Hwy 72 from CO Hwy 93, 0.9 mi. north on Plainview Road, then 290 m. west to a small reservoir. | itinerary | Ranson/Edwards Homestead Open Space Park | feature_absent_from_index |  | unsupported |
| F39 | Valley floors, head of Cottonwood Creek, an eastern tributary of Carrizo Creek, near the Bob Dodge Ranch, 7 mi. S and 16 mi. e. of Kim, just w. of the Baca Co. line. | orthogonal_offsets | Kim | candidates_found | Kim (Populated Place, Las Animas, exact_official) | unsupported |
| F40 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Transfer Campground area, junction of Chicken Creek Trail and Rim Trail, ca 6.5 air mi NE of Mancos. | orthogonal_offsets |  |  |  | invalid_extraction |
| F41 | North-central Colorado: Park Range: along old logging road between Jolley and Horse creeks, ca 4 air mi W of Kremmling. | orthogonal_offsets |  |  |  | invalid_extraction |
| F42 | San Luis Valley, ca. 7 mi. E of Hwy 17 along Sand Dunes entrance road; on greasewood flat near San Luis Lake. | distance_and_direction | Hwy 17 | feature_absent_from_index |  | needs_information |
| F43 | Manitou Experimental Forest, ca. 8 miles N of Woodland Park. 2 air miles east State Hwy 67, along Hotel Gulch Rd (349). | orthogonal_offsets |  |  |  | invalid_extraction |
| F44 | Arkansas River Valley. Palmer Land Trust private ranch, ca. 3.5 miles S of Wetmore near highway 96. Along Colo. Hwy 389 (Greenwood Road) and near Hardscrabble Creek. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| F45 | Monte Cristo Creek, 4 mi. N. of Hoosier Pass. | distance_and_direction | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | needs_information |
| F46 | Lost Creek Area, Tarryall Mtns., 80 km (50 mi) southwest of Denver and 80 km northwest of Colo. Springs; along trail to Hankins Pass. | itinerary |  |  |  | invalid_extraction |
| F47 | Arapaho National Forest, along Willow Creek, 0.2 mile downstream of Bronco Creek. | route_relative | Bronco Creek | candidates_found | Bronco Creek (Stream, Grand, exact_official) | unsupported |
| F48 | North Park, 10 mi. SE of Walden on E side of Owl Creek at main highway crossing. | named_feature | North Park | candidates_found | North Park (Flat, Jackson, exact_official) | needs_information |
| F49 | Peekaboo Basin, ca. 6.3 miles southwest of Hwy 82 on South Fork of Lake Creek road, San Isabel National Forest. | route_relative | Hwy 82 | feature_absent_from_index |  | unsupported |
| F50 | Rocky Mountain National Park. On top of Thunder Pass, 16 mi N of Grand Lake. | named_feature | Rocky Mountain National Park | feature_absent_from_index |  | needs_information |
