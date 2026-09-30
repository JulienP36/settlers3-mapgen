from s3mapgen.application.ui.i18n.shell import ARCHETYPE_INPUT_LABELS, ARCHETYPE_LABELS, MODE_LABELS
from s3mapgen.application.ui.i18n.viewer import HEATMAP_LABELS, VIEW_LABELS
from s3mapgen.application.ui.viewer.options import HEATMAP_ICON_COLORS, VIEW_ICON_COLORS
from s3mapgen.application.workflows.generation import GenerationWorkflowController
from s3mapgen.application.custom.controller import CustomGeneratorController


def test_french_view_terms_are_localized():
    assert 'starts' not in VIEW_LABELS['fr']
    assert 'starts' not in VIEW_LABELS['en']
    assert VIEW_LABELS['fr']['heightmap']=='Élévation'
    assert VIEW_LABELS['fr']['heatmap']=='Carte thermique'
    assert ARCHETYPE_LABELS['fr']['large_islands']=='Grandes îles'
    assert ARCHETYPE_LABELS['fr']['small_islands']=='Petites îles'


def test_french_mode_terms_are_localized():
    assert MODE_LABELS['fr']['legacy']=='Classique'
    assert 'Amélioré' in MODE_LABELS['fr']['upgraded']
    assert MODE_LABELS['fr']['custom']=='Personnalisé'


def test_main_archetype_selector_names_both_continental_profiles():
    assert ARCHETYPE_INPUT_LABELS['fr']['classic']=='Classique'
    assert ARCHETYPE_INPUT_LABELS['fr']['continental']=='Continental'
    assert ARCHETYPE_INPUT_LABELS['fr']['edited']=='Profil personnalisé'
    assert ARCHETYPE_INPUT_LABELS['fr']['edited_option']=='Personnalisé'
    assert ARCHETYPE_INPUT_LABELS['en']['edited_option']=='Custom'
    assert ARCHETYPE_INPUT_LABELS['de']['edited_option']=='Benutzerdefiniert'
    assert ARCHETYPE_INPUT_LABELS['es']['edited_option']=='Personalizado'
    assert ARCHETYPE_INPUT_LABELS['fr']['large_islands']=='Grandes îles'
    assert ARCHETYPE_INPUT_LABELS['fr']['small_islands']=='Petites îles'


def test_status_uses_the_selected_profile_name_without_changing_geography():
    controller = GenerationWorkflowController.__new__(GenerationWorkflowController)
    controller.prefs = {'language': 'fr'}
    controller._arch_key = lambda: 'continental'
    controller._custom_main_archetype_input_key = lambda: 'edited'

    assert controller._arch_display_label() == 'Profil personnalisé'
    controller._custom_main_archetype_input_key = lambda: 'classic'
    assert controller._arch_display_label() == 'Classique'
    assert controller._arch_key() == 'continental'



def test_main_archetype_selector_adds_custom_state_only_when_profile_is_edited():
    class FakeController:
        def __init__(self):
            self.selected = 'classic'

        def _custom_main_archetype_input_key(self):
            return self.selected

    controller = FakeController()
    named = CustomGeneratorController._custom_main_archetype_input_options(
        controller, 'fr'
    )
    assert 'edited' not in named

    controller.selected = 'edited'
    edited = CustomGeneratorController._custom_main_archetype_input_options(
        controller, 'fr'
    )
    assert edited['edited'] == 'Personnalisé'
    assert list(edited.values()).count('Personnalisé') == 1


def test_main_archetype_selector_refresh_tracks_profile_edit_and_language():
    class Variable:
        value = ''

        def set(self, value):
            self.value = value

    class Combo:
        values = ()

        def configure(self, **kwargs):
            self.values = kwargs['values']

    class FakeController:
        def __init__(self):
            self.selected = 'classic'
            self.arch_input = Variable()
            self.arch_combo = Combo()

        def _custom_main_archetype_input_key(self):
            return self.selected

        def _custom_language(self):
            return 'fr'

        def _custom_main_archetype_input_options(self, language):
            return CustomGeneratorController._custom_main_archetype_input_options(
                self, language
            )

    controller = FakeController()
    refresh = CustomGeneratorController._custom_refresh_main_archetype_input
    refresh(controller)
    assert controller.arch_input.value == 'Classique'
    assert 'Personnalisé' not in controller.arch_combo.values

    controller.selected = 'edited'
    refresh(controller)
    assert controller.arch_input.value == 'Personnalisé'
    assert 'Personnalisé' in controller.arch_combo.values

    controller.selected = 'continental'
    refresh(controller)
    assert controller.arch_input.value == 'Continental'
    assert 'Personnalisé' not in controller.arch_combo.values

def test_view_and_heatmap_choices_use_real_raster_color_specs():
    # Emoji color markers may render monochrome under Windows/Tk. Every
    # selectable entry instead has an explicit RGB hex
    # color used to draw a PhotoImage icon.
    for lang in ('fr','en'):
        assert set(VIEW_LABELS[lang]) == set(VIEW_ICON_COLORS)
        assert set(HEATMAP_LABELS[lang]) == set(HEATMAP_ICON_COLORS)
    assert len(set(VIEW_ICON_COLORS.values())) == len(VIEW_ICON_COLORS)
    assert HEATMAP_ICON_COLORS['coal']=='#101010'
    assert HEATMAP_ICON_COLORS['iron']=='#ff9400'
    assert HEATMAP_ICON_COLORS['gold']=='#ffff00'
    assert HEATMAP_ICON_COLORS['gems']=='#ce0000'
