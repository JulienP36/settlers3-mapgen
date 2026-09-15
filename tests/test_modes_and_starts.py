import pytest
from s3mapgen.application.paths import LEGACY_PROFILE,UPGRADED_REFERENCE,LIBRARY
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.rules import PIPELINE_STAGES
from s3mapgen.generation.modes import MODES
from s3mapgen.generation.archetypes import ARCHETYPES

def gen():return MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)

ALL_START_PACKAGES = (
    'start_forest', 'start_building_stones', 'start_mini_swamp',
    'start_rocky_minerals', 'start_lake_fish_river',
)

@pytest.fixture(scope='module')
def upgraded4():return gen().generate(4,2026082202,mode='upgraded',archetype='continental')
@pytest.fixture(scope='module')
def upgraded20():return gen().generate(20,2026082203,mode='upgraded',archetype='continental')

def test_architecture_names_are_separate():
    assert set(MODES)=={'legacy','upgraded','custom'};assert 'continental' in ARCHETYPES;assert MODES['legacy'].implemented;assert MODES['upgraded'].implemented;assert MODES['custom'].implemented

def test_provisional_starts_are_kept_before_terrain_hydrology():assert PIPELINE_STAGES.index('starts.provisional_bridge') < PIPELINE_STAGES.index('hydrology.bathymetry')

def test_upgraded_4p_hard_validators(upgraded4):
    assert upgraded4.state.metadata['starts_placed_early'] is False;assert upgraded4.state.metadata['starts_placed_provisionally'] is True;assert all(v.passed for v in upgraded4.validations if v.hard);assert upgraded4.state.metadata['mode_key']=='upgraded'

def test_upgraded_20p_starts_survive_full_pipeline(upgraded20):
    assert len(upgraded20.state.starts)==20;assert all(v.passed for v in upgraded20.validations if v.hard)

def test_custom_uses_the_active_upgraded_profile():
    from s3mapgen.generation.custom import build_custom_config
    config = build_custom_config().with_value('trees.adult_global_target', 100)
    result = gen().generate(2,2026081901,mode='custom',archetype='continental',side=256,custom_config=config)
    assert result.state.metadata['mode_key']=='custom'
    assert result.state.metadata['generator']=='continental_custom_upgraded'
    assert result.state.metadata['custom_profile_applied'] is True
    assert result.state.metadata['custom_configuration_digest']==config.digest
    assert result.state.metadata['upgraded_trees']['adult_global_requested'] == 11
    assert all(v.passed for v in result.validations if v.hard)


def test_custom_upgraded_can_use_the_zero_native_mud_parameter():
    import numpy as np
    from s3mapgen.generation.custom import build_custom_config

    config = build_custom_config('upgraded')
    sections = config.semantic_sections()
    sections['terrains']['mud'] = {'enabled': True, 'rate_percent': 100}
    config = config.with_sections(sections)
    result = gen().generate(2, 20260905, mode='custom', archetype='continental', side=256, custom_config=config)

    assert np.isin(result.state.terrain, (23, 144, 145)).any()
    assert result.state.metadata['upgraded_mud_generation'] is True
    assert result.state.metadata['custom_terrain']['rates']['mud'] == 100.0
    assert all(v.passed for v in result.validations if v.hard)


def test_custom_upgraded_tree_and_stone_sections_change_global_quotas_only():
    from s3mapgen.generation.custom import build_custom_config

    config = build_custom_config('upgraded')
    sections = config.semantic_sections()
    sections['trees'].update({
        'base_quota_percent': 50,
        'saplings': {
            'enabled': True,
            'in_global_pool': False,
            'global_share_percent': 0,
            'quota_percent': 0,
            'placement': 'forests_only',
        },
        'forests': {
            'enabled': True,
            'share_percent': 100,
            'trees_per_forest': 21.6,
            'tree_count_variation_percent': 0,
        },
        'palm_quota_percent': 0,
    })
    sections['building_stones'].update({
        'anchor_density_percent': 50,
        'average_quantity': 6,
        'groups': {
            'enabled': False,
            'share_percent': 0,
            'stones_per_group': 8,
            'stone_count_variation_percent': 0,
        },
    })
    result = gen().generate(
        2,
        20260904,
        mode='custom',
        archetype='continental',
        side=256,
        custom_config=config.with_sections(sections),
    )

    trees = result.state.metadata['upgraded_trees']
    stones = result.state.metadata['upgraded_stones']
    assert trees['adult_global_requested'] == 152
    assert trees['small_global_requested'] == 0
    assert trees['palm_requested'] == 0
    assert trees['adult_start_bonus_placed'] == 0
    assert trees['forests_enabled'] is True
    assert trees['forest_share_percent'] == 100.0
    assert stones['global_anchor_requested'] == 94
    assert stones['cluster_requested'] == 0
    assert stones['global_stock_requested'] == stones['global_active_anchors'] * 6
    assert stones['average_quantity'] == 6
    assert all(value.passed for value in result.validations if value.hard)


