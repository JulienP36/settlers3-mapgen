"""Progress-overlay and task-status coordination for the desktop application."""

from __future__ import annotations

import tkinter as tk

from ..ui.i18n.common import _lang_text


class TaskController:
    """Host contract: canvas, status variables and themed feedback widgets."""
    def _task_overlay_dimensions(self):
        """Responsive overlay dimensions relative to the visible map viewport."""
        try:
            self.canvas.update_idletasks()
            cw=max(1,int(self.canvas.winfo_width()))
        except tk.TclError:
            cw=720
        # Keep comfortable margins on small windows, but do not make the panel
        # absurdly wide on large monitors.
        width=max(300,min(680,int(cw*0.52)))
        width=min(width,max(220,cw-36))
        return width,86

    def _fit_progress_detail(self,text,max_px):
        """Elide a technical status string only when it cannot fit inside the bar."""
        text=str(text or '')
        try:
            import tkinter.font as tkfont
            font=tkfont.nametofont('TkDefaultFont')
            if font.measure(text)<=max_px:return text
            ell='…'; budget=max(20,max_px-font.measure(ell))
            left='';right='';li=0;ri=len(text)-1;turn=True
            while li<=ri:
                if turn:
                    cand=left+text[li]
                    if font.measure(cand)+font.measure(right)>budget:break
                    left=cand;li+=1
                else:
                    cand=text[ri]+right
                    if font.measure(left)+font.measure(cand)>budget:break
                    right=cand;ri-=1
                turn=not turn
            return left+ell+right
        except Exception:
            return text

    def _draw_task_progress(self,value,detail=None):
        if self._task_overlay is None or not hasattr(self,'_task_overlay_progress'):return
        value=max(0,min(100,float(value)));self._task_overlay_value=value
        if detail is not None:self._task_overlay_detail=str(detail)
        c=self._task_overlay_progress
        try:c.update_idletasks()
        except tk.TclError:return
        c.delete('all');w=max(1,int(c.winfo_width()));h=max(1,int(c.winfo_height()))
        colors=getattr(self,'_ui_theme_colors',{})
        bg=colors.get('bar_bg','#3c4043');fg=colors.get('bar_fg','#35a853');text_color=colors.get('fg','#e8eaed')
        c.configure(bg=bg,highlightthickness=0)
        if value>0:c.create_rectangle(0,0,max(1,round(w*value/100.0)),h,fill=fg,outline='')
        shown=self._fit_progress_detail(self._task_overlay_detail,max(40,w-18))
        # Keep the halo only in dark mode. In the light theme the same dark
        # text plus a dark outline makes the glyphs look artificially bold.
        cx,cy=w//2,h//2
        if colors.get('dark',False):
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                c.create_text(cx+dx,cy+dy,text=shown,fill='#151719',anchor='center')
        c.create_text(cx,cy,text=shown,fill=text_color,anchor='center')

    def _layout_task_overlay(self,event=None):
        if self._task_overlay is None:return
        try:
            width,height=self._task_overlay_dimensions()
            self._task_overlay.place_configure(relx=.5,rely=.5,anchor='center',width=width,height=height)
            self._task_overlay_title.configure(wraplength=max(180,width-28))
            self._task_overlay.update_idletasks()
            self._draw_task_progress(self._task_overlay_value)
            self._task_overlay.lift()
        except tk.TclError:pass

    def _task_begin(self,label,value=5):
        self._status_kind='busy';self.status.set(label);getattr(self,'_sync_status_display',lambda:None)()
        self._close_task_overlay()
        colors=getattr(self,'_ui_theme_colors',{})
        panel=colors.get('panel','#292a2d');fg=colors.get('fg','#e8eaed')
        overlay=tk.Frame(self.canvas,bg=panel,bd=1,relief='solid',highlightthickness=0)
        self._task_overlay=overlay
        title=label.strip() if label else _lang_text(self.prefs.get('language','fr'),'Génération…','Generating…','Generierung…','Generando…')
        self._task_overlay_title=tk.Label(overlay,text=title,bg=panel,fg=fg,anchor='center',justify='center')
        self._task_overlay_title.pack(fill='x',padx=14,pady=(11,7))
        self._task_overlay_progress=tk.Canvas(overlay,height=24,bg=colors.get('bar_bg','#3c4043'),highlightthickness=0,bd=0)
        self._task_overlay_progress.pack(fill='x',expand=True,padx=14,pady=(0,12))
        self._task_overlay_value=max(0,min(100,float(value)));self._task_overlay_detail=_lang_text(self.prefs.get('language','fr'),'Initialisation…','Initializing…','Initialisierung…','Inicializando…')
        self.canvas.bind('<Configure>',self._layout_task_overlay,add='+')
        self._layout_task_overlay();self._draw_task_progress(value,self._task_overlay_detail);self.update_idletasks()

    def _task_progress(self,value,label=None):
        # Fast-changing stage detail belongs in the progress bar/overlay, not in the human status strip.
        if self._task_overlay is not None:self._draw_task_progress(max(0,min(99,value)),label if label else None)
        self.update_idletasks()

    def _close_task_overlay(self):
        if self._task_overlay is not None:
            try:self._task_overlay.destroy()
            except tk.TclError:pass
            self._task_overlay=None

    def _task_done(self,label=None):
        self._status_kind='success'
        if label:self.status.set(label)
        self._sync_status_display()
        if self._task_overlay is not None:
            self._draw_task_progress(100,label if label else None);self.update_idletasks()
        self._close_task_overlay()

    def _task_error(self,label='Erreur'):
        self._status_kind='error';self.status.set(label);getattr(self,'_sync_status_display',lambda:None)();self._close_task_overlay();self.update_idletasks()
