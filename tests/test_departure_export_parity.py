"""User's real R47 EDM, independent native acceptance and round-trip parity."""
from pathlib import Path
import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.binary import read_area, export_with_scaffold
from s3mapgen.map_data.editor_height import prepare_editor_export
from s3mapgen.generation.start_diagnostics import departure_source, departure_diagnostics
from s3mapgen.generation.editor_starts import placed_start_checks
from s3mapgen.application.paths import EDM_SCAFFOLD
from s3mapgen.application.rendering.preview import _overlay_rgb

@pytest.fixture(scope='module')
def real_states():
    with np.load(Path(__file__).parent/'fixtures/export_departures_r48.npz') as d:
        original=MapState(768,d['area'].copy(),list(map(tuple,d['starts'])))
        imported=MapState(768,d['exported'].copy(),list(map(tuple,d['starts'])))
    return original,imported

@pytest.mark.parametrize('context',['before_objects','current'])
@pytest.mark.parametrize('policy',['valid_all','valid_0','valid_1','valid_2','valid_3'])
def test_real_seed_export_normalization_and_every_filter_are_identical(real_states,context,policy):
    original,imported=real_states
    before=original.area.copy()
    a=departure_diagnostics(original,policy,context=context)
    b=departure_diagnostics(imported,policy,context=context)
    for key in ('valid','green','yellow','relocation','visible','terrain','clearance'):
        assert np.array_equal(a[key],b[key]),key
    assert np.array_equal(original.area,before)

def test_user_player_five_editor_acceptance_is_visible_and_not_red(real_states):
    _,s=real_states;s=MapState(s.side,s.area.copy(),list(s.starts)+[(265,404)],metadata={'player_nations':[255]*4+[0]})
    report=departure_diagnostics(s,'valid_0:current')
    # Both original editors accept this point; original exact-position game
    # helper refuses it. Native initial search chose 265,398 in the audit.
    assert report['green'][404,265] and report['relocation'][404,265]
    assert not report['game_exact'][404,265]
    row=placed_start_checks(s)[4]
    assert row['editor'] and row['status']=='green' and row['relocation_possible']
    assert tuple(_overlay_rgb(s,'valid_starts','valid_0:current')[404,265])==(50,255,100)

@pytest.mark.parametrize('context',['before_objects','current'])
def test_real_edm_round_trip_not_just_in_memory_preparation(real_states,tmp_path,context):
    original,_=real_states
    path=tmp_path/'roundtrip.edm';export_with_scaffold(original,EDM_SCAFFOLD,path)
    restored=read_area(path)
    a=departure_diagnostics(original,'valid_all',context=context)
    b=departure_diagnostics(restored,'valid_all',context=context)
    assert np.array_equal(a['green'],b['green']) and np.array_equal(a['yellow'],b['yellow'])

def test_context_is_explicit_and_cache_follows_in_place_edits():
    s=MapState.empty(64);s.terrain[:]=16;s.height[:]=10
    s.objects[32,32]=68;s.accessibility[32,32]=1
    assert departure_diagnostics(s,'valid_0',context='before_objects')['green'][32,32]
    assert not departure_diagnostics(s,'valid_0:current')['green'][32,32]
    a,_=departure_source(s,'current');b,_=departure_source(s,'current')
    assert a.area is b.area and not a.area.flags.writeable
    s.objects[32,32]=0;s.accessibility[32,32]=0
    assert departure_diagnostics(s,'valid_0:current')['green'][32,32]
    s.starts=[(32,32)];assert len(placed_start_checks(s))==1
    s.metadata['player_nations']=[1];s.terrain[:]=64
    assert placed_start_checks(s)[0]['status']=='green'
    s.metadata['player_nations']=[0]
    assert placed_start_checks(s)[0]['status']=='invalid'

def test_writer_preparation_is_idempotent_on_the_attached_map(real_states):
    _,imported=real_states;a=imported.area.copy();prepare_editor_export(a)
    assert np.array_equal(a,imported.area)

@pytest.mark.parametrize('lang',['fr','en','de','es'])
def test_viewer_hover_reports_editor_admission_and_possible_nearby_search(real_states,lang):
    from types import SimpleNamespace
    from s3mapgen.application.viewer.controller import ViewerController
    from s3mapgen.application.ui.i18n.viewer import VALID_START_LABELS
    _,s=real_states;messages=[]
    viewer=SimpleNamespace(prefs={'language':lang,'valid_start_filter':'valid_0:current'},
                           current=SimpleNamespace(state=s),inspector_var=SimpleNamespace(set=messages.append),
                           _source_cell_from_canvas=lambda event:(265,404),_view_key=lambda:'valid_starts')
    viewer._departure_report=lambda:ViewerController._departure_report(viewer)
    viewer._departure_summary=lambda report,island=0:ViewerController._departure_summary(viewer,report,island)
    ViewerController._inspect_motion(viewer,None)
    assert messages and '265' in messages[-1] and '404' in messages[-1]
    marker={'fr':'recherche voisine possible','en':'nearby search possible','de':'Nachbarsuche möglich','es':'búsqueda cercana posible'}[lang]
    assert marker in messages[-1]
    assert len(VALID_START_LABELS[lang])==10

def test_context_setting_survives_restart(tmp_path,monkeypatch):
    from s3mapgen.application.settings import preferences
    monkeypatch.setattr(preferences,'settings_path',lambda:tmp_path/'settings.json')
    preferences.save_settings({'valid_start_filter':'valid_2:current'})
    assert preferences.load_settings()['valid_start_filter']=='valid_2:current'
