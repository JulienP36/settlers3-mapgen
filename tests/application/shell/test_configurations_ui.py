"""Exercise presets against the real application and deferred Tk traces."""
from copy import deepcopy
import os
import time
import tkinter as tk
from tkinter import ttk
import traceback

import pytest


def test_batch_context_choices_restore_custom_without_changing_main_editor(tmp_path, monkeypatch):
    if os.name != 'nt' and not os.environ.get('DISPLAY'):
        pytest.skip('A real Tk display is required (Windows or Xvfb).')
    monkeypatch.setenv('APPDATA',str(tmp_path))
    from s3mapgen.application.runtime import App
    from s3mapgen.application.ui.i18n.shell import MODE_LABELS
    from s3mapgen.generation.custom import build_custom_config
    def edited_config():
        config=build_custom_config('upgraded','team_islands')
        profile=deepcopy(config.archetype_profile)
        profile['relief']['mountain_threshold']=133
        return config.with_archetype_profile(profile)

    app=App();errors=[]
    app.report_callback_exception=lambda *args: errors.append(''.join(traceback.format_exception(*args)))
    def settle():
        for _ in range(5):app.update();time.sleep(.02)
        assert not errors, '\n'.join(errors)
    try:
        for generator_custom,archetype_custom in ((False,False),(True,False),(False,True),(True,True)):
            config=edited_config() if archetype_custom else build_custom_config('upgraded','team_islands')
            mode='custom' if generator_custom else 'upgraded'
            snapshot=dict(mode=mode,archetype='team_islands',size=512,players=4,
                          mirror=0,starts='auto',nations=[255]*20,teams=[1,1,2,2]+[0]*16,
                          random_team_count=4,custom=config.to_dict())
            app._configuration_apply(snapshot);settle()
            main_before=app._configuration_capture()
            app._open_batch_window();settle()
            context=app._batch_context
            assert ('custom' in context.modes)==generator_custom
            assert ('edited' in context.archetypes)==archetype_custom
            first=app._batch_rows[0]
            assert app._batch_arch_choice(first['arch_var'].get())==context.archetype_choice
            expected=app._batch_collect_requests()[0]['config'].to_dict()
            first['mode_var'].set(MODE_LABELS['fr']['legacy'])
            first['arch_var'].set(app._batch_arch_label('classic','fr'))
            app._batch_collect_requests()
            first['mode_var'].set(MODE_LABELS['fr'][mode])
            first['arch_var'].set(app._batch_arch_label(context.archetype_choice,'fr'))
            assert app._batch_collect_requests()[0]['config'].to_dict()==expected
            app.prefs['language']='de';app._retranslate_batch_window();settle()
            assert app._batch_collect_requests()[0]['config'].to_dict()==expected
            assert app._configuration_capture()==main_before
            assert app._batch_base_label.winfo_ismapped()
            assert app._batch_start_button.winfo_rooty()+app._batch_start_button.winfo_height() <= app._batch_window.winfo_rooty()+app._batch_window.winfo_height()
            app._close_batch_window();app.prefs['language']='fr'
    finally:app.destroy()


