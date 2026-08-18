from __future__ import annotations

WATER_IDS = tuple(range(8))
GRASS = 16
ROCK_TRANS_1 = 17
GRASS_DESERT_TRANS = 20
GRASS_SWAMP_TRANS = 21
ROCKY = 32
ROCK_TRANS_2 = 33
ROCK_SNOW_TRANS = 35
SHORE = 48
DESERT = 64
DESERT_TRANS = 65
SWAMP = 80
SWAMP_TRANS = 81
RIVER_IDS = (96, 97, 98, 99)
SNOW = 128
SNOW_TRANS = 129
MOUNTAIN_IDS = (17, 33, 32, 35, 129, 128)
DESERT_IDS = (20, 65, 64)
SWAMP_IDS = (21, 81, 80)
HEX6 = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1))
HEX_STRUCTURE = ((1,1,0),(1,1,1),(0,1,1))

START_FOOTPRINT = tuple(
    (i-2, j-3)
    for j, row in enumerate((range(0,3),range(0,4),range(0,5),range(0,6),range(1,6),range(2,7),range(3,6),range(4,6)))
    for i in row
)
assert len(START_FOOTPRINT) == 33
