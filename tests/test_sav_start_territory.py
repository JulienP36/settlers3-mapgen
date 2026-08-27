import struct
from s3mapgen.map_data.binary import _extract_sav_starts_from_player_block

def test_extract_original_starts_from_sav_player_block():
    b=bytearray(96+20*328)
    starts=[(299,339),(311,112),(373,486),(666,400)]
    for pid,(x,y) in enumerate(starts):struct.pack_into('<III',b,96+pid*328,pid,x,y)
    struct.pack_into('<III',b,96+len(starts)*328,0,384,384)
    assert _extract_sav_starts_from_player_block(b,768)==starts
