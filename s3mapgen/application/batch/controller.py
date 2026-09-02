"""Batch window, request queue, thumbnails and result assignment.

``BatchController`` is a behavior-preserving mixin. Its host supplies the
application cache, rendering options, feedback, history and comparison APIs.
"""

from __future__ import annotations
import random
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from ...generation.archetypes import ARCHETYPES, ARCHETYPE_ORDER
from ...generation.core import native_size_warning_kind
from ...generation.modes import MODES, MODE_ORDER
from ..rendering.preview import compose_start_markers, project_parallelogram, render_square_base
from ..session.cache import GenerationCacheKey
from ..shell import NATIVE_LIMITS
from ..ui.i18n.batch import BATCH_HINTS, BATCH_TEXT, _BATCH_CAPACITY_TEXT
from ..ui.i18n.history import _CONTEXT_TEXT
from ..ui.i18n.shell import ARCHETYPE_LABELS, MIRROR_LABELS, MODE_LABELS
from ..ui.theme import THEME_PALETTES
from ..ui.widgets import _thumbnail_with_magnifier

class BatchController:
    def _batch_text(self,key,**values):
        text=BATCH_TEXT[self.prefs.get('language','fr')][key]
        return text.format(**values) if values else text

    @staticmethod
    def _batch_label_key(value,label_tables,fallback):
        for labels in label_tables.values():
            for key,label in labels.items():
                if label==value:return key
        return fallback

    def _open_batch_window(self):
        if self._batch_window is not None:
            try:self._batch_window.deiconify();self._batch_window.lift();self._batch_window.focus_force();return
            except tk.TclError:self._batch_window=None
        lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang]
        win=tk.Toplevel(self);self._batch_window=win
        win.title(bt['title']);win.transient(self);win.geometry('1120x650');win.minsize(900,560)
        win.protocol('WM_DELETE_WINDOW',self._close_batch_window)
        shell=ttk.Frame(win,padding=12);shell.pack(fill='both',expand=True)

        header=ttk.Frame(shell);header.pack(fill='x',pady=(0,6))
        self._batch_i18n={'shell':shell}
        self._batch_i18n['count_label']=ttk.Label(header,text=bt['count']);self._batch_i18n['count_label'].pack(side='left')
        self._batch_count_var=tk.StringVar(value='4')
        self._batch_count_spin=ttk.Spinbox(header,from_=1,to=4,textvariable=self._batch_count_var,width=4,command=self._batch_update_row_visibility)
        self._batch_count_spin.pack(side='left',padx=(7,8));self._batch_count_spin.bind('<KeyRelease>',self._batch_count_typed);self._batch_count_spin.bind('<Return>',self._batch_commit_count);self._batch_count_spin.bind('<FocusOut>',self._batch_commit_count)
        self._batch_randomize_button=ttk.Button(header,text=bt['randomize'],command=self._batch_randomize_seeds)
        self._batch_randomize_button.pack(side='left',padx=(0,12))
        self._batch_common_seed_var=tk.StringVar(value=str(self._default_batch_seed()))
        self._batch_common_seed_entry=ttk.Entry(header,textvariable=self._batch_common_seed_var,width=13);self._batch_common_seed_entry.pack(side='left')
        self._batch_common_seed_random=ttk.Button(header,text='🎲',width=3,command=self._batch_randomize_common_seed);self._batch_common_seed_random.pack(side='left',padx=(4,0))
        self._batch_apply_seed_button=ttk.Button(header,text=bt['apply_seed'],command=self._batch_apply_seed_all);self._batch_apply_seed_button.pack(side='left',padx=(4,0))
        self._batch_i18n['hint_label']=ttk.Label(header,text=BATCH_HINTS.get(lang,BATCH_HINTS['en']));self._batch_i18n['hint_label'].pack(side='right')

        rows_host=ttk.Frame(shell);rows_host.pack(fill='both',expand=True)
        rows_host.columnconfigure(0,weight=1)
        self._batch_rows=[]
        current_mode=self._mode_key();current_arch=self._arch_key();current_mirror=self._mirror_key() if hasattr(self,'_mirror_key') else 0;current_size=str(self.size.get());current_players=str(self.players.get())
        first_seed=self._default_batch_seed();self._batch_common_seed_var.set(str(first_seed))
        for index in range(1,5):
            frame=ttk.Labelframe(rows_host,text=bt['map'].format(index=index),padding=(1,1))
            frame.grid(row=index-1,column=0,sticky='ew',pady=(0,4));frame.columnconfigure(0,weight=1)
            controls=ttk.Frame(frame);controls.grid(row=0,column=0,sticky='ew',padx=(7,0),pady=(3,0))
            row={'index':index,'frame':frame,'result':None,'state':'waiting','cached':False,'error':'','progress_value':0};input_widgets=[];row['group_labels']={}

            def group(key):
                box=ttk.Frame(controls);box.pack(side='left',padx=(0,7));label=ttk.Label(box,text=bt[key]);label.pack(anchor='w',pady=(0,2));row['group_labels'][key]=label;return box

            box=group('mode');row['mode_var']=tk.StringVar(value=MODE_LABELS[lang][current_mode])
            row['mode']=ttk.Combobox(box,textvariable=row['mode_var'],values=[MODE_LABELS[lang][k] for k in MODE_ORDER],state='readonly',width=19);row['mode'].pack();input_widgets.append((row['mode'],'readonly'))
            box=group('archetype');row['arch_var']=tk.StringVar(value=ARCHETYPE_LABELS[lang][current_arch])
            row['arch']=ttk.Combobox(box,textvariable=row['arch_var'],values=[ARCHETYPE_LABELS[lang][k] for k in ARCHETYPE_ORDER],state='readonly',width=17);row['arch'].pack();input_widgets.append((row['arch'],'readonly'))
            box=group('modifiers');row['modifier_var']=tk.StringVar(value=bt['none'])
            row['modifier']=ttk.Combobox(box,textvariable=row['modifier_var'],values=[bt['none']],state='readonly',width=13);row['modifier'].pack();input_widgets.append((row['modifier'],'readonly'))
            box=group('mirror');row['mirror_var']=tk.StringVar(value=MIRROR_LABELS[lang][current_mirror])
            mirror_width=max(8,max((len(str(value)) for value in MIRROR_LABELS[lang].values()),default=0)+2)
            row['mirror']=ttk.Combobox(box,textvariable=row['mirror_var'],values=list(MIRROR_LABELS[lang].values()),state='readonly',width=mirror_width);row['mirror'].pack();input_widgets.append((row['mirror'],'readonly'))
            box=group('size');row['size_var']=tk.StringVar(value=current_size)
            row['size']=ttk.Combobox(box,textvariable=row['size_var'],values=[str(x) for x in NATIVE_LIMITS],state='readonly',width=7);row['size'].pack();input_widgets.append((row['size'],'readonly'))
            box=group('players');row['players_var']=tk.StringVar(value=current_players)
            row['players']=ttk.Spinbox(box,from_=2,to=NATIVE_LIMITS.get(int(current_size),20),textvariable=row['players_var'],width=7);row['players'].pack();input_widgets.append((row['players'],'normal'))
            box=group('seed');row['seed_var']=tk.StringVar(value=str(first_seed))
            seed_line=ttk.Frame(box);seed_line.pack(fill='x');row['seed']=ttk.Entry(seed_line,textvariable=row['seed_var'],width=14);row['seed'].pack(side='left');input_widgets.append((row['seed'],'normal'))
            row['random']=ttk.Button(seed_line,text='🎲',width=3,command=lambda r=row:self._batch_randomize_row(r));row['random'].pack(side='left',padx=(4,0));input_widgets.append((row['random'],'normal'))
            row['size'].bind('<<ComboboxSelected>>',lambda e,r=row:self._batch_row_size_changed(r))

            mini_bg=getattr(self,'_ui_theme_colors',{}).get('panel','#292a2d')
            row['thumbnail_host']=tk.Frame(frame,width=182,height=122,bg=mini_bg,bd=0,highlightthickness=0);row['thumbnail_host'].grid(row=0,column=1,rowspan=2,sticky='e');row['thumbnail_host'].grid_propagate(False)
            row['thumbnail']=tk.Label(row['thumbnail_host'],text=str(index),bg=mini_bg,bd=0,highlightthickness=0,cursor='hand2');row['thumbnail'].place(relx=.5,rely=.5,anchor='center')
            row['thumbnail'].bind('<Button-1>',lambda e,r=row:self._batch_toggle_large_preview(r));row['thumbnail'].bind('<Enter>',lambda e,r=row:self._batch_schedule_hover_preview(r));row['thumbnail'].bind('<Leave>',lambda e,r=row:self._batch_thumbnail_leave(r))
            row['thumbnail_host'].bind('<Enter>',lambda e,r=row:self._batch_schedule_hover_preview(r),add='+');row['thumbnail_host'].bind('<Leave>',lambda e,r=row:self._batch_thumbnail_leave(r),add='+')
            result_line=ttk.Frame(frame);result_line.grid(row=1,column=0,sticky='ew',padx=(7,8),pady=(7,3));result_line.columnconfigure(3,weight=1)
            row['status_var']=tk.StringVar(value=bt['waiting'])
            row['show']=ttk.Button(result_line,text=bt['show'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_show_result(r));row['show'].grid(row=0,column=0,padx=(0,4))
            row['set_a']=ttk.Button(result_line,text=bt['set_a'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_assign_result(r,'A'));row['set_a'].grid(row=0,column=1,padx=2)
            row['set_b']=ttk.Button(result_line,text=bt['set_b'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_assign_result(r,'B'));row['set_b'].grid(row=0,column=2,padx=(2,7))
            row['progress']=tk.Canvas(result_line,height=26,highlightthickness=0,bd=0);row['progress'].grid(row=0,column=3,sticky='ew');row['progress'].bind('<Configure>',lambda e,r=row:self._batch_draw_progress(r))
            row['input_widgets']=input_widgets;self._batch_rows.append(row)
            self._batch_draw_progress(row)

        footer=ttk.Frame(shell);footer.pack(fill='x',pady=(2,0))
        self._batch_summary_var=tk.StringVar(value=bt['waiting']);self._batch_i18n['summary_label']=ttk.Label(footer,textvariable=self._batch_summary_var,anchor='w');self._batch_i18n['summary_label'].pack(side='left',fill='x',expand=True)
        self._batch_start_button=ttk.Button(footer,text=bt['start'],command=self._start_batch);self._batch_start_button.pack(side='right',padx=(5,0))
        self._batch_cancel_button=ttk.Button(footer,text=bt['cancel'],command=self._cancel_batch,state='disabled');self._batch_cancel_button.pack(side='right',padx=(5,0))
        self._batch_close_button=ttk.Button(footer,text=bt['close'],command=self._close_batch_window);self._batch_close_button.pack(side='right')
        self._batch_update_row_visibility();self._fit_batch_window_initial();self._feedback('batch_opened','info')

    def _fit_batch_window_initial(self):
        win=self._batch_window
        if win is None:return
        try:
            win.update_idletasks();screen_w=win.winfo_screenwidth();screen_h=win.winfo_screenheight();max_w=max(900,screen_w-64);max_h=max(560,screen_h-96)
            wanted_w=max(1120,win.winfo_reqwidth());wanted_h=max(650,win.winfo_reqheight());width=min(wanted_w,max_w);height=min(wanted_h,max_h)
            self.update_idletasks();x=self.winfo_rootx()+(self.winfo_width()-width)//2;y=self.winfo_rooty()+(self.winfo_height()-height)//2
            x=max(8,min(x,screen_w-width-8));y=max(8,min(y,screen_h-height-48));win.minsize(min(900,width),min(560,height));win.geometry(f'{width}x{height}+{x}+{y}')
        except tk.TclError:pass

    def _default_batch_seed(self):
        try:return int(self.seed.get())
        except (TypeError,ValueError):return random.randint(1,2_147_483_647)

    def _batch_apply_seed_all(self):
        value=self._batch_common_seed_var.get().strip()
        try:int(value)
        except (TypeError,ValueError):
            messagebox.showerror(self._batch_text('invalid_title'),self._batch_text('invalid_seed'),parent=self._batch_window);return
        for row in self._batch_rows:row['seed_var'].set(value)

    def _batch_randomize_common_seed(self):
        self._batch_common_seed_var.set(str(random.randint(1,2_147_483_647)))

    def _batch_update_progress(self,row,value,text=None,state=None):
        row['progress_value']=max(0,min(100,float(value)))
        if text is not None:row['status_var'].set(str(text))
        if state is not None:row['state']=state
        self._batch_draw_progress(row)

    def _batch_draw_progress(self,row):
        canvas=row.get('progress')
        if canvas is None:return
        try:
            canvas.update_idletasks();w=max(1,canvas.winfo_width());h=max(1,canvas.winfo_height());canvas.delete('all')
            colors=getattr(self,'_ui_theme_colors',{});bg=colors.get('bar_bg','#3c4043');state=row.get('state','waiting')
            fill={'running':colors.get('bar_fg','#35a853'),'success':'#35a853','cached':'#2879d0','not_cached':colors.get('warning','#f9ab00'),'failed':'#d84a3a','cancelled':'#7f858d'}.get(state,colors.get('muted','#7f858d'))
            value=float(row.get('progress_value',0));canvas.configure(bg=bg)
            if value>0:canvas.create_rectangle(0,0,max(1,round(w*value/100)),h,fill=fill,outline='')
            shown=self._fit_progress_detail(row.get('status_var').get() if row.get('status_var') else '',max(40,w-18))
            canvas.create_text(w//2,h//2,text=shown,fill=colors.get('fg','#e8eaed'),anchor='center')
        except tk.TclError:pass

    def _batch_render_thumbnail(self,row):
        out=row.get('result')
        if out is None:return
        state_key=id(out.state);projection=self.prefs.get('projection','square')
        if row.get('preview_square_base_key')!=state_key:
            row['preview_square_base_image']=render_square_base(out.state,view='global',overlay_alpha=100,heatmap_resource='trees')
            row['preview_square_base_key']=state_key;row['preview_projected_base_image']=None;row['preview_projected_base_key']=None
        if projection=='parallelogram':
            if row.get('preview_projected_base_key')!=state_key:
                row['preview_projected_base_image']=project_parallelogram(row['preview_square_base_image']);row['preview_projected_base_key']=state_key
            row['preview_base_image']=row['preview_projected_base_image']
        else:row['preview_base_image']=row['preview_square_base_image']
        row['preview_base_key']=(state_key,projection)
        image=self._batch_compose_preview(row)
        thumb=image.copy();thumb.thumbnail((180,120),Image.Resampling.NEAREST)
        row['thumbnail_base_image']=thumb;self._batch_refresh_thumbnail_photo(row)

    def _batch_refresh_thumbnail_photo(self,row):
        base=row.get('thumbnail_base_image');label=row.get('thumbnail')
        if base is None or label is None:return
        shown=_thumbnail_with_magnifier(base,self._magnifier_state_for('batch',row));row['thumbnail_photo']=ImageTk.PhotoImage(shown,master=label);label.configure(image=row['thumbnail_photo'],text='')

    def _batch_compose_preview(self,row):
        base=row.get('preview_base_image');out=row.get('result')
        if base is None or out is None:return None
        marker_mode=self.prefs.get('preview_start_markers','small')
        if marker_mode=='hidden':return base
        return compose_start_markers(base,out.state,projection=self.prefs.get('projection','square'),scale=2 if marker_mode=='normal' else 1)

    def _refresh_batch_previews(self):
        if not getattr(self,'_batch_rows',None):return
        visible_row=self._batch_preview_row;visible=self._batch_preview_window is not None
        for row in self._batch_rows:
            if row.get('result') is not None:self._batch_render_thumbnail(row)
        if visible and visible_row is not None and visible_row.get('result') is not None:self._batch_refresh_preview_tooltip(visible_row)

    def _batch_schedule_hover_preview(self,row):
        self._batch_cancel_hover_preview()
        if row.get('result') is None:return
        self._set_magnifier_hover('batch',row)
        if not self._batch_preview_pinned:self._batch_hover_after=self.after(700,lambda r=row:self._batch_hover_preview_ready(r))

    def _batch_hover_preview_ready(self,row):
        self._batch_hover_after=None
        if self._magnifier_hover_kind=='batch' and self._magnifier_hover_ref is row:self._batch_show_preview_tooltip(row,False)

    def _batch_cancel_hover_preview(self,event=None):
        if self._batch_hover_after is not None:
            try:self.after_cancel(self._batch_hover_after)
            except tk.TclError:pass
            self._batch_hover_after=None

    def _batch_thumbnail_leave(self,row=None):
        self._batch_cancel_hover_preview()
        try:self.after_idle(lambda r=row:self._batch_finish_thumbnail_leave(r))
        except tk.TclError:pass

    def _batch_finish_thumbnail_leave(self,row):
        if row is not None:
            host=row.get('thumbnail_host')
            try:
                x,y=host.winfo_pointerxy();inside=host.winfo_rootx()<=x<host.winfo_rootx()+host.winfo_width() and host.winfo_rooty()<=y<host.winfo_rooty()+host.winfo_height()
                if inside:return
            except (tk.TclError,AttributeError):pass
        if self._magnifier_hover_kind=='batch' and self._magnifier_hover_ref is row:self._set_magnifier_hover()
        if not self._batch_preview_pinned:self._batch_hide_preview_tooltip()
        else:self._restore_magnifier_visual()

    def _batch_toggle_large_preview(self,row):
        if self._batch_preview_pinned and self._batch_preview_row is row:
            self._batch_hide_preview_tooltip();return
        self._batch_show_preview_tooltip(row,True)

    def _batch_show_preview_tooltip(self,row,pinned=False):
        self._batch_cancel_hover_preview()
        if row.get('result') is None:return
        if row.get('preview_base_image') is None:self._batch_render_thumbnail(row)
        image=self._batch_compose_preview(row)
        old_win=self._batch_preview_window;preserved=None
        if old_win is not None and self._batch_preview_pinned:
            try:preserved=(old_win.winfo_x(),old_win.winfo_y())
            except tk.TclError:pass
        if pinned:shown,size,x,y=self._batch_preview_geometry(row,image)
        else:shown,size,x,y=self._temporary_preview_geometry(image,self._batch_preview_zoom,row['thumbnail_host'])
        if preserved is not None:x,y=self._batch_clamp_preview_position(preserved[0],preserved[1],size)
        win,label,photo=self._batch_build_preview_surface(shown,size,x,y,pinned)
        self._batch_preview_window=win;self._batch_preview_label=label;self._batch_preview_photo=photo;self._batch_preview_row=row;self._batch_preview_pinned=bool(pinned);self._batch_preview_projection=self.prefs.get('projection','square');self._activate_magnifier('batch',row)
        win.deiconify();win.lift();win.update_idletasks()
        if old_win is not None and old_win is not win:
            try:old_win.destroy()
            except tk.TclError:pass

    def _batch_build_preview_surface(self,shown,size,x,y,pinned):
        chroma='#ff00ff';win=tk.Toplevel(self._batch_window or self);win.withdraw()
        win.overrideredirect(True);win.configure(bg=chroma);win.attributes('-topmost',True)
        try:win.wm_attributes('-transparentcolor',chroma)
        except tk.TclError:pass
        photo=ImageTk.PhotoImage(shown,master=win);label=tk.Label(win,image=photo,bg=chroma,bd=0,highlightthickness=0,cursor='fleur' if pinned else 'arrow');label.pack()
        win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        if pinned:
            label.bind('<ButtonPress-1>',self._batch_preview_drag_start);label.bind('<B1-Motion>',self._batch_preview_drag_move);label.bind('<ButtonRelease-1>',self._batch_preview_drag_end)
        label.bind('<MouseWheel>',self._batch_preview_wheel);label.bind('<Button-4>',lambda e:self._batch_preview_wheel(e,1));label.bind('<Button-5>',lambda e:self._batch_preview_wheel(e,-1))
        win.bind('<Escape>',lambda e:self._batch_hide_preview_tooltip(),add='+')
        win.update_idletasks();return win,label,photo

    def _batch_preview_geometry(self,row,image):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight();anchor=row['thumbnail_host'];anchor.update_idletasks()
        ax=anchor.winfo_rootx();ay=anchor.winfo_rooty();aw=anchor.winfo_width();ah=anchor.winfo_height();margin=14
        left_space=max(0,ax-margin-8);right_space=max(0,screen_w-(ax+aw)-margin-8);place_left=left_space>=right_space
        side_space=left_space if place_left else right_space
        if side_space<360:place_left=not place_left
        # Match History preview: zoom is constrained by the visible screen, not
        # by the narrow strip beside the Batch window. Overlap is preferable to
        # silently flattening most of the requested zoom range.
        max_w=max(320,screen_w-80);max_h=max(280,screen_h-120)
        factor=min(max_w/image.width,max_h/image.height,float(self._batch_preview_zoom));size=(max(1,int(image.width*factor)),max(1,int(image.height*factor)));shown=image.resize(size,Image.Resampling.NEAREST)
        x=(ax-size[0]-margin) if place_left else (ax+aw+margin);x=max(8,min(x,screen_w-size[0]-8))
        y=ay+(ah-size[1])//2;y=max(8,min(y,screen_h-size[1]-48))
        return shown,size,x,y

    def _batch_clamp_preview_position(self,x,y,size):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight()
        return max(8,min(int(x),screen_w-size[0]-8)),max(8,min(int(y),screen_h-size[1]-48))

    def _batch_preview_drag_start(self,event):
        win=self._batch_preview_window
        if win is None or not self._batch_preview_pinned:return 'break'
        try:self._batch_preview_drag_origin=(event.x_root,event.y_root,win.winfo_x(),win.winfo_y())
        except tk.TclError:self._batch_preview_drag_origin=None
        return 'break'

    def _batch_preview_drag_move(self,event):
        win=self._batch_preview_window;origin=self._batch_preview_drag_origin
        if win is None or origin is None or not self._batch_preview_pinned:return 'break'
        try:
            size=(win.winfo_width(),win.winfo_height());x,y=self._batch_clamp_preview_position(origin[2]+event.x_root-origin[0],origin[3]+event.y_root-origin[1],size)
            win.geometry(f'+{x}+{y}')
        except tk.TclError:pass
        return 'break'

    def _batch_preview_drag_end(self,event=None):
        self._batch_preview_drag_origin=None;return 'break'

    def _batch_preview_wheel(self,event,direction=None):
        if direction is None:direction=1 if getattr(event,'delta',0)>0 else -1
        self._batch_preview_zoom=max(.35,min(1.25,self._batch_preview_zoom+(.1 if direction>0 else -.1)));self._batch_refresh_preview_tooltip(self._batch_preview_row);return 'break'

    def _batch_refresh_preview_tooltip(self,row):
        win=self._batch_preview_window;label=self._batch_preview_label
        if win is None or label is None or self._batch_preview_row is not row:return
        try:
            current=(win.winfo_x(),win.winfo_y());image=self._batch_compose_preview(row)
            if self._batch_preview_pinned:
                shown,size,_,_=self._batch_preview_geometry(row,image);x,y=self._batch_clamp_preview_position(current[0],current[1],size)
            else:shown,size,x,y=self._temporary_preview_geometry(image,self._batch_preview_zoom,row['thumbnail_host'])
            projection=self.prefs.get('projection','square')
            if projection!=self._batch_preview_projection:
                new_win,new_label,new_photo=self._batch_build_preview_surface(shown,size,x,y,self._batch_preview_pinned)
                self._batch_preview_window=new_win;self._batch_preview_label=new_label;self._batch_preview_photo=new_photo;self._batch_preview_projection=projection
                new_win.deiconify();new_win.lift();new_win.update_idletasks();win.destroy();return
            photo=ImageTk.PhotoImage(shown);label.configure(image=photo);self._batch_preview_photo=photo
            win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        except tk.TclError:pass

    def _batch_hide_preview_tooltip(self):
        closing_row=self._batch_preview_row
        if self._batch_preview_window is not None:
            try:self._batch_preview_window.destroy()
            except tk.TclError:pass
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None
        if self._magnifier_active_kind=='batch' and self._magnifier_active_ref is closing_row:self._set_magnifier_active()
        self._restore_magnifier_visual()

    def _retranslate_batch_window(self):
        win=getattr(self,'_batch_window',None)
        if win is None:return
        try:
            lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang];win.title(bt['title'])
            self._batch_i18n['count_label'].configure(text=bt['count']);self._batch_randomize_button.configure(text=bt['randomize']);self._batch_apply_seed_button.configure(text=bt['apply_seed'])
            self._batch_i18n['hint_label'].configure(text=BATCH_HINTS.get(lang,BATCH_HINTS['en']))
            for row in self._batch_rows:
                mode=self._batch_label_key(row['mode_var'].get(),MODE_LABELS,'legacy');arch=self._batch_label_key(row['arch_var'].get(),ARCHETYPE_LABELS,'continental');mirror=self._batch_label_key(row.get('mirror_var').get() if row.get('mirror_var') is not None else MIRROR_LABELS[lang][0],MIRROR_LABELS,0)
                row['frame'].configure(text=bt['map'].format(index=row['index']))
                for key,label in row['group_labels'].items():label.configure(text=bt[key])
                row['mode'].configure(values=[MODE_LABELS[lang][key] for key in MODE_ORDER]);row['mode_var'].set(MODE_LABELS[lang][mode])
                row['arch'].configure(values=[ARCHETYPE_LABELS[lang][key] for key in ARCHETYPE_ORDER]);row['arch_var'].set(ARCHETYPE_LABELS[lang][arch])
                if row.get('mirror') is not None:
                    row['mirror'].configure(values=list(MIRROR_LABELS[lang].values()),width=max(8,max((len(str(value)) for value in MIRROR_LABELS[lang].values()),default=0)+2));row['mirror_var'].set(MIRROR_LABELS[lang][mirror])
                row['modifier'].configure(values=[bt['none']]);row['modifier_var'].set(bt['none']);row['show'].configure(text=bt['show']);row['set_a'].configure(text=bt['set_a']);row['set_b'].configure(text=bt['set_b'])
                state=row.get('state','waiting');key='not_cached' if state=='not_cached' else ('cached' if row.get('cached') else ('success' if state=='success' else state))
                if key=='failed':text=bt['failed'].format(error=row.get('error',''))
                elif key in bt:text=bt[key]
                else:text=bt['waiting']
                if row.get('viability_warning') and key in ('success','cached'):
                    try:warning_side=int(row['size_var'].get())
                    except (TypeError,ValueError,tk.TclError):warning_side=0
                    if warning_side:
                        warning_text_key='extended_size_warning' if row.get('size_warning_kind')=='extended' else 'small_size_warning'
                        text=f"{text} · {bt[warning_text_key].format(side=warning_side,max_players=NATIVE_LIMITS[warning_side])}"
                row['status_var'].set(text);self._batch_draw_progress(row)
            self._batch_start_button.configure(text=bt['start']);self._batch_cancel_button.configure(text=bt['cancel']);self._batch_close_button.configure(text=bt['close'])
            self._refresh_batch_assignment_buttons()
        except tk.TclError:pass

    def _batch_update_row_visibility(self):
        if self._batch_running:return
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError,tk.TclError):return
        for i,row in enumerate(self._batch_rows):
            if i<count:row['frame'].grid()
            else:row['frame'].grid_remove()

    def _batch_count_typed(self,event=None):
        try:count=int(self._batch_count_var.get())
        except (TypeError,ValueError,tk.TclError):return
        if 1<=count<=4:self._batch_update_row_visibility()

    def _batch_commit_count(self,event=None):
        try:count=int(self._batch_count_var.get())
        except (TypeError,ValueError,tk.TclError):count=1
        self._batch_count_var.set(str(max(1,min(4,count))));self._batch_update_row_visibility()

    def _batch_row_size_changed(self,row):
        try:side=int(row['size_var'].get());maximum=NATIVE_LIMITS[side];row['players'].configure(to=maximum)
        except (TypeError,ValueError,KeyError):return
        try:
            if int(row['players_var'].get())>maximum:row['players_var'].set(str(maximum))
        except (TypeError,ValueError):pass

    def _batch_randomize_row(self,row):row['seed_var'].set(str(random.randint(1,2_147_483_647)))

    def _batch_randomize_seeds(self):
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError):count=1
        for row in self._batch_rows[:count]:self._batch_randomize_row(row)

    def _batch_collect_requests(self):
        lang=self.prefs.get('language','fr');errors=[];requests=[]
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError):count=1
        for row in self._batch_rows[:count]:
            error=None
            row['viability_warning']=False
            row['size_warning_kind']=None
            try:side=int(row['size_var'].get())
            except (TypeError,ValueError):side=0
            mode=self._batch_label_key(row['mode_var'].get(),MODE_LABELS,'legacy')
            archetype=self._batch_label_key(row['arch_var'].get(),ARCHETYPE_LABELS,'continental')
            mirror=self._batch_label_key(row.get('mirror_var').get() if row.get('mirror_var') is not None else MIRROR_LABELS[lang][0],MIRROR_LABELS,0)
            try:players=int(row['players_var'].get())
            except (TypeError,ValueError):players=0
            try:seed=int(row['seed_var'].get())
            except (TypeError,ValueError):seed=None
            if side not in NATIVE_LIMITS:error=BATCH_TEXT[lang]['unsupported_size']
            elif not MODES[mode].implemented:error=BATCH_TEXT[lang]['unsupported_mode']
            elif not ARCHETYPES[archetype].implemented:error=BATCH_TEXT[lang]['unsupported_archetype']
            elif mode!='legacy' and side!=768:error=BATCH_TEXT[lang]['unsupported_mode_size']
            elif mirror and not (mode=='legacy' and archetype=='continental'):error=BATCH_TEXT[lang]['unsupported_mirror']
            elif not 2<=players<=NATIVE_LIMITS[side]:error=BATCH_TEXT[lang]['invalid_players'].format(maximum=NATIVE_LIMITS[side])
            elif seed is None:error=BATCH_TEXT[lang]['invalid_seed']
            if error:
                errors.append(BATCH_TEXT[lang]['invalid_row'].format(index=row['index'],error=error));continue
            revision='continental_legacy_native_content' if mode=='legacy' and archetype=='continental' else 'v1.5-stable'
            key=GenerationCacheKey(seed=seed,side=side,players=players,mode=mode,archetype=archetype,modifiers=(),engine_revision=revision,mirror_mode=mirror)
            row['size_warning_kind']=native_size_warning_kind(side) if mode=='legacy' and archetype=='continental' else None
            row['viability_warning']=row['size_warning_kind'] is not None
            requests.append({'row':row,'key':key})
        if errors:raise ValueError('\n'.join(errors))
        return requests

    def _batch_set_running_controls(self,running):
        state='disabled' if running else 'normal';self.batch_generate_button.configure(state=state)
        self._batch_count_spin.configure(state=state);self._batch_randomize_button.configure(state=state)
        self._batch_common_seed_entry.configure(state=state);self._batch_common_seed_random.configure(state=state);self._batch_apply_seed_button.configure(state=state)
        self._batch_start_button.configure(state=state);self._batch_cancel_button.configure(state='normal' if running else 'disabled')
        for row in self._batch_rows:
            for widget,normal_state in row['input_widgets']:widget.configure(state='disabled' if running else normal_state)

    def _start_batch(self):
        if self._batch_running:return
        try:requests=self._batch_collect_requests()
        except ValueError as exc:
            messagebox.showerror(self._batch_text('invalid_title'),str(exc),parent=self._batch_window);return
        if not self._confirm_batch_cache_capacity(requests):return
        self._batch_queue=list(requests);self._batch_active_count=len(requests);self._batch_running=True;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None
        for request in requests:
            row=request['row'];row['result']=None;row['cached']=False;row['error']='';row.pop('history_key',None);row.pop('preview_image',None);row.pop('thumbnail_photo',None);row.pop('thumbnail_base_image',None);row['thumbnail'].configure(image='',text=str(row['index']))
            self._batch_update_progress(row,0,self._batch_text('waiting'),'waiting')
            row['show'].configure(state='disabled');row['set_a'].configure(state='disabled');row['set_b'].configure(state='disabled')
        self._batch_set_running_controls(True);self._batch_summary_var.set(self._batch_text('running',current=1,total=len(requests)))
        self.after(20,self._batch_run_next)

    def _confirm_batch_cache_capacity(self,requests):
        forecast=self._batch_cache_capacity_forecast(requests)
        if forecast['existing_evicted']==0 and forecast['batch_dropped']==0:return True
        return self._show_batch_cache_warning(forecast)

    def _batch_cache_capacity_forecast(self,requests):
        """Simulate generation plus final re-touch without mutating the real LRU."""
        entries=self.session_cache.entries();original_keys=[key for key,_ in entries]
        simulated={key:value for key,value in reversed(entries)};capacity=self.session_cache.max_entries
        protected_ids={id(value) for value in (getattr(self,'current',None),self._compare_slots.get('A'),self._compare_slots.get('B'),*self._manual_history_locks) if value is not None and any(cached is value for cached in simulated.values())}
        requested_keys=[request['key'] for request in requests];requested_values={};last_value=None
        def trim(fallback_key=None):
            while len(simulated)>capacity:
                victim=next((key for key,value in simulated.items() if id(value) not in protected_ids),None)
                if victim is None and fallback_key in simulated:victim=fallback_key
                if victim is None:victim=next(iter(simulated),None)
                if victim is None:break
                simulated.pop(victim,None)
        for key in requested_keys:
            is_new=key not in simulated
            if not is_new:value=simulated.pop(key)
            elif key in requested_values:value=requested_values[key]
            else:value=object()
            requested_values.setdefault(key,value);simulated[key]=value;last_value=value;trim(key if is_new else None)
        if getattr(self,'current',None) is None and last_value is not None:protected_ids.add(id(last_value))
        for key in requested_keys:
            value=requested_values[key];is_new=key not in simulated;simulated.pop(key,None);simulated[key]=value;trim(key if is_new else None)
        final_keys=set(simulated);unique_requested=list(dict.fromkeys(requested_keys))
        existing_evicted=sum(key not in final_keys for key in original_keys)
        batch_dropped=sum(key not in final_keys for key in unique_requested)
        return {'used':len(entries),'capacity':capacity,'requested':len(unique_requested),'retained':len(unique_requested)-batch_dropped,'protected':len(protected_ids),'existing_evicted':existing_evicted,'batch_dropped':batch_dropped}

    def _show_batch_cache_warning(self,forecast):
        lang=self.prefs.get('language','fr');text=_BATCH_CAPACITY_TEXT[lang];result={'continue':False}
        parent=self._batch_window or self;win=tk.Toplevel(parent);win.withdraw();win.title(text['title']);win.transient(parent);win.resizable(False,False)
        colors=getattr(self,'_ui_theme_colors',THEME_PALETTES.get(self.prefs.get('theme','dark'),THEME_PALETTES['dark']));win.configure(background=colors.get('window','#202124'))
        shell=ttk.Frame(win,padding=16);shell.pack(fill='both',expand=True)
        ttk.Label(shell,text=text['title'],style='Section.TLabel').pack(anchor='w',fill='x',pady=(0,10))
        lines=[text['intro'].format(**forecast)]
        if forecast['existing_evicted']:lines.append(text['existing'].format(count=forecast['existing_evicted']))
        if forecast['batch_dropped']:lines.append(text['batch'].format(count=forecast['batch_dropped']))
        lines.extend((text['kept'],text['question']))
        ttk.Label(shell,text='\n\n'.join((lines[0],'\n'.join(lines[1:-2]),lines[-2],lines[-1])),justify='left',wraplength=520).pack(anchor='w',fill='x')
        buttons=ttk.Frame(shell);buttons.pack(fill='x',pady=(16,0))
        def close(accepted=False):
            result['continue']=bool(accepted)
            try:win.grab_release()
            except tk.TclError:pass
            win.destroy()
        ttk.Button(buttons,text=text['cancel'],command=lambda:close(False)).pack(side='right')
        ttk.Button(buttons,text=text['continue'],command=lambda:close(True)).pack(side='right',padx=(0,8))
        win.protocol('WM_DELETE_WINDOW',lambda:close(False));win.bind('<Escape>',lambda e:close(False),add='+');win.bind('<Return>',lambda e:close(True),add='+')
        win.update_idletasks();width=max(480,win.winfo_reqwidth());height=win.winfo_reqheight();screen_w=win.winfo_screenwidth();screen_h=win.winfo_screenheight()
        x=parent.winfo_rootx()+(parent.winfo_width()-width)//2;y=parent.winfo_rooty()+(parent.winfo_height()-height)//2;x=max(8,min(x,screen_w-width-8));y=max(8,min(y,screen_h-height-48));win.geometry(f'{width}x{height}+{x}+{y}')
        win.deiconify();win.lift();win.focus_force();win.grab_set();win.wait_window();return result['continue']

    def _batch_run_next(self):
        if not self._batch_running:return
        if self._batch_cancel_requested:
            while self._batch_queue:
                request=self._batch_queue.pop(0);row=request['row'];self._batch_update_progress(row,100,self._batch_text('cancelled'),'cancelled')
            self._finish_batch();return
        if not self._batch_queue:self._finish_batch();return
        request=self._batch_queue.pop(0);row=request['row'];key=request['key'];self._batch_active_row=row
        total=self._batch_active_count
        done=sum(1 for r in self._batch_rows[:total] if r['state'] in ('success','cached','failed','cancelled'))
        self._batch_summary_var.set(self._batch_text('running',current=min(total,done+1),total=total))
        self._batch_update_progress(row,2,self._batch_text('generating'),'running')
        try:
            out=self.session_cache.get(key);cached=out is not None
            if out is None:out=self.generator.generate(key.players,key.seed,mode=key.mode,archetype=key.archetype,side=key.side,mirror_mode=key.mirror_mode)
            self.session_cache.put(key,out);self.session_cache.set_metadata(key,{'origin':'batch'});row['history_key']=key;row['result']=out;row['cached']=cached;self._batch_last_success=out
            result_state='cached' if cached else 'success'
            result_text=self._batch_text(result_state)
            if row.get('viability_warning'):
                warning_text_key='extended_size_warning' if row.get('size_warning_kind')=='extended' else 'small_size_warning'
                result_text=f"{result_text} · {self._batch_text(warning_text_key,side=key.side,max_players=NATIVE_LIMITS[key.side])}"
            self._batch_update_progress(row,100,result_text,result_state);self._batch_render_thumbnail(row)
        except Exception as exc:
            row['error']=str(exc);self._batch_update_progress(row,100,self._batch_text('failed',error=str(exc)),'failed')
        finally:
            self._batch_active_row=None;self._refresh_history();self.after(30,self._batch_run_next)

    def _cancel_batch(self):
        if not self._batch_running:return
        self._batch_cancel_requested=True;self._batch_cancel_button.configure(state='disabled');self._batch_summary_var.set(self._batch_text('cancel_pending'))

    def _finish_batch(self):
        active=self._batch_rows[:self._batch_active_count]
        success=sum(row['state'] in ('success','cached') for row in active);failed=sum(row['state']=='failed' for row in active);cancelled=sum(row['state']=='cancelled' for row in active)
        self._batch_running=False;self._batch_active_row=None;self._batch_set_running_controls(False);self._batch_summary_var.set(self._batch_text('finished',success=success,failed=failed,cancelled=cancelled))
        for row in active:
            enabled='normal' if row['state'] in ('success','cached') and row.get('result') is not None else 'disabled'
            row['show'].configure(state=enabled);row['set_a'].configure(state=enabled);row['set_b'].configure(state=enabled)
        self._refresh_history();self._refresh_batch_assignment_buttons()
        if self._batch_last_success is not None:
            # Batch is a producer, not an implicit navigation command. It fills an
            # empty viewer for convenience, but never replaces an existing map.
            if self._batch_should_autodisplay():
                self.current=self._batch_last_success;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            # Re-touch successful rows under the final protection set so the
            # preflight forecast and the actual retained set follow the same rule.
            for row in active:
                key=row.get('history_key');out=row.get('result')
                if key is not None and out is not None:self.session_cache.put(key,out);self.session_cache.set_metadata(key,{'origin':'batch'})
            self._refresh_history()
        lost_ids=set()
        for row in active:
            out=row.get('result')
            if out is not None and row.get('state') in ('success','cached') and not self._output_in_history(out):
                lost_ids.add(id(out));self._batch_update_progress(row,100,self._batch_text('not_cached'),'not_cached')
        if lost_ids:self._batch_summary_var.set(self._batch_text('finished_retention',success=success,failed=failed,cancelled=cancelled,lost=len(lost_ids)))
        self._feedback('batch_done','success' if failed==0 and not lost_ids else 'warning',success=success,failed=failed,cancelled=cancelled)

    def _batch_should_autodisplay(self):
        return getattr(self,'current',None) is None

    def _batch_show_result(self,row):
        out=row.get('result')
        if out is None:return
        self.current=out;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)

    def _batch_assign_result(self,row,slot):
        out=row.get('result')
        if out is None:return
        action,other=self._set_compare_output(slot,out)
        key='moved' if action=='moved' else ('already_assigned' if action=='already' else 'assigned')
        values={'index':row['index'],'slot':slot}
        if other:values['other']=other
        self._batch_summary_var.set(self._batch_text(key,**values))

    def _close_batch_window(self):
        if self._batch_running:
            self._cancel_batch();self._batch_summary_var.set(self._batch_text('close_running'));return
        if self._batch_window is not None:
            try:self._batch_window.destroy()
            except tk.TclError:pass
        self._batch_cancel_hover_preview();self._batch_hide_preview_tooltip()
        self._batch_window=None;self._batch_rows=[];self.batch_generate_button.configure(state='normal')

    def _refresh_batch_assignment_buttons(self):
        lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang];ctx=_CONTEXT_TEXT[lang]
        for row in getattr(self,'_batch_rows',[]):
            out=row.get('result')
            show=row.get('show')
            if show is not None:
                active=out is not None and out is getattr(self,'current',None)
                try:show.configure(text=ctx['shown'] if active else bt['show'],image=self._compare_led_on if active else self._compare_led_off)
                except tk.TclError:pass
            for slot,key in (('A','set_a'),('B','set_b')):
                button=row.get(key)
                if button is not None:
                    active=out is not None and self._compare_slots.get(slot) is out
                    try:button.configure(text=ctx['assigned_a' if slot=='A' else 'assigned_b'] if active else bt['set_a' if slot=='A' else 'set_b'],image=self._compare_led_on if active else self._compare_led_off)
                    except tk.TclError:pass
