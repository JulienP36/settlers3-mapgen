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

def parse_parts(path:Path|str, *, allow_terminal_padding:bool=False):
    """Parse sequential EDM/MAP parts.

    Some editor-written EDM files append one to three opaque bytes after the
    terminal ``type=0, total_size=8`` part so the complete file ends on a
    DWORD boundary.  Import readers may accept that confirmed file-level
    padding.  Writers keep the historical strict default so an unknown tail is
    never discarded while rebuilding a scaffold.
    """
    b=Path(path).read_bytes(); version=struct.unpack_from('<I',b,4)[0]
    off=8; parts=[]
    while off+8<=len(b):
        t,total=struct.unpack_from('<II',b,off)
        if total<8 or off+total>len(b): raise ValueError(f'Invalid part at {off}')
        parts.append([t,decrypt(b[off+8:off+total],t)])
        off += total
    if off!=len(b):
        tail=b[off:]
        terminal=bool(parts and parts[-1][0]==0 and len(parts[-1][1])==0)
        aligned=len(b)%4==0
        if not (allow_terminal_padding and terminal and aligned and 1<=len(tail)<=3):
            raise ValueError('Part scan did not end at EOF')
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
    version,parts=parse_parts(path,allow_terminal_padding=True)
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
        _,parts=parse_parts(path,allow_terminal_padding=True)
        for t,p in parts:
            if t==2 and len(p)>=45 and len(p)%45==0:
                out=[]
                for off in range(0,len(p),45):
                    _,x,y=struct.unpack_from('<III',p,off);out.append((int(x),int(y)))
                return out
    except Exception:
        pass
    return []
SAV_PLAYER_BLOCK_NATIVE_PREFIX = 84
SAV_PLAYER_BLOCK_LEGACY_PREFIX = 96
SAV_PLAYER_RECORD_STRIDE = 328
SAV_PLAYER_RECORD_COUNT = 20

# The supplied immediate-save corpus gives a direct, format-level signature
# for the native initial territory raster: every active player owns either
# 3,500 or 4,000 cells in type-3 byte 8, and no other claim value is present.
# The cells themselves are always copied from the SAV; these values are only a
# conservative gate that prevents a later, expanded runtime claim raster from
# being advertised as an initial mask.
SAV_INITIAL_MASK_CELL_COUNTS = frozenset((3500, 4000))


def _sav_player_block_prefix(payload:bytes|bytearray)->int|None:
    """Return the exact prefix size for a known fixed-record player block.

    The native SAV corpus supplied for the mapping work is ``84 + 20×328``
    bytes.  A small synthetic fixture used by the original regression suite
    predates that observation and is ``96 + 20×328``; accepting it here keeps
    the reader backwards compatible without treating the old layout as native.
    """
    size=len(payload)
    for prefix in (SAV_PLAYER_BLOCK_NATIVE_PREFIX, SAV_PLAYER_BLOCK_LEGACY_PREFIX):
        if size>=prefix and (size-prefix)%SAV_PLAYER_RECORD_STRIDE==0:
            return prefix
    return None


