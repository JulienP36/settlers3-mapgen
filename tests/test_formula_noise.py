from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import pytest
from s3mapgen.generation.archetypes.formula import FORMULA_EXAMPLES, normalize_formula
from s3mapgen.generation.archetypes.noise_sources import generate_noise_source
from s3mapgen.generation.archetypes.profiles import NOISE_SOURCE_SETTING_DEFAULTS, default_archetype_profile, normalize_archetype_profile, duplicate_noise_layer
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig
from s3mapgen.application.custom.formula_editor import ensure_applied_formula_inputs


def field(expression, side=64, seed=42, **settings):
    return generate_noise_source('formula',side,seed,{**NOISE_SOURCE_SETTING_DEFAULTS,'bias_percent':0,'contrast_percent':100,**settings,'expression':expression})


@pytest.mark.parametrize('expression',FORMULA_EXAMPLES)
def test_examples_finite_deterministic_and_bounded(expression):
    a=field(expression);b=field(expression)
    assert a.shape==(64,64) and a.dtype==np.float32 and np.isfinite(a).all()
    assert a.min()>=-1 and a.max()<=1
    np.testing.assert_array_equal(a,b)


def test_noise_seed_and_offsets_are_explicit():
    np.testing.assert_array_equal(field('fbm(4,5,10)'),field('fbm(4,5)',seed=52))
    assert not np.array_equal(field('fbm()'),field('fbm()',seed=43))
    np.testing.assert_array_equal(field('fbm()'),generate_noise_source('fbm',64,42,{**NOISE_SOURCE_SETTING_DEFAULTS,'bias_percent':0,'contrast_percent':100}))
    np.testing.assert_array_equal(field('fbm()',contrast_percent=200),np.clip(field('fbm()')*2,-1,1))


def test_coordinates_constants_and_clipping_have_fixed_scale():
    np.testing.assert_allclose(field('x')[0],np.linspace(-1,1,64),atol=1e-6)
    assert np.all(field('3')==1) and np.all(field('-0.25')==-0.25)
    np.testing.assert_allclose(field('min(x,y)'),np.minimum(field('x'),field('y')))
    assert np.all(field('smoothstep(-1,1,x)')[:,0]==0)


@pytest.mark.parametrize('expression',['__import__("os")','x.__class__','[x]','x[0]','lambda: 1','fbm(x)','fbm(0)','fbm(4,9)','fbm(4,2.5)','fbm(4,2,0.5)','x**x','x**999','True','1e999','9'*800,'fbm(seed=1)','sum(x)','fbm()+fbm()+fbm()+fbm()+fbm()+fbm()+fbm()'])
def test_rejects_code_and_unbounded_work(expression):
    with pytest.raises(ValueError): normalize_formula(expression)


@pytest.mark.parametrize('expression',['1/0','sqrt(-1)','clamp(x,1,-1)','smoothstep(1,1,x)'])
def test_numeric_errors_are_explicit(expression):
    with pytest.raises(ValueError): field(expression)


def test_formula_survives_normalization_serialization_digest_and_layer_copy():
    config=build_custom_config('upgraded');p=deepcopy(config.archetype_profile)
    p['morphology']['relief_source']='formula';p['morphology']['relief_source_settings']['expression']='fbm(4)-0.2*r'
    p['morphology']['noise_layer_count']=1;l=p['morphology']['noise_layers'][0]
    l.update(enabled=True,source='formula',family='formula');l['settings']['expression']='sin(pi*x)'
    config=config.with_archetype_profile(p);restored=CustomGenerationConfig.from_dict(config.to_dict())
    assert restored.digest==config.digest
    assert restored.archetype_profile['morphology']['relief_source_settings']['expression']=='fbm(4)-0.2*r'
    copied,count=duplicate_noise_layer(config.archetype_profile['morphology']['noise_layers'],1,0)
    assert count==2
    assert copied[1]['settings']['expression']=='sin(pi*x)'
    q=deepcopy(config.archetype_profile);q['morphology']['relief_source_settings']['expression']='fbm(5)'
    assert config.with_archetype_profile(q).digest!=config.digest
    assert normalize_archetype_profile(config.archetype_profile)==config.archetype_profile


def test_invalid_visible_edit_cannot_generate_previous_formula():
    c=build_custom_config('upgraded');p=deepcopy(c.archetype_profile);p['morphology']['relief_source']='formula';c=c.with_archetype_profile(p)
    owner=SimpleNamespace(_custom_formula_panels={'primary':SimpleNamespace(active=True,dirty=True)},_custom_archetype_relief_source_vars={'expression':SimpleNamespace(get=lambda:'1/0')},_custom_language=lambda:'fr')
    with pytest.raises(ValueError,match='pas appliquée'): ensure_applied_formula_inputs(owner,c)
    owner._custom_formula_panels['primary'].dirty=False
    ensure_applied_formula_inputs(owner,c) # loading a different saved profile is not an edit


