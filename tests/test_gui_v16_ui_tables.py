from s3mapgen.gui_v16 import VIEW_LABELS, HEATMAP_LABELS, OBJECT_NAMES, WINDOW_TITLES, FEEDBACK_TEXT


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


def test_window_title_is_fully_localized_for_v18_dev6():
    assert WINDOW_TITLES['fr'] == 'Settlers III MapGen v1.8 DEV_9_R2 — moteur de génération v1.5'
    assert WINDOW_TITLES['en'] == 'Settlers III MapGen v1.8 DEV_9_R2 — generation engine v1.5'
    assert WINDOW_TITLES['de'] == 'Settlers III MapGen v1.8 DEV_9_R2 — Generierungs-Engine v1.5'
    assert WINDOW_TITLES['es'] == 'Settlers III MapGen v1.8 DEV_9_R2 — motor de generación v1.5'


def test_feedback_text_has_human_status_and_locked_control_hint_in_both_languages():
    for lang in ('fr','en','de','es'):
        assert '{seed}' in FEEDBACK_TEXT[lang]['generating']
        assert '{seed}' in FEEDBACK_TEXT[lang]['generated']
        assert any(term in FEEDBACK_TEXT[lang]['heatmap_locked'].lower() for term in ('heatmap','thermique','calor'))


def test_ab_clear_helpers_clear_slots_and_active_state():
    from s3mapgen.gui_v16 import App
    class Status:
        def __init__(self): self.value=''
        def set(self,value): self.value=value
    class Dummy:
        pass
    d=Dummy();d._compare_slots={'A':object(),'B':object()};d._compare_active='A';d.prefs={'language':'fr'};d.status=Status();d.refreshed=0
    d._refresh_compare_label=lambda: setattr(d,'refreshed',d.refreshed+1)
    App._clear_compare_slot(d,'A')
    assert d._compare_slots['A'] is None and d._compare_slots['B'] is not None
    assert d._compare_active is None and d.refreshed==1
    App._clear_compare_slots(d)
    assert d._compare_slots=={'A':None,'B':None}
    assert d.refreshed==2
