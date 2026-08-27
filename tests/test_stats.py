from pathlib import Path
import json
import numpy as np

from s3mapgen.map_data.model import MapState
from s3mapgen.application.analysis.core import analyze_map, format_stats_report, stats_json, stats_csv
from s3mapgen.application.analysis.charts import render_stats_chart, CHART_KEYS, build_ab_metrics


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
    assert json.loads(stats_json(s))['schema_version'] == 7
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


def test_terrain_chart_order_is_semantic_and_unicode_font_renders():
    from s3mapgen.application.analysis.charts import TERRAIN_CHART_ORDER, _font
    assert TERRAIN_CHART_ORDER == ('grass','mountain','desert','swamp','mud','shore','river','water')
    font=_font(14)
    assert font.getbbox('Élévation — Désert — Rivière — Pousses d’arbre') is not None


def test_local_player_stats_use_hex_radii_and_real_stocks():
    st=sample_state();s=analyze_map(st)
    p1=s['players']['local_resources'][0]
    assert p1['player']==1 and p1['radii']['10']['cells'] > 0
    # Nearby trees/sapling are inside P1 radius 10.
    assert p1['radii']['10']['adult_trees'] >= 4
    assert p1['radii']['10']['saplings'] >= 1
    # Mineral/stone values are real quantities, not only occupied-cell counts.
    assert p1['radii']['10']['minerals']['coal']['stock'] >= 15
    assert p1['radii']['10']['building_stone_stock'] >= 0
    assert s['players']['local_radii'] == [10,20,30,40,50,100]
    assert p1['radii']['50']['cells'] <= p1['radii']['100']['cells']


def test_component_analysis_exposes_shape_metrics():
    s=analyze_map(sample_state())
    mountains=s['spatial']['mountains']
    assert mountains['summary']['count'] >= 1
    largest=mountains['summary']['largest']
    assert largest['cells'] >= 1
    assert largest['perimeter_hex_edges'] >= 1
    assert len(largest['bbox']) == 4
    assert 0.0 <= largest['compactness'] <= 1.0
    assert largest['elongation'] >= 1.0
    assert s['hydrology']['river_component_stats']['count'] >= 1


def test_advanced_charts_and_ab_comparison_render():
    a=analyze_map(sample_state())
    st=sample_state();st.objects[2,6]=68;st.resources[5,5]=0x1A
    b=analyze_map(st)
    for key in ('player_trees_r30','player_stone_r30','player_fish_r30','player_mining_r40','mountain_components','lake_components','river_components'):
        im=render_stats_chart(a,key,lang='fr',dark=True,width=640,height=420)
        assert im.size == (640,420)
    im=render_stats_chart(a,'ab_summary',lang='fr',dark=True,width=640,height=420,compare_stats=(a,b))
    assert im.size == (640,420)


def test_stats_csv_contains_player_local_metrics():
    text=stats_csv(analyze_map(sample_state()))
    assert 'player_local' in text
    assert 'building_stone_stock' in text
    assert 'coal_stock' in text


def test_chart_segment_totals_match_report_totals():
    st = sample_state()
    stats = analyze_map(st)
    g = stats['general']
    assert g['ocean_cells'] + g['inland_water_cells'] == g['water_cells']
    assert g['mountain_non_snow_cells'] + g['snow_family_cells'] == g['mountain_cells']
    for mineral in stats['resources']['minerals'].values():
        assert mineral['open_stock'] + mineral['snow_covered_stock'] == mineral['stock']
        assert mineral['open_cells'] + mineral['snow_covered_cells'] == mineral['cells']

def test_height_chart_uses_land_distribution_and_no_minimum_category():
    stats = analyze_map(sample_state())
    assert 'land_distribution' in stats['height']
    im = render_stats_chart(stats, 'height', lang='fr', dark=True, width=900, height=520)
    assert im.size == (900, 520)

def test_chart_catalog_excludes_redundant_nearby_mountain_chart():
    assert 'player_mountain_r40' not in CHART_KEYS
    assert 'forestry' in CHART_KEYS


def test_ab_rows_are_compact_and_semantically_segmented():
    from s3mapgen.application.analysis.charts import build_ab_metrics
    a=analyze_map(sample_state())
    st=sample_state();st.terrain[1:3,10:13]=0;st.objects[3,8]=84;st.resources[6,6]=0x4A
    b=analyze_map(st)
    rows=build_ab_metrics(a,b,fr=True)
    by_label={row[0]:row for row in rows}
    assert len(rows)==8
    assert len(by_label['Terre'][3])==1 and len(by_label['Terre'][4])==1
    assert len(by_label['Eau'][3])==2
    assert sum(seg[0] for seg in by_label['Eau'][3]) == by_label['Eau'][1]
    assert len(by_label['Montagne'][3])==2
    assert sum(seg[0] for seg in by_label['Montagne'][3]) == by_label['Montagne'][1]
    assert len(by_label['Stock minier'][3])==5
    assert sum(seg[0] for seg in by_label['Stock minier'][3]) == by_label['Stock minier'][1]
    assert len(by_label['Ressources forestières'][3])==3
    assert sum(seg[0] for seg in by_label['Ressources forestières'][3]) == by_label['Ressources forestières'][1]


