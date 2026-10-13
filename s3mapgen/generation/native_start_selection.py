"""Random branch of S3 0x5074B0 selection control flow, with explicit runtime callbacks.

Used by classic_starts on the completed map. Its runtime owns native validity
and successive town effects. Raw mode IDs
and even unresolved slot calls are preserved, rather than silently repaired.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .generators.legacy.native_terrain import NativeRng16


@dataclass
class NativeStartSlot:
    enabled: int = 0
    placed: int = 0
    mirror_id: int = 0
    fixed_x: int = -1
    fixed_y: int = 0


@dataclass(frozen=True)
class NativeSelectionOutcome:
    disabled_slots: tuple[int, ...]


def native_start_distance(x: int, y: int, other_x: int, other_y: int) -> int:
    """0x4FF320, unsigned comparisons and DWORD arithmetic (also out of bounds)."""
    a,b,c,d = (int(v) & 0xFFFFFFFF for v in (x,y,other_x,other_y))
    if a < c:
        value = max(c-a,d-b) if b < d else b-a-d+c
    else:
        value = a-b-c+d if b < d else max(a-c,b-d)
    return value & 0xFFFFFFFF


def select_native_starts(
    side: int, mode: int, slots: Sequence[NativeStartSlot], rng: NativeRng16,
    *,
    quality: Callable[[int, int, int, int], bool],
    create_town: Callable[[int, int, int], object],
) -> NativeSelectionOutcome:
    """Select random starts; town callbacks own placed/context/PRNG writes.

    Quality calls whose results the EXE ignores are deliberately retained.
    Fixed-coordinate/manual departures are outside this fresh-map route.
    """
    if not 64 <= int(side) <= 768 or len(slots) != 20:
        raise ValueError('Expected square side 64..768 and 20 native slots')
    disabled = []

    def mirror(key):
        return next((i for i,s in enumerate(slots)
                     if s.enabled and not s.placed and s.mirror_id == key), -1)

    def town(i,x,y):
        create_town(i,x,y)

    for i,slot in enumerate(slots):
        if not slot.enabled or slot.placed or not 0 <= mode <= 3:
            continue
        margin = 32 if mode in (1,2) else 16
        span = side - (2*margin-1)
        for attempt in range(1000000):
            x,y = margin+((rng.next()*span)>>16),margin+((rng.next()*span)>>16)
            swap = (y,x)
            complement = (side-1-x,side-1-y)
            anti = (side-1-y,side-1-x)
            if mode in (1,3) and native_start_distance(x,y,*swap) <= 60:
                continue
            if mode == 2 and native_start_distance(x,y,*anti) <= 60:
                continue
            if mode == 3 and native_start_distance(x,y,*anti) <= 60:
                continue
            if not quality(i,x,y,attempt):
                continue
            partners = []
            if mode:
                m1 = mirror(1)
                if m1 != -1:
                    point1 = anti if mode == 2 else swap
                    if not quality(m1,*point1,attempt):
                        continue
                    partners.append((m1,point1))
                    if mode == 3:
                        m2 = mirror(2)
                        if m2 != -1:
                            if not quality(m2,*anti,attempt):
                                continue
                            partners.append((m2,anti))
                            m3 = mirror(3)
                            if m3 != -1:
                                if not quality(m3,*complement,attempt):
                                    continue
                                partners.append((m3,complement))
                # Revalidation of the primary before creation; return ignored.
                quality(i,x,y,attempt)
            town(i,x,y)
            for partner,point in partners:
                quality(partner,*point,attempt)
                town(partner,*point)
            break
        else:
            slot.enabled = 0
            disabled.append(i)
    return NativeSelectionOutcome(tuple(disabled))
