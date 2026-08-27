from s3mapgen.application.ui.viewer import MINERAL_NAMES, OBJECT_NAMES, TERRAIN_NAMES


def test_inspector_catalogues_keep_known_runtime_entries():
    assert MINERAL_NAMES[0x40] == "Gemstones"
    assert TERRAIN_NAMES[34] == "Rocky detail"
    assert OBJECT_NAMES[84] == "Small Tree"
    assert OBJECT_NAMES[127] == "Building Stone 13"
