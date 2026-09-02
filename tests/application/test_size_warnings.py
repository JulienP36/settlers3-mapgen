from __future__ import annotations

from s3mapgen.application.ui.i18n.batch import BATCH_TEXT
from s3mapgen.application.ui.i18n.shell import FEEDBACK_TEXT
from s3mapgen.application.workflows.generation import GenerationWorkflowController


def test_all_supported_languages_expose_both_size_warning_messages():
    for language in ("fr", "en", "de", "es"):
        assert "size_viability_warning" in FEEDBACK_TEXT[language]
        assert "size_extended_warning" in FEEDBACK_TEXT[language]
        assert "small_size_warning" in BATCH_TEXT[language]
        assert "extended_size_warning" in BATCH_TEXT[language]


def test_extended_warning_mentions_editor_support_and_native_limit():
    for language in ("fr", "en", "de", "es"):
        assert "768" in FEEDBACK_TEXT[language]["size_extended_warning"]
        assert "768" in BATCH_TEXT[language]["extended_size_warning"]
        assert "{side}" in FEEDBACK_TEXT[language]["size_extended_warning"]
        assert "{max_players}" in BATCH_TEXT[language]["extended_size_warning"]


def test_warning_feedback_is_limited_to_legacy_continental():
    warning_key = GenerationWorkflowController._legacy_size_warning_key
    assert warning_key("legacy", "continental", 256) == "size_viability_warning"
    assert warning_key("legacy", "continental", 832) == "size_extended_warning"
    assert warning_key("legacy", "continental", 768) is None
    assert warning_key("upgraded", "continental", 832) is None
    assert warning_key("legacy", "large_islands", 832) is None
