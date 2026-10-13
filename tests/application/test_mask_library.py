"""Real PNG validation, portable resolutions and drawing/history contracts."""
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from s3mapgen.application.custom.mask_library import (
    MaskCatalogue, MaskDrawing, MaskImageError, MASK_SIDES, fit_mask, read_mask_image,
)
from s3mapgen.application.custom.mask_editor import TEXT
from s3mapgen.generation.archetypes import normalize_archetype_profile, generate_mask_component_previews


def test_catalogue_keeps_valid_pngs_when_neighbors_are_invalid(tmp_path):
    gray = np.zeros((128, 128), dtype=np.uint8)
    gray[20:100, 30:75] = 160
    Image.fromarray(gray).save(tmp_path/'good.PNG')
    Image.new('L', (64, 64), 0).save(tmp_path/'black.png')
    Image.new('L', (120, 70), 200).save(tmp_path/'rectangle.png')
    Image.new('L', (64, 64), 255).save(tmp_path/'fake.png', format='JPEG')
    (tmp_path/'broken.png').write_bytes(b'not an image')
    (tmp_path/'ignored.txt').write_text('ignore me')
    catalogue = MaskCatalogue(tmp_path)
    entries = {p.name: catalogue.entry(p) for p in catalogue.paths()}
    assert len(entries) == 5
    assert np.array_equal(entries['good.PNG'].grid, gray)
    assert entries['black.png'].issue == 'uniform' and entries['black.png'].grid is not None
    assert entries['rectangle.png'].issue == 'rectangular' and entries['rectangle.png'].grid is None
    assert entries['fake.png'].issue == 'not_png'
    assert entries['broken.png'].issue == 'unreadable'
    cached = catalogue.entry(tmp_path/'good.PNG')
    assert cached is entries['good.PNG']
    Image.new('L', (64, 64), 255).save(tmp_path/'good.PNG')
    assert catalogue.entry(tmp_path/'good.PNG').grid.min() == 255


def test_decode_flattens_alpha_and_bounds_actual_image_dimensions(tmp_path):
    path = tmp_path/'alpha.png'
    image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
    image.putpixel((32, 32), (255, 255, 255, 128))
    image.save(path)
    gray = np.asarray(read_mask_image(path, png_only=True))
    assert gray[0, 0] == 0 and gray[32, 32] == 128
    Image.new('L', (2049, 2)).save(path)
    with pytest.raises(MaskImageError, match='too_large'):
        read_mask_image(path)
    Image.new('L', (64, 64)).save(path, save_all=True,
             append_images=[Image.new('L', (64, 64), 255)], duration=100)
    with pytest.raises(MaskImageError, match='animated'):
        read_mask_image(path)


def test_rectangular_framing_is_explicit_and_distinct():
    image = Image.new('L', (160, 80), 200)
    pad = fit_mask(image, 128, 'pad')
    crop = fit_mask(image, 128, 'crop')
    assert pad[0].max() == 0 and pad[64].min() == 200
    assert crop.min() == 200
    with pytest.raises(MaskImageError, match='framing'):
        fit_mask(image, 128, 'unknown')


def test_library_save_delete_protects_names_and_keeps_profile_snapshot(tmp_path):
    directory = tmp_path/'masks'
    catalogue = MaskCatalogue(directory)
    grid = np.tile(np.arange(128, dtype=np.uint8), (128, 1))
    path = catalogue.save('My mask', grid)
    loaded = catalogue.entry(path).grid.copy()
    with pytest.raises(FileExistsError):
        catalogue.save('My mask', grid)
    for name in ('../escape', 'CON', 'AUX.txt', 'test/', 'bad?', ''):
        with pytest.raises(MaskImageError, match='name'):
            catalogue.save(name, grid)
    outside = tmp_path/'provided.png'
    Image.fromarray(grid).save(outside)
    with pytest.raises(MaskImageError, match='protected'):
        catalogue.delete(outside)
    catalogue.save('My mask', np.zeros_like(grid), overwrite=True)
    assert np.array_equal(loaded, grid)
    catalogue.delete(path)
    assert not path.exists() and outside.exists()
    assert np.array_equal(loaded, grid)