@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_formula_runs_in_full_pipeline_and_preview(mode):
    from s3mapgen.application.paths import LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE
    from s3mapgen.generation import MapGenerator
    from s3mapgen.generation.archetypes import generate_archetype_preview
    c=build_custom_config(mode);p=deepcopy(c.archetype_profile)
    p['morphology']['relief_source']='formula';p['morphology']['relief_source_settings']['expression']='fbm(4)'
    c=c.with_archetype_profile(p)
    sections=c.semantic_sections();sections['rivers']['algorithm']='improved';c=c.with_sections(sections)
    result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(2,20260920,mode='custom',archetype='continental',side=256,custom_config=c)
    assert all(v.passed for v in result.validations if v.hard),result.validations
    preview=generate_archetype_preview(c.archetype_profile,256,42)
    assert preview.noise.shape==result.state.height.shape
    assert np.isfinite(preview.noise).all()
    baseline=deepcopy(p);baseline['morphology']['relief_source']='fbm'
    other=generate_archetype_preview(baseline,256,42)
    np.testing.assert_array_equal(preview.noise,other.noise)


@pytest.mark.parametrize('expression,success',[('fbm(5)',True),('1/0',False)])
def test_editor_commit_is_transactional(expression,success):
    from s3mapgen.application.custom.formula_editor import FormulaPanel
    class Var:
        def __init__(self,value): self.value=value
        def get(self): return self.value
        def set(self,value): self.value=value
    config=build_custom_config('upgraded');p=deepcopy(config.archetype_profile);p['morphology']['relief_source']='formula';config=config.with_archetype_profile(p)
    owner=SimpleNamespace(_custom_config=config,size=Var('256'),seed=Var('42'))
    var=Var(expression);message=Var('');calls=[]
    def apply():
        calls.append(True);profile=deepcopy(owner._custom_config.archetype_profile)
        profile['morphology']['relief_source_settings']['expression']=var.get()
        owner._custom_config=owner._custom_config.with_archetype_profile(profile)
    panel=SimpleNamespace(cancel=lambda:None,active=True,dirty=True,variable=var,owner=owner,source_key='primary',callback=apply,message=message,language='fr')
    FormulaPanel.commit(panel)
    assert bool(calls)==success
    if success:
        assert not panel.dirty and owner._custom_config.archetype_profile['morphology']['relief_source_settings']['expression']==expression
    else:
        assert owner._custom_config.digest==config.digest and panel.dirty and 'non appliquée' in message.get()


def test_formula_controls_follow_actual_calls_and_explicit_arguments():
    from s3mapgen.generation.archetypes.noise_sources import noise_source_setting_applies as applies
    assert not applies('formula','frequency',{'expression':'fbm(4)+ridged(9)'})
    assert applies('formula','frequency',{'expression':'fbm()+ridged(9)'})
    assert not applies('formula','octaves',{'expression':'fbm(4,3)'})
    assert not applies('formula','warp_strength_percent',{'expression':'fbm()'})
    assert applies('formula','warp_strength_percent',{'expression':'domain_warp()'})
    assert applies('formula','expression',{'expression':'1/0'})


def test_every_existing_noise_is_available_without_recursive_formula_calls():
    from s3mapgen.generation.archetypes.formula import NOISE_FUNCTIONS
    from s3mapgen.generation.archetypes.noise_sources import NOISE_SOURCE_OPTIONS
    assert NOISE_FUNCTIONS == set(NOISE_SOURCE_OPTIONS)-{'formula'}
    for name in sorted(NOISE_FUNCTIONS):
        a=field(name+'()')
        expected=generate_noise_source(name,64,42,{**NOISE_SOURCE_SETTING_DEFAULTS,'bias_percent':0,'contrast_percent':100})
        np.testing.assert_array_equal(a,expected)


@pytest.mark.parametrize('changed',[False,True])
def test_formula_text_trace_covers_paste_and_profile_sync(changed):
    from s3mapgen.application.custom.formula_editor import FormulaPanel
    c=build_custom_config('upgraded');p=deepcopy(c.archetype_profile);p['morphology']['relief_source']='formula';c=c.with_archetype_profile(p)
    value='fbm(6)' if changed else c.archetype_profile['morphology']['relief_source_settings']['expression']
    messages=[];scheduled=[]
    panel=SimpleNamespace(_committing=False,cancel=lambda:None,active=True,dirty=True,source_key='primary',owner=SimpleNamespace(_custom_config=c),variable=SimpleNamespace(get=lambda:value),message=SimpleNamespace(set=messages.append),language='fr',after=lambda delay,action: scheduled.append(delay) or 'timer',commit=lambda:None)
    FormulaPanel.schedule(panel)
    assert bool(scheduled)==changed
    assert panel.dirty==changed
    if changed: assert scheduled==[750]
