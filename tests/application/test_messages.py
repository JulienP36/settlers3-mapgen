"""Reports preserve useful diagnostics; real Tk proves grouping and copying."""
import os
import tkinter as tk
import struct

import pytest

from s3mapgen.application.ui.messages import TEXT, make_report, show_message
from s3mapgen.version import APP_VERSION


def test_report_preserves_original_error_context_and_chained_traceback():
    try:
        try:
            raise OSError('Cause originale échec\n' + 'x' * 2000)
        except OSError as cause:
            raise RuntimeError('Positions compatibles avec terrain, objets et relief insuffisantes : 1/4') from cause
    except RuntimeError as error:
        report = make_report('generation', exception=error, context={'Seed': 123, 'Players': 4})
    copied = report.copy_text()
    assert APP_VERSION in copied and 'Seed: 123' in copied and 'Players: 4' in copied
    assert TEXT['fr']['starts'] in copied
    assert 'x' * 2000 in copied and 'RuntimeError' in copied and 'OSError' in copied
    assert 'Cause originale échec\n' in copied


def test_permission_guidance_and_language_fallback():
    for language in TEXT:
        report = make_report('import', exception=PermissionError('private.edm'), language=language)
        assert report.action == TEXT[language]['permission']
        assert report.message == TEXT[language]['import']
        invalid = make_report('import', exception=struct.error('buffer too short'), language=language)
        assert invalid.message == TEXT[language]['invalid_file']
        assert invalid.action == TEXT[language]['file_action']
    assert make_report('ui', language='unknown').language == 'en'


def test_real_message_window_copy_grouping_theme_and_modal_restoration(tmp_path, monkeypatch):
    if os.name != 'nt' and not os.environ.get('DISPLAY'):
        pytest.skip('A real Tk display is required (Windows or Xvfb).')
    monkeypatch.setenv('APPDATA', str(tmp_path))
    from s3mapgen.application.runtime import App
    app = App()
    try:
        app.update()
        modal = tk.Toplevel(app)
        modal.update()
        modal.grab_set()
        error = PermissionError('Données\nfichier.edm\n' + 'long error\n' * 200)
        window = show_message(modal, 'import', exception=error, context={'File': 'fichier.edm'})
        app.update()
        assert app.grab_current() is None
        assert not window.expanded
        window.copy_button.invoke()
        copied = app.clipboard_get()
        assert 'long error\n' * 200 in copied and APP_VERSION in copied
        assert 'File: fichier.edm' in copied
        same = show_message(app, 'import', exception=error, context={'File': 'fichier.edm'})
        assert same is window and len(window.reports) == 1 and window.counts == [2]
        show_message(app, 'preview', exception=ValueError('preview error'))
        app.update()
        assert len(window.reports) == 2 and window.selector.winfo_ismapped()
        window.copy_all_button.invoke()
        assert 'preview error' in app.clipboard_get() and 'fichier.edm' in app.clipboard_get()
        for language in TEXT:
            app.prefs['language'] = language
            show_message(app, 'ui', exception=RuntimeError('UI error'))
            assert window.copy_button.cget('text') == TEXT[language]['copy']
            for theme in ('dark', 'light'):
                app.prefs['theme'] = theme
                app._apply_theme()
                window.toggle_button.invoke()
                app.update()
                assert window.detail_text.cget('background') == app._ui_theme_colors['field']
                button = window.copy_button
                hit = app.winfo_containing(button.winfo_rootx()+button.winfo_width()//2,
                                           button.winfo_rooty()+button.winfo_height()//2)
                assert hit is button
        window.copy_all_button.invoke()
        copied = app.clipboard_get()
        window.close_button.invoke()
        app.update()
        assert app._message_window is None and app.grab_current() is modal
        assert app.clipboard_get() == copied
        modal.destroy()
    finally:
        app.destroy()
