"""Known display names used by the map-cell inspector."""

MINERAL_NAMES = {
    0x10: "Coal", 0x20: "Iron", 0x30: "Gold", 0x40: "Gemstones", 0x50: "Sulfur",
}

TERRAIN_NAMES = {
    16: "Grass", 22: "Agricultural runtime", 24: "Yellow Grass",
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
