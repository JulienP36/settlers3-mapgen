from pathlib import Path

import pytest

from s3mapgen.application.exports.planning import (
    existing_export_paths,
    map_export_capabilities,
    map_export_paths,
    safe_export_basename,
    stats_export_paths,
)
from s3mapgen.application.ui.i18n.exports import EXPORT_TEXT


ANALYSIS_SRC=Path('s3mapgen/application/analysis/controller.py').read_text(encoding='utf-8')
EXPORT_SRC=Path('s3mapgen/application/exports/controller.py').read_text(encoding='utf-8')


def test_export_basename_is_windows_safe_and_never_empty():
    assert safe_export_basename('  My map: 4P / test?.  ')=='My_map__4P___test_'
    assert safe_export_basename('valid_name')=='valid_name'
    assert safe_export_basename('CON')=='_CON'
    with pytest.raises(ValueError):safe_export_basename(' . ')


def test_map_capabilities_follow_validated_writer_rules(tmp_path):
    sav=tmp_path/'source.sav';sav.write_bytes(b'S3')
    assert map_export_capabilities(768,sav)=={'edm':True,'map':True,'sav':True,'png_global':True,'png_current':True}
    for side in (640, 832, 896, 960, 1024):
        assert map_export_capabilities(side,sav)=={'edm':True,'map':True,'sav':True,'png_global':True,'png_current':True}
    assert map_export_capabilities(768,tmp_path/'missing.sav')['sav'] is False
    assert map_export_capabilities(768,tmp_path/'source.edm')['sav'] is False


def test_map_and_stats_plans_use_one_safe_basename(tmp_path):
    maps=map_export_paths(tmp_path,'My Map',['edm','map','sav','png_global','png_current'])
    assert {key:path.name for key,path in maps.items()}=={
        'edm':'My_Map.edm','map':'1-My_Map.map','sav':'My_Map.sav',
        'png_global':'My_Map_global.png','png_current':'My_Map_current_view.png',
    }
    stats=stats_export_paths(tmp_path,'My Stats',['json','csv','png'])
    assert [path.name for path in stats.values()]==['My_Stats.json','My_Stats.csv','My_Stats.png']


def test_conflict_detection_is_grouped(tmp_path):
    paths=stats_export_paths(tmp_path,'stats',['json','csv','png'])
    paths['csv'].write_text('existing',encoding='utf-8')
    assert existing_export_paths(paths)==[paths['csv']]


def test_export_centers_are_bilingual_and_replace_separate_chart_buttons():
    assert EXPORT_TEXT['fr']['map_title']=='Exporter la carte'
    assert EXPORT_TEXT['en']['stats_title']=='Export statistics and chart'
    charts=ANALYSIS_SRC[ANALYSIS_SRC.index('def _build_stats_charts_tab'):ANALYSIS_SRC.index('def _refresh_stats_chart_labels')]
    assert "command=self._open_stats_export_center" in charts
    assert "text='Exporter JSON'" not in charts
    assert "text='Exporter CSV'" not in charts
    assert "text='Exporter PNG'" not in charts


def test_map_center_keeps_sav_copy_only_and_two_distinct_real_png_renders():
    center=EXPORT_SRC[EXPORT_SRC.index('def _open_map_export_center'):]
    assert "shutil.copy2(source_path,paths['sav'])" in center
    assert "labels=False,view='global'" in center
    assert "render(state,paths['png_current'],labels=True,**self._render_options())" in center
    assert "self._confirm_export_conflicts(paths,w,text)" in center
    assert 'write_sav' not in center


def test_global_view_disables_redundant_current_view_png_and_selects_global_png():
    center=EXPORT_SRC[EXPORT_SRC.index('def _open_map_export_center'):]
    assert "capabilities['png_current']=self._view_key()!='global'" in center
    assert "preferred_png='png_global' if self._view_key()=='global' else 'png_current'" in center
    assert "hints.append(text['current_unavailable'])" in center


def test_export_windows_fill_their_client_area_and_keep_bottom_safety_margin():
    place=EXPORT_SRC[EXPORT_SRC.index('def _place_export_center'):EXPORT_SRC.index('def _open_stats_export_center')]
    assert 'window.winfo_reqheight()+16' in place
    assert EXPORT_SRC.count("w.rowconfigure(0,weight=1)")>=2
    assert EXPORT_SRC.count("w.configure(background=self._ui_theme_colors.get('panel'")>=2


def test_checkbutton_hover_is_explicitly_themed_in_dark_and_light_modes():
    theme=Path('s3mapgen/application/settings/controller.py').read_text(encoding='utf-8')
    assert "s.configure('TCheckbutton',background=bg,foreground=fg)" in theme
    assert "s.map('TCheckbutton',background=[('disabled',bg),('active',bg),('pressed',bg)]" in theme


def test_unavailable_export_formats_are_muted_and_struck_through():
    theme=Path('s3mapgen/application/settings/controller.py').read_text(encoding='utf-8')
    assert "from tkinter import font as tkfont" in theme
    assert "self._unavailable_font.configure(overstrike=True)" in theme
    assert "s.configure('Unavailable.TCheckbutton'" in theme
    center=EXPORT_SRC[EXPORT_SRC.index('def _open_map_export_center'):]
    assert "style='Unavailable.TCheckbutton'" in center


def test_export_centers_disable_the_windows_parent_for_true_modality():
    modal=EXPORT_SRC[EXPORT_SRC.index('def _close_export_center'):EXPORT_SRC.index('def _place_export_center')]
    assert "self.attributes('-disabled',False)" in modal
    activate=EXPORT_SRC[EXPORT_SRC.index('def _activate_export_modal'):EXPORT_SRC.index('def _place_export_center')]
    assert "self.attributes('-disabled',True)" in activate
    assert activate.index('window.grab_set()') < activate.index("self.attributes('-disabled',True)")
    assert 'window.focus_force()' in activate
    assert EXPORT_SRC.count('self._activate_export_modal(w)')==2


def test_imported_sav_source_identity_is_persisted_for_later_ab_export():
    source=Path('s3mapgen/application/imports/controller.py').read_text(encoding='utf-8')
    imported=source[source.index('def import_file'):]
    assert "'source_format':'SAV'" in imported
    assert "'source_path':str(p)" in imported
    current=EXPORT_SRC[EXPORT_SRC.index('def _current_source_path'):EXPORT_SRC.index('def _choose_export_folder')]
    assert "metadata.get('source_path')" in current
