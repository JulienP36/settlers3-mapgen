import struct
from pathlib import Path

from s3mapgen.map_data.binary import (
    _extract_sav_player_records,
    _extract_sav_starts_from_player_block,
    read_sav_state,
)

def test_extract_original_starts_from_sav_player_block():
    b=bytearray(96+20*328)
    starts=[(299,339),(311,112),(373,486),(666,400)]
    for pid,(x,y) in enumerate(starts):struct.pack_into('<III',b,96+pid*328,pid,x,y)
    struct.pack_into('<III',b,96+len(starts)*328,0,384,384)
    assert _extract_sav_starts_from_player_block(b,768)==starts


def test_extract_native_player_records_uses_the_84_byte_prefix_and_record_offsets():
    b=bytearray(84+20*328)
    struct.pack_into('<II',b,84,1,3)
    struct.pack_into('<II',b,84+16,128,54)
    struct.pack_into('<II',b,84+328,1,0)
    struct.pack_into('<II',b,84+328+16,225,30)
    records=_extract_sav_player_records(b,256)
    assert len(records)==20
    assert records[0]['active'] is True
    assert records[0]['active_flag']==1
    assert (records[0]['start_x'],records[0]['start_y'])==(128,54)
    assert records[0]['tribe_code_candidate']==3
    assert records[1]['active'] is True
    assert records[1]['active_flag']==1
    assert (records[1]['start_x'],records[1]['start_y'])==(225,30)
    assert _extract_sav_starts_from_player_block(b,256)==[(128,54),(225,30)]


def test_native_flag_two_is_an_active_computer_player():
    b=bytearray(84+20*328)
    struct.pack_into('<II',b,84,1,2)
    struct.pack_into('<II',b,84+16,128,54)
    struct.pack_into('<II',b,84+328,2,1)
    struct.pack_into('<II',b,84+328+16,225,30)
    records=_extract_sav_player_records(b,256)
    assert records[0]['active'] is True and records[1]['active'] is True
    assert records[1]['active_flag']==2
    assert _extract_sav_starts_from_player_block(b,256)==[(128,54),(225,30)]


def test_real_native_sav_exposes_start_mask_and_player_field_status():
    path=Path('/workspace/scratch/92f09fe5484c/upload/slot 9 - ff17.sav')
    if not path.is_file():
        return
    state=read_sav_state(path)
    assert state.starts==[(128,54)]
    assert state.metadata['sav_player_block']['prefix_bytes']==84
    assert state.metadata['sav_player_block']['record_stride']==328
    assert state.metadata['sav_player_metadata_status']['effective_color']=='not_decoded'
    assert state.metadata['sav_player_metadata_status']['mana_current']=='not_decoded'


def test_real_immediate_four_player_sav_exposes_the_exact_byte8_initial_mask():
    path=Path('/workspace/scratch/92f09fe5484c/upload/S3_Continental_Legacy_4P_768x768_seed_2026081901_MapGenV1_8.sav')
    if not path.is_file():
        return
    state=read_sav_state(path)
    assert state.starts==[(652,652),(424,46),(54,324),(212,710)]
    records=state.metadata['sav_player_records']
    assert [row['active_flag'] for row in records[:4]]==[1,2,2,2]
    assert state.metadata['initial_territory_mask_status']=='direct'
    assert state.metadata['initial_territory_mask_source']=='sav_type3_byte8_direct_initial_claims'
    assert state.metadata['initial_territory_direct_counts']=={'1':3500,'2':3500,'3':4000,'4':4000}
    assert state.metadata['initial_territory_direct_total_cells']==15000
    for player,count in state.metadata['initial_territory_direct_counts'].items():
        assert len(state.metadata['initial_territory_direct_cells'][player])==count


def test_later_sav_claim_growth_is_not_mislabeled_as_initial_mask():
    path=Path('/workspace/scratch/92f09fe5484c/upload/slot 9 - ff17.sav')
    if not path.is_file():
        return
    state=read_sav_state(path)
    assert state.metadata['runtime_claim_source']=='sav_type3_byte8'
    assert state.metadata['initial_territory_mask_status']=='not_detected'
    assert state.metadata['initial_territory_direct_cells'] is None