def _extract_sav_player_records(payload:bytes|bytearray, side:int, max_players:int=20)->list[dict]:
    """Decode only the player fields demonstrated by SAV v11 samples.

    Native records have the following confirmed/strongly supported positions:

    * ``+0``: active flag (``1`` human / ``2`` computer in active records,
      ``0`` in unused slots);
    * ``+4``: a repeated race/faction code, retained as a *candidate*;
    * ``+16`` / ``+20``: original start ``x`` / ``y`` coordinates.

    The remainder of the 328-byte record is deliberately left opaque.  In
    particular, no offset is labelled mana or effective colour until an
    independent corpus proves that meaning.  The legacy 96-byte fixture stores
    contiguous ``<player_id,start_x,start_y>`` tuples and is decoded only for
    compatibility with the old unit test.
    """
    prefix=_sav_player_block_prefix(payload)
    if prefix is None:
        return []
    count=min(max(0,int(max_players)), SAV_PLAYER_RECORD_COUNT, (len(payload)-prefix)//SAV_PLAYER_RECORD_STRIDE)
    records=[]
    if prefix==SAV_PLAYER_BLOCK_LEGACY_PREFIX:
        # Historical synthetic layout: records are contiguous and terminate at
        # the first record whose id is no longer the expected slot number.
        for slot in range(count):
            off=prefix+slot*SAV_PLAYER_RECORD_STRIDE
            rec_pid,x,y=struct.unpack_from('<III',payload,off)
            if rec_pid!=slot:
                break
            valid=0<=x<side and 0<=y<side
            records.append({
                'player':slot+1,'slot':slot+1,'active':bool(valid),
                'active_flag':1 if valid else 0,
                'start_x':int(x) if valid else None,'start_y':int(y) if valid else None,
                'tribe_code_candidate':None,'layout':'legacy_fixture',
                'record_offset':off,
            })
        return records

    for slot in range(count):
        off=prefix+slot*SAV_PLAYER_RECORD_STRIDE
        active_flag=struct.unpack_from('<I',payload,off)[0]
        tribe_code=struct.unpack_from('<I',payload,off+4)[0]
        x,y=struct.unpack_from('<II',payload,off+16)
        valid=0<=x<side and 0<=y<side
        # Native v11 uses 1 for a human-controlled active slot and 2 for a
        # computer-controlled active slot.  Both records carry an original
        # start and participate in the byte-8 territory raster.
        active=active_flag in (1,2)
        records.append({
            'player':slot+1,'slot':slot+1,'active':active,'active_flag':int(active_flag),
            'start_x':int(x) if active and valid else None,
            'start_y':int(y) if active and valid else None,
            'tribe_code_candidate':int(tribe_code) if tribe_code<=255 else None,
            'layout':'native_v11','record_offset':off,
        })
    return records


def _extract_sav_initial_territory_direct_cells(claim: "np.ndarray", player_records: list[dict]) -> dict|None:
    """Return exact native initial-mask cells when the SAV has the known signature.

    This function deliberately performs no radius, shape, wrapping, or
    interpolation.  It only copies coordinates of cells whose type-3 byte 8
    value is one of the active players.  A later SAV whose claims have grown or
    been otherwise modified simply fails the strict immediate-save signature
    and remains available through ``MapState.claim`` as the current runtime
    raster.
    """
    import numpy as np

    active = [
        int(row['player']) - 1
        for row in player_records
        if row.get('active') and row.get('start_x') is not None and row.get('start_y') is not None
    ]
    if not active:
        return None
    active_set = set(active)
    present = {int(value) for value in np.unique(claim) if int(value) != 255}
    if present != active_set:
        return None
    counts = {pid: int(np.count_nonzero(claim == pid)) for pid in active}
    if any(count not in SAV_INITIAL_MASK_CELL_COUNTS for count in counts.values()):
        return None

    cells: dict[str, list[list[int]]] = {}
    for pid in active:
        # np.argwhere returns (y, x); metadata is stored as the map's public
        # (x, y) coordinates, matching starts and all other map APIs.
        ys, xs = np.where(claim == pid)
        cells[str(pid + 1)] = [[int(x), int(y)] for y, x in zip(ys, xs)]
    return {
        'cells': cells,
        'player_cell_counts': {str(pid + 1): counts[pid] for pid in active},
        'total_cells': int(sum(counts.values())),
        'source': 'sav_type3_byte8_direct_initial_claims',
        'signature': 'active_player_counts_3500_or_4000',
    }


def _extract_sav_starts_from_player_block(payload:bytes|bytearray, side:int, max_players:int=20)->list[tuple[int,int]]:
    """Recover original player start coordinates from a SAV v11 player block."""
    out=[]
    for row in _extract_sav_player_records(payload,side,max_players):
        x,y=row.get('start_x'),row.get('start_y')
        if row.get('active') and x is not None and y is not None:
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
    best_player_records=[]
    best_player_layout=None
    for block in player_blocks:
        records=_extract_sav_player_records(block,side)
        candidate=[(int(row['start_x']),int(row['start_y'])) for row in records if row.get('active') and row.get('start_x') is not None and row.get('start_y') is not None]
        if len(candidate)>len(starts) or (records and not best_player_records):
            starts=candidate
            best_player_records=records
            best_player_layout=_sav_player_block_prefix(block)
    st=MapState(side,area); st.starts=starts
    direct_initial_mask = _extract_sav_initial_territory_direct_cells(area[:,:,3], best_player_records)
    st.metadata.update({
        'source_format':'SAV','source_path':str(path),'sav_version':version,
        'territories_available':True,'runtime_terrain_preserved':True,'runtime_objects_preserved':True,
        'sav_original_starts_available':bool(starts),
        'start_territory_source':'sav_player_block_type6' if starts else 'unavailable',
        # Byte 8 is the exact current runtime claim raster for every SAV.  A
        # second, opt-in field is attached only when the complete raster also
        # matches the observed immediate-save signature above.
        'runtime_claim_source':'sav_type3_byte8',
        'initial_territory_mask_status':'direct' if direct_initial_mask else 'not_detected',
        'initial_territory_mask_source':direct_initial_mask['source'] if direct_initial_mask else None,
        'initial_territory_direct_cells':direct_initial_mask['cells'] if direct_initial_mask else None,
        'initial_territory_direct_counts':direct_initial_mask['player_cell_counts'] if direct_initial_mask else None,
        'initial_territory_direct_total_cells':direct_initial_mask['total_cells'] if direct_initial_mask else 0,
        'initial_territory_direct_signature':direct_initial_mask['signature'] if direct_initial_mask else None,
        # These values are structural facts of the native corpus, not guesses
        # about the opaque fields that follow each player record.
        'sav_player_block': {
            'part_type':6, 'prefix_bytes':best_player_layout,
            'record_stride':SAV_PLAYER_RECORD_STRIDE,
            'record_count':len(best_player_records),
            'active_count':sum(1 for row in best_player_records if row.get('active')),
        } if best_player_records else None,
        'sav_player_records':best_player_records,
        'sav_player_metadata_status': {
            'start_coordinates':'confirmed',
            'active_flag':'confirmed',
            'tribe_code':'candidate',
            'effective_color':'not_decoded',
            'mana_current':'not_decoded',
            'mana_maximum':'not_decoded',
        },
    })
    return st