def test_custom_upgraded_start_bonus_section_changes_player_bonuses():
    from s3mapgen.generation.custom import build_custom_config

    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["distance_from_border"] = 12
    sections["start_bonus"]["forest"].update(
        adult_trees_per_player=7,
        saplings_per_player=3,
        radius_min=3,
        radius_max=3,
    )
    sections["start_bonus"]["building_stones"].update(
        anchors_per_player=2,
        average_quantity=5.0,
        radius_min=3,
        radius_max=3,
    )
    sections["start_bonus"]["mini_swamp"].update(radius=1, shape="hexagon")
    sections["start_bonus"]["rocky_minerals"].update(
        radius_min=2,
        radius_max=2,
        coal={"enabled": True},
        iron={"enabled": False},
        gold={"enabled": False},
    )
    result = gen().generate(
        2,
        20260909,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config.with_sections(sections).with_start_packages(ALL_START_PACKAGES),
    )

    trees = result.state.metadata["upgraded_trees"]
    stones = result.state.metadata["upgraded_stones"]
    swamp = result.state.metadata["upgraded_start_mini_swamps"]
    rocky = result.state.metadata["upgraded_start_rocky_minerals"]
    assert trees["adult_start_bonus_requested"] == 14
    assert trees["adult_start_bonus_placed"] == 14
    assert trees["small_start_bonus_requested"] == 6
    assert trees["small_start_bonus_placed"] == 6
    assert stones["start_bonus_anchor_requested"] == 4
    assert stones["start_bonus_anchors"] == 4
    assert stones["start_bonus_stock_requested"] == 20
    assert stones["start_bonus_stock"] == 20
    assert swamp["requested_cells_per_start"] == 7
    assert swamp["placed_cells_per_start"] == [7, 7]
    assert rocky["distance_from_border"] == 12
    assert rocky["radius_min"] == rocky["radius_max"] == 2
    assert rocky["zones_requested_per_player"] == 1
    assert rocky["placed_zones"] == 2
    assert all(value.passed for value in result.validations if value.hard)


def test_custom_legacy_tree_and_stone_sections_replace_the_selected_object_families():
    from s3mapgen.generation.custom import build_custom_config

    config = build_custom_config('legacy')
    sections = config.semantic_sections()
    sections['trees']['base_quota_percent'] = 50
    sections['building_stones']['anchor_density_percent'] = 50
    result = gen().generate(
        2,
        20260904,
        mode='custom',
        archetype='continental',
        side=256,
        custom_config=config.with_sections(sections),
    )

    import numpy as np
    from s3mapgen.map_data.constants import GRASS_IDS

    trees = result.state.metadata['trees']
    stones = result.state.metadata['stones']
    assert result.state.metadata['custom_object_controls']['replaced'] == ('trees', 'stones')
    assert trees['tree_target'] == 152
    assert stones['building_stone_target'] == 94
    assert len(result.state.metadata['building_stone_footprint_cells']) == (stones['building_stone_anchors'] - stones['global_exhausted_anchors']) * 7
    stone_mask = np.isin(result.state.objects, tuple(range(115, 128)))
    assert np.all(np.isin(result.state.terrain[stone_mask], GRASS_IDS))
    assert all(value.passed for value in result.validations if value.hard)


def test_upgraded_builtin_uses_the_custom_preset_route_with_bonus_switches_off():
    result = gen().generate(
        3,
        2026081901,
        mode='upgraded',
        archetype='continental',
        side=384,
    )

    assert result.state.metadata['mode_key'] == 'upgraded'
    assert result.state.metadata['generator_route'] == 'custom_preset'
    assert result.state.metadata['upgraded_start_mini_swamps']['enabled'] is False
    assert result.state.metadata['upgraded_trees']['adult_start_bonus_placed'] == 0
    assert result.state.metadata['upgraded_stones']['start_bonus_anchors'] == 0
    assert all(value.passed for value in result.validations if value.hard)


