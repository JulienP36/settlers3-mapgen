"""Interactive map viewer controls, rendering and cell inspection."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from ..rendering.focus import apply_focus_overlay, focus_mask, focus_signature, focus_view
from ..rendering.preview import START_MARKER_SCALES, compose_rendered_map, render_square_base
from ..ui.i18n.common import _lang_text
from ..ui.i18n.shell import (
    PREVIEW_START_MARKER_LABELS,
    PROJECTION_LABELS,
    TEXTS,
)
from ..ui.i18n.viewer import HEATMAP_LABELS, VIEW_LABELS
from ..ui.viewer import (
    localized_object_name,
    localized_resource_text,
    localized_terrain_name,
)
from ..ui.viewer.options import VIEW_CHOICES
from ..ui.widgets import ColorMenuSelect, _selector_icon


class ViewerController:
    """Host contract: viewer widgets, current map and persisted preferences."""
    def _build_viewer_toolbar(self,top):
        """Build map-specific controls independently from the application header."""
        left=self.canvas.master
        self.viewer_toolbar=ttk.Frame(left,padding=(4,3))
        self.viewer_toolbar.pack(fill='x',before=self.canvas,pady=(0,3))
        self.viewer_toolbar.columnconfigure(1,weight=1)
        self._viewer_migrated_widgets=set()

        self.viewer_view_label=ttk.Label(self.viewer_toolbar,text='Vue')
        self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
        self._history_outside_icon=_selector_icon(self.viewer_toolbar,'#f2b84b','warning',20)
        self.history_residency_label=ttk.Label(self.viewer_toolbar,image='',cursor='hand2')
        self.history_residency_label.bind('<Button-1>',lambda e:self._history_residency_hint())
        self.history_residency_label.bind('<Enter>',lambda e:self._history_residency_tooltip())
        self.history_residency_label.bind('<Leave>',lambda e:self._hide_ui_tooltip())
        self._view_combo=ColorMenuSelect(self.viewer_toolbar,self.view,width=16,command=self._view_changed)
        self._view_combo.grid(row=0,column=2,sticky='ew',padx=(0,6))

        self.heatmap_title=ttk.Label(self.viewer_toolbar,text='Filtre carte thermique',compound='left')
        self.heatmap_title.grid(row=0,column=3,sticky='w',padx=(2,4))
        self.heatmap_combo=ColorMenuSelect(self.viewer_toolbar,self.heatmap_var,width=21,command=self._heatmap_changed)
        self.heatmap_combo.grid(row=0,column=4,padx=(0,6))

        self.viewer_recenter_button=ttk.Button(self.viewer_toolbar,text='Recentrer',command=self._reset_view)
        self.viewer_recenter_button.grid(row=0,column=5,padx=(0,8))
        self.viewer_zoom_label=ttk.Label(self.viewer_toolbar,text='Zoom')
        self.viewer_zoom_label.grid(row=0,column=6,sticky='w',padx=(0,4))
        self.zoom_scale=ttk.Scale(self.viewer_toolbar,from_=0.5,to=4.0,variable=self.zoom_var,command=lambda v:self._zoom_changed())
        self.zoom_scale.grid(row=0,column=7,sticky='ew');self.viewer_toolbar.columnconfigure(7,weight=1,minsize=90)
        self._bind_scale_jump(self.zoom_scale,self.zoom_var,.5,4.0,self._zoom_changed)
        self.viewer_toolbar.bind('<Configure>',self._apply_viewer_toolbar_layout,add='+')

    def _apply_viewer_toolbar_layout(self,event=None):
        """Reflow viewer-specific tools independently from the global header."""
        if not hasattr(self,'viewer_toolbar'):return
        try:width=int(self.viewer_toolbar.winfo_width())
        except tk.TclError:return
        compact=width<720
        mode='compact' if compact else 'wide'
        if getattr(self,'_viewer_toolbar_mode',None)==mode:return
        self._viewer_toolbar_mode=mode
        widgets=(self.viewer_view_label,self.history_residency_label,self._view_combo,self.heatmap_title,self.heatmap_combo,self.viewer_recenter_button,self.viewer_zoom_label,self.zoom_scale)
        for w in widgets:
            try:w.grid_forget()
            except tk.TclError:pass
        for c in range(8):self.viewer_toolbar.columnconfigure(c,weight=0,minsize=0)
        if compact:
            self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
            self.history_residency_label.grid(row=0,column=1,padx=(0,4))
            self._view_combo.grid(row=0,column=2,sticky='ew',padx=(0,6))
            self.viewer_recenter_button.grid(row=0,column=3,padx=(0,4))
            self.heatmap_title.grid(row=1,column=0,sticky='w',padx=(0,4),pady=(3,0))
            self.heatmap_combo.grid(row=1,column=2,sticky='ew',padx=(0,6),pady=(3,0))
            self.viewer_zoom_label.grid(row=1,column=3,sticky='w',padx=(0,4),pady=(3,0))
            self.zoom_scale.grid(row=1,column=4,sticky='ew',pady=(3,0))
            self.viewer_toolbar.columnconfigure(2,weight=0);self.viewer_toolbar.columnconfigure(4,weight=1,minsize=80)
        else:
            self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
            self.history_residency_label.grid(row=0,column=1,padx=(0,4))
            self._view_combo.grid(row=0,column=2,sticky='ew',padx=(0,6))
            self.heatmap_title.grid(row=0,column=3,sticky='w',padx=(2,4))
            self.heatmap_combo.grid(row=0,column=4,padx=(0,6))
            self.viewer_recenter_button.grid(row=0,column=5,padx=(0,8))
            self.viewer_zoom_label.grid(row=0,column=6,sticky='w',padx=(0,4))
            self.zoom_scale.grid(row=0,column=7,sticky='ew')
            self.viewer_toolbar.columnconfigure(2,weight=0);self.viewer_toolbar.columnconfigure(7,weight=1,minsize=90)

    def _heatmap_locked_hint(self):
        if self._view_key()!='heatmap':self._feedback('heatmap_locked','info')

    def _opacity_locked_hint(self,event=None):
        if self._view_key()=='global':self._feedback('opacity_locked','info');return 'break'

    def _projection_key(self):
        value=self.projection_var.get()
        for labels in PROJECTION_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('projection','square')

    def _preview_marker_key(self):
        value=self.preview_marker_var.get() if hasattr(self,'preview_marker_var') else ''
        for labels in PREVIEW_START_MARKER_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('preview_start_markers','small')

    def _view_key(self):
        value=self.view.get()
        for labels in VIEW_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return VIEW_CHOICES.get(value,'global')

    def _heatmap_key(self):
        value=self.heatmap_var.get() if hasattr(self,'heatmap_var') else 'Arbres'
        for labels in HEATMAP_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return 'trees'

    def _projection_changed(self):
        self.prefs['projection']=self._projection_key();self._save_prefs();self._refresh_preview(False);self._refresh_batch_previews();self._refresh_history_preview()

    def _preview_marker_changed(self):
        self.prefs['preview_start_markers']=self._preview_marker_key();self._save_prefs();self._refresh_preview(False);self._refresh_batch_previews();self._refresh_history_preview()

    def _opacity_changed(self):
        self.opacity_label.configure(text=f'{int(self.opacity_var.get())} %');self.prefs['overlay_alpha']=int(self.opacity_var.get());self._schedule_prefs_save()
        if self._view_key()=='starts':self._invalidate_preview_composite()
        else:self._invalidate_preview()
        self._schedule_preview()

    def _wheel_changed(self):
        self.wheel_label.configure(text=f'×{self.wheel_var.get():.2f}');self.prefs['wheel_zoom']=float(self.wheel_var.get());self._schedule_prefs_save()

    def _update_view_controls(self):
        view=self._view_key();lang=self.prefs.get('language','fr')
        if hasattr(self,'opacity_scale'):self.opacity_scale.configure(state='disabled' if view=='global' else 'normal')
        if hasattr(self,'heatmap_combo'):
            locked=view!='heatmap';self.heatmap_combo.set_enabled(not locked)
            if hasattr(self,'heatmap_title'):self.heatmap_title.configure(text='Filtre carte thermique' if lang=='fr' else TEXTS['Filtre carte thermique'].get(lang,TEXTS['Filtre carte thermique']['en']),image=self._lock_closed_icon if locked else self._lock_open_icon)

    def _view_changed(self):self._update_view_controls();self._refresh_preview(False)

    def _heatmap_changed(self):self._refresh_preview(False)

    def _reset_view(self):self.zoom_var.set(1.0);self.zoom=1.0;self._refresh_preview(True);self._feedback('view_reset','info')

    def _render_options(self):
        view=self._view_key();marker_mode=self.prefs.get('preview_start_markers','small')
        return {'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),'projection':self.prefs['projection'],'heatmap_resource':self._heatmap_key(),'start_markers':bool(view=='starts' and marker_mode!='hidden'),'start_marker_scale':START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small'])}

    def _chart_focus_options(self, options):
        """Temporarily route the preview through the hovered chart semantic."""
        focus=None
        link_var=getattr(self,'stats_link_var',None)
        if link_var is not None and link_var.get():
            focus=getattr(self,'_chart_link_focus',None)
        if not focus:
            return options,None
        effective=dict(options);effective['view']=focus_view(focus);effective['overlay_alpha']=100
        return effective,focus

    def _capture_view_anchor(self):
        """Capture the map point currently at the centre of the canvas."""
        image=getattr(self,'_preview_base',None)
        factor=float(getattr(self,'_display_factor',0.0) or 0.0)
        if image is None or factor<=0 or not hasattr(self,'canvas'):
            return None
        try:
            cw=max(100,int(self.canvas.winfo_width()));ch=max(100,int(self.canvas.winfo_height()))
            left=float(self.canvas.canvasx(0));top=float(self.canvas.canvasy(0))
        except (tk.TclError,TypeError,ValueError):
            return None
        origin=getattr(self,'_display_origin',(0,0));width,height=getattr(self,'_display_base_size',image.size)
        px=(left+cw/2-float(origin[0]))/factor;py=(top+ch/2-float(origin[1]))/factor
        return {'x':px,'y':py,'x_ratio':px/max(1.0,float(width)),'y_ratio':py/max(1.0,float(height)),'size':(int(width),int(height))}

    def _remember_view_anchor(self):
        anchor=self._capture_view_anchor()
        if anchor is not None and getattr(self,'_pending_view_anchor',None) is None:
            self._pending_view_anchor=anchor

    def _restore_view_anchor(self,anchor,image_size,origin,factor,cw,ch,scroll_width,scroll_height):
        """Move the canvas so the captured source point remains centred."""
        if not anchor:
            self.canvas.xview_moveto(0);self.canvas.yview_moveto(0);return
        old_size=tuple(anchor.get('size',(0,0)));new_size=tuple(image_size)
        if old_size==new_size:
            px=float(anchor.get('x',new_size[0]/2));py=float(anchor.get('y',new_size[1]/2))
        else:
            px=float(anchor.get('x_ratio',.5))*new_size[0];py=float(anchor.get('y_ratio',.5))*new_size[1]
        px=max(0.0,min(float(new_size[0]),px));py=max(0.0,min(float(new_size[1]),py))
        target_left=float(origin[0])+px*float(factor)-cw/2
        target_top=float(origin[1])+py*float(factor)-ch/2
        target_left=max(0.0,min(max(0.0,float(scroll_width-cw)),target_left))
        target_top=max(0.0,min(max(0.0,float(scroll_height-ch)),target_top))
        self.canvas.xview_moveto(target_left/max(1.0,float(scroll_width)));self.canvas.yview_moveto(target_top/max(1.0,float(scroll_height)))

    def _invalidate_preview(self):
        """Discard both the colorized square layer and its projected composites."""
        self._remember_view_anchor()
        self._preview_base=None;self._preview_key=None;self._preview_layer_base=None;self._preview_layer_key=None;self._preview_projection_cache={};self._preview_focus_mask_cache={}

    def _invalidate_preview_composite(self):
        """Keep the costly colorized layer and discard only cheap decorations."""
        self._remember_view_anchor()
        self._preview_base=None;self._preview_key=None;self._preview_projection_cache={}

    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        anchor=None if reset_pan else (getattr(self,'_pending_view_anchor',None) or self._capture_view_anchor())
        self._pending_view_anchor=None
        self._update_view_controls();opts=self._render_options();opts,focus=self._chart_focus_options(opts);state=self.current.state
        # Global and Starts share the same marker-free terrain raster.  Starts
        # opacity affects only its sprite layer, so changing it never recolors
        # the map.  Other overlays bake their opacity into the square layer.
        layer_view='global' if opts['view'] in ('global','starts') else opts['view']
        layer_alpha=100 if layer_view=='global' else opts['overlay_alpha']
        layer_key=(id(state),layer_view,layer_alpha,opts['heatmap_resource'])
        if layer_key!=self._preview_layer_key:
            if self._preview_layer_key is not None and self._preview_layer_key[0]!=id(state):
                self._preview_focus_mask_cache={}
            self._preview_layer_base=render_square_base(state,layer_view,layer_alpha,opts['heatmap_resource']);self._preview_layer_key=layer_key;self._preview_projection_cache={}
        composite_key=(opts['projection'],opts['view'],opts['overlay_alpha'],opts.get('start_markers'),opts.get('start_marker_scale'),focus_signature(focus))
        if composite_key not in self._preview_projection_cache:
            if focus is None:
                self._preview_projection_cache[composite_key]=compose_rendered_map(self._preview_layer_base,state,labels=True,view=opts['view'],overlay_alpha=opts['overlay_alpha'],projection=opts['projection'],start_markers=opts.get('start_markers'),start_marker_scale=opts.get('start_marker_scale',1))
            else:
                mask_key=(id(state),focus_signature(focus))
                mask=self._preview_focus_mask_cache.get(mask_key)
                if mask is None:
                    mask=focus_mask(state,focus);self._preview_focus_mask_cache[mask_key]=mask
                focused_base=apply_focus_overlay(self._preview_layer_base,state,focus,mask)
                self._preview_projection_cache[composite_key]=compose_rendered_map(focused_base,state,labels=True,view=opts['view'],overlay_alpha=opts['overlay_alpha'],projection=opts['projection'],start_markers=opts.get('start_markers'),start_marker_scale=opts.get('start_marker_scale',1),focus=focus)
        self._preview_base=self._preview_projection_cache[composite_key];self._preview_key=(layer_key,composite_key)
        im=self._preview_base;cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height());factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom);new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)))
        shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown);self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1]);x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2);self.canvas.create_image(x,y,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,sw,sh));self._restore_view_anchor(anchor,im.size,(x,y),new[0]/im.width,cw,ch,sw,sh)
        self._display_origin=(x,y);self._display_factor=new[0]/im.width;self._display_base_size=im.size

    def _source_cell_from_canvas(self,event):
        if not self.current or self._display_factor<=0:return None
        cx=self.canvas.canvasx(event.x);cy=self.canvas.canvasy(event.y);px=(cx-self._display_origin[0])/self._display_factor;py=(cy-self._display_origin[1])/self._display_factor;side=self.current.state.side
        if self.prefs.get('projection')=='parallelogram':
            y=int(py//2)
            if not 0<=y<side:return None
            shift=side-1-y;x=int((px-shift)//2)
        else:x=int(px);y=int(py)
        return (x,y) if 0<=x<side and 0<=y<side else None

    def _resource_text(self,terrain,raw):
        return localized_resource_text(terrain, raw, self.prefs.get('language', 'fr'))

    def _inspect_motion(self,event):
        cell=self._source_cell_from_canvas(event)
        if cell is None:return self._clear_inspector()
        x,y=cell;st=self.current.state;t=int(st.terrain[y,x]);o=int(st.objects[y,x]);r=int(st.resources[y,x]);h=int(st.height[y,x]);a=int(st.accessibility[y,x]);c=int(st.claim[y,x]);claim='—' if c==255 else f'P{c+1}'
        lang=self.prefs.get('language','fr')
        tname=localized_terrain_name(t, lang)
        oname=localized_object_name(o, lang)
        labels={'fr':('Terrain','Objet','Ressource','Hauteur','Accès','Territoire'),'en':('Terrain','Object','Resource','Height','Access','Claim'),'de':('Gelände','Objekt','Ressource','Höhe','Zugang','Territorium'),'es':('Terreno','Objeto','Recurso','Altura','Acceso','Territorio')}.get(lang,('Terrain','Object','Resource','Height','Access','Claim'))
        self.inspector_var.set(f'x={x}  y={y}  {labels[0]}={t} ({tname})  {labels[1]}={o} ({oname})  {labels[2]}={self._resource_text(t,r)}  {labels[3]}={h}  {labels[4]}={a}  {labels[5]}={claim}')

    def _clear_inspector(self):
        if hasattr(self,'inspector_var'):self.inspector_var.set(_lang_text(self.prefs.get('language','fr'),'Inspecteur : —','Inspector: —','Inspektor: —','Inspector: —'))
