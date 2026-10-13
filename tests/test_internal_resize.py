"""Behavioral checks for the two internal panes and their redraw scheduling."""
from types import SimpleNamespace
import weakref

from PIL import Image

from s3mapgen.application.shell.foundation import ShellWindow
from s3mapgen.application.viewer.controller import ViewerController
from s3mapgen.application.analysis.controller import AnalysisController
from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.application.settings import preferences
import s3mapgen.application.viewer.controller as viewer_module


class IdleQueue:
    def __init__(self):
        self.jobs = {}
        self.counter = 0

    def after_idle(self, callback):
        self.counter += 1
        self.jobs[self.counter] = callback
        return self.counter

    def after_cancel(self, job):
        del self.jobs[job]

    def flush(self):
        jobs, self.jobs = self.jobs, {}
        for callback in jobs.values():
            callback()


class SplitProbe(IdleQueue):
    _vertical_split_configure = ShellWindow._vertical_split_configure
    _apply_vertical_split_layout = ShellWindow._apply_vertical_split_layout
    _vertical_split_press = ShellWindow._vertical_split_press
    _vertical_split_release = ShellWindow._vertical_split_release

    def __init__(self):
        super().__init__()
        self.total, self.natural, self.position = 700, 210, 250
        self._vertical_paned = self
        self.header_root = self
        self._vertical_split_height = None
        self._vertical_split_dragging = False
        self._vertical_split_initialized = False
        self._vertical_split_apply_after = None
        self.prefs = {}
        self.saves = 0
        self.sash_hit = '0'

    def winfo_height(self):
        return self.total

    def winfo_reqheight(self):
        return self.natural

    def sashpos(self, index, value=None):
        assert index == 0
        if value is not None:
            self.position = value
        return self.position

    def identify(self, x, y):
        return self.sash_hit

    def _schedule_prefs_save(self):
        self.saves += 1


def test_header_stays_attached_when_window_grows_and_controls_reflow():
    c = SplitProbe()
    for total, natural in ((700, 210), (1200, 210), (1200, 140), (700, 210)):
        c.total, c.natural = total, natural
        c._vertical_split_configure()
        c.flush()
        assert c.position == natural
    assert c._vertical_split_height is None


def test_manual_collapse_has_no_rebound_and_survives_resize():
    c = SplitProbe()
    event = SimpleNamespace(x=10, y=10)
    c._vertical_split_configure()
    c._vertical_split_press(event)
    assert not c.jobs
    for height in (60, 0):
        c._vertical_split_press(event)
        c.position = height
        c._vertical_split_release(event)
        c.flush()
        assert c.position == height
        assert c.prefs['vertical_split_height'] == height
        for total in (500, 1200):
            c.total = total
            c._vertical_split_configure()
            c.flush()
            assert c.position == height
    c.position = c.natural
    c._vertical_split_press(event)
    c._vertical_split_release(event)
    c.flush()
    assert c.prefs['vertical_split_height'] is None
    c.sash_hit = ''
    c._vertical_split_press(event)
    c._vertical_split_release(event)
    assert not c._vertical_split_dragging and c.saves == 3


def test_header_height_preferences_keep_auto_and_collapsed_states(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    for height in (None, 0, 55, 210):
        preferences.save_settings({'vertical_split_height': height, 'vertical_split_ratio': .65})
        loaded = preferences.load_settings()
        assert loaded['vertical_split_height'] == height
        c = SimpleNamespace(prefs=loaded)
        assert ShellWindow._initial_vertical_split_height(c) == height
    preferences.save_settings({'vertical_split_ratio': .65})
    assert preferences.load_settings()['vertical_split_height'] is None


def test_internal_resize_redraws_coalesce_without_fixed_or_restarted_timers():
    # No after(milliseconds) method: a fixed timer is a failure, as is
    # canceling/restarting the pending redraw for each pointer event.
    viewer = IdleQueue()
    viewer.current = object()
    viewer._preview_resize_after = None
    viewer.width = 200
    drawn = []
    def finish_view():
        viewer._preview_resize_after = None
        drawn.append(viewer.width)
    viewer._finish_preview_resize = finish_view
    for width in (220, 250, 300):
        viewer.width = width
        ViewerController._preview_canvas_configured(viewer)
    assert len(viewer.jobs) == 1
    viewer.flush()
    assert drawn == [300]
    ViewerController._preview_canvas_configured(viewer)
    assert len(viewer.jobs) == 1

    charts = IdleQueue()
    charts._stats_chart_after = None
    charts._finish_stats_chart_refresh = lambda: None
    for _ in range(3):
        AnalysisController._schedule_stats_chart_refresh(charts)
    assert len(charts.jobs) == 1

    host = IdleQueue()
    archetype = SimpleNamespace(
        _custom_archetype_preview_size_key='adaptive',
        _custom_archetype_preview_layout_after=None,
        _custom_archetype_tab=host,
        _custom_resize_archetype_preview_canvases=lambda: None,
    )
    for _ in range(3):
        CustomGeneratorController._custom_archetype_preview_surface_changed(archetype)
    assert len(host.jobs) == 1


def test_viewer_keeps_old_photo_alive_until_canvas_receives_replacement(monkeypatch):
    class Photo:
        pass
    previous = Photo()
    previous_ref = weakref.ref(previous)
    new_photo = Photo()
    calls = []
    canvas = SimpleNamespace(
        winfo_width=lambda: 400, winfo_height=lambda: 300,
        coords=lambda *args: None, configure=lambda **kw: None,
    )
    def swap(item, **kwargs):
        assert item == 4 and previous_ref() is not None
        assert kwargs['image'] is new_photo
        calls.append(item)
    canvas.itemconfigure = swap
    c = SimpleNamespace(
        current=SimpleNamespace(state=object()), _zoom_after=None,
        _cancel_preview_resize=lambda: None, _capture_view_anchor=lambda: None,
        _pending_view_anchor=None, _update_view_controls=lambda: None,
        _render_options=lambda: {'view':'global', 'projection':'square', 'overlay_alpha':100, 'heatmap_resource':None},
        _chart_focus_options=lambda opts: (opts, None),
        _preview_layer_key=None, _preview_projection_cache={},
        _restore_view_anchor=lambda *args: None, zoom=1.0,
        canvas=canvas, _preview_canvas_item=4, photo=previous,
    )
    del previous
    raster = Image.new('RGB', (8, 8))
    monkeypatch.setattr(viewer_module, 'render_square_base', lambda *args: raster)
    monkeypatch.setattr(viewer_module, 'compose_rendered_map', lambda *args, **kwargs: raster)
    monkeypatch.setattr(viewer_module.ImageTk, 'PhotoImage', lambda image: new_photo)
    ViewerController._refresh_preview(c)
    assert calls == [4] and c.photo is new_photo and previous_ref() is None
