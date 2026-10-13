"""A hidden notebook page must not starve Tk's idle queue with scrollbar relayouts."""
from types import SimpleNamespace

import s3mapgen.application.settings.controller as module
from s3mapgen.application.settings.controller import SettingsController


class Widget:
    def __init__(self, parent=None, **options):
        self.parent, self.options = parent, options
        self.manager = ''
        self.width, self.height = 300, 200
        self.required_w, self.required_h = 720, 500
        self.callbacks = {}
        self.jobs = {}
        self.counter = 0
        self.refreshes = 0
        self.scroll_positions = []

    def grid(self, **options):
        self.manager = 'grid'

    def grid_remove(self):
        self.manager = ''

    def winfo_manager(self):
        return self.manager

    def winfo_ismapped(self):
        # A notebook page remains unmapped even if a scrollbar was gridded.
        return False

    def winfo_width(self):
        return self.width

    def winfo_height(self):
        return self.height

    def winfo_reqwidth(self):
        return self.required_w

    def winfo_reqheight(self):
        return self.required_h

    def rowconfigure(self, *args, **kwargs):
        pass

    columnconfigure = rowconfigure
    set = rowconfigure
    itemconfigure = rowconfigure

    def configure(self, **options):
        self.options.update(options)

    def create_window(self, position, **options):
        return 1

    def bbox(self, *args):
        return (0, 0, 720, 500)

    def xview_moveto(self, value):
        self.scroll_positions.append(('x', value))

    def yview_moveto(self, value):
        self.scroll_positions.append(('y', value))

    def bind(self, sequence, callback, add=None):
        self.callbacks[sequence] = callback

    def after_idle(self, callback):
        self.counter += 1
        self.jobs[self.counter] = callback
        return self.counter

    def drain(self, limit=20):
        # Bounded on purpose: the old idle loop is reproduced without hanging
        # pytest itself. Tk's update_idletasks has no such artificial limit.
        for _ in range(limit):
            if not self.jobs:
                return
            jobs, self.jobs = self.jobs, {}
            for callback in jobs.values():
                self.refreshes += 1
                callback()
        assert not self.jobs, 'Hidden tab keeps rescheduling scrollbar layout forever'


def hidden_tab(monkeypatch):
    bars = []
    monkeypatch.setattr(module.ttk, 'Frame', Widget)
    monkeypatch.setattr(module.tk, 'Canvas', Widget)
    def scrollbar(*args, **kwargs):
        bar = Widget(*args, **kwargs)
        bars.append(bar)
        return bar
    monkeypatch.setattr(module.ttk, 'Scrollbar', scrollbar)
    host = SimpleNamespace(
        nb=SimpleNamespace(add=lambda *args, **kwargs: None),
        _ensure_scrollable_tab_wheel_bindings=lambda: None,
        _scroll_tab_surfaces=[],
    )
    inner = SettingsController._scroll_notebook_tab(host, 'Hidden editor')
    return inner, inner._scroll_canvas, bars


def test_hidden_tab_scrollbar_layout_settles_before_window_is_mapped(monkeypatch):
    inner, canvas, bars = hidden_tab(monkeypatch)
    canvas.drain()
    assert all(bar.winfo_manager() == 'grid' and not bar.winfo_ismapped() for bar in bars)
    assert canvas.refreshes == 2
    assert not canvas.jobs


def test_hidden_tab_scrollbars_remove_and_return_without_idle_loop(monkeypatch):
    inner, canvas, bars = hidden_tab(monkeypatch)
    canvas.drain()
    inner.required_w, inner.required_h = 100, 100
    inner.callbacks['<Configure>'](None)
    canvas.drain()
    assert all(bar.winfo_manager() == '' for bar in bars)
    assert canvas.scroll_positions == [('x', 0), ('y', 0)]
    inner.required_w, inner.required_h = 720, 500
    inner.callbacks['<Configure>'](None)
    canvas.drain()
    assert all(bar.winfo_manager() == 'grid' for bar in bars)
    assert canvas.refreshes == 6
    assert not canvas.jobs
