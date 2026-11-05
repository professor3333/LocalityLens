# dev-2: rules baseline (`rules-5`)

Specimens `gbif-cu-2026-11-01` · gazetteer `gnis-co-2026-09-29` · policy `gbif-bp-2020/1` · seed `dev-2/1`

> System output only. Correctness needs Claude's annotations; the top candidate is the rules ranking, not a reviewed choice, and extents come from the reviewed-extent store where it has one.

**relation**: `named_feature` 24 · `distance_and_direction` 12 · `direction_only` 7 · `other` 5 · `between_features` 2

**retrieval**: `candidates_found` 36 · `no_reference_feature` 7 · `feature_absent_from_index` 7

**proposal**: `needs_information` 33 · `computed` 10 · `unsupported` 7

| id | locality | relation | reference | retrieval | top candidate | proposal |
|---|---|---|---|---|---|---|
| E01 | North-central Colorado:North Park: along County Road 6 in the vicinity of Trappers Gulch at the south end of Battle Ridge, ca 11 air mi WNW of Cowdrey; ca 17 air mi NW of Walden. | distance_and_direction | Cowdrey | candidates_found | Cowdrey (Populated Place, Jackson, exact_official) | needs_information |
| E02 | Lost Creek Area, Tarryall Mtn., 80 km (50mi) southwest of Denver and 80 km northwest of Colo. Springs. | direction_only | Denver | candidates_found | Denver (Populated Place, Denver, exact_official) | needs_information |
| E03 | Hugo, 0.7 mi. NW. Mount Calvary Cemetery. | distance_and_direction | Hugo | candidates_found | Hugo (Populated Place, Lincoln, exact_official) | needs_information |
| E04 | S. Arthur Henry Middle School, corner of W Bates and S Golden, Bear Valley, SW Denver. | other |  | no_reference_feature |  | unsupported |
| E05 | Tributary of the Colorado River, approx. 100 m above confluence with Colorado River, 1 mi NW of Blue Hill. | distance_and_direction | Blue Hill | candidates_found | Blue Hill (Summit, Eagle, exact_official) | needs_information |
| E06 | N.W. Moffat county. 6 mi SW of Greystone on NE-facing slope of Douglas Mountain. | distance_and_direction | Greystone | candidates_found | Greystone (Populated Place, Moffat, exact_official) | needs_information |
| E07 | Los Pinos (Bayfield). | named_feature | Bayfield | candidates_found | Bayfield (Populated Place, La Plata, exact_official) | computed |
| E08 | ½ mi. N of Almont. | distance_and_direction | Almont | candidates_found | Almont (Populated Place, Gunnison, exact_official) | needs_information |
| E09 | Neota Wilderness. 7 mi S of Hwy. 14 on Long Draw Rd. West of road on summit of Flattop Mountain. | distance_and_direction | Hwy | feature_absent_from_index |  | needs_information |
| E10 | Heil Valley Ranch, Ingersoll Quarry; | other |  | no_reference_feature |  | unsupported |
| E11 | Rio Grande National Forest; ~12 miles SE of South Fork; W of Forest Road 14 | distance_and_direction | South Fork | candidates_found | Cabin Creek (Stream, Boulder, exact_variant) | needs_information |
| E12 | Trail from Slavonia to Gilpin Lake and Continental Divide, Routt National Forest, ca. 30 mi. N of Steamboat Springs. | distance_and_direction | Steamboat Springs | candidates_found | Steamboat Springs (Populated Place, Routt, exact_official) | needs_information |
| E13 | Campus of University, Boulder. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| E14 | Artists glen, Pikes Peak region. | named_feature | Pikes Peak | candidates_found | Pikes Peak (Summit, El Paso, exact_official) | needs_information |
| E15 | Upper Dolores River Drainage and Adjacent Areas: San Juan National Forest: Forest Trail 607, S of Colo Hwy 145, ca 16 air mi NE of Dolores on Morrison Trail, Bear Creek drainage. | distance_and_direction | Dolores | candidates_found | Dolores (Populated Place, Montezuma, exact_official) | computed |
| E16 | Mosquito Range Mountains; High Creek Fen, The Nature Conservancy. South of Fairplay. | direction_only | Fairplay | candidates_found | Fairplay (Populated Place, Park, exact_official) | needs_information |
| E17 | S. Table Mt. S. facing slope just W. of Quaker rd. below mesa edge; common on 1980 burn site. | direction_only | Quaker | candidates_found | Quaker Mountain (Summit, Routt, core_official) | needs_information |
| E18 | Dinosaur National Monument. N of Bear Draw and Mantle Ranch Road. | direction_only | Bear Draw | candidates_found | Bear Draw (Valley, Moffat, exact_official) | needs_information |
| E19 | Rosalie Peak, Mt. Evans Wilderness, Arapahoe National Forest. | named_feature | Rosalie Peak | candidates_found | Rosalie Peak (Summit, Park, exact_official) | computed |
| E20 | Flat Tops/White River Plateau: ridge between Cyclone and Rough Creek drainages, ca 18 air mi WSW of Oak Creek. | between_features |  | no_reference_feature |  | unsupported |
| E21 | Clear Creek, near Wheat Ridge. | named_feature | Wheat Ridge | candidates_found | Wheat Ridge (Populated Place, Jefferson, exact_official) | needs_information |
| E22 | Near Beaver Creek. | named_feature | Near Beaver Creek | candidates_found | East Beaver Creek (Stream, Rio Blanco, fuzzy_official) | needs_information |
| E23 | Along the road up the mesa W of the National Bureau of Standards, Boulder. | direction_only | National Bureau of Standards | feature_absent_from_index |  | needs_information |
| E24 | Swede Spring on Cold Springs Mountain. | named_feature | Swede Spring | candidates_found | Swede Spring (Spring, Moffat, exact_official) | computed |
| E25 | Mesa Verde NP; Yucca House, east of new acquisition. | named_feature | Mesa Verde NP | candidates_found | Mesa Verde (Summit, Montezuma, fuzzy_official) | needs_information |
| E26 | Browns Park, Goose Refuge. | named_feature | Browns Park | candidates_found | Browns Park (Flat, Moffat, exact_official) | needs_information |
| E27 | Niwot Ridge, upper saddle. | named_feature | Niwot Ridge | candidates_found | Niwot Ridge (Ridge, Boulder, exact_official) | needs_information |
| E28 | 30 miles north of Craig. | distance_and_direction | Craig | candidates_found | Craig (Populated Place, Moffat, exact_official) | computed |
| E29 | Rocky Flats Site, 7 mi S of Boulder, on Rocky Flats Pediment. By Woman Ck. and in meadow S of Woman Ck. | named_feature | Rocky Flats Site | feature_absent_from_index |  | needs_information |
| E30 | 10 mi. W of Mosca SW of Great Sand dunes National Monument. | distance_and_direction | Mosca SW of Great Sand | feature_absent_from_index |  | needs_information |
| E31 | University camp between Nederland and Ward. | between_features |  | no_reference_feature |  | unsupported |
| E32 | Plains and mesas, Boulder. | named_feature | Boulder | candidates_found | Boulder (Populated Place, Boulder, exact_official) | computed |
| E33 | South side of Douglas Pass. | named_feature | Douglas Pass | candidates_found | Douglas Pass (Gap, Garfield, exact_official) | needs_information |
| E34 | Near small lake at summit of ridge above San Francisco Pass. | named_feature | San Francisco Pass | candidates_found | San Francisco Pass (Gap, Las Animas, exact_official) | needs_information |
| E35 | 4 miles east of Cahone. | distance_and_direction | Cahone | candidates_found | Cahone (Populated Place, Dolores, exact_official) | needs_information |
| E36 | Junction of road O and R, Pasture 5D. | other |  | no_reference_feature |  | unsupported |
| E37 | On Audubon Mt. | named_feature | On Audubon Mt. | feature_absent_from_index |  | needs_information |
| E38 | Slope of Blue Mesa a few miles southwest of Sapinero. | direction_only | Sapinero | candidates_found | Sapinero (Populated Place, Gunnison, exact_official) | needs_information |
| E39 | Milner Pass. | named_feature | Milner Pass | candidates_found | Milner Pass (Gap, Grand, exact_official) | computed |
| E40 | Hoosier Pass. | named_feature | Hoosier Pass | candidates_found | Hoosier Pass (Gap, Summit, exact_official) | computed |
| E41 | NCAR Mesa. | named_feature | NCAR Mesa | feature_absent_from_index |  | needs_information |
| E42 | North Fork Poudre. | named_feature | North Fork Poudre | feature_absent_from_index |  | needs_information |
| E43 | Arapahoe glacier. | named_feature | Arapahoe | candidates_found | Arapahoe (Populated Place, Cheyenne, exact_official) | needs_information |
| E44 | Medicine Bow Forest. | other |  | no_reference_feature |  | unsupported |
| E45 | Mt. Audubon. | named_feature | Mt. Audubon | candidates_found | Mount Audubon (Summit, Boulder, exact_official) | needs_information |
| E46 | Boulder Falls. | named_feature | Boulder Falls | candidates_found | Boulder Falls (Falls, Boulder, exact_official) | needs_information |
| E47 | Verdun. | other |  | no_reference_feature |  | unsupported |
| E48 | North slope, Minnehaha. | named_feature | Minnehaha | candidates_found | Minnehaha (Populated Place, El Paso, exact_official) | needs_information |
| E49 | Somerset. | named_feature | Somerset | candidates_found | Somerset (Populated Place, Gunnison, exact_official) | computed |
| E50 | North of Moffat. | direction_only | Moffat | candidates_found | Moffat (Populated Place, Saguache, exact_official) | needs_information |
