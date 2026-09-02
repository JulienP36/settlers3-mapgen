from __future__ import annotations

WATER_IDS = tuple(range(8))
GRASS = 16
GRASS_DETAIL_IDS = (18, 19)
DRY_GRASS = 24
GRASS_IDS = (GRASS, *GRASS_DETAIL_IDS, DRY_GRASS)
BEE_NEST_IDS = tuple(range(247, 254))
ADULT_TREE_IDS = tuple(range(68, 78)) + (80, 81)
PALM_TREE_IDS = (78, 79)
# Confirmed object lifecycle groups from the 208–239 calibration.  The palm
# saplings are kept explicit so aggregate graph categories can expose them
# without losing their species-specific counts.
PLANTATION_IDS = (84,)
TREE_SAPLING_STAGE_2_IDS = (216, 217, 218, 219, 220, 222)
PALM_SAPLING_STAGE_2_IDS = (221,)
TREE_SAPLING_STAGE_1_IDS = (224, 225, 226, 227, 228, 230)
PALM_SAPLING_STAGE_1_IDS = (229,)
SAPLING_STAGE_2_IDS = TREE_SAPLING_STAGE_2_IDS + PALM_SAPLING_STAGE_2_IDS
SAPLING_STAGE_1_IDS = TREE_SAPLING_STAGE_1_IDS + PALM_SAPLING_STAGE_1_IDS
ROCK_TRANS_1 = 17
GRASS_DESERT_TRANS = 20
GRASS_SWAMP_TRANS = 21
ROCKY = 32
ROCK_TRANS_2 = 33
ROCKY_DETAIL = 34
ROCK_SNOW_TRANS = 35
SHORE = 48
DESERT = 64
DESERT_TRANS = 65
SWAMP = 80
SWAMP_TRANS = 81
RIVER_IDS = (96, 97, 98, 99)
SNOW = 128
SNOW_TRANS = 129
MUD = 23
MUD_TRANS_1 = 144
MUD_TRANS_2 = 145
MOUNTAIN_IDS = (17, 33, 32, 35, 129, 128)
MOUNTAIN_FAMILY_IDS = (*MOUNTAIN_IDS, ROCKY_DETAIL)
DESERT_IDS = (20, 65, 64)
SWAMP_IDS = (21, 81, 80)
MUD_IDS = (MUD, MUD_TRANS_1, MUD_TRANS_2)
HEX6 = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1))
HEX_STRUCTURE = ((1,1,0),(1,1,1),(0,1,1))

START_FOOTPRINT = tuple(
    (i-2, j-3)
    for j, row in enumerate((range(0,3),range(0,4),range(0,5),range(0,6),range(1,6),range(2,7),range(3,6),range(4,6)))
    for i in row
)
assert len(START_FOOTPRINT) == 33
