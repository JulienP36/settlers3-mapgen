"""Construction stones: controls, collision geometry and exhausted states."""

import random

import numpy as np
import pytest

from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.generators.legacy.objects import add_building_stones, finalize_accessibility
from s3mapgen.generation.generators.upgraded.content import UpgradedContent
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.hexgrid import hex_distance


FOOTPRINT = [(-1, -1), (0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (1, 1)]


def stone_state(engine, *, groups=True, density=100, average=6, group_average=8, variation=0, side=64):
    state = MapState.empty(side)
    state.terrain[:] = 16
    state.objects[30, 30] = 68
    state.accessibility[30, 30] = 1
    cfg = dict(
        footprint=FOOTPRINT, anchor_min_hex_distance=4, active_ids=list(range(115, 127)),
        exhausted_id=127, global_anchor_target=100, global_stock_target=600,
        global_exhausted_anchor_target=5, cluster_share=0.3, cluster_centers=6,
        global_anchor_target_768=100 * (768 / side) ** 2,
        global_stock_target_768=600 * (768 / side) ** 2,
        anchor_density_percent=density, average_quantity=average,
        groups={
            'enabled': groups,
            'share_percent': 100,
            'stones_per_group': group_average,
            'stone_count_variation_percent': variation,
        },
    )
    if engine == 'legacy':
        meta = add_building_stones(state, {'legacy_content': {'building_stones': cfg}},
                                  np.zeros((side, side), bool), np.random.default_rng(12))
        finalize_accessibility(state)
    else:
        placer = UpgradedContent({})
        placer.side = placer.reference_side = side
        placer.profile = {'building_stones': cfg, 'starts': {'technical_clear_hex': 0}}
        placer._custom_sections = {'building_stones': cfg}
        placer._content_core = lambda _: np.zeros((side, side), bool)
        placer._core_mask = lambda *_: np.zeros((side, side), bool)
        placer._start_package_enabled = lambda _: False
        placer.log = lambda *_: None
        placer._place_building_stones(state, np.random.default_rng(12), random.Random(12))
        placer._final_accessibility(state)
        meta = state.metadata['upgraded_stones']
    return state, meta


@pytest.mark.parametrize('engine', ['legacy', 'upgraded'])
def test_stone_family_spacing_and_occupation(engine):
    state, _ = stone_state(engine)
    records = state.metadata['building_stone_anchors']
    for i, (x, y, quantity, _) in enumerate(records):
        if quantity:
            assert hex_distance(x, y, 30, 30) >= 3
            assert all(state.accessibility[y + dy, x + dx] == 1 for dx, dy in FOOTPRINT)
            for xx, yy, other, _ in records[i + 1:]:
                if other:
                    assert hex_distance(x, y, xx, yy) >= 4
        else:
            assert all(state.accessibility[y + dy, x + dx] == 0 for dx, dy in FOOTPRINT)
    assert len(state.metadata['building_stone_footprint_cells']) == 7 * sum(q > 0 for _, _, q, _ in records)


@pytest.mark.parametrize('engine', ['legacy', 'upgraded'])
def test_groups_can_be_disabled_without_losing_the_share(engine):
    state, meta = stone_state(engine, groups=False)
    assert meta['cluster_placed'] == 0
    assert meta['groups_enabled'] is False
    assert len(state.metadata['building_stone_anchors']) == 100


@pytest.mark.parametrize('engine', ['legacy', 'upgraded'])
def test_group_average_controls_the_number_of_groups(engine):
    small_groups, small_meta = stone_state(engine, group_average=4)
    large_groups, large_meta = stone_state(engine, group_average=20)
    small_count = small_meta.get('cluster_centers', len(small_meta.get('group_centers', ())))
    large_count = large_meta.get('cluster_centers', len(large_meta.get('group_centers', ())))
    assert small_count > large_count
    assert 0 <= small_meta['cluster_placed'] <= small_meta['cluster_target']
    assert 0 <= large_meta['cluster_placed'] <= large_meta['cluster_target']
    assert len(small_groups.metadata['building_stone_anchors']) == 100
    assert len(large_groups.metadata['building_stone_anchors']) == 100


@pytest.mark.parametrize('engine', ['legacy', 'upgraded'])
def test_zero_quota_and_average_limits(engine):
    empty, _ = stone_state(engine, density=0)
    assert not np.any((empty.objects >= 115) & (empty.objects <= 127))
    for percent, quantity in ((0, 1), (200, 12)):
        state, _ = stone_state(engine, average=quantity)
        active = state.objects[(state.objects >= 115) & (state.objects <= 126)]
        assert np.all(127 - active == quantity)


@pytest.mark.parametrize('engine', ['legacy', 'upgraded'])
def test_average_quantity_uses_half_steps_and_the_full_active_range(engine):
    for requested_average in (6.5, 7.0, 11.5):
        state, meta = stone_state(engine, average=requested_average)
        records = state.metadata['building_stone_anchors']
        quantities = [quantity for _, _, quantity, _ in records if quantity > 0]

        assert meta['average_quantity'] == requested_average
        assert abs(sum(quantities) / len(quantities) - requested_average) < 0.02
        assert all(1 <= quantity <= 12 for quantity in quantities)
        if requested_average == 11.5:
            assert 1 not in quantities
        assert (
            meta.get('quantity_distribution_model') == 'full_range_mean_tilt'
            or meta.get('global_quantity_distribution_model') == 'full_range_mean_tilt'
        )


def test_group_defaults_and_roundtrip():
    for mode, enabled in [('legacy', False), ('upgraded', True)]:
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        assert sections['building_stones']['groups']['enabled'] is enabled
        sections['building_stones']['groups'].update(enabled=False, share_percent=70)
        stones = config.with_sections(sections).semantic_sections()['building_stones']
        assert stones['groups']['enabled'] is False
        assert stones['groups']['share_percent'] == 70


def test_stone_placement_reports_saturation_without_overlapping():
    state = MapState.empty(16)
    state.terrain[:] = 16
    cfg = dict(footprint=FOOTPRINT, anchor_min_hex_distance=4,
               active_ids=list(range(115, 127)), exhausted_id=127,
               global_anchor_target_768=1000000, global_stock_target_768=6000000)
    meta = add_building_stones(state, {'legacy_content': {'building_stones': cfg}},
                              np.ones((16, 16), bool), np.random.default_rng(1))
    assert meta['building_stone_target'] > 0
    assert meta['building_stone_anchors'] == 0


def test_group_checkbox_passes_a_boolean_to_the_configuration():
    from types import SimpleNamespace
    from s3mapgen.application.custom.controller import CustomGeneratorController

    config = build_custom_config('upgraded')
    received = []
    host = SimpleNamespace(
        _custom_language=lambda: 'fr', _custom_current_mode=lambda: 'upgraded',
        _custom_current_archetype=lambda: 'continental',
        _custom_ensure_config=lambda *_: config,
        _custom_activate=received.append,
    )
    CustomGeneratorController._custom_section_changed(host, ('building_stones', 'groups', 'enabled'), False)
    stones = received[0].semantic_sections()['building_stones']
    assert stones['groups']['enabled'] is False
    assert stones['groups']['share_percent'] == 30


def test_stone_average_editor_keeps_half_step_precision():
    from types import SimpleNamespace
    from s3mapgen.application.custom.controller import CustomGeneratorController

    config = build_custom_config('upgraded')
    received = []
    host = SimpleNamespace(
        _custom_language=lambda: 'fr', _custom_current_mode=lambda: 'upgraded',
        _custom_current_archetype=lambda: 'continental',
        _custom_ensure_config=lambda *_: config,
        _custom_activate=received.append,
    )
    CustomGeneratorController._custom_section_changed(
        host, ('building_stones', 'average_quantity'), '6.5'
    )
    assert received[0].semantic_sections()['building_stones']['average_quantity'] == 6.5
