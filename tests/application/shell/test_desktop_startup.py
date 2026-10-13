"""Exercise real Tk stacking; importing modules cannot detect covered controls."""
import os
import time
import tkinter as tk
import traceback

import pytest


def test_desktop_generator_controls_and_departure_menu_are_reachable(tmp_path, monkeypatch):
    if os.name != 'nt' and not os.environ.get('DISPLAY'):
        pytest.skip('A real Tk display is required (Windows or Xvfb).')
    monkeypatch.setenv('APPDATA', str(tmp_path))
    from s3mapgen.application.runtime import App
    from s3mapgen.application.ui.i18n.starts import START_LABELS

    app = App()
    errors = []
    app.report_callback_exception = lambda *args: errors.append(
        ''.join(traceback.format_exception(*args)))

    def settle():
        deadline = time.monotonic() + .15
        while time.monotonic() < deadline:
            app.update()
            time.sleep(.005)
        assert not errors, '\n'.join(errors)

    def assert_exposed(widget, canvas=None):
        assert widget.winfo_ismapped()
        if canvas is not None:
            y = widget.winfo_rooty() - canvas.winfo_rooty()
            if y < 0 or y + widget.winfo_height() > canvas.winfo_height():
                region = tuple(float(v) for v in canvas.cget('scrollregion').split())
                canvas.yview_moveto(max(0, canvas.canvasy(y) - 8) / max(1, region[3]))
                settle()
        hit = app.winfo_containing(widget.winfo_rootx() + widget.winfo_width() // 2,
                                   widget.winfo_rooty() + widget.winfo_height() // 2)
        assert hit is widget, f'{widget} is covered by {hit}; {widget.winfo_rootx()},{widget.winfo_rooty()}'

    try:
        for language in ('fr', 'en', 'de', 'es'):
            app.prefs['language'] = language
            app._apply_language()
            app.nb.select(app._custom_generator_tab._scroll_host)
            for theme in ('dark', 'light'):
                app.prefs['theme'] = theme
                app._apply_theme()
                for geometry in ('1080x720', '1380x860', '1800x1000'):
                    app.geometry(geometry)
                    settle()
                    assert_exposed(app.start_button)
                    for shell, header, body, refresh in app._custom_section_frames.values():
                        # Collapsed section headers must be clickable, not hidden
                        # behind the independent-row geometry master.
                        assert_exposed(header, app._custom_generator_tab._scroll_canvas)
            for index, key in enumerate(('auto', 'balanced', 'fair', 'islands')):
                app.start_menu.invoke(index)
                assert app._start_algorithm_key() == key
                assert app.start_text.get() == START_LABELS[language][key]
            assert app.start_menu.entrycget(5, 'state') == 'normal'
    finally:
        app.destroy()
