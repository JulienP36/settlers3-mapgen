from s3mapgen.application.ui.viewer import (
    MINERAL_NAMES,
    OBJECT_NAMES,
    TERRAIN_NAMES,
    localized_object_name,
    localized_resource_text,
    localized_terrain_name,
)


def test_inspector_catalogues_keep_known_runtime_entries():
    assert MINERAL_NAMES[0x40] == "Gemstones"
    assert TERRAIN_NAMES[34] == "Rocky grass patch"
    assert OBJECT_NAMES[84] == "Small Tree"
    assert OBJECT_NAMES[127] == "Building Stone 13"


def test_inspector_names_are_localized_instead_of_showing_raw_tuple_values():
    assert localized_terrain_name(34, 'fr') == 'Patch d’herbe rocheuse'
    assert localized_terrain_name(34, 'en') == 'Rocky grass patch'
    assert localized_terrain_name(34, 'de') == 'Felsgrasfleck'
    assert localized_terrain_name(34, 'es') == 'Parche de hierba rocosa'
    assert localized_object_name(68, 'fr') == 'Bouleau 1'
    assert localized_object_name(68, 'en') == 'Birch 1'
    assert localized_object_name(68, 'de') == 'Birke 1'
    assert localized_object_name(68, 'es') == 'Abedul 1'
    assert localized_object_name(215, 'fr') == 'Objet inconnu 215'
    assert localized_resource_text(0, 7, 'fr') == 'Poisson 7'
    assert localized_resource_text(0, 7, 'de') == 'Fisch 7'
    assert localized_resource_text(32, 0x4A, 'es') == 'Gemas 10'
