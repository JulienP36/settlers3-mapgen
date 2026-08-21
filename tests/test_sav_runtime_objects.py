import struct
import numpy as np
from s3mapgen.binary import encrypt, read_sav_state


def _write_sav(tmp_path, cells):
    side=len(cells)
    out=bytearray(8)
    struct.pack_into('<I',out,4,11)
    for x in range(side):
        arr=np.zeros((side,24),dtype=np.uint8)
        for y in range(side):
            arr[y,4]=0
            arr[y,6]=22 if (x,y)==(1,1) else 16
            arr[y,7]=cells[y][x][0]
            arr[y,14]=cells[y][x][1]
            arr[y,8]=255
        t=(x<<16)|3
        payload=arr.tobytes()
        out += struct.pack('<II',t,8+len(payload)) + encrypt(payload,t)
    p=tmp_path/'runtime.sav';p.write_bytes(out);return p


def test_played_sav_uses_runtime_object_byte_7_not_static_byte_14(tmp_path):
    cells=[[(0,0) for _ in range(4)] for _ in range(4)]
    cells[1][1]=(88,0)       # current wheat crop; static map had nothing here
    cells[2][2]=(0,70)       # tree was removed during gameplay; static field is stale
    state=read_sav_state(_write_sav(tmp_path,cells))
    assert int(state.objects[1,1])==88
    assert int(state.objects[2,2])==0
    assert state.metadata['runtime_objects_preserved'] is True