def test_custom_start_packages_are_registry_driven():
    from s3mapgen.generation.custom import START_PACKAGE_CATALOG, build_custom_config
    config = build_custom_config().with_start_packages(())
    assert {item.key for item in START_PACKAGE_CATALOG} >= {
        'start_forest','start_building_stones','start_mini_swamp',
        'start_rocky_minerals','start_lake_fish_river',
    }
    result = gen().generate(2,2026081901,mode='custom',archetype='continental',side=256,custom_config=config)
    assert result.state.metadata['custom_start_packages']==[]
    assert result.state.metadata['upgraded_start_mini_swamps']['enabled'] is False
    assert result.state.metadata['upgraded_trees']['adult_start_bonus_placed']==0
    assert result.state.metadata['upgraded_stones']['start_bonus_anchors']==0
    assert all(v.passed for v in result.validations if v.hard)


def test_explicit_bonus_config_works_while_public_mode_stays_legacy_or_upgraded():
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        sections["start_bonus"]["forest"].update(
            adult_trees_per_player=4,
            saplings_per_player=2,
        )
        config = config.with_sections(sections).with_start_packages(("start_forest",))
        result = gen().generate(
            2,
            20260910,
            mode=mode,
            archetype="continental",
            side=256,
            custom_config=config,
        )

        assert result.state.metadata["mode_key"] == "custom"
        assert result.state.metadata["custom_profile_diagnostics"]["base_mode"] == mode
        if mode == "legacy":
            assert result.state.metadata["legacy_start_forest"]["adult_placed"] == 8
        else:
            assert result.state.metadata["upgraded_trees"]["adult_start_bonus_placed"] == 8
        assert all(value.passed for value in result.validations if value.hard)


def test_all_start_bonus_packages_work_on_both_public_base_routes():
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        sections["objects"]["grass_compatible_on_dry_and_details"] = True
        sections["start_bonus"]["forest"].update(
            adult_trees_per_player=4,
            saplings_per_player=2,
        )
        sections["start_bonus"]["building_stones"].update(
            anchors_per_player=2,
            average_quantity=5,
        )
        sections["start_bonus"]["mini_swamp"].update(radius=1, shape="hexagon")
        sections["start_bonus"]["rocky_minerals"].update(radius_min=2, radius_max=2)
        sections["start_bonus"]["lake_fish_river"].update(
            radius_min=4,
            radius_max=4,
            water_proximity_from_territory_border=0,
        )
        result = gen().generate(
            2,
            20260910,
            mode=mode,
            archetype="continental",
            side=384,
            custom_config=config.with_sections(sections).with_start_packages(ALL_START_PACKAGES),
        )

        metadata = result.state.metadata
        assert metadata["custom_profile_diagnostics"]["base_mode"] == mode
        assert metadata["upgraded_start_mini_swamps"]["enabled"] is True
        assert metadata["upgraded_start_rocky_minerals"]["enabled"] is True
        assert metadata["upgraded_start_lake_fish_river"]["enabled"] is True
        if mode == "legacy":
            assert metadata["legacy_start_forest"]["adult_placed"] == 8
            assert metadata["legacy_start_building_stones"]["anchors_placed"] == 4
        else:
            assert metadata["upgraded_trees"]["adult_start_bonus_placed"] == 8
            assert metadata["upgraded_stones"]["start_bonus_anchors"] == 4
        assert all(value.passed for value in result.validations if value.hard)


def test_custom_legacy_preserves_native_output_and_reports_deferred_overrides():
    from s3mapgen.generation.custom import build_custom_config
    result = gen().generate(2,2026081901,mode='custom',archetype='continental',side=256,custom_config=build_custom_config('legacy'))
    assert result.state.metadata['mode_key']=='custom'
    assert result.state.metadata['generator']=='continental_custom_legacy'
    assert result.state.metadata['custom_profile_applied'] is False
    assert result.state.metadata['custom_profile_diagnostics']['unapplied_sections']
    assert all(v.passed for v in result.validations if v.hard)


def test_legacy_custom_uses_historical_hex_mineral_placer():
    from s3mapgen.generation.custom import build_custom_config

    kwargs = dict(players=2, seed=2026081901, archetype='continental', side=256)
    legacy = gen().generate(**kwargs, mode='legacy')
    preset = build_custom_config('legacy')
    custom = gen().generate(
        **kwargs,
        mode='custom',
        custom_config=preset.with_sections(preset.semantic_sections()),
    )

    assert legacy.state.metadata['mode_key'] == 'legacy'
    assert custom.state.metadata['mode_key'] == 'custom'
    assert custom.state.metadata['minerals']['model'] == 'custom_legacy_hex_zones_r17'
    assert custom.state.metadata['minerals']['radius_choices'] == [3, 4, 5]
    assert custom.state.metadata['minerals']['placement'] == 'sequential_random_hex_zones_uniform_fill'


