import numpy as np
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.constants import GRASS
from s3mapgen.application.rendering.preview import BOUNDARY_START_MARKER_SIZE_PROJECTED, BOUNDARY_START_MARKER_SIZE_SQUARE, PLAYER_COLORS, PLAYER_START_MARKERS, START_TERRITORY_RADIUS, INITIAL_TERRITORY_ROW_RANGES, _centered_marker_origin, _ordered_boundary_offsets, compose_start_markers, initial_territory_cells, initial_territory_boundary, render

def _state(side=128):
    s=MapState.empty(side);s.terrain[:]=GRASS;s.height[:]=np.arange(side,dtype=np.uint8)[:,None];s.resources[8:12,8:12]=0x1f;s.claim[4:20,4:20]=0;return s

def test_overlay_alpha_zero_matches_global():
    s=_state();assert np.array_equal(np.asarray(render(s,view='heightmap',overlay_alpha=0,labels=False)),np.asarray(render(s,view='global',labels=False)))

def test_overlay_alpha_changes_visualization():
    s=_state();a=np.asarray(render(s,view='resources',overlay_alpha=25));b=np.asarray(render(s,view='resources',overlay_alpha=100));assert not np.array_equal(a,b)

def test_parallelogram_projection_uses_exact_half_cell_row_offset():
    s=_state(32);im=render(s,projection='parallelogram',labels=False);assert im.height==64 and im.width==95 and im.mode=='RGBA'

def test_legacy_start_mask_reference_shape_is_stable():
    assert START_TERRITORY_RADIUS==35 and len(INITIAL_TERRITORY_ROW_RANGES)==71
    assert len(initial_territory_cells((64,64),128))==3500
    assert len(initial_territory_boundary((64,64),128))==210

def test_initial_territory_wraps_without_losing_cells():
    assert len(initial_territory_cells((3,3),128))==3500

def test_player_marker_palette_supports_twenty_players():
    assert len(PLAYER_COLORS)==20 and len(set(PLAYER_COLORS))==20

def test_global_is_clean_and_starts_view_adds_sprite_boundary():
    s=_state();s.starts=[(64,64)]
    clean=np.asarray(render(s,labels=True,view='global',projection='square'))
    baseline=np.asarray(render(s,labels=False,view='global',projection='square'))
    assert np.array_equal(clean,baseline)
    starts=np.asarray(render(s,labels=True,view='starts',projection='square'))
    assert not np.array_equal(starts,baseline)

def test_crops_view_uses_distinct_wheat_vine_rice_colors():
    s=_state(32)
    s.objects[5,5]=88
    s.objects[6,6]=98
    s.objects[7,7]=106
    rgb=np.asarray(render(s,view='crops',labels=False))[:,:,:3]
    assert tuple(rgb[5,5])==(235,205,75)
    assert tuple(rgb[6,6])==(165,85,185)
    assert tuple(rgb[7,7])==(80,205,110)
    assert len({tuple(rgb[5,5]),tuple(rgb[6,6]),tuple(rgb[7,7])})==3


def test_crops_view_highlights_bee_nests_with_honey_color():
    s=_state(32)
    s.objects[8,8]=247
    s.objects[9,9]=253
    rgb=np.asarray(render(s,view='crops',labels=False))[:,:,:3]
    assert tuple(rgb[8,8])==(205,118,24)
    assert tuple(rgb[9,9])==(205,118,24)


def test_paths_view_does_not_highlight_agricultural_terrain_22():
    s=_state(32)
    s.terrain[5,5]=22
    s.terrain[6,6]=28
    rgb=np.asarray(render(s,view='paths',labels=False))[:,:,:3]
    # Terrain 28 remains the dedicated path highlight.
    assert tuple(rgb[6,6])==(235,175,85)
    # Terrain 22 must not use the former dedicated agricultural highlight.
    assert tuple(rgb[5,5])!=(195,135,75)

def test_resource_view_uses_requested_mineral_colors():
    s=_state(32)
    for x,raw in enumerate((0x11,0x21,0x31,0x41,0x51),start=5):
        s.resources[10,x]=raw
    rgb=np.asarray(render(s,view='resources',labels=False))[:,:,:3]
    assert tuple(rgb[10,5])==(0,0,0)          # coal: editor black
    assert tuple(rgb[10,6])==(255,148,0)      # iron: editor orange
    assert tuple(rgb[10,7])==(255,255,0)      # gold: editor yellow
    assert tuple(rgb[10,8])==(206,0,0)        # gems: editor red
    assert tuple(rgb[10,9])==(196,178,92)     # sulfur: lighter beige/ochre for separation


def test_player_9_is_near_white_and_distinct():
    assert min(PLAYER_COLORS[8]) >= 225
    assert len(set(PLAYER_COLORS)) == 20

def test_start_marker_reference_extracts_twenty_ordered_native_sprites():
    assert len(PLAYER_START_MARKERS)==20
    assert {marker.size for marker in PLAYER_START_MARKERS}=={(36,48)}
    assert all(marker.mode=='RGBA' and marker.getchannel('A').getbbox() for marker in PLAYER_START_MARKERS)

def test_global_batch_marker_mode_adds_centers_without_initial_boundaries():
    s=_state();s.starts=[(64,64)]
    clean=np.asarray(render(s,labels=False,view='global'))[:,:,:3]
    marked=np.asarray(render(s,labels=False,view='global',start_markers=True,start_marker_scale=2))[:,:,:3]
    assert not np.array_equal(clean[20:70,40:90],marked[20:70,40:90])
    x,y=next(iter(initial_territory_boundary((64,64),128)))
    assert tuple(marked[y,x])==tuple(clean[y,x])