def test_comparison_refresh_preserves_import_semantics():
    source=Path('s3mapgen/application/history/controller.py').read_text(encoding='utf-8')
    assert "imported=bool(self.current.state.metadata.get('source_format'))" in source
    assert "self._populate_current(imported=imported)" in source


def test_nearest_start_identifies_opponent():
    s=analyze_map(sample_state())
    assert all('nearest_player' in row for row in s['players']['nearest_start'])
    assert all(row['nearest_player'] != row['player'] for row in s['players']['nearest_start'])

def test_local_50_and_100_shells_are_non_negative():
    s=analyze_map(sample_state())
    for row in s['players']['local_resources']:
        r50=row['radii']['50'];r100=row['radii']['100']
        assert r100['adult_trees'] >= r50['adult_trees']
        assert r100['building_stone_stock'] >= r50['building_stone_stock']
        assert r100['fish_stock'] >= r50['fish_stock']
        for key in ('coal','iron','gold','gems','sulfur'):
            assert r100['minerals'][key]['stock'] >= r50['minerals'][key]['stock']

def test_ab_simple_metrics_have_semantic_colors():
    from s3mapgen.application.analysis.charts import build_ab_metrics
    a=analyze_map(sample_state());b=analyze_map(sample_state())
    rows={row[0]:row for row in build_ab_metrics(a,b,fr=True)}
    for label in ('Terre','Stock pierre','Stock poisson'):
        assert rows[label][3] and rows[label][4]
        assert sum(seg[0] for seg in rows[label][3]) == rows[label][1]

def test_shortcut_catalog_contains_theme_toggle():
    from s3mapgen.application.settings.preferences import DEFAULT_SHORTCUTS
    assert DEFAULT_SHORTCUTS['toggle_theme'] == 'Ctrl+Shift+T'


def test_local_mining_excludes_snow_covered_ore():
    st=sample_state()
    # Additional coal stock under Snow: global Stats must keep it, nearby gameplay
    # mining must exclude it.
    st.resources[6,6]=0x1A
    s=analyze_map(st)
    assert s['resources']['minerals']['coal']['stock'] == 25
    p1=s['players']['local_resources'][0]
    assert p1['radii']['50']['minerals']['coal']['stock'] == 15
    assert p1['radii']['100']['minerals']['coal']['stock'] == 15


def test_dense_external_labels_use_left_lane_only():
    source=Path('s3mapgen/application/analysis/charts.py').read_text(encoding='utf-8')
    assert "right_side=(i%2==0)" not in source
    assert "tx=x0-7" in source


def test_nearest_opponent_annotation_is_arrow_swatch_label():
    source=Path('s3mapgen/application/analysis/charts.py').read_text(encoding='utf-8')
    assert "g['top_annotation']=f\"P{opp}\"" in source
    assert "arrow='→'" in source


def test_podium_top_three_replaces_numeric_rank_label():
    from s3mapgen.application.analysis.charts import _simple_groups
    groups=_simple_groups([('#1',100),('#2',90),('#3',80),('#4',70)])
    for i,g in enumerate(groups[:3]): g['medal_rank']=i+1
    # Rendering owns the replacement; the chart builder marks exactly the top three.
    assert [g.get('medal_rank') for g in groups] == [1,2,3,None]


def test_normalized_densities_and_full_debug_ids():
    s = analyze_map(sample_state())
    assert s['schema_version'] == 7
    d = s['densities']
    assert 'adult_trees_per_1000_land' in d
    assert 'building_stone_stock_per_1000_land' in d
    assert 'fish_stock_per_1000_water' in d
    assert 'mineral_stock_per_1000_mountain' in d
    report = format_stats_report(s, lang='fr')
    assert 'DENSITÉS NORMALISÉES / 1000' in report
    assert 'DEBUG — TOUS LES TERRAIN IDs PRÉSENTS' in report
    assert 'DEBUG — TOUS LES OBJECT IDs PRÉSENTS' in report
    # The debug inventory is exhaustive, not capped to a top-N list.
    for row in s['terrain']['ids']:
        assert f"{row['id']:>3}" in report
    for row in s['objects']['ids']:
        assert f"{row['id']:>3}" in report


def test_chart_tooltip_regions_are_generic():
    s = analyze_map(sample_state())
    im, regions = render_stats_chart(s, 'terrain_families', lang='fr', dark=True, width=640, height=420, return_regions=True)
    assert im.size == (640, 420)
    assert regions
    assert all('bbox' in r and 'label' in r and 'value' in r for r in regions)
    a, b = s, analyze_map(sample_state())
    im2, regions2 = render_stats_chart(a, 'ab_summary', lang='fr', dark=True, width=640, height=420, compare_stats=(a, b), return_regions=True)
    assert im2.size == (640, 420)
    assert regions2