def test_profile_resolutions_survive_normalization_and_sampling():
    for side in MASK_SIDES:
        grid = np.zeros((side, side), dtype=np.uint8)
        grid[side//4:side*3//4, side//8:side*5//8] = 173
        profile = normalize_archetype_profile({'morphology': {'mask_layer_count': 1,
            'mask_layers': [{'type': 'manual', 'provider_settings': {
                'grid_side': side, 'grid': grid.tolist()}}]}})
        provider = profile['morphology']['mask_layers'][0]['provider_settings']
        assert provider['grid_side'] == side and len(provider['grid']) == side*side
        signal = generate_mask_component_previews(profile, 128, seed=77)[0]
        assert signal.shape == (128, 128) and signal.max() > 0
        portable = normalize_archetype_profile(profile)
        assert portable == profile
    with pytest.raises(ValueError, match='Résolution'):
        normalize_archetype_profile({'morphology': {'mask_layer_count': 1,
            'mask_layers': [{'type':'manual', 'provider_settings':{'grid_side':63,'grid':[0]*3969}}]}})


def test_gray_strokes_have_no_gaps_and_undo_is_one_stroke():
    drawing = MaskDrawing(np.zeros((128, 128), dtype=np.uint8))
    drawing.checkpoint()
    drawing.stroke((4, 64), (120, 64), 4, 170, 0)
    assert np.all(drawing.grid[64, 4:121] == 170)
    assert len(drawing.undo_stack) == 1
    drawing.undo()
    assert drawing.grid.max() == 0
    drawing.redo()
    assert drawing.grid.max() == 170
    drawing.checkpoint()
    drawing.paint(60, 60, 15, 255, 1)
    assert 0 < drawing.grid[60, 50] < drawing.grid[60, 60] == 255
    drawing.replace(255-drawing.grid)
    drawing.undo()
    drawing.redo()
    for _ in range(40):
        drawing.checkpoint()
    assert len(drawing.undo_stack) == 32


def test_new_editor_messages_cover_all_four_languages():
    assert all(len(values) == 4 and all(values) for values in TEXT.values())


def test_editor_applies_a_portable_copy_to_latest_config_only(monkeypatch):
    from copy import deepcopy
    from types import SimpleNamespace
    import s3mapgen.application.custom.mask_editor as editor_module
    from s3mapgen.application.custom.controller import CustomGeneratorController
    from s3mapgen.generation.custom.config import build_custom_config
    profile = {'morphology': {'mask_layer_count': 1,
                              'mask_layers': [{'type': 'manual'}]}}
    config = build_custom_config(archetype_profile=profile)
    captured = {}
    def editor(parent, grid, **options):
        captured.update(options)
        captured['grid'] = grid
    monkeypatch.setattr(editor_module, 'MaskEditor', editor)
    app = SimpleNamespace(_custom_config=config, prefs={'theme': 'dark'},
        _custom_language=lambda: 'fr',
        _custom_archetype_mask_type_options=lambda lang: {'manual':'Dessin libre','ellipse':'Ellipse'})
    def commit(current, layers, count):
        updated = deepcopy(current.archetype_profile)
        updated['morphology']['mask_layers'] = layers
        updated['morphology']['mask_layer_count'] = count
        app._custom_config = current.with_archetype_profile(updated)
    app._custom_commit_archetype_mask_layer_stack = commit
    CustomGeneratorController._custom_archetype_mask_layer_edit(app, 0)
    assert app._custom_config is config and captured['grid'].shape == (64, 64)
    app._custom_config = config.with_archetype_value(('morphology','native_refinement_percent'), 123)
    original = app._custom_config.archetype_profile['morphology']['native_refinement_percent']
    image = np.full((256, 256), 143, dtype=np.uint8)
    captured['apply'](image)
    image.fill(0)
    provider = app._custom_config.archetype_profile['morphology']['mask_layers'][0]['provider_settings']
    assert provider['grid_side'] == 256 and set(provider['grid']) == {143}
    assert app._custom_config.archetype_profile['morphology']['native_refinement_percent'] == original


def test_editor_numeric_sliders_follow_fields_and_picker_with_real_tcl_traces():
    import tkinter as tk
    from types import SimpleNamespace
    from s3mapgen.application.custom.mask_editor import MaskEditor
    root = tk.Tcl()
    color = {}
    app = SimpleNamespace(
        numeric_limits={'gray': (0,255,255), 'size': (1,128,4), 'softness': (0,100,0)},
        numeric_vars={k:tk.StringVar(root, value=str(v)) for k,v in [('gray',255),('size',4),('softness',0)]},
        slider_vars={k:tk.DoubleVar(root, value=v) for k,v in [('gray',255),('size',4),('softness',0)]},
        gray_preview=SimpleNamespace(configure=lambda **options:color.update(options)),
        number=MaskEditor.number,
    )
    tokens=[]
    for key,var in app.numeric_vars.items():
        tokens.append((var,var.trace_add('write',lambda *args,k=key:MaskEditor.sync_numeric(app,k))))
    MaskEditor.slider_changed(app,'gray','128.2')
    assert app.numeric_vars['gray'].get()=='128'
    assert app.slider_vars['gray'].get()==128 and color['background']=='#808080'
    # The picker uses this exact field assignment.
    app.numeric_vars['gray'].set('37')
    assert app.slider_vars['gray'].get()==37 and color['background']=='#252525'
    app.numeric_vars['gray'].set('')
    assert app.slider_vars['gray'].get()==37
    MaskEditor.finish_numeric(app,'gray')
    assert app.numeric_vars['gray'].get()=='255'
    for key,value,expected in [('size','200',128),('softness','-10',0)]:
        MaskEditor.slider_changed(app,key,value)
        assert int(app.numeric_vars[key].get())==expected and app.slider_vars[key].get()==expected
    for var,token in tokens:
        var.trace_remove('write',token)


def test_round_square_brushes_and_new_mask_save_are_independent(tmp_path):
    from types import SimpleNamespace
    from s3mapgen.application.custom.mask_editor import MaskEditor
    circle=MaskDrawing(np.zeros((64,64),dtype=np.uint8))
    square=MaskDrawing(np.zeros((64,64),dtype=np.uint8))
    circle.paint(32,32,4,170,0)
    square.paint(32,32,4,170,0,'square')
    assert circle.grid[29,29]==0 and square.grid[29,29]==170
    assert square.grid[32,32]==170
    square.checkpoint()
    square.paint(32,32,8,255,1,'square')
    assert square.grid[32,32]==255 and 0<square.grid[25,25]<255
    previous=square.grid.copy()
    app=SimpleNamespace(drawing=square,mask_name='old name',status=SimpleNamespace(set=lambda value:None),
                        end_stroke=lambda:None,text=lambda key:key,queue_redraw=lambda:None,may_replace=lambda:True)
    MaskEditor.new_mask(app)
    assert app.mask_name=='' and app.drawing.grid.max()==0
    assert not app.drawing.undo_stack and app.saved_grid is None
    catalogue=MaskCatalogue(tmp_path)
    path=catalogue.save('new drawing',app.drawing.grid)
    assert catalogue.entry(path).grid.max()==0


def test_named_user_mask_remains_portable_when_layer_controls_change(tmp_path):
    from copy import deepcopy
    from types import SimpleNamespace
    import tkinter as tk
    from s3mapgen.application.custom.controller import CustomGeneratorController
    from s3mapgen.generation.custom.config import build_custom_config

    class Host(CustomGeneratorController):
        def _custom_commit_archetype_mask_layer_stack(self, config, layers, count):
            profile = deepcopy(config.archetype_profile)
            profile['morphology']['mask_layers'] = layers
            profile['morphology']['mask_layer_count'] = count
            self._custom_config = config.with_archetype_profile(profile)
            self._custom_sync_archetype_mask_layer_variables()

    host = Host()
    host._custom_config = build_custom_config(archetype_profile={'morphology': {
        'mask_layer_count': 1, 'mask_layers': [{'type': 'manual', 'enabled': True}]}})
    host._custom_language = lambda: 'fr'
    host._custom_current_mode = lambda: 'custom'
    host._custom_current_archetype = lambda: 'custom'
    host._custom_ensure_config = lambda *args: host._custom_config
    root = tk.Tcl()
    layer = host._custom_config.archetype_profile['morphology']['mask_layers'][0]
    host._custom_archetype_mask_layer_vars = {0: {
        'enabled': tk.BooleanVar(root, value=True), 'type': tk.StringVar(root),
        'operation': tk.StringVar(root), 'strength': tk.StringVar(root),
        **{key: tk.StringVar(root, value=str(value)) for key, value in layer['settings'].items()},
    }}
    host._custom_status_var = tk.StringVar(root)
    host._custom_user_mask_catalogue = MaskCatalogue(tmp_path)
    grid = np.zeros((128, 128), dtype=np.uint8)
    grid[30:70, 20:90] = 170
    path = host._custom_user_mask_catalogue.save('Test', grid)
    host._custom_select_user_mask(0, path)
    variables = host._custom_archetype_mask_layer_vars[0]
    assert variables['type'].get() == 'Dessin libre · Test'
    path.unlink()
    variables['strength'].set('73')
    host._custom_archetype_mask_layer_changed(0)
    actual = host._custom_config.archetype_profile['morphology']['mask_layers'][0]
    assert actual['strength_percent'] == 73
    assert actual['provider_settings']['mask_name'] == 'Test'
    assert np.array_equal(np.asarray(actual['provider_settings']['grid']).reshape(128,128), grid)
    assert normalize_archetype_profile(host._custom_config.archetype_profile) == host._custom_config.archetype_profile


def test_editor_coordinate_mapping_follows_centered_square_after_resize():
    from types import SimpleNamespace
    from s3mapgen.application.custom.mask_editor import MaskEditor
    grid = np.zeros((128,128), dtype=np.uint8)
    app = SimpleNamespace(canvas_side=400, drawing=MaskDrawing(grid),
                          view_origin=lambda: (100,50))
    assert MaskEditor.point(app, SimpleNamespace(x=100,y=50)) == (0,0)
    assert MaskEditor.point(app, SimpleNamespace(x=499,y=449)) == (127,127)
    assert MaskEditor.point(app, SimpleNamespace(x=99,y=80)) is None
    assert MaskEditor.point(app, SimpleNamespace(x=500,y=80)) is None
    app.canvas_side=200
    assert MaskEditor.point(app, SimpleNamespace(x=299,y=249)) == (127,127)
    assert np.array_equal(app.drawing.grid, grid)
