from copy import deepcopy
import json

import numpy as np
import pytest

from s3mapgen.generation.object_quotas import (
    ObjectQuotaBasis, density_target, support_reference,
    quota_geometry_signature, quota_preview_input, estimate_stone_quota,
)
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation import MapGenerator
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE, MAP_SCAFFOLD, EDM_SCAFFOLD
from s3mapgen.map_data.binary import export_with_scaffold, parse_parts


def test_density_is_linear_in_compatible_support_and_percent_without_a_second_size_factor():
    for seed in range(20):
        full = density_target(1000, 10000, 10000, seed=seed, channel='trees')
        half = density_target(1000, 5000, 10000, seed=seed, channel='trees')
        doubled = density_target(1000, 5000, 10000, 200, seed=seed, channel='trees')
        assert (full, half, doubled) == (1000, 500, 1000)
        assert density_target(1000, 0, 10000, seed=seed) == 0
        assert density_target(1000, 5000, 10000, 0, seed=seed) == 0


def test_seeded_fractional_rounding_keeps_rare_objects_without_a_forced_minimum():
    outcomes = [density_target(8, 500, 10000, seed=s, channel='palms') for s in range(1024)]
    assert set(outcomes) == {0, 1}
    assert abs(np.mean(outcomes) - .4) < .04
    assert outcomes == [density_target(8, 500, 10000, seed=s, channel='palms') for s in range(1024)]
    assert all(density_target(8, 500, 10000, 200, seed=s, channel='palms') >= outcomes[s] for s in range(1024))


def test_basis_ignores_objects_and_is_frozen_across_global_family_placement():
    state = MapState.empty(64);state.terrain[:] = 16
    reserved = np.zeros((64, 64), bool);reserved[10:20, 10:20] = True
    basis = ObjectQuotaBasis.capture(state, reserved)
    assert basis.cells[16] == 62 * 62 - 100
    before = basis.target(100, (16,), channel='trees')
    state.objects[:] = 68
    state.terrain[:] = 64
    assert basis.target(100, (16,), channel='trees') == before
    assert basis.cells[64] == 0
    json.dumps(state.metadata)


def test_geometry_signature_keeps_object_edits_but_invalidates_terrain_changes():
    config = build_custom_config('upgraded', 'continental')
    sections = config.semantic_sections();sections['building_stones']['anchor_density_percent'] = 150
    assert quota_geometry_signature(config) == quota_geometry_signature(config.with_sections(sections))
    profile = deepcopy(config.archetype_profile);profile['relief']['mountain_threshold'] += 1
    assert quota_geometry_signature(config) != quota_geometry_signature(config.with_archetype_profile(profile))


def make_preview_state():
    config = build_custom_config('upgraded', 'continental')
    state = MapState.empty(64);state.terrain[:] = 16;state.metadata['seed'] = 42
    basis = ObjectQuotaBasis.capture(state)
    inputs = quota_preview_input(4, 42)
    state.metadata['object_quota_geometry_signature'] = quota_geometry_signature(config)
    state.metadata['object_quota_inputs'] = inputs
    return config, state, inputs


def test_preview_uses_only_matching_generation_support_and_handles_object_edits():
    config, state, inputs = make_preview_state()
    expected = density_target(1683, 62 * 62, support_reference((16,)), 150, seed=42, channel='stones.anchors')
    requested, kind, support = estimate_stone_quota(config, 64, 1683, 150, state=state, inputs=inputs)
    assert (requested, kind, support) == (expected, 'current', 62 * 62)
    sections=config.semantic_sections();sections['building_stones']['average_quantity']=7
    assert estimate_stone_quota(config.with_sections(sections),64,1683,150,state=state,inputs=inputs)[1] == 'current'


@pytest.mark.parametrize('change', ['seed', 'players', 'teams', 'nations', 'mirror_mode', 'start_algorithm'])
def test_preview_rejects_stale_generation_inputs(change):
    config, state, inputs = make_preview_state()
    altered = deepcopy(inputs)
    altered[change] = {'seed':43,'players':3,'teams':[1,1,2,2],'nations':[0,1,2,3],'mirror_mode':1,'start_algorithm':'fair'}[change]
    assert estimate_stone_quota(config,64,1683,100,state=state,inputs=altered)[1] == 'reference'


@pytest.mark.parametrize('mode', ['legacy', 'upgraded'])
def test_decoration_edit_preserves_unedited_families_and_legality(mode):
    generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    config=build_custom_config(mode,'continental');sections=config.semantic_sections();sections['decorations']['cacti']=150
    output=generator.generate(4,42,mode=mode,side=384,custom_config=config.with_sections(sections))
    state=output.state
    assert all(v.passed for v in output.validations if v.hard)
    for ids in (range(1,9),range(50,53),range(57,62)):
        assert np.count_nonzero(np.isin(state.objects,tuple(ids))) > 0
    assert np.all(state.terrain[np.isin(state.objects,(45,46,47,48))] == 64)


def test_supported_quotas_match_preview_exports_and_configured_stone_mean(tmp_path):
    generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    config=build_custom_config('upgraded','large_islands');sections=config.semantic_sections();sections['building_stones']['average_quantity']=7.5
    config=config.with_sections(sections)
    output=generator.generate(4,42,side=384,archetype='large_islands',custom_config=config)
    state=output.state
    assert all(v.passed for v in output.validations if v.hard)
    basis=state.metadata['object_quota_basis'];stones=state.metadata['upgraded_stones']
    assert basis['quotas']['stones.anchors']['requested'] == stones['global_anchor_requested']
    assert stones['global_anchor_requested'] < round(1683 / 4)
    active=stones['global_anchors']-stones['global_exhausted_anchors']
    assert abs(stones['global_stock'] - active*7.5) <= 1
    inputs=quota_preview_input(4,42)
    assert estimate_stone_quota(config,384,1683,100,state=state,inputs=inputs)[0] == stones['global_anchor_requested']
    for scaffold,suffix in ((MAP_SCAFFOLD,'map'),(EDM_SCAFFOLD,'edm')):
        path=tmp_path/f'quotas.{suffix}'
        export_with_scaffold(state,scaffold,path)
        assert 6 in dict(parse_parts(path,allow_terminal_padding=True)[1])
