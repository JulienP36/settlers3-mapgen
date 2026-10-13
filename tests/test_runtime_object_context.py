"""SAV interpretation must agree across preview, statistics and chart focus."""
import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.preview import global_rgb, REEF_COLOR, SAPLING_COLOR
from s3mapgen.map_data.object_context import reef_mask, construction_mask
from s3mapgen.application.rendering.preview import render_square_base
from s3mapgen.application.rendering.focus import focus_mask
from s3mapgen.application.analysis.core import analyze_map
from s3mapgen.application.analysis.charts import _decorative_groups
from s3mapgen.generation.start_diagnostics import departure_source


def sample(fmt='SAV', side=64):
    state = MapState.empty(side)
    state.terrain[:] = 16
    state.metadata['source_format'] = fmt
    # All four reef stages, two land markers, unknowns, lifecycle and consumed tree.
    for index, oid in enumerate((13,14,15,16,112,113,111,114,224,216,208,128,133,135,0)):
        state.objects[20,index+20] = oid
    state.terrain[20,20:24] = 0
    state.original_objects = np.full((side,side), 70, np.uint8)
    return state


def test_runtime_reef_names_counts_graphs_and_focus_share_context():
    state=sample(); before=state.area.copy()
    stats=analyze_map(state)
    assert stats['objects']['families']['reefs'] == 4
    assert stats['objects']['decorative_families']['reefs'] == 4
    assert stats['objects']['decorative_families']['decorative_stones'] == 0
    names={r['id']:r['name_fr'] for r in stats['objects']['ids']}
    assert names[13] == 'Récif 1'
    assert names[112] == 'Panneau de chantier'
    assert names[113] == 'Piquet de chantier'
    assert 'inconnu' in names[111] and 'inconnu' in names[114]
    assert 'abattage' in names[128]
    assert 'non confirmé' in names[133] and 'non confirmé' in names[135]
    groups=_decorative_groups(stats)
    reefs=next(g for g in groups if g['label']=='Récifs')
    assert sum(segment[0] for segment in reefs['segments']) == 4
    stones=next(g for g in groups if g['label']=='Pierres décoratives')
    assert sum(segment[0] for segment in stones['segments']) == 0
    focus=reefs['segments'][0][4]
    assert focus['ids'] == (13,14,15,16)
    assert np.array_equal(focus_mask(state,focus),reef_mask(state))
    # Explicit raw-ID selection remains a raw-ID selection, unlike semantic family focus.
    assert focus_mask(state,{'kind':'object_ids','ids':(112,113)}).sum() == 2
    assert not focus_mask(state,{'kind':'object_family','family':'border_stones','ids':tuple(range(13,21))}).any()
    assert np.array_equal(state.area,before)


@pytest.mark.parametrize('view',['global','heightmap','resources','territories'])
def test_sav_reefs_only_on_water_in_all_rendered_views(view):
    state=sample();image=np.asarray(render_square_base(state,view))
    assert np.all(image[20,20:24] == REEF_COLOR)
    assert not np.any(np.all(image[20,24:28] == REEF_COLOR,axis=-1))
    rgb=global_rgb(state)
    assert tuple(rgb[20,28]) == SAPLING_COLOR
    assert tuple(rgb[20,34]) == (72,148,69)  # consumed tree must stay absent


def test_static_maps_keep_their_reef_and_border_stone_catalogue():
    state=sample('MAP');stats=analyze_map(state)
    assert stats['objects']['families']['reefs'] == 4
    assert stats['objects']['decorative_families']['decorative_stones'] == 4
    mask=focus_mask(state,{'kind':'object_family','family':'reefs','ids':(111,112,113,114)})
    assert mask[20,24:28].all() and not mask[20,20:24].any()
    assert np.all(global_rgb(state)[20,24:28] == REEF_COLOR)


def test_empty_water_and_unconfirmed_terrestrial_runtime_ids_are_not_reefs():
    state=sample();state.objects[30,30]=13;state.objects[31,31]=0;state.terrain[31,31]=0
    assert not reef_mask(state)[30,30] and not reef_mask(state)[31,31]
    assert analyze_map(state)['objects']['families']['reefs'] == 4


def test_start_filter_ignores_building_markers_on_copy_without_restoring_originals():
    state=sample();state.objects[40,40]=70;state.claim[:]=0
    before=state.area.copy()
    source,_=departure_source(state,'current')
    assert np.all(source.objects[construction_mask(state)] == 0)
    assert source.objects[40,40] == 70
    assert np.all(source.claim == 255)
    assert source.objects[20,34] == 0  # no resurrection via byte14
    assert np.array_equal(state.area,before)