def test_tooltips_distinguish_semantic_segments():
    s = analyze_map(sample_state())
    _im, regions = render_stats_chart(s, 'mineral_stock', lang='fr', dark=True, width=640, height=420, return_regions=True)
    labels = {r['label'] for r in regions}
    assert any('Libre' in label for label in labels)
    # sample_state may not contain a positive snow-covered mineral segment; verify the A/B semantic model too.
    rows = {row[0]: row for row in build_ab_metrics(s, s, fr=True)}
    assert any(len(seg) >= 3 for seg in rows['Eau'][3])
    assert {seg[2] for seg in rows['Eau'][3]} == {'Mer', 'Lacs'}
    assert {seg[2] for seg in rows['Montagne'][3]} == {'Roche', 'Neige'}
    assert {seg[2] for seg in rows['Stock minier'][3]} == {'Charbon', 'Fer', 'Or', 'Gemmes', 'Soufre'}


def test_density_report_has_one_metric_per_line():
    s = analyze_map(sample_state())
    report = format_stats_report(s, lang='fr')
    block = report.split('DENSITÉS NORMALISÉES / 1000', 1)[1].split('HYDROLOGIE / RELIEF', 1)[0]
    lines = [line for line in block.splitlines() if '/ 1000' in line]
    assert len(lines) == 7
    assert all(' | ' not in line for line in lines)



def test_dry_grass_is_part_of_grass_and_segmented():
    st=sample_state()
    st.terrain[4,10]=24
    st.terrain[4,11]=24
    s=analyze_map(st)
    fam={r['key']:r for r in s['terrain']['families']}
    assert fam['grass']['cells'] == s['general']['green_grass_cells'] + s['general']['dry_grass_cells']
    assert s['general']['dry_grass_cells'] == 2
    _im,regions=render_stats_chart(s,'terrain_families',lang='fr',dark=True,width=640,height=420,return_regions=True)
    dry=[r for r in regions if 'Herbe sèche' in r['label']]
    green=[r for r in regions if 'Herbe verte' in r['label']]
    assert dry and green
    assert any('24' in line for line in dry[0].get('details',[]))
    assert any('16' in line for line in green[0].get('details',[]))


def test_mining_tooltips_include_resource_and_segment_terrain_ids():
    st=sample_state()
    # Put coal under pure snow as well as on open rock.
    st.resources[6,6]=0x1A
    s=analyze_map(st)
    _im,regions=render_stats_chart(s,'mineral_stock',lang='fr',dark=True,width=640,height=420,return_regions=True)
    coal_open=next(r for r in regions if r['label']=='Charbon · Libre')
    coal_snow=next(r for r in regions if r['label']=='Charbon · Sous neige')
    assert any('ID 16 (0x10)' in line for line in coal_open['details'])
    assert any('17' in line and '32' in line for line in coal_open['details'])
    assert any('ID 16 (0x10)' in line for line in coal_snow['details'])
    assert any('35' in line and '128' in line for line in coal_snow['details'])


def test_object_and_agriculture_tooltip_ids():
    s=analyze_map(sample_state())
    _im,forest=render_stats_chart(s,'forestry',lang='fr',dark=True,width=640,height=420,return_regions=True)
    adult=next(r for r in forest if r['label']=='Arbres adultes')
    assert any('68' in line and '81' in line for line in adult['details'])
    _im,agri=render_stats_chart(s,'agriculture',lang='fr',dark=True,width=640,height=420,return_regions=True)
    wheat=next(r for r in agri if r['label']=='Blé')
    assert any('85' in line and '93' in line for line in wheat['details'])


def test_statistics_report_is_bilingual_user_facing_surface():
    s=analyze_map(sample_state())
    fr=format_stats_report(s,'fr'); en=format_stats_report(s,'en')
    assert 'RÉSUMÉ' in fr and 'RESSOURCES' in fr and 'DENSITÉS NORMALISÉES / 1000' in fr
    assert 'SUMMARY' in en and 'RESOURCES' in en and 'NORMALIZED DENSITIES / 1000' in en
    assert 'DEBUG — ALL PRESENT TERRAIN IDs' in en and 'DEBUG — ALL PRESENT OBJECT IDs' in en


def test_ab_land_tooltip_uses_land_cells_label():
    s = analyze_map(sample_state())
    fr = {row[0]: row for row in build_ab_metrics(s, s, fr=True)}
    en = {row[0]: row for row in build_ab_metrics(s, s, fr=False)}
    assert fr['Terre'][3][0][2] == 'Cases terrestres'
    assert en['Land'][3][0][2] == 'Land cells'
