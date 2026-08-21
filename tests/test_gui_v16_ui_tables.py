from s3mapgen.gui_v16 import VIEW_LABELS, HEATMAP_LABELS, OBJECT_NAMES


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
