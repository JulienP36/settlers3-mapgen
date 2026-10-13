from s3mapgen.application.ui.tooltip_position import tooltip_position
from s3mapgen.application.history.controller import HistoryController
from s3mapgen.application.history import controller


def test_tooltip_stays_beside_pointer_and_flips_at_screen_edges():
    assert tooltip_position(900,500,360,80,1920,1080) == (912,518)
    assert tooltip_position(1910,1070,360,80,1920,1080) == (1538,978)
    assert tooltip_position(0,0,360,80,1920,1080) == (12,18)


def test_native_menu_zero_origin_does_not_place_tooltip_at_screen_origin(monkeypatch):
    class Window:
        def __init__(self,*a,**kw):self.position=None
        def withdraw(self):pass
        def overrideredirect(self,*a):pass
        def attributes(self,*a):pass
        def update_idletasks(self):pass
        def winfo_reqwidth(self):return 360
        def winfo_reqheight(self):return 80
        def geometry(self,value):self.position=value
        def deiconify(self):pass
        def lift(self):pass
    class Label:
        def __init__(self,*a,**kw):pass
        def pack(self):pass
    class Menu:
        def winfo_rootx(self):return 0
        def winfo_rooty(self):return 0
        def winfo_screenwidth(self):return 1920
        def winfo_screenheight(self):return 1080
    class Host(HistoryController):
        _ui_tooltip_window=None
        _ui_tooltip_key=None
        def _hide_ui_tooltip(self):pass
        def winfo_pointerxy(self):return (900,500)
    monkeypatch.setattr(controller.tk,'Toplevel',Window)
    monkeypatch.setattr(controller.tk,'Label',Label)
    host=Host();host._show_ui_tooltip(Menu(),'help')
    assert host._ui_tooltip_window.position == '+912+518'
