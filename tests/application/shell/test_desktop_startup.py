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
    # Windows runners may have a smaller work area than the requested layouts.
    # Place the window explicitly and constrain test sizes to the actual desktop;
    # an off-screen widget is not evidence of another widget covering it.
    left = top = 0
    desktop_width, desktop_height = app.winfo_screenwidth(), app.winfo_screenheight()
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        area = wintypes.RECT()
        if not ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(area), 0):
            raise ctypes.WinError()
        left, top = area.left, area.top
        desktop_width, desktop_height = area.right - area.left, area.bottom - area.top
    available_width = max(1, desktop_width - 48)
    available_height = max(1, desktop_height - 80)
    minimum_width, minimum_height = app.minsize()
    assert available_width >= minimum_width and available_height >= minimum_height, (
        f'Desktop work area {desktop_width}x{desktop_height} cannot fit the normal '
        f'application minimum {minimum_width}x{minimum_height}; prepare the CI desktop first.'
    )
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
            region = tuple(float(v) for v in canvas.cget('scrollregion').split())
            x = widget.winfo_rootx() + widget.winfo_width() // 2 - canvas.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() // 2 - canvas.winfo_rooty()
            # Centre the hit-test point in the viewport on either axis. Wide
            # headers can require horizontal scrolling as well as vertical.
            if x < 0 or x >= canvas.winfo_width():
                target = canvas.canvasx(x) - canvas.winfo_width() / 2 - region[0]
                canvas.xview_moveto(max(0, target) / max(1, region[2] - region[0]))
            if y < 0 or y >= canvas.winfo_height():
                target = canvas.canvasy(y) - canvas.winfo_height() / 2 - region[1]
                canvas.yview_moveto(max(0, target) / max(1, region[3] - region[1]))
            settle()
        hit = app.winfo_containing(widget.winfo_rootx() + widget.winfo_width() // 2,
                                   widget.winfo_rooty() + widget.winfo_height() // 2)
        assert hit is widget, (
            f'{widget} is covered by {hit}; widget='
            f'{widget.winfo_rootx()},{widget.winfo_rooty()},'
            f'{widget.winfo_width()}x{widget.winfo_height()}; '
            f'window={app.geometry()}; desktop={desktop_width}x{desktop_height}; '
            f'canvas={canvas.winfo_geometry() if canvas else None}; '
            f'view={canvas.yview() if canvas else None}'
        )

    try:
        for language in ('fr', 'en', 'de', 'es'):
            app.prefs['language'] = language
            app._apply_language()
            app.nb.select(app._custom_generator_tab._scroll_host)
            for theme in ('dark', 'light'):
                app.prefs['theme'] = theme
                app._apply_theme()
                for geometry in ('1080x720', '1380x860', '1800x1000'):
                    width, height = (int(value) for value in geometry.split('x'))
                    app.geometry(f'{min(width, available_width)}x{min(height, available_height)}+{left}+{top}')
                    app.lift()
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
