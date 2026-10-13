"""Exact permission masks and display preferences, six functional scenarios."""
from copy import deepcopy
import numpy as np
import pytest
from s3mapgen.generation.archetypes.profiles import default_archetype_profile, normalize_archetype_profile
from s3mapgen.generation.archetypes.morphology import apply_native_noise_layers, _configured_source_field, _fuse_source, generate_noise_component_previews
from s3mapgen.application.custom.preview_dock import choose_placement
from s3mapgen.application.settings import preferences


def profile(gray, target='source'):
    p = default_archetype_profile()
    m = p['morphology']
    m.update(mask_layer_count=1, finite_domain_mode='percent', frame_margin_percent=0)
    mask = m['mask_layers'][0]
    mask.update(enabled=True, operation='mask', target=target, type='manual', strength_percent=100)
    mask['settings'].update(width_percent=100, height_percent=100, softness_percent=0)
    mask['provider_settings']={'grid_side':64, 'grid':np.full((64,64),gray,np.uint8).reshape(-1).tolist()}
    return p


def test_black_white_gray_and_strength_have_exact_permission_semantics():
    raw=np.full((64,64),180,np.uint8)
    for gray in (0,64,128,255):
        p=profile(gray)
        output=apply_native_noise_layers(raw,p,seed=42)
        np.testing.assert_array_equal(output,np.full_like(raw,round(180*gray/255)))
    white=profile(255)
    white['morphology']['finite_domain_mode']=default_archetype_profile()['morphology']['finite_domain_mode']
    np.testing.assert_array_equal(apply_native_noise_layers(raw,white,seed=42),raw)
    p=profile(0);p['morphology']['mask_layers'][0]['strength_percent']=50
    np.testing.assert_array_equal(apply_native_noise_layers(raw,p,seed=42),np.full_like(raw,90))
    p['morphology']['mask_layers'][0]['strength_percent']=101
    with pytest.raises(ValueError):normalize_archetype_profile(p)


def test_black_fusion_is_identity_for_every_blend_operator_and_gray_scales_delta():
    raw=np.full((64,64),150,np.uint8)
    for operation in ('replace','blend','add','subtract','multiply','min','max'):
        for gray in (0,128,255):
            p=profile(gray,'fusion:0');m=p['morphology'];m['noise_layer_count']=1
            f=m['noise_layers'][0];f.update(enabled=True,strength_percent=80,operation=operation)
            before=raw.astype(np.float32)/255
            component,domain=_configured_source_field(64,42 ^ 0x9E3779B9,f['source'],f['settings'],p,f['mask_settings'])
            candidate=_fuse_source(before,component,domain,operation,80)
            expected=np.rint((before+(candidate-before)*(gray/255))*255).astype(np.uint8)
            np.testing.assert_array_equal(apply_native_noise_layers(raw,p,seed=42),expected)


def test_inversion_and_multiple_permissions_cannot_be_undone_by_modulation():
    raw=np.full((64,64),180,np.uint8)
    p=profile(255);p['morphology']['mask_layers'][0]['inverted']=True
    np.testing.assert_array_equal(apply_native_noise_layers(raw,p),np.zeros_like(raw))
    p=profile(128);m=p['morphology'];m['mask_layer_count']=2
    m['mask_layers'][1]=deepcopy(m['mask_layers'][0]);m['mask_layers'][1]['order']=1
    np.testing.assert_array_equal(apply_native_noise_layers(raw,p),np.full_like(raw,round(180*(128/255)**2)))
    m['mask_layers'][0]['provider_settings']['grid']=[0]*4096
    m['mask_layers'][1].update(operation='add',strength_percent=100)
    np.testing.assert_array_equal(apply_native_noise_layers(raw,p),np.zeros_like(raw))


def test_permission_previews_and_cache_follow_inversion():
    p=profile(0,'fusion:0');m=p['morphology'];m['noise_layer_count']=1
    m['noise_layers'][0].update(enabled=True,strength_percent=100)
    cache={}
    _,masked=generate_noise_component_previews(p,64,42,component_cache=cache)
    assert masked[0].max()==0
    m['mask_layers'][0]['inverted']=True
    _,visible=generate_noise_component_previews(p,64,42,component_cache=cache)
    assert visible[0].max()>0
    m['mask_layers'][0]['inverted']=False
    _,masked_again=generate_noise_component_previews(p,64,42,component_cache=cache)
    np.testing.assert_array_equal(masked[0],masked_again[0])


def test_auto_placement_uses_available_space_and_hysteresis():
    assert choose_placement(800,700)=='top'
    assert choose_placement(1120,700)=='right'
    assert choose_placement(1050,700,'right')=='right'
    assert choose_placement(1050,700,'top')=='top'
    assert choose_placement(999,700,'right')=='top'
    assert choose_placement(1500,500,'right')=='top'


def test_preview_placement_survives_preferences_roundtrip(monkeypatch,tmp_path):
    monkeypatch.setenv('APPDATA',str(tmp_path))
    for mode in ('free','top','right','auto'):
        preferences.save_settings({'archetype_preview_placement':mode})
        assert preferences.load_settings()['archetype_preview_placement']==mode
    preferences.save_settings({'archetype_preview_placement':'nonsense'})
    assert preferences.load_settings()['archetype_preview_placement']=='top'
