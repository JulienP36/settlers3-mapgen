"""Mask targets: composition order, previews and persistent fusion identity."""
from copy import deepcopy
from types import SimpleNamespace

import numpy as np

from s3mapgen.generation.archetypes.profiles import (
    default_archetype_profile, normalize_archetype_profile, has_active_mask_layers,
    remap_mask_targets,
)
from s3mapgen.generation.archetypes.morphology import (
    _apply_mask_layers_to_field, _configured_source_field, _fuse_source,
    apply_native_noise_layers, generate_noise_component_previews, build_noise_lab,
)
from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.generation.custom import build_custom_config


def setup_profile():
    p = default_archetype_profile()
    m = p['morphology']
    m['noise_layer_count'] = 2
    for fusion in m['noise_layers'][:2]:
        fusion.update(enabled=True, strength_percent=65, operation='blend')
    m['mask_layer_count'] = 1
    m['mask_layers'][0].update(enabled=True, type='ellipse', strength_percent=60, operation='multiply')
    return p


def test_old_profiles_keep_result_target_and_exact_output():
    p = setup_profile()
    raw = np.full((64, 64), 150, np.uint8)
    expected = apply_native_noise_layers(raw, p, seed=42)
    for mask in p['morphology']['mask_layers']:
        mask.pop('target')
    assert normalize_archetype_profile(p)['morphology']['mask_layers'][0]['target'] == 'result'
    np.testing.assert_array_equal(apply_native_noise_layers(raw, p, seed=42), expected)


def test_targets_operate_on_source_or_component_before_blending():
    p = setup_profile()
    p['morphology']['noise_layer_count'] = 1
    raw = np.full((64, 64), 150, np.uint8)
    fusion = p['morphology']['noise_layers'][0]
    results = []
    for target in ('source', 'fusion:0', 'result'):
        p['morphology']['mask_layers'][0]['target'] = target
        source = raw.astype(np.float32) / 255
        component, domain = _configured_source_field(64, 42 ^ 0x9E3779B9, fusion['source'], fusion['settings'], p, fusion['mask_settings'])
        if target == 'source':
            source, _ = _apply_mask_layers_to_field(source, p, 42, target=target)
        if target == 'fusion:0':
            component, _ = _apply_mask_layers_to_field(component, p, 42, target=target)
            component = np.where(domain, component, 0)
        expected = _fuse_source(source, component, domain, fusion['operation'], fusion['strength_percent'])
        if target == 'result':
            expected, _ = _apply_mask_layers_to_field(expected, p, 42)
        result = apply_native_noise_layers(raw, p, seed=42)
        np.testing.assert_array_equal(result, np.rint(expected * 255).astype(np.uint8))
        results.append(result)
    assert all(np.any(a != b) for a, b in zip(results, results[1:]))


def test_unavailable_targets_are_inert_and_do_not_change_source():
    p = setup_profile()
    raw = np.full((64, 64), 150, np.uint8)
    for target in ('fusion:5', 'missing:0', 'fusion:0'):
        p['morphology']['mask_layers'][0]['target'] = target
        p['morphology']['noise_layers'][0]['enabled'] = False
        assert not has_active_mask_layers(p)
        disabled = deepcopy(p)
        disabled['morphology']['mask_layer_count'] = 0
        np.testing.assert_array_equal(apply_native_noise_layers(raw, p, seed=42), apply_native_noise_layers(raw, disabled, seed=42))


def test_mask_order_and_previews_include_only_their_own_target():
    p = setup_profile()
    m = p['morphology']
    m['mask_layers'][0]['target'] = 'source'
    raw = np.full((64, 64), 150, np.uint8)
    principal, _ = generate_noise_component_previews(p, 64, 42, source_height=raw)
    np.testing.assert_array_equal(principal, build_noise_lab(raw, p, seed=42).source_height)
    m['mask_layer_count'] = 2
    m['mask_layers'][1] = deepcopy(m['mask_layers'][0])
    m['mask_layers'][1].update(operation='blend', type='star', order=1)
    before = apply_native_noise_layers(raw, p, seed=42)
    m['mask_layers'][:2] = m['mask_layers'][1::-1]
    after = apply_native_noise_layers(raw, p, seed=42)
    assert np.any(before != after)
    m['mask_layer_count'] = 1
    m['mask_layers'][0]['target'] = 'fusion:0'
    cache = {}
    source_a, active = generate_noise_component_previews(p, 64, 42, component_cache=cache)
    m['noise_layers'][0]['enabled'] = False
    source_b, disabled = generate_noise_component_previews(p, 64, 42, component_cache=cache)
    np.testing.assert_array_equal(source_a, source_b)
    np.testing.assert_array_equal(active[1], disabled[1])
    assert np.any(active[0] != disabled[0])
    m['noise_layers'][0]['enabled'] = True
    _, active_again = generate_noise_component_previews(p, 64, 42, component_cache=cache)
    np.testing.assert_array_equal(active[0], active_again[0])


def test_fusion_actions_preserve_masks_and_deletion_never_reattaches():
    c = CustomGeneratorController()
    p = setup_profile()
    p['morphology']['mask_layers'][0]['target'] = 'fusion:0'
    c._custom_config = build_custom_config('upgraded', 'continental').with_archetype_profile(p)
    c._custom_ensure_config = lambda *args: c._custom_config
    c._custom_current_mode = lambda: 'upgraded'
    c._custom_current_archetype = lambda: 'continental'
    c._custom_archetype_noise_layer_solo = None
    c._custom_status_var = SimpleNamespace(set=lambda message: None)
    def commit(config, layers, count):
        profile = config.archetype_profile
        profile['morphology'].update(noise_layers=layers, noise_layer_count=count)
        c._custom_config = config.with_archetype_profile(profile)
    c._custom_commit_archetype_noise_layer_stack = commit
    c._custom_archetype_noise_layer_reorder(0, 1)
    assert c._custom_config.archetype_profile['morphology']['mask_layers'][0]['target'] == 'fusion:1'
    c._custom_archetype_noise_layer_duplicate(0)
    assert c._custom_config.archetype_profile['morphology']['mask_layers'][0]['target'] == 'fusion:2'
    c._custom_archetype_noise_layer_remove(2)
    assert c._custom_config.archetype_profile['morphology']['mask_layers'][0]['target'] == 'missing:2'
    c._custom_archetype_noise_layer_duplicate(0)
    target = c._custom_config.archetype_profile['morphology']['mask_layers'][0]['target']
    assert target == 'missing:2'
    assert remap_mask_targets([{'target': target}], {2: 0})[0]['target'] == target