def test_complete_configuration_ui_roundtrip_and_collection_actions(tmp_path, monkeypatch):
    if os.name != 'nt' and not os.environ.get('DISPLAY'):
        pytest.skip('A real Tk display is required (Windows or Xvfb).')
    monkeypatch.setenv('APPDATA', str(tmp_path))
    from s3mapgen.application.runtime import App
    from s3mapgen.application.configurations import controller, model
    from s3mapgen.application.ui.i18n.shell import MODE_LABELS
    from s3mapgen.generation.custom import build_custom_config
    import s3mapgen.application.custom.controller as custom

    config = build_custom_config('upgraded', 'team_islands')
    profile = deepcopy(config.archetype_profile)
    profile['morphology']['mask_layer_count'] = 1
    profile['morphology']['mask_layers'][0].update(
        enabled=True, type='manual', provider_settings={'grid_side': 64, 'grid': [n % 256 for n in range(4096)]})
    config = config.with_archetype_profile(profile)
    target = dict(mode='custom', archetype='team_islands', size=768, players=6,
                  mirror=2, starts='teams', nations=[0, 1, 2, 3, 255]*4,
                  teams=[-1, 0, 1, 2, 20]*4, random_team_count=4, custom=config.to_dict())
    item = model.preset('Équipes à jouer', target)
    model.write_collection(model.collection_path(), [item])
    app = App()
    errors = []
    app.report_callback_exception = lambda *args: errors.append(''.join(traceback.format_exception(*args)))
    def forbidden(*args, **kwargs):
        pytest.fail('Preset loading must not generate maps or resolve hidden island contours')
    monkeypatch.setattr(app, 'generate', forbidden)
    monkeypatch.setattr(custom, 'resolve_island_profile', forbidden)
    def settle(duration=.15):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            app.update()
            time.sleep(.005)
        assert not errors, '\n'.join(errors)
    try:
        app.nb.select(app._configuration_tab)
        # Built-in generator choices retain their identity, including modern
        # Continental's custom geography over a built-in content generator.
        for mode in ('legacy', 'upgraded', 'custom'):
            for source, profile in app._custom_archetype_profile_presets().items():
                arch = source if source in ('large_islands', 'team_islands') else 'continental'
                value = dict(target, mode=mode, archetype=arch,
                             custom=build_custom_config('upgraded' if mode == 'custom' else mode, arch).with_archetype_profile(profile).to_dict())
                app._configuration_apply(value)
                settle()
                assert app._configuration_capture() == value
                assert app.nb.select() == str(app._configuration_tab)
        app._configuration_tree.selection_set(item['id'])
        app.seed.set('999')
        current = app.current
        for language in ('fr', 'en', 'de', 'es'):
            app.prefs['language'] = language
            app._apply_language()
            app._configuration_load()
            settle()
            assert app._configuration_capture() == target
            assert app.seed.get() == '999'
            assert app.nb.select() == str(app._configuration_tab)
            assert app.current is current
            assert app._configuration_buttons['load'].cget('text') == controller.TEXT[language]['load']
        app.prefs['language'] = 'fr'
        app._apply_language()
        settle(.6)
        assert not app._configuration_modified
        app.seed.set('1000')
        settle(.6)
        assert not app._configuration_modified  # Seed intentionally excluded.
        app.mirror.set(controller.MIRROR_LABELS['fr'][0])
        settle(.6)
        assert app._configuration_modified
        assert model.read_collection(model.collection_path())[0]['configuration'] == target
        app._configuration_load()
        settle(.6)
        assert not app._configuration_modified

        # Save through the actual themed dialog: seed is unchecked by default.
        app._configuration_save()
        dialog = next(widget for widget in app.winfo_children() if isinstance(widget, tk.Toplevel))
        entry = next(widget for widget in dialog.winfo_children() if isinstance(widget, ttk.Entry))
        check = next(widget for widget in dialog.winfo_children() if isinstance(widget, ttk.Checkbutton))
        assert not check.instate(['selected'])
        entry.insert(0, 'Deuxième')
        next(widget for widget in dialog.winfo_children() if isinstance(widget, ttk.Button) and widget.cget('text') == controller.TEXT['fr']['accept']).invoke()
        settle()
        assert len(model.read_collection(model.collection_path())) == 2

        # Replace has an explicit seed choice and retains its identity.
        saved_id = app._configuration_selected()['id']
        app._configuration_replace()
        dialog = next(widget for widget in app.winfo_children() if isinstance(widget, tk.Toplevel))
        check = next(widget for widget in dialog.winfo_children() if isinstance(widget, ttk.Checkbutton))
        check.invoke()
        next(widget for widget in dialog.winfo_children() if isinstance(widget, ttk.Button) and widget.cget('text') == controller.TEXT['fr']['accept']).invoke()
        settle()
        saved = app._configuration_selected()
        assert saved['id'] == saved_id and saved['configuration']['seed'] == 1000
        app.seed.set('123')
        settle(.6)
        assert app._configuration_modified
        app._configuration_load()
        settle(.6)
        assert app.seed.get() == '1000' and not app._configuration_modified

        monkeypatch.setattr(controller, 'themed_prompt', lambda *args, **kwargs: 'Renommée')
        app._configuration_rename()
        assert app._configuration_selected()['name'] == 'Renommée'
        export = tmp_path / 'all-presets.json'
        monkeypatch.setattr(controller.filedialog, 'asksaveasfilename', lambda **kwargs: str(export))
        app._configuration_export()
        assert model.read_collection(export) == app._configuration_entries
        monkeypatch.setattr(controller.filedialog, 'askopenfilename', lambda **kwargs: str(export))
        app._configuration_import()
        assert len(app._configuration_entries) == 4
        assert 'Renommée (2)' in [value['name'] for value in app._configuration_entries]
        before = model.collection_path().read_bytes()
        export.write_text('{', encoding='utf-8')
        reported = []
        monkeypatch.setattr(app, '_configuration_error', reported.append)
        app._configuration_import()
        assert reported and model.collection_path().read_bytes() == before
        monkeypatch.setattr(controller, 'themed_prompt', lambda *args, **kwargs: True)
        app._configuration_delete()
        assert len(model.read_collection(model.collection_path())) == 3
        assert app.current is current
        # A corrupt local collection cannot be silently replaced by Save/Import.
        app._configuration_load_error = ValueError('Unreadable')
        with pytest.raises(ValueError):
            app._configuration_commit([])
        assert len(model.read_collection(model.collection_path())) == 3
        assert not errors
    finally:
        app.destroy()
