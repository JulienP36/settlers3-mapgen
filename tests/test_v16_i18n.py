from s3mapgen.gui_v16 import (
    VIEW_LABELS, HEATMAP_LABELS, MODE_LABELS, ARCHETYPE_LABELS,
    VIEW_ICON_COLORS, HEATMAP_ICON_COLORS,
)


def test_french_view_terms_are_localized():
    assert VIEW_LABELS['fr']['heightmap']=='Élévation'
    assert VIEW_LABELS['fr']['heatmap']=='Carte thermique'
    assert ARCHETYPE_LABELS['fr']['large_islands']=='Grandes îles'
    assert ARCHETYPE_LABELS['fr']['small_islands']=='Petites îles'


def test_french_mode_terms_are_localized():
    assert 'Héritage' in MODE_LABELS['fr']['legacy']
    assert 'Amélioré' in MODE_LABELS['fr']['upgraded']


def test_view_and_heatmap_choices_use_real_raster_color_specs():
    # R5 intentionally contains no emoji color markers: Windows/Tk may render
    # them monochrome. Every selectable entry instead has an explicit RGB hex
    # color used to draw a PhotoImage icon.
    for lang in ('fr','en'):
        assert set(VIEW_LABELS[lang]) == set(VIEW_ICON_COLORS)
        assert set(HEATMAP_LABELS[lang]) == set(HEATMAP_ICON_COLORS)
    assert len(set(VIEW_ICON_COLORS.values())) == len(VIEW_ICON_COLORS)
    assert HEATMAP_ICON_COLORS['coal']=='#101010'
    assert HEATMAP_ICON_COLORS['iron']=='#ff9400'
    assert HEATMAP_ICON_COLORS['gold']=='#ffff00'
    assert HEATMAP_ICON_COLORS['gems']=='#ce0000'
