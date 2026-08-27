from pathlib import Path

from s3mapgen.application.ui.i18n.shell import (
    TEXTS,
)
from s3mapgen.application.analysis.core import analyze_map, format_stats_report
from s3mapgen.application.analysis.charts import CHART_KEYS, render_stats_chart
from test_stats import sample_state


def test_legacy_shell_text_entries_keep_all_fallback_languages():
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
    source='\n'.join(
        Path(path).read_text(encoding='utf-8')
        for path in (
            's3mapgen/application/main_window.py',
            's3mapgen/application/ui/i18n/controller.py',
        )
    )
    for flag in ('flag_fr','flag_en','flag_de','flag_es'):
        assert flag in source
    assert "next((key for key,label in LANGUAGE_LABELS.items() if label==selected),'en')" in source
