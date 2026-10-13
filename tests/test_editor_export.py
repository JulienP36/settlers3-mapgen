from pathlib import Path
import struct
import numpy as np
import pytest
from s3mapgen.map_data.editor_height import correct_editor_heights, prepare_editor_export
from s3mapgen.map_data.preview import editor_minimap_payload
from s3mapgen.map_data.binary import export_with_scaffold,parse_parts,read_area,checksum,encrypt
from s3mapgen.map_data.model import MapState
from s3mapgen.application.paths import MAP_SCAFFOLD,EDM_SCAFFOLD

@pytest.mark.parametrize('side',[1,3,7,16])
def test_exact_united_height_fixture(side):
    with np.load(Path(__file__).parent/'fixtures/editor_height_united.npz') as data:
        area=data[f'input_{side}'].copy()
        correct_editor_heights(area)
        assert np.array_equal(area,data[f'expected_{side}'])
        assert correct_editor_heights(area)['changed_cells']==0

@pytest.mark.parametrize('scaffold',[MAP_SCAFFOLD,EDM_SCAFFOLD])
def test_export_prepares_copy_and_preserves_opaque_parts(tmp_path,scaffold):
    state=MapState.empty(128);state.height[:]=20;state.terrain[:]=16
    state.height[60:65,60:65]=50;state.objects[50,50]=68;state.resources[52,52]=0x28
    state.starts=[(40,40),(80,80)];state.metadata={'player_nations':[0,3],'player_teams':[7,7]}
    before=state.area.copy();expected=before.copy();prepare_editor_export(expected)
    output=tmp_path/'test.map';export_with_scaffold(state,scaffold,output)
    assert np.array_equal(state.area,before)
    assert np.array_equal(read_area(output).area,expected)
    data=output.read_bytes();assert len(data)%4==0;assert checksum(data)==struct.unpack_from('<I',data)[0]
    version,parts=parse_parts(output,allow_terminal_padding=True);assert version==11
    actual=dict(parts);original=dict(parse_parts(scaffold,allow_terminal_padding=True)[1])
    assert actual[3][33:]==bytes([0,0,0,0])
    for kind,payload in original.items():
        if kind not in (1,2,3,4,6):assert actual[kind]==payload
    if 4 in original:assert actual[4]==editor_minimap_payload(MapState(128,expected))
    else:assert 4 not in actual

@pytest.mark.parametrize('nation,version',[(0,10),(1,10),(2,10),(255,10),(3,11)])
def test_native_version_selection(tmp_path,nation,version):
    state=MapState.empty(32);state.terrain[:]=16;state.height[:]=20
    state.starts=[(16,16)];state.metadata={'player_nations':[nation]}
    output=tmp_path/'test.map';export_with_scaffold(state,MAP_SCAFFOLD,output)
    assert parse_parts(output,allow_terminal_padding=True)[0]==version

@pytest.mark.parametrize('side',[832,896,960,1024])
@pytest.mark.parametrize('scaffold',[MAP_SCAFFOLD,EDM_SCAFFOLD])
def test_extended_size_export_is_rejected_without_creating_file(tmp_path,side,scaffold):
    state=MapState.empty(side)
    output=tmp_path/('test'+scaffold.suffix)
    with pytest.raises(ValueError,match='maximum 768'):
        export_with_scaffold(state,scaffold,output)
    assert not output.exists()

def test_minimap_rgb555_and_current_terrain():
    state=MapState.empty(16);payload=editor_minimap_payload(state)
    assert len(payload)==4+256*256*2
    assert struct.unpack_from('<I',payload)[0]==256
    assert struct.unpack_from('<H',payload,4)[0]==9885
    state.terrain[:]=16
    assert payload!=editor_minimap_payload(state)

def test_extended_goods_promote_version(tmp_path):
    version,parts=parse_parts(MAP_SCAFFOLD,allow_terminal_padding=True)
    goods=bytearray(struct.pack('<I',1)+bytes([10,0,10,0,34,1,0,0]))
    parts=[entry for entry in parts if entry[0]!=9]
    parts.insert(len(parts)-1,[9,goods])
    data=bytearray(struct.pack('<II',0,10))
    for kind,payload in parts:data+=struct.pack('<II',kind,len(payload)+8)+encrypt(payload,kind)
    rem=len(data)%4
    if rem:data+=struct.pack('<I',rem)[:4-rem]
    struct.pack_into('<I',data,0,checksum(data));scaffold=tmp_path/'shell.map';scaffold.write_bytes(data)
    state=MapState.empty(32);state.terrain[:]=16;state.height[:]=20;state.starts=[(16,16)]
    output=tmp_path/'test.map';export_with_scaffold(state,scaffold,output)
    assert parse_parts(output,allow_terminal_padding=True)[0]==11

@pytest.mark.parametrize('side',[1,2,3,7,16,32])
def test_complete_export_matches_unmodified_united_routines(side):
    with np.load(Path(__file__).parent/'fixtures/editor_export_united.npz') as data:
        area=data[f'input_{side}'].copy()
        prepare_editor_export(area)
        assert np.array_equal(area,data[f'expected_{side}'])

@pytest.mark.parametrize('scaffold',[MAP_SCAFFOLD,EDM_SCAFFOLD])
def test_export_applies_coast_swamp_context_without_mutating_session(tmp_path,scaffold):
    with np.load(Path(__file__).parent/'fixtures/editor_export_united.npz') as data:
        area=data['input_32'].copy();expected=data['expected_32']
        state=MapState(32,area,[(12,12),(20,20)])
        state.metadata={'player_teams':[0,0]}
        output=tmp_path/('prepared'+scaffold.suffix)
        export_with_scaffold(state,scaffold,output)
        assert np.array_equal(read_area(output).area,expected)
        assert np.array_equal(state.area,data['input_32'])
        assert dict(parse_parts(output,allow_terminal_padding=True)[1])[3][33:]==bytes([0,0,1,0])

@pytest.mark.parametrize('teams,expected',[
    ([0,0,0,0],[0,1,2,3]),([7,7,0,20],[0,0,1,2]),
    ([20,0,20,3],[0,1,0,2]),([1,1,2,2],[0,0,1,1]),([],[]),
])
def test_ui_alliances_encode_as_contiguous_native_teams(teams,expected):
    from s3mapgen.map_data.binary import encode_player_teams
    assert encode_player_teams(teams)==expected

@pytest.mark.parametrize('scaffold',[MAP_SCAFFOLD,EDM_SCAFFOLD])
def test_partial_export_keeps_original_alliances_then_renumbers_native_groups(tmp_path,scaffold):
    state=MapState.empty(32);state.terrain[:]=16;state.height[:]=20
    state.starts=[(12,12),(20,20)];state.metadata={
        'player_teams':[0,20,7,20],'start_slot_indices':[1,3],
        'player_nations':[0,1,2,3],'start_disabled_slots':[0,2]}
    output=tmp_path/'partial.edm'
    export_with_scaffold(state,scaffold,output,test_edm=True)
    parts=dict(parse_parts(output,allow_terminal_padding=True)[1])
    assert parts[3][33:]==bytes([0,0,0,0])
    assert [struct.unpack_from('<I',parts[2],i*45)[0] for i in range(2)]==[1,3]
