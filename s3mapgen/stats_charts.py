from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CHART_KEYS = (
    'terrain_families','mineral_stock','building_stones','vegetation','height','agriculture','nearest_starts'
)

CHART_LABELS = {
    'fr': {
        'terrain_families':'Familles de terrain','mineral_stock':'Stock minier','building_stones':'États des pierres de construction',
        'vegetation':'Végétation','height':'Distribution des hauteurs','agriculture':'Agriculture','nearest_starts':'Distances au plus proche adversaire',
    },
    'en': {
        'terrain_families':'Terrain families','mineral_stock':'Mining stock','building_stones':'Building stone states',
        'vegetation':'Vegetation','height':'Height distribution','agriculture':'Agriculture','nearest_starts':'Nearest opponent distance',
    },
}

# Kept centralized on purpose: the visual palette can be redesigned later without
# touching chart logic or statistics semantics.
CHART_THEME = {
    'dark': {'bg':(33,34,37),'fg':(235,235,235),'muted':(170,174,181),'grid':(72,74,80),'bar':(53,168,83)},
    'light': {'bg':(250,250,250),'fg':(32,33,36),'muted':(100,104,110),'grid':(218,220,224),'bar':(40,140,75)},
}

TERRAIN_CHART_ORDER = ('grass','mountain','desert','swamp','mud','shore','river','water')


def _font_candidates(bold=False):
    if bold:
        names = (
            r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\arialbd.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        )
    else:
        names = (
            r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Supplemental/Arial.ttf',
        )
    return names


def _font(size=14, bold=False):
    """Use a Unicode-capable system font without bundling font files."""
    for candidate in _font_candidates(bold):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                pass
    # Pillow may resolve these names through the local font subsystem.
    for candidate in ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf', 'arialbd.ttf' if bold else 'arial.ttf'):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _horizontal_bar_chart(items, title, width=900, height=520, dark=True, value_suffix=''):
    """Categories on Y, values on X: deliberately horizontal / landscape charts."""
    theme = CHART_THEME['dark' if dark else 'light']
    bg,fg,muted,grid,bar = (theme[k] for k in ('bg','fg','muted','grid','bar'))
    im = Image.new('RGB',(width,height),bg); d=ImageDraw.Draw(im)
    title_font=_font(18,bold=True); label_font=_font(12); value_font=_font(11)
    d.text((24,18),title,fill=fg,font=title_font)
    if not items:
        d.text((24,70),'—',fill=muted,font=label_font);return im

    left=max(190, min(280, width//3));right=70;top=68;bottom=46
    plot_w=max(10,width-left-right);plot_h=max(10,height-top-bottom)
    maxv=max(float(v) for _,v in items) or 1.0
    n=len(items);gap=max(4, min(10, plot_h//max(1,n)//3));bar_h=max(8,int((plot_h-gap*(n-1))/max(1,n)))

    # X/value grid helps compare lengths while keeping category labels flat on Y.
    for step in range(6):
        x=left+round(plot_w*step/5)
        d.line((x,top,x,top+plot_h),fill=grid,width=1)
        tick=maxv*step/5
        tick_txt=f'{tick:,.0f}'
        bbox=d.textbbox((0,0),tick_txt,font=value_font)
        d.text((x-(bbox[2]-bbox[0])//2,top+plot_h+8),tick_txt,fill=muted,font=value_font)

    for i,(label,value) in enumerate(items):
        y=top+i*(bar_h+gap)
        txt_label=str(label)
        d.text((20,y+max(0,(bar_h-12)//2)),txt_label[:34],fill=fg,font=label_font)
        x2=left+int(plot_w*float(value)/maxv)
        d.rectangle((left,y,max(left+1,x2),y+bar_h),fill=bar)
        txt=f"{value:,}{value_suffix}" if isinstance(value,int) else f"{value:.2f}{value_suffix}"
        tx=min(width-right-2, x2+7)
        bbox=d.textbbox((0,0),txt,font=value_font)
        if tx+bbox[2]-bbox[0] > width-8:
            tx=max(left+4,x2-(bbox[2]-bbox[0])-6)
        d.text((tx,y+max(0,(bar_h-11)//2)),txt,fill=fg,font=value_font)
    d.line((left,top,left,top+plot_h),fill=grid,width=1)
    return im


def render_stats_chart(stats, chart_key='terrain_families', lang='fr', dark=True, width=900, height=520):
    labels=CHART_LABELS['en' if lang=='en' else 'fr']; fr=lang!='en'
    if chart_key=='terrain_families':
        by_key={r['key']:r for r in stats['terrain']['families']}
        rows=[by_key[k] for k in TERRAIN_CHART_ORDER if k in by_key]
        items=[(r['name_fr' if fr else 'name_en'],r['cells']) for r in rows]
    elif chart_key=='mineral_stock':
        items=[(v['name_fr' if fr else 'name_en'],v['stock']) for v in stats['resources']['minerals'].values()]
    elif chart_key=='building_stones':
        items=[(str(r['object_id']),r['anchors']) for r in stats['building_stones']['states'] if r['anchors']>0]
    elif chart_key=='vegetation':
        v=stats['vegetation']; names={
            'birch':('Bouleaux','Birch'),'elm':('Ormes','Elm'),'oak':('Chênes','Oak'),
            'other_adult':('Autres arbres adultes','Other adult trees'),'palm':('Palmiers','Palm')
        }
        items=[(names[k][0 if fr else 1],v['families'][k]) for k in ('birch','elm','oak','other_adult','palm')]
        items.append(("Pousses d’arbre" if fr else 'Tree saplings',v['saplings']))
    elif chart_key=='height':
        h=stats['height']['distribution']; keys=('min','p10','p25','median','p75','p90','p95','p99','max');items=[(k.upper(),float(h[k])) for k in keys]
    elif chart_key=='agriculture':
        ag=stats['agriculture'];items=[(('Blé' if fr else 'Wheat'),ag['wheat']),(('Vigne' if fr else 'Vine'),ag['vine']),(('Riz' if fr else 'Rice'),ag['rice'])]
    elif chart_key=='nearest_starts':
        items=[(f"P{r['player']}",r['distance']) for r in stats['players']['nearest_start']]
    else: items=[]
    return _horizontal_bar_chart(items,labels.get(chart_key,chart_key),width,height,dark)
