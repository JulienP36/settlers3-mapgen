import s3mapgen.application.ui.theme.controller as theme


class _ThemeButton:
    def __init__(self):
        self.configuration = {}

    def configure(self, **values):
        self.configuration.update(values)


def test_theme_button_icon_renders_without_a_real_tk_window(monkeypatch):
    monkeypatch.setattr(theme.ImageTk, "PhotoImage", lambda image: image)
    app = type("ThemeButtonHost", (), {})()
    app.prefs = {"theme": "dark", "language": "fr"}
    app._theme_button = _ThemeButton()

    theme.ThemeController._refresh_theme_button_icon(app)

    assert app._theme_button_icon.mode == "RGBA"
    assert app._theme_button_icon.size == (20, 20)
    assert app._theme_button_icon.getbbox() is not None
    assert app._theme_button.configuration["image"] is app._theme_button_icon
