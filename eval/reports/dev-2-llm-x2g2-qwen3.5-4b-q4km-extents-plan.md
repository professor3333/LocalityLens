# dev-2: LLM extraction (`llm-x2g2-qwen3.5-4b-q4km`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-2/1`

> System output only. Correctness needs the owner's annotations; the top candidate is the system's ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `named_feature` 26 · `distance_and_direction` 11 · `other` 5 · `orthogonal_offsets` 2 · `itinerary` 2 · `route_relative` 1 · `between_features` 1 · `no_locality` 1 · `direction_only` 1

**retrieval**: `candidates_found` 25 · `feature_absent_from_index` 13 · `None` 6 · `no_reference_feature` 6

**proposal**: `needs_information` 33 · `unsupported` 9 · `invalid_extraction` 6 · `computed` 2

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| E01 | North-central Colorado:North Park: along County Road 6 in the vicinity of Trappers Gulch at the south end of Battle Ridge, ca 11 air mi WNW of Cowdrey; ca 17 air mi NW of Walden. | distance_and_direction | Cowdrey | candidates_found | Cowdrey (Populated Place, Jackson, exact_official) | needs_information |
| E02 | Lost Creek Area, Tarryall Mtn., 80 km (50mi) southwest of Denver and 80 km northwest of Colo. Springs. | distance_and_direction |  |  |  | invalid_extraction |
| E03 | Hugo, 0.7 mi. NW. Mount Calvary Cemetery. | distance_and_direction | Hugo | candidates_found | Hugo (Populated Place, Lincoln, exact_official) | needs_information |
| E04 | S. Arthur Henry Middle School, corner of W Bates and S Golden, Bear Valley, SW Denver. | named_feature | S. Arthur Henry Middle School | feature_absent_from_index |  | needs_information |
| E05 | Tributary of the Colorado River, approx. 100 m above confluence with Colorado River, 1 mi NW of Blue Hill. | orthogonal_offsets |  |  |  | invalid_extraction |
| E06 | N.W. Moffat county. 6 mi SW of Greystone on NE-facing slope of Douglas Mountain. | distance_and_direction | Greystone | candidates_found | Greystone (Populated Place, Moffat, exact_official) | needs_information |
| E07 | Los Pinos (Bayfield). | named_feature | Los Pinos | feature_absent_from_index |  | needs_information |
| E08 | ½ mi. N of Almont. | distance_and_direction | Almont | candidates_found | Almont (Populated Place, Gunnison, exact_official) | needs_information |
| E09 | Neota Wilderness. 7 mi S of Hwy. 14 on Long Draw Rd. West of road on summit of Flattop Mountain. | orthogonal_offsets | Hwy. 14 | feature_absent_from_index |  | unsupported |
| E10 | Heil Valley Ranch, Ingersoll Quarry; | named_feature | Heil Valley Ranch | feature_absent_from_index |  | needs_information |
| E11 | Rio Grande National Forest; ~12 miles SE of South Fork; W of Forest Road 14 | distance_and_direction | South Fork | candidates_found | South Fork (Populated Place, Rio Grande, exact_official) | needs_information |
| E12 | Trail from Slavonia to Gilpin Lake and Continental Divide, Routt National Forest, ca. 30 mi. N of Steamboat Springs. | itinerary | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | unsupported |
| E13 | Campus of University, Boulder. | other |  | no_reference_feature |  | unsupported |
| E14 | Artists glen, Pikes Peak region. | other |  | no_reference_feature |  | unsupported |
| E15 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Forest Trail 607, S of Colo Hwy 145, ca 16 air mi NE of Dolores on Morrison Trail, Bear Creek drainage. | itinerary |  |  |  | invalid_extraction |
| E16 | Mosquito Range Mountains; High Creek Fen, The Nature Conservancy. South of Fairplay. | other |  | no_reference_feature |  | unsupported |
| E17 | S. Table Mt. S. facing slope just W. of Quaker rd. below mesa edge; common on 1980 burn site. | named_feature | S. Table Mt. | feature_absent_from_index |  | needs_information |
| E18 | Dinosaur National Monument. N of Bear Draw and Mantle Ranch Road. | named_feature | Dinosaur National Monument | feature_absent_from_index |  | needs_information |
| E19 | Rosalie Peak, Mt. Evans Wilderness, Arapahoe National Forest. | named_feature | Rosalie Peak | candidates_found | Rosalie Peak (Summit, Park, exact_official) | needs_information |
| E20 | Flat Tops/White River Plateau: ridge between Cyclone and Rough Creek drainages, ca 18 air mi WSW of Oak Creek. | distance_and_direction | Oak Creek | candidates_found | Oak Creek (Stream, Rio Blanco, exact_official) | needs_information |
| E21 | Clear Creek, near Wheat Ridge. | named_feature | Clear Creek | candidates_found | Clear Creek (Stream, Jackson, exact_official) | needs_information |
| E22 | Near Beaver Creek. | named_feature | Beaver Creek | candidates_found | Beaver Creek (Stream, Routt, exact_official) | needs_information |
| E23 | Along the road up the mesa W of the National Bureau of Standards, Boulder. | route_relative | National Bureau of Standards | feature_absent_from_index |  | unsupported |
| E24 | Swede Spring on Cold Springs Mountain. | named_feature | Cold Springs Mountain | candidates_found | Cold Springs (Spring, Conejos, core_official) | computed |
| E25 | Mesa Verde NP; Yucca House, east of new acquisition. | named_feature | Yucca House | feature_absent_from_index |  | needs_information |
| E26 | Browns Park, Goose Refuge. | named_feature | Browns Park | candidates_found | Browns Park (Flat, Moffat, exact_official) | needs_information |
| E27 | Niwot Ridge, upper saddle. | named_feature | Niwot Ridge | candidates_found | Niwot Ridge (Ridge, Boulder, exact_official) | needs_information |
| E28 | 30 miles north of Craig. | distance_and_direction | Craig | candidates_found | Craig (Populated Place, Moffat, exact_official) | needs_information |
| E29 | Rocky Flats Site, 7 mi S of Boulder, on Rocky Flats Pediment. By Woman Ck. and in meadow S of Woman Ck. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| E30 | 10 mi. W of Mosca SW of Great Sand dunes National Monument. | distance_and_direction |  |  |  | invalid_extraction |
| E31 | University camp between Nederland and Ward. | between_features |  |  |  | invalid_extraction |
| E32 | Plains and mesas, Boulder. | other |  | no_reference_feature |  | unsupported |
| E33 | South side of Douglas Pass. | named_feature | Douglas Pass | candidates_found | Douglas Pass (Gap, Garfield, exact_official) | needs_information |
| E34 | Near small lake at summit of ridge above San Francisco Pass. | named_feature | San Francisco Pass | candidates_found | San Francisco Pass (Gap, Las Animas, exact_official) | needs_information |
| E35 | 4 miles east of Cahone. | distance_and_direction | Cahone | candidates_found | Cahone (Populated Place, Dolores, exact_official) | needs_information |
| E36 | Junction of road O and R, Pasture 5D. | named_feature | Junction of road O and R | feature_absent_from_index |  | needs_information |
| E37 | On Audubon Mt. | named_feature | Audubon Mt. | candidates_found | Mount Audubon (Summit, Boulder, core_official) | needs_information |
| E38 | Slope of Blue Mesa a few miles southwest of Sapinero. | distance_and_direction |  |  |  | invalid_extraction |
| E39 | Milner Pass. | named_feature | Milner Pass | candidates_found | Milner Pass (Gap, Grand, exact_official) | needs_information |
| E40 | Hoosier Pass. | named_feature | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | computed |
| E41 | NCAR Mesa. | named_feature | NCAR Mesa | feature_absent_from_index |  | needs_information |
| E42 | North Fork Poudre. | named_feature | North Fork Poudre | feature_absent_from_index |  | needs_information |
| E43 | Arapahoe glacier. | named_feature | Arapahoe glacier | candidates_found | Arapaho Glacier (Glacier, Boulder, fuzzy_official) | needs_information |
| E44 | Medicine Bow Forest. | other |  | no_reference_feature |  | unsupported |
| E45 | Mt. Audubon. | named_feature | Mt. Audubon | candidates_found | Mount Audubon (Summit, Boulder, exact_official) | needs_information |
| E46 | Boulder Falls. | named_feature | Boulder Falls | candidates_found | Boulder Falls (Falls, Boulder, exact_official) | needs_information |
| E47 | Verdun. | named_feature | Verdun | feature_absent_from_index |  | needs_information |
| E48 | North slope, Minnehaha. | named_feature | Minnehaha | candidates_found | Minnehaha (Populated Place, El Paso, exact_official) | needs_information |
| E49 | Somerset. | no_locality |  | no_reference_feature |  | unsupported |
| E50 | North of Moffat. | direction_only | Moffat | candidates_found | Moffat (Populated Place, Saguache, exact_official) | needs_information |
