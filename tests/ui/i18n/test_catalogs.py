from string import Formatter

from s3mapgen.application.ui.i18n.batch import BATCH_TEXT, _BATCH_CAPACITY_TEXT
from s3mapgen.application.ui.i18n.exports import EXPORT_TEXT
from s3mapgen.application.ui.i18n.history import (
    HISTORY_TEXT,
    _CONTEXT_TEXT,
    _HISTORY_CAPACITY_DIALOG_TEXT,
)
from s3mapgen.application.ui.i18n.shell import (
    ARCHETYPE_LABELS,
    COMMAND_LABELS,
    FEEDBACK_TEXT,
    LANGUAGE_LABELS,
    MODE_LABELS,
    PREVIEW_START_MARKER_LABELS,
    PROJECTION_LABELS,
    THEME_LABELS,
    WINDOW_TITLES,
)
from s3mapgen.application.ui.i18n.shortcuts import SHORTCUT_UI_TEXT
from s3mapgen.application.ui.i18n.viewer import HEATMAP_LABELS, VIEW_LABELS
from s3mapgen.application.ui.viewer.options import VIEW_CHOICES
from s3mapgen.application.analysis.charts import CHART_LABELS
from s3mapgen.version import APP_VERSION


LANGUAGES = {"fr", "en", "de", "es"}
CATALOGUES = (
    FEEDBACK_TEXT,
    BATCH_TEXT,
    EXPORT_TEXT,
    VIEW_LABELS,
    HEATMAP_LABELS,
    MODE_LABELS,
    ARCHETYPE_LABELS,
    COMMAND_LABELS,
    THEME_LABELS,
    PROJECTION_LABELS,
    PREVIEW_START_MARKER_LABELS,
    SHORTCUT_UI_TEXT,
    HISTORY_TEXT,
    _CONTEXT_TEXT,
    _BATCH_CAPACITY_TEXT,
    _HISTORY_CAPACITY_DIALOG_TEXT,
    CHART_LABELS,
)


def _fields(value):
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(value)
        if field_name is not None
    }


def test_all_feature_catalogues_keep_language_key_and_placeholder_parity():
    assert set(LANGUAGE_LABELS) == LANGUAGES
    for catalogue in CATALOGUES:
        assert set(catalogue) == LANGUAGES
        reference_keys = set(catalogue["fr"])
        assert all(set(values) == reference_keys for values in catalogue.values())
        for key in reference_keys:
            expected_fields = _fields(catalogue["fr"][key])
            assert all(_fields(catalogue[lang][key]) == expected_fields for lang in LANGUAGES)


def test_view_option_owner_preserves_the_historical_order():
    assert list(VIEW_CHOICES) == [
        'Global', 'Départs', 'Territoires', 'Élévation', 'Ressources',
        'Chemins', 'Cultures', 'Carte thermique',
    ]
    assert list(VIEW_CHOICES.values())[:3] == ["global", "starts", "territories"]


def test_window_titles_cover_every_supported_language():
    assert set(WINDOW_TITLES) == LANGUAGES
    assert all(APP_VERSION in title for title in WINDOW_TITLES.values())