def test_custom_keeps_unimplemented_archetypes_guarded():
    with pytest.raises(NotImplementedError):
        gen().generate(2,2026081901,mode='custom',archetype='large_islands',side=256)

def test_legacy_native_rebuild_is_reachable():
    result=gen().generate(2,2026081901,mode='legacy',archetype='continental',side=384)
    assert result.state.metadata['mode_key']=='legacy'
    assert result.state.metadata['engine_revision'].endswith('native-legacy-v1')
    assert len(result.state.starts)==2
    assert all(v.passed for v in result.validations if v.hard)

def test_upgraded_native_mirror_is_reachable_on_small_test_maps():
    result=gen().generate(2,2026081901,mode='upgraded',archetype='continental',side=256,mirror_mode=3)
    assert result.state.metadata['mode_key']=='upgraded'
    assert result.state.metadata['native_mode_mask']==3
    assert result.state.metadata['native_mirror_main_diagonal'] is True
    assert result.state.metadata['native_mirror_anti_diagonal'] is True
    assert all(v.passed for v in result.validations if v.hard)

def test_reported_small_seed_finishes_without_relief_loop():
    result=gen().generate(2,297650040,mode='legacy',archetype='continental',side=256)
    assert result.state.side==256
    assert result.state.metadata['native_relief_relax_passes']<=128
    assert all(v.passed for v in result.validations if v.hard)

def test_legacy_native_tables_are_transcribed():
    from s3mapgen.generation.generators.legacy.native import NATIVE_NORMAL_START_FOOTPRINT,native_build_hex_offset_bank
    from s3mapgen.map_data.constants import START_FOOTPRINT
    bank=native_build_hex_offset_bank()
    assert len(bank)==19999
    assert [(o.dx,o.dy,o.ring,o.orientation) for o in bank[:7]]==[(0,0,0,0),(1,0,1,0),(1,1,1,1),(0,1,1,2),(-1,0,1,3),(-1,-1,1,4),(0,-1,1,5)]
    assert len(NATIVE_NORMAL_START_FOOTPRINT)==33
    assert set(NATIVE_NORMAL_START_FOOTPRINT)==set(START_FOOTPRINT)

def test_upgraded_snow_is_blocked_and_swamp_chain_is_legal(upgraded4):
    from s3mapgen.map_data.constants import SNOW,SNOW_TRANS
    import numpy as np
    snow=np.isin(upgraded4.state.terrain,[SNOW_TRANS,SNOW]);assert snow.any();assert np.all(upgraded4.state.accessibility[snow]==1)
    rules={v.rule_id:v for v in upgraded4.validations};assert rules['UPGRADED_WATER_ACCESS'].passed;assert rules['UPGRADED_NO_MUD'].passed


def test_upgraded_preset_keeps_start_content_opt_in(upgraded4):
    assert upgraded4.state.metadata['generator'] == 'continental_upgraded_native'
    assert upgraded4.state.metadata['upgraded_base_pipeline'] == 'independent_copy_of_continental_legacy_native'
    assert upgraded4.state.metadata['upgraded_start_content_deferred'] is False
    assert upgraded4.state.metadata['generator_route'] == 'custom_preset'
    assert upgraded4.state.metadata['upgraded_start_mini_swamps']['placed_cells_per_start'] == [0] * 4
    assert upgraded4.state.metadata['upgraded_trees']['adult_start_bonus_placed'] == 0
    assert upgraded4.state.metadata['upgraded_trees']['small_start_bonus_placed'] == 0
    assert upgraded4.state.metadata['upgraded_stones']['start_bonus_stock'] == 0
    assert not any(int(v) in (23, 144, 145) for v in upgraded4.state.terrain.flat)


