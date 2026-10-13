"""Measure actual Tk requests and pack independent rows without fixed breakpoints."""
from tkinter import ttk, font


def content_width(widget):
    width=widget.winfo_width()
    canvas=getattr(widget,'_scroll_canvas',None)
    if canvas is not None and canvas.winfo_width()>1:
        width=min(width,canvas.winfo_width()) if width>1 else canvas.winfo_width()
    padding=tuple(int(value) for value in widget.tk.splitlist(widget.cget('padding')))
    if len(padding)==1:horizontal=padding[0]*2
    elif len(padding)==2:horizontal=padding[0]*2
    elif len(padding)>=3:horizontal=padding[0]+padding[2]
    else:horizontal=0
    return max(0,width-horizontal)


def natural_width(widget):
    requested=widget.winfo_reqwidth()
    if isinstance(widget,ttk.Button) and widget.cget('text'):
        width=widget.cget('width')
        if str(width) and int(width)>0:
            style=ttk.Style(widget)
            face=font.Font(widget,font=style.lookup(widget.cget('style') or 'TButton','font') or 'TkDefaultFont')
            requested+=face.measure(widget.cget('text'))-int(width)*face.measure('0')
    return max(1,requested)


def flow_rows(widgets, available, gap=0):
    rows=[];row=[];used=0
    for widget in widgets:
        width=widget.winfo_reqwidth()
        if row and used+gap+width>available:
            rows.append(row);row=[];used=0
        used+=width+(gap if row else 0);row.append(widget)
    if row:rows.append(row)
    return rows


def grid_independent_rows(parent, rows, widgets, hosts, *, gap=0, start_row=0):
    """Each row owns its columns: a wide item in another row cannot add a gap."""
    for (owner,_),host in hosts.items():
        if owner is parent:host.grid_remove()
    for row_index,keys in enumerate(rows):
        marker=(parent,tuple(keys))
        host=hosts.get(marker)
        if host is None:
            host=hosts[marker]=ttk.Frame(parent)
        host.grid(row=start_row+row_index,column=0,sticky='nw')
        for column,key in enumerate(keys):
            widgets[key].grid(in_=host,row=0,column=column,columnspan=1,sticky='nw',
                              padx=(0,gap if column<len(keys)-1 else 0))
            # grid(in_=...) changes the geometry master, not the Tk parent.
            # These sibling widgets predate the row host, which would cover
            # them unless their stacking order is restored after every reflow.
            widgets[key].lift(host)
