"""The language selector must rewrite the already displayed read-only report."""
from types import SimpleNamespace

from s3mapgen.application.analysis.controller import AnalysisController
from s3mapgen.application.analysis.core import analyze_map, format_stats_report
from s3mapgen.application.session.cache import SessionStatsCache
from s3mapgen.application.ui.i18n.controller import LanguageController
from s3mapgen.application.ui.i18n.shell import LANGUAGE_LABELS
from s3mapgen.application.ui.i18n.viewer import HEATMAP_LABELS
from test_stats import sample_state
import s3mapgen.application.analysis.controller as analysis_module


class Field:
    def __init__(self):
        self.value = ''

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def configure(self, **kwargs):
        pass

    def set_items(self, items):
        pass

    def _sync_icon(self):
        pass


class Report:
    """Match Text's silent rejection of insert/delete while disabled."""
    def __init__(self, text):
        self.text = text
        self.state = 'disabled'
        self.position = .35

    def cget(self, name):
        assert name == 'state'
        return self.state

    def configure(self, **options):
        self.state = options.get('state', self.state)

    def delete(self, *args):
        if self.state == 'normal':
            self.text = ''
            self.position = 0

    def insert(self, index, text):
        if self.state == 'normal':
            self.text += text

    def yview(self):
        return self.position, self.position + .1

    def yview_moveto(self, position):
        self.position = position


class LanguageProbe(LanguageController, AnalysisController):
    def __init__(self, state, stats):
        self.prefs = {'language':'fr', 'theme':'dark', 'projection':'square'}
        self.current = SimpleNamespace(state=state)
        self.session_stats_cache = SessionStatsCache()
        self.session_stats_cache.put(state, stats)
        self.stats = Report(format_stats_report(stats, 'fr'))
        for key in ('lang_var','view','heatmap_var','mode','arch','theme_var','projection_var'):
            setattr(self, key, Field())
        for key in ('_view_combo','heatmap_combo','mode_combo','arch_combo','lang_combo'):
            setattr(self, key, Field())
        self.arch_input = Field()
        self._theme_combo = self._projection_combo = None
        for key in (
            '_refresh_stats_chart_labels','_refresh_stats_chart','_refresh_compare_buttons',
            '_refresh_shortcut_validation','_retranslate_history_center',
            '_retranslate_history_capacity_dialog','_retranslate_help_window',
            '_update_view_controls','_clear_inspector','_retranslate_feedback',
            '_save_prefs','_retranslate_batch_window','_apply_compact_action_icons',
        ):
            setattr(self, key, lambda: None)
        self._view_key = lambda: 'global'
        self._heatmap_key = lambda: next(iter(HEATMAP_LABELS['fr']))
        self._mode_key = lambda: 'legacy'
        self._arch_key = lambda: 'continental'
        self.title = lambda text: None
        self._refresh_preview = lambda reset_pan: None


def test_language_selector_translates_existing_disabled_report_without_regeneration(monkeypatch):
    state = sample_state()
    stats = analyze_map(state)
    app = LanguageProbe(state, stats)
    report = app.stats
    source_bytes = (state.terrain.tobytes(), state.objects.tobytes(), state.resources.tobytes())
    def unexpected_analysis(_state):
        raise AssertionError('Changing language must reuse the cached statistics')
    monkeypatch.setattr(analysis_module, 'analyze_map', unexpected_analysis)
    for language, heading in (
        ('en','SUMMARY'), ('de','ZUSAMMENFASSUNG'), ('es','RESUMEN'), ('fr','RÉSUMÉ'),
    ):
        app.lang_var.set(LANGUAGE_LABELS[language])
        app._language_changed()
        assert report.text.startswith(heading)
        assert report.text == format_stats_report(stats, language)
        assert report.state == 'disabled' and report.position == .35
        assert app.stats is report and app.current.state is state
        assert app.session_stats_cache.get(state) is stats
    assert source_bytes == (state.terrain.tobytes(), state.objects.tobytes(), state.resources.tobytes())
