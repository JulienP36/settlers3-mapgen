from s3mapgen.application.ui.theme import THEME_PALETTES


def test_built_in_palettes_have_identical_semantic_roles():
    assert set(THEME_PALETTES) == {"dark", "light"}
    assert set(THEME_PALETTES["dark"]) == set(THEME_PALETTES["light"])
    for role in (
        "window", "panel", "surface", "field", "text", "muted",
        "disabled", "border", "hover", "pressed", "selection", "primary",
        "success", "warning", "danger", "info",
    ):
        assert role in THEME_PALETTES["dark"]
