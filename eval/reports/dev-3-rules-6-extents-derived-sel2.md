# dev-3: rules baseline (`rules-6`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-3/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the rules ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `distance_and_direction` 26 · `named_feature` 15 · `direction_only` 4 · `between_features` 2 · `other` 1 · `route_relative` 1 · `orthogonal_offsets` 1

**retrieval**: `candidates_found` 37 · `feature_absent_from_index` 9 · `no_reference_feature` 4

**proposal**: `needs_information` 35 · `computed` 10 · `unsupported` 5

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| F01 | Between Yampa and Toponas. | between_features |  | no_reference_feature |  | unsupported |
| F02 | Several miles north of the town of Jefferson via county roads 35 & 37 to Deadman Gulch SE to east of Jefferson Hill. | direction_only | Jefferson Hill | candidates_found | Jefferson Hill (Summit, Park, exact_official) | needs_information |
| F03 | Roadside rangeland between I-76 & railroad. | other |  | no_reference_feature |  | unsupported |
| F04 | Top of range near Ivanhoe. | named_feature | Ivanhoe | feature_absent_from_index |  | needs_information |
| F05 | Near Teller Lake. | named_feature | Near Teller Lake | feature_absent_from_index |  | needs_information |
| F06 | About 5 miles NW of Rangely on Colorado Hwy 64. | distance_and_direction | Rangely | candidates_found | Rangely (Populated Place, Rio Blanco, exact_official) | computed |
| F07 | San Juan Nat. Forest: Tenmile Basin, Animas River drainage ca. 18 mi. S.E. of Silverton; alpine meadow west of Lake 12260', on shelf on the south side of the valley. | distance_and_direction | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| F08 | Steep talus along Hwy. 40, 4 mi e. of Gunnison Co. line and 7 mi. e. of Parlin. | distance_and_direction | Parlin | candidates_found | Parlin (Populated Place, Gunnison, exact_official) | needs_information |
| F09 | State Route 131, 12.7 km (7.9 mi) north of Wolcott (measured from the Eagle River bridge). | direction_only | Wolcott | candidates_found | Wolcott (Populated Place, Eagle, exact_official) | needs_information |
| F10 | SE Pueblo County. Vigil & St. Vrain Grant. On Pipeline Road 10 mi S of jct with Hwy 10. | named_feature | Vigil | candidates_found | Vigil (Populated Place, Las Animas, exact_official) | needs_information |
| F11 | Spring Creek Mesa. [Neuguets Ranche.] [sp.?] | named_feature | Spring Creek Mesa | candidates_found | Spring Creek Mesa (Summit, Montrose, exact_official) | needs_information |
| F12 | White River National Forest; ~6 miles S of Minturn; N of Half Moon Pass | distance_and_direction | Minturn | candidates_found | Minturn (Populated Place, Eagle, exact_official) | needs_information |
| F13 | Bank of Boulder Creek at bridge on west end of White Rocks, 8 mi NE of Boulder. | distance_and_direction | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| F14 | Empire Pass. | named_feature | Empire Pass | candidates_found | Empire Pass (Gap, Clear Creek, exact_official) | needs_information |
| F15 | Black Canyon of the Gunnison National Monument, South rim, 1.2 mi. S of Visitior Center. | distance_and_direction | Visitior Center | feature_absent_from_index |  | needs_information |
| F16 | Devil's Creek. | named_feature | Devil's Creek | candidates_found | Devils Creek (Stream, Hinsdale, exact_official) | computed |
| F17 | San Juan National Forest: No-Name Basin, Animas River drainage, ca. 18 mi SE of Silverton. On the north side of Monitor. | distance_and_direction | Silverton | candidates_found | Silverton (Populated Place, San Juan, exact_official) | needs_information |
| F18 | Arapaho National Forest. Engelmann Peak, 3 miles north of Bakerville. | named_feature | Arapaho National Forest | feature_absent_from_index |  | needs_information |
| F19 | Rocky Mountain National Park, Glacier Gorge Trail, 1 Mile SE of Bear Lake. | distance_and_direction | Bear Lake | candidates_found | Bear Lake (Lake, Larimer, exact_official) | computed |
| F20 | Specimen Mountain. | named_feature | Specimen Mountain | candidates_found | Specimen Mountain (Summit, Larimer, exact_official) | needs_information |
| F21 | Flat Tops/White River Plateau: meadows above Deep Creek, ca 15 air miles NE of Glenwood Springs. | distance_and_direction | Glenwood Springs | candidates_found | Glenwood Springs (Populated Place, Garfield, exact_official) | computed |
| F22 | Cross Mountain Gorge. | named_feature | Cross Mountain Gorge | feature_absent_from_index |  | needs_information |
| F23 | Comanche National Grassland: Picture Canyon near restroom, 27.5 air mi SSW of Springfield. | distance_and_direction | Springfield | candidates_found | Springfield (Populated Place, Baca, exact_official) | needs_information |
| F24 | Upper Dolores River Drainage and Adjacent Areas: Paradox Valley area, ca 16 air mi W of Nucla on Davis Mesa along County Road DD16. | distance_and_direction | Nucla | candidates_found | Nucla (Populated Place, Montrose, exact_official) | needs_information |
| F25 | Lippincott Property. Northernmost Jefferson County, parcel jointly owned by Jefferson County Open Space and City of Boulder OSMP, southwest segment of parcel, nearly up to the railroad tracks, 22.6 km. north northwest of the GNIS location of Golden. | direction_only | GNIS | feature_absent_from_index |  | needs_information |
| F26 | Southern Gunnison Basin: Sawatch Range: along Agate Creek near the Agate Creek Campground, ca 3 air mi NE of Sargents; ca 7.2 air mi W of Chipeta Mountain. | distance_and_direction | Sargents | candidates_found | Sargents (Populated Place, Saguache, exact_official) | needs_information |
| F27 | Rio Grande National Forest; ~9 miles WNW of Platoro; N of Crater Lake Trail | distance_and_direction | Platoro | candidates_found | Platoro (Populated Place, Conejos, exact_official) | needs_information |
| F28 | Central Colorado: Gore Range, West Slope Continental Divide: Shrine Ridge Trail just NW of Shrine Pass, ca 12 air mi SE of Vail | distance_and_direction | Vail | candidates_found | Vail (Populated Place, Eagle, exact_official) | needs_information |
| F29 | Comanche National Grassland: N of David Canyon Road, ca 16 air mi S of La Junta. | distance_and_direction | La Junta | candidates_found | La Junta (Populated Place, Otero, exact_official) | computed |
| F30 | Colorado National Monument, north end, ca. 3 mi south of Fruita, above Coke Ovens Overlook. | distance_and_direction | Fruita | candidates_found | Fruita (Populated Place, Mesa, exact_official) | computed |
| F31 | Rocky Cliffs, 1 mile southwest of Cathedral. | distance_and_direction | Cathedral | candidates_found | Cathedral (Populated Place, Hinsdale, exact_official) | computed |
| F32 | Rio Grande National Forest; ~17 miles SSE of Platoro; "First Meadows" of Elk Creek | distance_and_direction | Platoro | candidates_found | Platoro (Populated Place, Conejos, exact_official) | needs_information |
| F33 | Baca National Wildlife Refuge, San Luis Valley; ca. 1.8 miles southwest of Crestone. South of Crestone Creek near old cattle shelter. | distance_and_direction | Crestone | candidates_found | Crestone (Populated Place, Saguache, exact_official) | needs_information |
| F34 | Region of the Mesa de Maya. Side of Carrizo Mt., about 15 miles SE of Kim. | distance_and_direction | Kim | candidates_found | Kim (Populated Place, Las Animas, exact_official) | computed |
| F35 | West fork of Fawn Creek in White River National Forest, 6.5 mi. north of Buford. | distance_and_direction | Buford | candidates_found | Buford (Populated Place, Rio Blanco, exact_official) | needs_information |
| F36 | Little South Fork of Elk River, 2 mi S of Seedhouse G.S., Routt National Forest, ca 28 mi N of Steamboat Springs. | distance_and_direction | Seedhouse G | feature_absent_from_index |  | needs_information |
| F37 | White River Plateau, ½ mile N of Crane Park. | distance_and_direction | Crane Park | candidates_found | Crane Park (Flat, Garfield, exact_official) | needs_information |
| F38 | Ranson/Edwards Homestead Open Space Park. High plains above Rocky Flats, 19.4 km. NNW of the GNIS location of Golden, 1.6 mi. west on CO Hwy 72 from CO Hwy 93, 0.9 mi. north on Plainview Road, then 290 m. west to a small reservoir. | route_relative |  | no_reference_feature |  | unsupported |
| F39 | Valley floors, head of Cottonwood Creek, an eastern tributary of Carrizo Creek, near the Bob Dodge Ranch, 7 mi. S and 16 mi. e. of Kim, just w. of the Baca Co. line. | orthogonal_offsets | Kim | candidates_found | Kim (Populated Place, Las Animas, exact_official) | unsupported |
| F40 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Transfer Campground area, junction of Chicken Creek Trail and Rim Trail, ca 6.5 air mi NE of Mancos. | distance_and_direction | Mancos | candidates_found | Mancos (Populated Place, Montezuma, exact_official) | computed |
| F41 | North-central Colorado: Park Range: along old logging road between Jolley and Horse creeks, ca 4 air mi W of Kremmling. | between_features |  | no_reference_feature |  | unsupported |
| F42 | San Luis Valley, ca. 7 mi. E of Hwy 17 along Sand Dunes entrance road; on greasewood flat near San Luis Lake. | named_feature | San Luis Valley | candidates_found | San Luis Valley (Valley, Alamosa, exact_official) | needs_information |
| F43 | Manitou Experimental Forest, ca. 8 miles N of Woodland Park. 2 air miles east State Hwy 67, along Hotel Gulch Rd (349). | named_feature | Manitou Experimental Forest | feature_absent_from_index |  | needs_information |
| F44 | Arkansas River Valley. Palmer Land Trust private ranch, ca. 3.5 miles S of Wetmore near highway 96. Along Colo. Hwy 389 (Greenwood Road) and near Hardscrabble Creek. | distance_and_direction | Wetmore | candidates_found | Wetmore (Populated Place, Custer, exact_official) | needs_information |
| F45 | Monte Cristo Creek, 4 mi. N. of Hoosier Pass. | distance_and_direction | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | needs_information |
| F46 | Lost Creek Area, Tarryall Mtns., 80 km (50 mi) southwest of Denver and 80 km northwest of Colo. Springs; along trail to Hankins Pass. | direction_only | Denver | candidates_found | Denver (Populated Place, Denver, exact_official) | needs_information |
| F47 | Arapaho National Forest, along Willow Creek, 0.2 mile downstream of Bronco Creek. | named_feature | Willow Creek | candidates_found | Willow Creek (Stream, Grand, exact_official) | needs_information |
| F48 | North Park, 10 mi. SE of Walden on E side of Owl Creek at main highway crossing. | named_feature | North Park | candidates_found | North Park (Flat, Jackson, exact_official) | needs_information |
| F49 | Peekaboo Basin, ca. 6.3 miles southwest of Hwy 82 on South Fork of Lake Creek road, San Isabel National Forest. | named_feature | Peekaboo Basin | feature_absent_from_index |  | needs_information |
| F50 | Rocky Mountain National Park. On top of Thunder Pass, 16 mi N of Grand Lake. | named_feature | Thunder Pass | candidates_found | Thunder Pass (Gap, Jackson, exact_official) | needs_information |
