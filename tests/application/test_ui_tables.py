from s3mapgen.application.ui.i18n.shell import FEEDBACK_TEXT, WINDOW_TITLES
from s3mapgen.application.ui.i18n.viewer import HEATMAP_LABELS, VIEW_LABELS
from s3mapgen.application.ui.viewer import OBJECT_NAMES
from s3mapgen.version import APP_VERSION, ENGINE_VERSION


def test_view_and_heatmap_labels_are_localized_and_decorated():
    assert VIEW_LABELS['fr']['resources'].endswith('Ressources')
    assert VIEW_LABELS['en']['resources'].endswith('Resources')
    assert HEATMAP_LABELS['fr']['coal'].endswith('Charbon')
    assert HEATMAP_LABELS['fr']['iron'].endswith('Fer')
    assert HEATMAP_LABELS['fr']['gold'].endswith('Or')
    assert HEATMAP_LABELS['fr']['gems'].endswith('Gemmes')
    assert HEATMAP_LABELS['fr']['sulfur'].endswith('Soufre')
    assert HEATMAP_LABELS['fr']['trees'] == 'Arbres'


def test_inspector_object_table_contains_known_ids():
    assert OBJECT_NAMES[68]=='Birch 1'
    assert OBJECT_NAMES[84]=='Small Tree'
    assert OBJECT_NAMES[85]=='Wheat 1'
    assert OBJECT_NAMES[94]=='Vine 1'
    assert OBJECT_NAMES[103]=='Rice 1'
    assert OBJECT_NAMES[111]=='Reef 1'
    assert OBJECT_NAMES[127]=='Building Stone 13'


def test_window_title_is_fully_localized_and_versioned():
    prefix = f'Settlers III MapGen v{APP_VERSION}'
    suffix = f'v{ENGINE_VERSION}'
    assert WINDOW_TITLES['fr'] == f'{prefix} — moteur de génération {suffix}'
    assert WINDOW_TITLES['en'] == f'{prefix} — generation engine {suffix}'
    assert WINDOW_TITLES['de'] == f'{prefix} — Generierungs-Engine {suffix}'
    assert WINDOW_TITLES['es'] == f'{prefix} — motor de generación {suffix}'


def test_feedback_text_has_human_status_and_locked_control_hint_in_both_languages():
    for lang in ('fr','en','de','es'):
        assert '{seed}' in FEEDBACK_TEXT[lang]['generating']
        assert '{seed}' in FEEDBACK_TEXT[lang]['generated']
        assert any(term in FEEDBACK_TEXT[lang]['heatmap_locked'].lower() for term in ('heatmap','thermique','calor'))


def test_ab_clear_helpers_clear_slots_and_active_state():
    from s3mapgen.application.main_window import MainWindow
    class Status:
        def __init__(self): self.value=''
        def set(self,value): self.value=value
    class Dummy:
        pass
    d=Dummy();d._compare_slots={'A':object(),'B':object()};d._compare_active='A';d.prefs={'language':'fr'};d.status=Status();d.refreshed=0
    d._refresh_compare_label=lambda: setattr(d,'refreshed',d.refreshed+1)
    MainWindow._clear_compare_slot(d,'A')
    assert d._compare_slots['A'] is None and d._compare_slots['B'] is not None
    assert d._compare_active is None and d.refreshed==1
    MainWindow._clear_compare_slots(d)
    assert d._compare_slots=={'A':None,'B':None}
    assert d.refreshed==2