def test_active_upgraded_profile_exposes_round_mineral_and_start_rules():
    from s3mapgen.generation.generators.upgraded.profile import load_profile
    profile = load_profile()
    minerals = profile['minerals']
    assert minerals['shares'] == {'16': 0.525, '32': 0.225, '48': 0.15, '64': 0.05, '80': 0.05}
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_space'] == 'parallelogram_compensated'
    assert minerals['blob_aspect_min'] == minerals['blob_aspect_max'] == 1.0
    assert profile['start_bonus']['building_stones']['stock_units_per_player'] == 150
    assert profile['start_bonus']['mini_swamp']['outside_technical_zone'] is True
    assert profile['trees']['adult_global_target'] == 2736
    assert profile['trees']['adult_cluster_share'] == 0.30
    assert profile['building_stones']['global_stock_target'] == 16338
    assert len(profile['decor']['legacy_static_families']) == 16


def test_upgraded_generation_records_the_active_mineral_shape_variant(upgraded4):
    minerals = upgraded4.state.metadata['upgraded_minerals']
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_aspect_range'] == [1.0, 1.0]
    assert minerals['shape_space'] == 'parallelogram_compensated'
    rules = upgraded4.state.metadata['upgraded_start_bonus_rules']
    assert rules['outside_global_quota'] is True
    assert rules['building_stones']['stock_units_per_player'] == 150


def test_upgraded_default_resource_quantities_target_mean_ten_without_multiplier(upgraded4):
    import numpy as np

    resources = upgraded4.state.resources
    for family in (0x10, 0x20, 0x30, 0x40, 0x50):
        values = (resources[(resources & 0xF0) == family] & 0x0F).astype(float)
        assert len(values) > 0
        assert values.mean() == pytest.approx(10.0, abs=0.01)
    fish = resources[((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)].astype(np.uint8)
    assert len(fish) > 0
    assert (fish & 0x0F).astype(float).mean() == pytest.approx(10.0, abs=0.01)
    assert upgraded4.state.metadata['upgraded_fish']['quantity_multiplier_applied'] is False


def test_upgraded_uses_legacy_static_quotas_and_stone_states(upgraded4):
    decorations = upgraded4.state.metadata['upgraded_decorations']
    assert not any(decorations['legacy_static_shortfalls'].values())
    assert decorations['legacy_static']['reefs'] == 20
    stones = upgraded4.state.metadata['upgraded_stones']
    assert stones['global_anchors'] == 1683
    assert stones['global_stock'] == 16338
    assert 0 <= stones['global_exhausted_anchors'] <= stones['global_anchors']
    assert stones['cluster_placed'] == stones['cluster_target']
    assert all(stones['id_counts'][str(object_id)] > 0 for object_id in range(115, 127))


def test_upgraded_start_bonuses_are_additional_and_forests_keep_legacy_spacing(upgraded4):
    from s3mapgen.map_data.hexgrid import hex_distance
    import numpy as np

    trees = upgraded4.state.metadata['upgraded_trees']
    assert trees['global_quota_excludes_start_bonus'] is True
    assert trees['adult_global_placed'] == trees['adult_global_requested'] == 2736
    assert trees['small_global_placed'] == trees['small_global_requested'] == 1067
    assert trees['adult_trees'] == trees['adult_global_placed'] + trees['adult_start_bonus_placed']
    assert trees['small_trees'] == trees['small_global_placed'] + trees['small_start_bonus_placed']
    assert trees['adult_start_bonus_placed'] == 0
    assert trees['small_start_bonus_placed'] == 0
    assert trees['adult_forest_min_hex_distance'] == 3
    assert all(row['adult'] == 0 for row in trees['start_forests'])

    adult_ids = tuple(range(68, 78)) + (80, 81)
    adult_points = [
        (int(x), int(y))
        for y, x in np.argwhere(np.isin(upgraded4.state.objects, adult_ids))
    ]
    for forest in trees['global_forests'] + trees['start_forests']:
        if 'center_x' not in forest:
            continue
        points = [
            (x, y)
            for x, y in adult_points
            if hex_distance(forest['center_x'], forest['center_y'], x, y)
            <= forest.get('effective_radius', forest['radius'])
        ]
        for index, (x, y) in enumerate(points):
            nearest = min(
                (hex_distance(x, y, xx, yy) for other, (xx, yy) in enumerate(points) if other != index),
                default=trees['adult_forest_min_hex_distance'],
            )
            assert nearest >= trees['adult_forest_min_hex_distance']

    stones = upgraded4.state.metadata['upgraded_stones']
    assert stones['global_quota_excludes_start_bonus'] is True
    assert stones['anchors'] == stones['global_anchors']
    assert stones['stock'] == stones['global_stock']
    assert stones['global_anchors'] == 1683
    assert stones['global_stock'] == 16338
