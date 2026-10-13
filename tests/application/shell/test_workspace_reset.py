from types import SimpleNamespace
from s3mapgen.application.shell.foundation import ShellWindow


class Pane:
    def __init__(self):self.width=1200;self.position=80;self.moves=[]
    def winfo_width(self):return self.width
    def sashpos(self,index,value=None):
        if value is not None:self.position=value;self.moves.append(value)
        return self.position
    def identify(self,x,y):return '0'


def test_workspace_reset_follows_maximize_geometry_then_yields_to_manual_drag():
    host=SimpleNamespace(_vertical_split_height=400,_vertical_split_dragging=False,
                         _vertical_split_initialized=True,prefs={'vertical_split_height':400},
                         _workspace_default_split_active=False,_workspace_split_job=None,
                         _content_paned=Pane(),zoom=2.7,view='resources')
    state=['normal'];jobs=[];saved=[]
    host.grab_current=lambda:None
    def window_state(value=None):
        if value is not None:state[0]=value
        return state[0]
    host.state=window_state
    host.after_idle=lambda callback:jobs.append(callback) or len(jobs)
    host._vertical_split_configure=lambda:None
    host._schedule_prefs_save=lambda:saved.append(True)
    host._apply_workspace_split=lambda:ShellWindow._apply_workspace_split(host)
    host._workspace_split_configure=lambda:ShellWindow._workspace_split_configure(host)
    ShellWindow._reset_workspace(host)
    assert state[0]=='zoomed' and host.prefs['vertical_split_height'] is None
    assert host.zoom==2.7 and host.view=='resources' and saved
    ShellWindow._workspace_split_configure(host);assert len(jobs)==1
    jobs.pop(0)();assert host._content_paned.position==660
    host._content_paned.width=1800
    ShellWindow._workspace_split_configure(host);jobs.pop(0)()
    assert host._content_paned.position==990
    ShellWindow._workspace_split_press(host,SimpleNamespace(x=720,y=5))
    host._content_paned.position=90
    ShellWindow._workspace_split_configure(host)
    assert not jobs and host._content_paned.position==90
