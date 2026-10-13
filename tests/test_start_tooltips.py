from types import SimpleNamespace

from s3mapgen.application.workflows.generation import GenerationWorkflowController
from s3mapgen.application.ui.i18n.starts import START_TOOLTIPS
from s3mapgen.application.ui.i18n.starts import START_LABELS, START_LABEL_ALIASES
from s3mapgen.application.batch.controller import BatchController


class Menu:
    active = None
    def index(self, name):
        assert name == 'active'
        return self.active
    def winfo_rootx(self): return 100
    def winfo_rooty(self): return 100
    def winfo_width(self): return 200
    def yposition(self, index): return index * 20


class Host(GenerationWorkflowController):
    def __init__(self):
        self.prefs = {'language': 'fr'}
        self.start_menu = Menu()
        self.start_algorithm = SimpleNamespace(get=lambda: 'balanced')
        self.visible = None
    def _show_ui_tooltip(self, widget, text, **kwargs):
        self.visible = (text, kwargs)
    def _hide_ui_tooltip(self): self.visible = None


def test_menu_help_follows_hovered_choice_not_selected_algorithm():
    host = Host()
    for index, key in ((0,'auto'),(1,'balanced'),(2,'fair'),(3,'islands'),
                       (5,'classic'),(6,'nations')):
        host.start_menu.active = index
        host._start_menu_tooltip()
        assert host.visible[0] == START_TOOLTIPS['fr'][key]
        assert host._start_algorithm_key() == 'balanced'
    for index in (None, 4):
        host.start_menu.active = index
        host._start_menu_tooltip()
        assert host.visible is None


def test_language_is_resolved_when_help_is_shown():
    host = Host()
    for language in ('fr','en','de','es'):
        host.prefs['language'] = language
        host.start_menu.active = 2
        host._start_menu_tooltip()
        assert host.visible[0] == START_TOOLTIPS[language]['fair']
        assert host._start_tooltip_text() == START_TOOLTIPS[language]['balanced']


def test_old_batch_island_captions_keep_the_explicit_algorithm():
    for old in START_LABEL_ALIASES:
        assert BatchController._batch_label_key(old, START_LABELS, 'auto') == 'islands'
    for language in START_LABELS.values():
        assert BatchController._batch_label_key(language['islands'], START_LABELS, 'auto') == 'islands'
