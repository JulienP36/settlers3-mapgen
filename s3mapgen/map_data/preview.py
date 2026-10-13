"""Shared schematic colors and native RGB555 minimap serialization."""
from __future__ import annotations
import struct
import numpy as np
from PIL import Image
from .constants import *
from .model import MapState
from .object_context import decoration_objects, reef_mask, construction_mask, felling_mask, is_runtime

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
REEF_COLOR=(66,60,57)
SAPLING_COLOR=(150,210,112)
# ID 34 is the native one-cell rocky-grass patch.  The muted yellow/olive
# sample keeps it distinct from Rocky while staying close to the reference
# texture shown in the native editor.
ROCKY_GRASS_PATCH_COLOR=(178,157,52)
PALETTE={GRASS:(72,148,69),18:(101,166,78),19:(116,177,88),DRY_GRASS:(155,166,80),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),SWAMP:(25,89,79),SWAMP_TRANS:(42,111,88),GRASS_SWAMP_TRANS:(79,132,73),MUD:(137,98,62),MUD_TRANS_2:(116,82,54),MUD_TRANS_1:(86,61,45),22:(147,112,72),28:(126,99,66),ROCKY_DETAIL:ROCKY_GRASS_PATCH_COLOR,96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)}

# Retained native sculpture cells use the base land color in this schematic
# renderer. Keep their actual ID and blocking flag in MapState/export; this
# color does not assert a native texture or an original terrain name.
PALETTE[0x70] = PALETTE[GRASS]

def global_rgb(state:MapState)->np.ndarray:
    T=state.terrain;O=decoration_objects(state);side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    for i,c in enumerate(WATER_COLORS):rgb[T==i]=c
    for tid,c in PALETTE.items():rgb[T==tid]=c
    rgb[rgb.sum(axis=2)==0]=(150,150,150)
    # Static world-decor families are single-cell anchors in the preview.  The
    # colors are intentionally restrained so they remain legible over their
    # ecological support without pretending to be the game's sprites.
    rgb[np.isin(O,range(1,29))]=(130,130,126)      # stones
    rgb[np.isin(O,range(29,34))]=(126,91,58)       # wrecks
    rgb[O==34]=(112,106,106)                      # graves
    rgb[np.isin(O,range(35,43))]=(86,132,62)      # plants / fungi / stumps
    rgb[np.isin(O,range(43,45))]=(72,84,58)       # dead trees
    rgb[np.isin(O,range(45,50))]=(180,134,52)     # desert props
    rgb[np.isin(O,range(50,62))]=(66,137,58)      # flowers / bushes
    rgb[np.isin(O,range(62,68))]=(55,130,92)      # reeds
    adult=(O>=68)&(O<=81)&~np.isin(O,[78,79])
    rgb[adult]=(25,88,34);rgb[np.isin(O,[78,79])]=(46,113,51);rgb[O==84]=SAPLING_COLOR
    rgb[(O>=115)&(O<=126)]=(205,205,198);rgb[O==127]=(150,150,145)
    rgb[reef_mask(state)]=REEF_COLOR
    raw=state.objects
    rgb[np.isin(raw,range(224,231))]=SAPLING_COLOR
    rgb[np.isin(raw,range(216,223))]=(72,155,72)
    rgb[np.isin(raw,range(208,215))]=(126,91,58)
    if is_runtime(state):
        rgb[felling_mask(state)]=(106,112,54)
        rgb[construction_mask(state)]=(196,151,83)
    return rgb

def editor_minimap_payload(state: MapState) -> bytearray:
    image = Image.fromarray(global_rgb(state)).resize((256, 256), Image.Resampling.NEAREST)
    rgb = np.asarray(image, dtype=np.uint16) >> 3
    pixels = (rgb[:, :, 0] << 10) | (rgb[:, :, 1] << 5) | rgb[:, :, 2]
    return bytearray(struct.pack('<I', 256) + pixels.astype('<u2').tobytes())
