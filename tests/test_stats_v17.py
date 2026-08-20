from pathlib import Path
import json
import numpy as np

from s3mapgen.model import MapState
from s3mapgen.stats_analysis import analyze_map, format_stats_report, stats_json, stats_csv
from s3mapgen.stats_charts import render_stats_chart, CHART_KEYS


def sample_state():
    st=MapState.empty(16)
    st.terrain[:]=16
    st.terrain[0,:]=0
    st.terrain[:,0]=0
    st.terrain[5:8,5:8]=32
    st.terrain[6,6]=128
    st.terrain[10:12,10:12]=64
    st.terrain[3,3]=96;st.terrain[3,4]=97
    st.objects[2,2]=68;st.objects[2,3]=70;st.objects[2,4]=72;st.objects[2,5]=78
    st.objects[4,4]=84
    st.objects[8,8]=115;st.objects[8,9]=126;st.objects[8,10]=127
    st.objects[9,1]=85;st.objects[9,2]=94;st.objects[9,3]=103
    st.resources[5,5]=0x1F;st.resources[5,6]=0x25;st.resources[5,7]=0x33
    st.resources[0,5]=0x07
    st.starts=[(2,2),(12,12),(12,2)]
    st.claim[1:4,1:4]=0
    return st


def test_stats_core_invariants_and_sapling_semantics():
    st=sample_state();s=analyze_map(st)
    assert sum(r['cells'] for r in s['terrain']['ids']) == st.side**2
    assert s['general']['land_cells'] + s['general']['water_cells'] == st.side**2
    assert s['vegetation']['saplings'] == 1
    assert s['vegetation']['sapling_label_fr'] == "Pousses d’arbre"
    assert 'SmallTree84' not in format_stats_report(s,'fr')
    assert 'Tree saplings' in format_stats_report(s,'en')


def test_building_stone_stock_including_exhausted_127():
    s=analyze_map(sample_state())
    assert s['building_stones']['anchors_total'] == 3
    assert s['building_stones']['anchors_active'] == 2
    assert s['building_stones']['anchors_exhausted_127'] == 1
    assert s['building_stones']['stock_total'] == (127-115)+(127-126)
    state127=next(r for r in s['building_stones']['states'] if r['object_id']==127)
    assert state127['stock'] == 0 and state127['units_each'] == 0


def test_mineral_stock_and_fish_stock():
    s=analyze_map(sample_state())
    assert s['resources']['minerals']['coal']['cells'] == 1
    assert s['resources']['minerals']['coal']['stock'] == 15
    assert s['resources']['minerals']['iron']['stock'] == 5
    assert s['resources']['minerals']['gold']['stock'] == 3
    assert s['resources']['fish_cells'] == 1
    assert s['resources']['fish_stock'] == 7


def test_start_distance_distribution_and_claims():
    s=analyze_map(sample_state())
    assert len(s['players']['nearest_start']) == 3
    assert s['players']['claims']['1'] == 9
    assert all(row['distance'] > 0 for row in s['players']['nearest_start'])


def test_exports_roundtrip():
    s=analyze_map(sample_state())
    assert json.loads(stats_json(s))['schema_version'] == 1
    csv_text=stats_csv(s)
    assert 'terrain_family' in csv_text and 'building_stone' in csv_text and 'saplings' in csv_text


def test_all_initial_charts_render():
    s=analyze_map(sample_state())
    for key in CHART_KEYS:
        im=render_stats_chart(s,key,lang='fr',dark=True,width=640,height=420)
        assert im.size == (640,420)
        assert im.mode == 'RGB'

def test_all_validated_adult_tree_ids_are_counted_and_named_semantically():
    st=sample_state()
    ids=(73,74,75,76,77,80,81)
    for idx,oid in enumerate(ids): st.objects[12,idx+1]=oid
    s=analyze_map(st)
    assert s['vegetation']['families']['other_adult'] == len(ids)
    assert s['vegetation']['adult_wood_trees'] == 3 + len(ids)  # birch + elm + oak + other adults
    by_id={r['id']:r for r in s['objects']['ids']}
    assert all(by_id[oid]['name_fr'].startswith('Arbre adulte') for oid in ids)


def test_terrain_families_include_transition_cells_and_mud_family():
    st=sample_state()
    # Desert family: grass/desert transition + desert transition + desert.
    st.terrain[13,1]=20;st.terrain[13,2]=65;st.terrain[13,3]=64
    # Swamp family: grass/swamp transition + swamp transition + swamp.
    st.terrain[14,1]=21;st.terrain[14,2]=81;st.terrain[14,3]=80
    # Mud family includes all three known mud-family IDs.
    st.terrain[15,1]=23;st.terrain[15,2]=144;st.terrain[15,3]=145
    s=analyze_map(st);fam={r['key']:r['cells'] for r in s['terrain']['families']}
    assert fam['desert'] >= 3 and fam['swamp'] >= 3 and fam['mud'] == 3
    # Mountain family includes its transition chain and snow.
    st.terrain[12,8]=17;st.terrain[12,9]=33;st.terrain[12,10]=35;st.terrain[12,11]=129
    s=analyze_map(st);fam={r['key']:r['cells'] for r in s['terrain']['families']}
    assert fam['mountain'] >= 4


def test_terrain_chart_order_is_semantic_and_horizontal_unicode_font_renders():
    from s3mapgen.stats_charts import TERRAIN_CHART_ORDER, _font
    assert TERRAIN_CHART_ORDER == ('grass','mountain','desert','swamp','mud','shore','river','water')
    font=_font(14)
    assert font.getbbox('Élévation — Désert — Rivière — Pousses d’arbre') is not None
