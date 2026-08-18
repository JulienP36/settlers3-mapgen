from __future__ import annotations
from pathlib import Path
import struct
from .model import MapState


def decrypt(payload:bytes, part_type:int)->bytearray:
    out=bytearray(len(payload)); k=part_type&255
    for i,c in enumerate(payload):
        p=c^k; out[i]=p; k=((k<<1)&255)^p
    return out

def encrypt(payload:bytes, part_type:int)->bytearray:
    out=bytearray(len(payload)); k=part_type&255
    for i,p in enumerate(payload):
        out[i]=p^k; k=((k<<1)&255)^p
    return out

def checksum(buf:bytes|bytearray)->int:
    c=0
    for pos in range(8,(len(buf)//4)*4,4):
        v=struct.unpack_from('<I',buf,pos)[0]
        c=((c>>31)|((((c<<1)&0xffffffff)^v)&0xffffffff))&0xffffffff
    return c

def parse_parts(path:Path|str):
    b=Path(path).read_bytes(); version=struct.unpack_from('<I',b,4)[0]
    off=8; parts=[]
    while off+8<=len(b):
        t,total=struct.unpack_from('<II',b,off)
        if total<8 or off+total>len(b): raise ValueError(f'Invalid part at {off}')
        parts.append([t,decrypt(b[off+8:off+total],t)])
        off += total
    if off!=len(b): raise ValueError('Part scan did not end at EOF')
    return version,parts

def _set_players(parts, starts:list[tuple[int,int]]):
    count=len(starts)
    done={1:False,2:False,3:False}
    for i,(t,p) in enumerate(parts):
        if t==1 and len(p)>=24 and not done[1]:
            vals=list(struct.unpack_from('<6I',p,0)); vals[1]=count; vals[2]=max(0,count-1)
            parts[i][1]=bytearray(struct.pack('<6I',*vals)); done[1]=True
        elif t==2 and not done[2]:
            out=bytearray()
            for x,y in starts:
                rec=bytearray(45); struct.pack_into('<III',rec,0,255,int(x),int(y)); out+=rec
            parts[i][1]=out; done[2]=True
        elif t==3 and len(p)>=33 and not done[3]:
            out=bytearray(p[:33])
            for pid in range(count): out += bytes([pid&255,(pid%4)+1])
            parts[i][1]=out; done[3]=True
    if not all(done.values()): raise ValueError(f'Player metadata parts missing: {done}')

def export_with_scaffold(state:MapState, scaffold:Path|str, output:Path|str):
    version,parts=parse_parts(scaffold)
    area_done=False
    for i,(t,p) in enumerate(parts):
        if t==6 and len(p)>=4:
            side=struct.unpack_from('<I',p,0)[0]
            if side==state.side and len(p)==4+side*side*6:
                parts[i][1]=bytearray(struct.pack('<I',state.side)+state.area.tobytes())
                area_done=True; break
    if not area_done: raise ValueError('Compatible Area part not found in scaffold')
    _set_players(parts,state.starts)
    b=bytearray(8); struct.pack_into('<I',b,4,version)
    for t,p in parts: b += struct.pack('<II',t,8+len(p))+encrypt(p,t)
    struct.pack_into('<I',b,0,checksum(b))
    Path(output).write_bytes(b)
    return checksum(b),len(b)
