import struct
import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.sav_conversion import sav_to_map_state
from s3mapgen.map_data.binary import export_with_scaffold, read_area, read_starts, parse_parts
from s3mapgen.application.paths import EDM_SCAFFOLD, MAP_SCAFFOLD
from s3mapgen.map_data.preview import global_rgb
from s3mapgen.application.ui.i18n.exports import EXPORT_TEXT


def sample():
    s=MapState.empty(256);s.height[:]=10;s.terrain[:]=16;s.claim[:]=0
    s.starts=[(50,50),(100,100),(180,180)]
    s.metadata={'source_format':'SAV','sav_player_records':[
        dict(active=True,start_x=x,start_y=y,layout='native_v11',player=i+1,
             tribe_code_candidate=n,team_code=t)
        for i,((x,y),n,t) in enumerate(zip(s.starts,(2,3,1),(0,0,4)))]}
    s.runtime_flags=np.full((256,256),0x4c,np.uint8);s.runtime_flags[80,84]=0x4d
    s.original_objects=np.full((256,256),70,np.uint8)
    s.objects[30,30:34]=(13,14,15,16);s.terrain[30,30:34]=0;s.height[30,30:34]=0
    s.objects[60,60:62]=(112,113);s.objects[70,70:74]=(128,142,196,206)
    s.objects[80,80:87]=(216,224,208,88,123,127,255)
    s.terrain[80,83]=22;s.terrain[81,81]=28;s.resources[85,85]=0x17;s.resources[30,30]=5
    return s


def test_conversion_preserves_current_surface_and_alliances_without_mutation():
    s=sample();before=s.area.copy();flags=s.runtime_flags.copy();original=s.original_objects.copy()
    out=sav_to_map_state(s)
    np.testing.assert_array_equal(out.terrain,s.terrain);np.testing.assert_array_equal(out.resources,s.resources)
    assert out.objects[30,30:34].tolist()==[111,112,113,114]
    assert out.objects[60,60:62].tolist()==[0,0]
    assert out.objects[70,70:74].tolist()==[208,214,212,214]
    assert np.all(out.claim==255) and set(np.unique(out.accessibility)) <= {0,1}
    assert out.metadata['classic_start_nations']==(2,3,1)
    assert out.metadata['player_teams']==(1,1,5)
    assert sav_to_map_state(out) is out
    np.testing.assert_array_equal(s.area,before);np.testing.assert_array_equal(s.runtime_flags,flags)
    np.testing.assert_array_equal(s.original_objects,original)
    np.testing.assert_array_equal(global_rgb(s)[80,80:87],global_rgb(out)[80,80:87])
    assert out.objects[2,2]==0 # no resurrection from byte14


@pytest.mark.parametrize('suffix,scaffold',[('edm',EDM_SCAFFOLD),('map',MAP_SCAFFOLD)])
def test_real_writer_converted_objects_and_players(tmp_path,suffix,scaffold):
    s=sample();p=tmp_path/f'converted.{suffix}';export_with_scaffold(s,scaffold,p)
    imported=read_area(p);version,parts=parse_parts(p,allow_terminal_padding=True)
    assert version==11 and read_starts(p)==s.starts
    assert imported.objects[30,30:34].tolist()==[111,112,113,114]
    assert imported.objects[60,60:62].tolist()==[0,0]
    assert imported.resources[85,85]==0x17
    assert not any(t in (7,8,9) for t,_ in parts)
    setup=next(p for t,p in parts if t==3)
    assert [setup[33+2*i] for i in range(3)]==[0,0,1]


@pytest.mark.parametrize('oid',[111,114,133,135,215,223,231])
def test_unsupported_object_refused_before_write(tmp_path,oid):
    s=sample();s.objects[2,2]=oid;p=tmp_path/'unsafe.map'
    with pytest.raises(ValueError,match='non convertibles'):export_with_scaffold(s,MAP_SCAFFOLD,p)
    assert not p.exists() and s.objects[2,2]==oid


def test_empty_edm_ignores_invalid_player_metadata(tmp_path):
    s=sample();s.metadata['sav_player_records'][0]['tribe_code_candidate']=99
    p=tmp_path/'empty.edm';export_with_scaffold(s,EDM_SCAFFOLD,p,empty=True)
    assert read_starts(p)==[]


def test_missing_starts_cannot_write_map(tmp_path):
    s=sample();s.starts=[];s.metadata['sav_player_records']=[]
    with pytest.raises(ValueError,match='aucun départ'):export_with_scaffold(s,MAP_SCAFFOLD,tmp_path/'no.map')
    export_with_scaffold(s,EDM_SCAFFOLD,tmp_path/'empty.edm',empty=True)


def test_ordinary_map_identity():
    s=sample();s.metadata={};s.objects[1,1]=215
    assert sav_to_map_state(s) is s


def test_all_languages_explain_conversion():
    for lang in ('fr','en','de','es'):
        t=EXPORT_TEXT[lang]
        assert t['sav_map_notice'] and t['sav_map_no_starts']
        assert t['sav_map_result'].format(reefs_recoded=4,construction_markers_removed=2,felling_settled_to_stumps=3)
