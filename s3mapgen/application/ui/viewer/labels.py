"""Known display names used by the map-cell inspector."""

MINERAL_NAMES = {
    0x10: "Coal", 0x20: "Iron", 0x30: "Gold", 0x40: "Gemstones", 0x50: "Sulfur",
}

TERRAIN_NAMES = {
    16: "Grass", 18: "Grass detail 1", 19: "Grass detail 2",
    22: "Agricultural runtime", 24: "Yellow Grass",
    28: "Worked/Path runtime", 32: "Rocky", 34: "Rocky detail",
    35: "Rock/Snow transition", 48: "Shore", 128: "Snow",
    129: "Snow transition", 96: "River 1", 97: "River 2",
    98: "River 3", 99: "River 4",
}

OBJECT_NAMES = {
    **{i: f"Big Stone {i}" for i in range(1, 9)},
    **{i: f"Stone {i - 8}" for i in range(9, 13)},
    **{i: f"Border Stone {i - 12}" for i in range(13, 21)},
    **{i: f"Small Stone {i - 20}" for i in range(21, 29)},
    **{i: f"Wreck {i - 28}" for i in range(29, 34)},
    34: "Grave",
    **{i: f"Small Plant {i - 34}" for i in range(35, 38)},
    **{i: f"Toadstool {i - 37}" for i in range(38, 41)},
    **{i: f"Tree Stump {i - 40}" for i in range(41, 43)},
    **{i: f"Dead Tree {i - 42}" for i in range(43, 45)},
    **{i: f"Cactus {i - 44}" for i in range(45, 49)},
    49: "Skeleton",
    **{i: f"Small Flower {i - 49}" for i in range(50, 53)},
    **{i: f"Small Bush {i - 52}" for i in range(53, 57)},
    **{i: f"Bush {i - 56}" for i in range(57, 62)},
    **{i: f"Reed {i - 61}" for i in range(62, 68)},
    68: "Birch 1", 69: "Birch 2", 70: "Elm 1", 71: "Elm 2", 72: "Oak",
    78: "Palm 1", 79: "Palm 2", 84: "Small Tree",
    **{i: f"Wheat {i - 84}" for i in range(85, 94)},
    **{i: f"Vine {i - 93}" for i in range(94, 103)},
    **{i: f"Rice {i - 102}" for i in range(103, 111)},
    **{i: f"Reef {i - 110}" for i in range(111, 115)},
    **{i: f"Building Stone {i - 114}" for i in range(115, 128)},
}

# Data-mapping entries confirmed by the controlled 208–239 and 240–255
# calibrations.  The three crash-prone probes (215, 223 and 231) deliberately
# remain unresolved instead of being presented as valid gameplay objects.
OBJECT_NAMES.update({
    **{i: f"Tree stump — variant {i - 207}" for i in range(208, 215)},
    **{i: f"Tree sapling — stage 2 — variant {i - 215}" for i in range(216, 221)},
    221: "Palm sapling — stage 2",
    222: "Tree sapling — stage 2 — variant 7",
    **{i: f"Tree sapling — stage 1 — variant {i - 223}" for i in range(224, 229)},
    229: "Palm sapling — stage 1",
    230: "Tree sapling — stage 1 — variant 7",
    232: "Resource panel — none",
    233: "Resource panel — coal",
    234: "Resource panel — abundant coal",
    235: "Resource panel — iron",
    236: "Resource panel — abundant iron",
    237: "Resource panel — gold",
    238: "Resource panel — abundant gold",
    239: "Resource panel — gemstones",
    240: "Mineral discovery panel 1",
    241: "Mineral discovery panel 2",
    242: "Mineral discovery panel 3",
    243: "Burning tree — stage 1",
    244: "Burning tree — stage 2",
    245: "Burning tree — stage 3",
    246: "Burning tree — stage 4",
    247: "Bee nest — stage 1",
    248: "Bee nest — stage 2",
    249: "Bee nest — stage 3",
    250: "Bee nest — stage 4",
    251: "Bee nest — stage 5",
    252: "Bee nest — stage 6",
    253: "Bee nest — stage 7",
    254: "Red territory marker",
    255: "Red flag",
})