def test_territories_use_exact_player_palette_without_wrapping_unknown_claims():
    s=_state(32);s.claim[:]=255
    for player in range(20):s.claim[player,player]=player
    s.claim[20,20]=20
    rgb=np.asarray(render(s,view='territories',overlay_alpha=100,labels=False))[:,:,:3]
    for player,color in enumerate(PLAYER_COLORS):assert tuple(rgb[player,player])==color
    assert tuple(rgb[20,20])==(65,65,65)

def test_start_marker_is_geometrically_centered_on_start_in_batch_mode():
    s=_state();s.starts=[(64,64)]
    clean=np.asarray(render(s,labels=False,view='global'))[:,:,:3]
    marked=np.asarray(render(s,labels=False,view='global',start_markers=True))[:,:,:3]
    ys,xs=np.where(np.any(clean!=marked,axis=2))
    assert (xs.min(),ys.min(),xs.max()+1,ys.max()+1)==(55,52,73,76)
    assert _centered_marker_origin(PLAYER_START_MARKERS[0].resize((18,24)),64,64)==(55,52)

def test_cached_marker_free_base_composes_to_the_exact_direct_render():
    s=_state();s.starts=[(64,64)]
    for projection in ('square','parallelogram'):
        base=render(s,labels=False,view='global',projection=projection)
        untouched=np.asarray(base).copy()
        for scale in (1,2):
            layered=np.asarray(compose_start_markers(base,s,projection=projection,scale=scale))
            direct=np.asarray(render(s,labels=False,view='global',projection=projection,start_markers=True,start_marker_scale=scale))
            assert np.array_equal(layered,direct)
            assert np.array_equal(np.asarray(base),untouched)

def test_sprite_boundary_uses_all_210_cells_of_the_exact_native_outline():
    square=_ordered_boundary_offsets(False)
    projected=_ordered_boundary_offsets(True)
    canonical={(x-64,y-64) for x,y in initial_territory_boundary((64,64),128)}
    assert len(square)==len(set(square))==210
    assert len(projected)==len(set(projected))==210
    assert set(square)==canonical and set(projected)==canonical
    assert BOUNDARY_START_MARKER_SIZE_SQUARE==(1,1)
    assert BOUNDARY_START_MARKER_SIZE_PROJECTED==(2,2)

def test_starts_without_direct_mask_does_not_draw_a_reconstructed_boundary():
    s=_state();s.starts=[(64,64)]
    global_view=np.asarray(render(s,labels=True,view='global',projection='square'))
    starts=np.asarray(render(s,labels=True,view='starts',overlay_alpha=0,projection='square'))
    assert not np.array_equal(starts,global_view)
    # With no direct native mask attached, only the centred start sprite is
    # allowed; the 210-cell reconstructed contour must remain absent.
    x,y=next(iter(initial_territory_boundary((64,64),128)))
    assert tuple(starts[y,x])==tuple(global_view[y,x])

def test_territories_without_source_claims_stay_unclaimed():
    s=_state();s.claim[:]=255;s.starts=[(64,64)]
    for source_format in ('EDM','MAP','SAV'):
        s.metadata.update(source_format=source_format,territories_available=False)
        rgb=np.asarray(render(s,view='territories',overlay_alpha=100,labels=False))[:,:,:3]
        assert int(np.all(rgb==np.asarray(PLAYER_COLORS[0]),axis=2).sum())==0


def test_initial_mask_view_uses_only_explicit_direct_cells():
    s=_state(16);s.starts=[(2,2),(12,12)]
    s.metadata['initial_territory_direct_cells']={'1':[(1,1),(3,4)],'2':[(4,6)]}
    rgb=np.asarray(render(s,view='initial_territory',overlay_alpha=100,labels=False))[:,:,:3]
    assert tuple(rgb[1,1])==PLAYER_COLORS[0]
    assert tuple(rgb[4,3])==PLAYER_COLORS[0]
    assert tuple(rgb[6,4])==PLAYER_COLORS[1]
    assert tuple(rgb[0,0])==(65,65,65)


def test_initial_mask_view_adds_diagonal_hatching_only_inside_the_direct_mask():
    s=_state(32);s.starts=[(8,8)]
    cells=[(x,y) for y in range(4,20) for x in range(4,20)]
    s.metadata['initial_territory_direct_cells']={'1':cells}
    rgb=np.asarray(render(s,view='initial_territory',overlay_alpha=100,labels=False))[:,:,:3]
    hatch=np.all(rgb==np.asarray((245,245,245)),axis=2)
    assert int(hatch.sum())>0
    assert not np.any(hatch[:4]) and not np.any(hatch[20:])
    assert not np.any(hatch[:, :4]) and not np.any(hatch[:,20:])


def test_initial_mask_view_never_reconstructs_from_start_coordinates():
    s=_state(128);s.starts=[(64,64)]
    rgb=np.asarray(render(s,view='initial_territory',overlay_alpha=100,labels=False))[:,:,:3]
    assert int(np.all(rgb==np.asarray(PLAYER_COLORS[0]),axis=2).sum())==0

def test_sav_territories_keep_runtime_claims_instead_of_synthetic_radius():
    s=_state();s.claim[:]=255;s.claim[5,6]=1;s.starts=[(64,64)];s.metadata.update(source_format='SAV',territories_available=True)
    rgb=np.asarray(render(s,view='territories',overlay_alpha=100,labels=False))[:,:,:3]
    assert tuple(rgb[5,6])==PLAYER_COLORS[1]
    assert tuple(rgb[64,64])==(65,65,65)
