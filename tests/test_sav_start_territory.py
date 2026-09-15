import struct

from s3mapgen.map_data.binary import (
    _extract_sav_player_records,
    _extract_sav_starts_from_player_block,
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
