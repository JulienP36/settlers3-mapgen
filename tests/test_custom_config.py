from s3mapgen.generation.custom import (
    CustomGenerationConfig,
    build_custom_config,
    get_path,
    iter_parameter_descriptors,
    profile_digest,
    set_path,
)


def test_custom_profile_is_serializable_and_fingerprint_changes_with_values():
    config = build_custom_config()
    restored = CustomGenerationConfig.from_dict(config.to_dict())
    assert restored.to_dict() == config.to_dict()
    changed = config.with_value('trees.adult_global_target', 1)
    assert changed.digest != config.digest
    assert profile_digest(changed.to_dict()) == changed.digest


def test_custom_path_helpers_copy_nested_values_without_mutating_the_source():
    source = {'section': {'value': 4, 'items': [1, 2]}}
    changed = set_path(source, 'section.value', 8)
    assert get_path(source, 'section.value') == 4
    assert get_path(changed, ('section', 'value')) == 8
    changed['section']['items'].append(3)
    assert source['section']['items'] == [1, 2]


def test_parameter_catalog_discovers_new_scalar_leaves_and_skips_structural_fields():
    profile = {
        'profile_kind': 'upgraded',
        'side': 768,
        'trees': {'adult_global_target': 2736, 'forest_enabled': True},
    'new_section': {'ratio': 0.25, 'name': 'test', 'values': [1, 2]},
    }
    descriptors = iter_parameter_descriptors(profile)
    keys = {item.key for item in descriptors}
    assert 'trees.adult_global_target' in keys
    assert 'trees.forest_enabled' in keys
    assert 'new_section.ratio' in keys
    assert 'new_section.name' not in keys
    assert 'side' not in keys
    assert all(item.value_type in {'bool', 'int', 'float', 'str'} for item in descriptors)


def test_custom_profiles_remove_invariant_switches_and_metadata_names():
    from s3mapgen.generation.custom import build_custom_config, sanitize_custom_profile

    profile = {
        'profile_kind': 'upgraded',
        'river': {'stop_at_first_water': True, 'fish_forbidden': True, 'max_straight_run': 4},
        'water': {
            'cleanup_micro_water': True,
            'border_must_have_gradient': True,
            'terrain_ids': [1, 2],
        },
        'minerals': {'families': {'16': {'name': 'Coal', 'cells': 3}}},
    }
    cleaned = sanitize_custom_profile(profile)
    assert 'stop_at_first_water' not in cleaned['river']
    assert 'fish_forbidden' not in cleaned['river']
    assert 'cleanup_micro_water' not in cleaned['water']
    assert 'border_must_have_gradient' not in cleaned['water']
    assert cleaned['minerals']['families']['16']['name'] == 'Coal'
    assert cleaned['water']['terrain_ids'] == [1, 2]
    default_profile = build_custom_config().profile
    assert 'river' not in default_profile
    assert 'water' not in default_profile
    assert 'name' in default_profile['minerals']['families']['16']


def test_custom_parameter_labels_and_start_packages_follow_language():
    from s3mapgen.application.custom.i18n import parameter_group, parameter_label
    from s3mapgen.generation.custom import START_PACKAGE_CATALOG

    path = ('building_stones', 'global_stock_target')
    assert parameter_group(path, 'fr') == 'Pierres de construction'
    assert parameter_group(path, 'de') == 'Bausteine'
    assert parameter_label(path, 'es') == 'Piedras de construcción / Global Stock Objetivo'
    forest = next(item for item in START_PACKAGE_CATALOG if item.key == 'start_forest')
    assert forest.label('de') == 'Startwald'
    assert forest.localized_description('es').startswith('Árboles adultos')
