from pathlib import Path

from s3mapgen.gui_v16 import (
    LANGUAGE_LABELS, WINDOW_TITLES, TEXTS, FEEDBACK_TEXT, BATCH_TEXT,
    EXPORT_TEXT, VIEW_LABELS, HEATMAP_LABELS, MODE_LABELS,
    ARCHETYPE_LABELS, COMMAND_LABELS, THEME_LABELS, PROJECTION_LABELS,
    PREVIEW_START_MARKER_LABELS,
)
from s3mapgen.stats_analysis import analyze_map, format_stats_report
from s3mapgen.stats_charts import CHART_LABELS, CHART_KEYS, render_stats_chart
from test_stats_v17 import sample_state


LANGS={'fr','en','de','es'}


def test_all_runtime_catalogs_have_the_same_four_languages_and_keys():
    catalogs=(FEEDBACK_TEXT,BATCH_TEXT,EXPORT_TEXT,VIEW_LABELS,HEATMAP_LABELS,
              MODE_LABELS,ARCHETYPE_LABELS,COMMAND_LABELS,THEME_LABELS,
              PROJECTION_LABELS,PREVIEW_START_MARKER_LABELS,CHART_LABELS)
    assert set(LANGUAGE_LABELS)==LANGS
    for catalog in catalogs:
        assert set(catalog)==LANGS
        assert all(set(values)==set(catalog['fr']) for values in catalog.values())
    assert all({'en','de','es'} <= set(values) for values in TEXTS.values())


def test_german_and_spanish_reports_and_all_charts_render():
    stats=analyze_map(sample_state())
    assert format_stats_report(stats,'de').startswith('ZUSAMMENFASSUNG')
    assert format_stats_report(stats,'es').startswith('RESUMEN')
    for lang in ('de','es'):
        for key in CHART_KEYS:
            image=render_stats_chart(stats,key,lang=lang,dark=True,width=640,height=420)
            assert image.size==(640,420)


def test_language_selector_contains_four_deterministic_flags_and_reverse_lookup():
    source=Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')
    for flag in ('flag_fr','flag_en','flag_de','flag_es'):
        assert flag in source
    assert "next((key for key,label in LANGUAGE_LABELS.items() if label==selected),'en')" in source


def test_dev6_titles_exist_for_every_supported_language():
    assert set(WINDOW_TITLES)==LANGS
    assert all('DEV_9_R2' in title for title in WINDOW_TITLES.values())
