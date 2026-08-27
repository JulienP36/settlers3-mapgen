from pathlib import Path

from s3mapgen.application.main_window import MainWindow


SRC='\n'.join(
    Path(path).read_text(encoding='utf-8')
    for path in ('s3mapgen/application/main_window.py', 's3mapgen/application/batch/controller.py')
)


def test_pinned_preview_uses_drag_bindings_and_no_longer_closes_on_image_click():
    show=SRC[SRC.index('def _batch_show_preview_tooltip'):SRC.index('def _batch_preview_geometry')]
    assert "cursor='fleur' if pinned else 'arrow'" in show
    assert "label.bind('<ButtonPress-1>',self._batch_preview_drag_start)" in show
    assert "label.bind('<B1-Motion>',self._batch_preview_drag_move)" in show
    assert "label.bind('<ButtonRelease-1>',self._batch_preview_drag_end)" in show
    assert "label.bind('<Button-1>',lambda e:self._batch_hide_preview_tooltip())" not in show


def test_switching_pinned_rows_preserves_the_previous_window_position():
    show=SRC[SRC.index('def _batch_show_preview_tooltip'):SRC.index('def _batch_preview_geometry')]
    assert 'preserved=(old_win.winfo_x(),old_win.winfo_y())' in show
    assert "x,y=self._batch_clamp_preview_position(preserved[0],preserved[1],size)" in show
    toggle=SRC[SRC.index('def _batch_toggle_large_preview'):SRC.index('def _batch_show_preview_tooltip')]
    assert 'if self._batch_preview_pinned and self._batch_preview_row is row:' in toggle
    assert 'self._batch_hide_preview_tooltip();return' in toggle
    assert 'self._batch_show_preview_tooltip(row,True)' in toggle


def test_live_preview_refresh_keeps_current_position_and_escape_still_closes():
    refresh=SRC[SRC.index('def _batch_refresh_preview_tooltip'):SRC.index('def _batch_hide_preview_tooltip')]
    assert 'current=(win.winfo_x(),win.winfo_y())' in refresh
    assert "x,y=self._batch_clamp_preview_position(current[0],current[1],size)" in refresh
    show=SRC[SRC.index('def _batch_show_preview_tooltip'):SRC.index('def _batch_preview_geometry')]
    assert "win.bind('<Escape>',lambda e:self._batch_hide_preview_tooltip(),add='+')" in show


def test_projection_and_row_replacement_double_buffer_before_destroying_old_surface():
    show=SRC[SRC.index('def _batch_show_preview_tooltip'):SRC.index('def _batch_build_preview_surface')]
    assert show.index('win.deiconify();win.lift();win.update_idletasks()') < show.index('old_win.destroy()')
    refresh=SRC[SRC.index('def _batch_refresh_preview_tooltip'):SRC.index('def _batch_hide_preview_tooltip')]
    assert "if projection!=self._batch_preview_projection:" in refresh
    assert refresh.index('new_win.deiconify();new_win.lift();new_win.update_idletasks()') < refresh.index('win.destroy();return')
    assert refresh.index("if projection!=self._batch_preview_projection:") < refresh.index('label.configure(image=photo)')


def test_preview_position_is_clamped_inside_the_visible_screen():
    dummy=type('Dummy',(),{'winfo_screenwidth':lambda self:1000,'winfo_screenheight':lambda self:700})()
    assert MainWindow._batch_clamp_preview_position(dummy,-200,-100,(400,300))==(8,8)
    assert MainWindow._batch_clamp_preview_position(dummy,900,650,(400,300))==(592,352)


def test_drag_uses_root_pointer_delta_and_updates_only_the_window_position():
    class Win:
        x=50;y=60;width=400;height=300;last=None
        def winfo_x(self):return self.x
        def winfo_y(self):return self.y
        def winfo_width(self):return self.width
        def winfo_height(self):return self.height
        def geometry(self,value):self.last=value
    win=Win()
    dummy=type('Dummy',(),{
        '_batch_preview_window':win,'_batch_preview_pinned':True,'_batch_preview_drag_origin':None,
        'winfo_screenwidth':lambda self:1000,'winfo_screenheight':lambda self:700,
        '_batch_clamp_preview_position':MainWindow._batch_clamp_preview_position,
    })()
    assert MainWindow._batch_preview_drag_start(dummy,type('Event',(),{'x_root':100,'y_root':100})())=='break'
    assert dummy._batch_preview_drag_origin==(100,100,50,60)
    assert MainWindow._batch_preview_drag_move(dummy,type('Event',(),{'x_root':200,'y_root':220})())=='break'
    assert win.last=='+150+180'
    assert MainWindow._batch_preview_drag_end(dummy)=='break' and dummy._batch_preview_drag_origin is None
