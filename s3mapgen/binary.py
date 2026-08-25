"""Confirmed EDM/MAP serialization and read-only SAV parsing boundary.

Only structures demonstrated by project references belong here. EDM/MAP writes
reuse validated scaffolds; SAV data is inspected or copied unchanged, never
synthesized by this module.
"""

from __future__ import annotations
from pathlib import Path
import struct
from .model import MapState


GOODS_DEFAULT_LOW=1
GOODS_DEFAULT_MEDIUM=2
GOODS_DEFAULT_HIGH=3


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

def _goods_default_for_state(state:MapState)->int:
    """Map Info start-goods enum: 1=Low, 2=Medium, 3=High.

    Legacy deliberately defaults to Medium; Upgraded deliberately defaults to High.
    Imported/unknown modes fall back to Medium so the editor never receives the
    invalid/unselected value that previously caused Default-start crashes.
    """
    mode=str(state.metadata.get('mode_key','')).strip().lower()
    return GOODS_DEFAULT_HIGH if mode=='upgraded' else GOODS_DEFAULT_MEDIUM

def _set_players(parts, starts:list[tuple[int,int]], goods_default:int):
    count=len(starts)
    if goods_default not in (GOODS_DEFAULT_LOW,GOODS_DEFAULT_MEDIUM,GOODS_DEFAULT_HIGH):
        raise ValueError(f'Invalid Goods Default value: {goods_default}')
    done={1:False,2:False,3:False}
    for i,(t,p) in enumerate(parts):
        if t==1 and len(p)>=24 and not done[1]:
            vals=list(struct.unpack_from('<6I',p,0))
            vals[1]=count
            # Map Info DWORD 2 is the editor's "Goods Default" / start resources
            # setting. Historical bug: this was incorrectly written as count-1,
            # yielding invalid values (e.g. 19 for 20P) and no selected preset.
            vals[2]=goods_default
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
    _set_players(parts,state.starts,_goods_default_for_state(state))
    b=bytearray(8); struct.pack_into('<I',b,4,version)
    for t,p in parts: b += struct.pack('<II',t,8+len(p))+encrypt(p,t)
    struct.pack_into('<I',b,0,checksum(b))
    Path(output).write_bytes(b)
    return checksum(b),len(b)


def read_area(path:Path|str)->MapState:
    version,parts=parse_parts(path)
    for t,p in parts:
        if t==6 and len(p)>=4:
            side=struct.unpack_from('<I',p,0)[0]
            if len(p)==4+side*side*6:
                import numpy as np
                area=np.frombuffer(p,dtype=np.uint8,offset=4).reshape(side,side,6).copy()
                return MapState(side,area)
    raise ValueError('Compatible Area part not found')
def read_starts(path:Path|str)->list[tuple[int,int]]:
    try:
        _,parts=parse_parts(path)
        for t,p in parts:
            if t==2 and len(p)>=45 and len(p)%45==0:
                out=[]
                for off in range(0,len(p),45):
                    _,x,y=struct.unpack_from('<III',p,off);out.append((int(x),int(y)))
                return out
    except Exception:
        pass
    return []
def _extract_sav_starts_from_player_block(payload:bytes|bytearray, side:int, max_players:int=20)->list[tuple[int,int]]:
    """Recover original player start coordinates from the confirmed SAV v11 player block.

    Native corpus layout: 96-byte prefix, then 20 records of 328 bytes.
    Each active record starts with <III> = player_id, start_x, start_y.
    The sequence is contiguous from player 0; parsing stops at the first nonmatching id.
    """
    out=[]
    prefix=96; stride=328
    for pid in range(max_players):
        off=prefix+pid*stride
        if off+12>len(payload): break
        rec_pid,x,y=struct.unpack_from('<III',payload,off)
        if rec_pid!=pid: break
        if not (0<=x<side and 0<=y<side): break
        out.append((int(x),int(y)))
    return out


def read_sav_state(path:Path|str)->MapState:
    """Read confirmed static/runtime map fields and original starts from a version-11 SAV. Read-only."""
    import numpy as np
    b=Path(path).read_bytes()
    if len(b)<12: raise ValueError('SAV trop court')
    version=struct.unpack_from('<I',b,4)[0]
    if version!=11: raise ValueError(f'Version SAV non supportée: {version}')
    off=8; cols={}; player_blocks=[]
    while off+8<=len(b):
        t,total=struct.unpack_from('<II',b,off)
        if total<8 or off+total>len(b): raise ValueError(f'Part SAV invalide à {off}')
        payload=decrypt(b[off+8:off+total],t)
        low=t&0xffff; x=(t>>16)&0xffff
        if low==3 and len(payload)%24==0:
            cols[x]=payload
        elif t==6:
            player_blocks.append(payload)
        off+=total
    if not cols: raise ValueError('Aucune colonne runtime type-3 trouvée')
    side=max(cols)+1
    if len(cols)!=side: raise ValueError(f'Colonnes SAV incomplètes: {len(cols)}/{side}')
    area=np.zeros((side,side,6),np.uint8); area[:,:,3]=255
    for x in range(side):
        p=cols[x]
        if len(p)!=side*24: raise ValueError(f'Payload colonne {x}: {len(p)} != {side*24}')
        a=np.frombuffer(p,dtype=np.uint8).reshape(side,24)
        area[:,x,0]=a[:,4]
        area[:,x,1]=a[:,6]  # preserve runtime terrains, notably 22/28
        # Byte 7 is the CURRENT runtime object field in played SAVs.
        # Byte 14 preserves the static/original map object and becomes stale after
        # gameplay (harvested trees/stones, crops, buildings, etc.). Importing a
        # SAV must therefore expose byte 7 as MapState.objects.
        area[:,x,2]=a[:,7]
        area[:,x,3]=a[:,8]
        area[:,x,5]=a[:,17]
    starts=[]
    for block in player_blocks:
        candidate=_extract_sav_starts_from_player_block(block,side)
        if len(candidate)>len(starts): starts=candidate
    st=MapState(side,area); st.starts=starts
    st.metadata.update({
        'source_format':'SAV','source_path':str(path),'sav_version':version,
        'territories_available':True,'runtime_terrain_preserved':True,'runtime_objects_preserved':True,
        'sav_original_starts_available':bool(starts),
        'start_territory_source':'sav_player_block_type6' if starts else 'unavailable',
    })
    return st
