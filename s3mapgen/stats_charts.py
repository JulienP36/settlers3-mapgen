from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .preview import PALETTE, WATER_COLORS, PLAYER_COLORS
from .constants import GRASS, ROCKY, DESERT, SWAMP, SHORE

CHART_KEYS = (
    'terrain_families','mineral_stock','building_stones','forestry','height','agriculture','nearest_starts',
    'player_trees_r30','player_stone_r30','player_fish_r30','player_mining_r40',
    'mountain_components','lake_components','river_components','ab_summary'
)

CHART_LABELS = {
    'fr': {
        'terrain_families':'Familles de terrain','mineral_stock':'Stock minier','building_stones':'Stock des pierres de construction',
        'forestry':'Ressources forestières','height':'Distribution des hauteurs terrestres','agriculture':'Agriculture','nearest_starts':'Distances au plus proche adversaire',
        'player_trees_r30':'Arbres proches','player_stone_r30':'Pierres proches','player_fish_r30':'Poissons proches','player_mining_r40':'Stock minier proche',
        'mountain_components':'Taille des massifs','lake_components':'Taille des lacs','river_components':'Taille des rivières','ab_summary':'Comparaison A/B',
    },
    'en': {
        'terrain_families':'Terrain families','mineral_stock':'Mining stock','building_stones':'Building stone stock',
        'forestry':'Forestry resources','height':'Land height distribution','agriculture':'Agriculture','nearest_starts':'Nearest opponent distance',
        'player_trees_r30':'Nearby trees','player_stone_r30':'Nearby stone stock','player_fish_r30':'Nearby fish stock','player_mining_r40':'Nearby mining stock',
        'mountain_components':'Mountain sizes','lake_components':'Lake sizes','river_components':'River sizes','ab_summary':'A/B comparison',
    },
    'de': {
        'terrain_families':'Geländefamilien','mineral_stock':'Mineralvorrat','building_stones':'Bausteinvorrat',
        'forestry':'Forstressourcen','height':'Verteilung der Landhöhen','agriculture':'Landwirtschaft','nearest_starts':'Abstand zum nächsten Gegner',
        'player_trees_r30':'Bäume in der Nähe','player_stone_r30':'Steinvorrat in der Nähe','player_fish_r30':'Fischvorrat in der Nähe','player_mining_r40':'Mineralvorrat in der Nähe',
        'mountain_components':'Gebirgsgrößen','lake_components':'Seegrößen','river_components':'Flussgrößen','ab_summary':'A/B-Vergleich',
    },
    'es': {
        'terrain_families':'Familias de terreno','mineral_stock':'Reservas minerales','building_stones':'Reservas de piedra de construcción',
        'forestry':'Recursos forestales','height':'Distribución de alturas terrestres','agriculture':'Agricultura','nearest_starts':'Distancia al oponente más cercano',
        'player_trees_r30':'Árboles cercanos','player_stone_r30':'Piedra cercana','player_fish_r30':'Peces cercanos','player_mining_r40':'Minerales cercanos',
        'mountain_components':'Tamaño de macizos','lake_components':'Tamaño de lagos','river_components':'Tamaño de ríos','ab_summary':'Comparación A/B',
    },
}

CHART_THEME = {
    'dark': {'bg':(33,34,37),'fg':(235,235,235),'muted':(170,174,181),'grid':(72,74,80),'axis':(110,113,120)},
    'light': {'bg':(250,250,250),'fg':(32,33,36),'muted':(100,104,110),'grid':(218,220,224),'axis':(145,148,154)},
}

TERRAIN_COLORS = {
    'grass': PALETTE.get(GRASS,(72,148,69)),
    'mountain': PALETTE.get(ROCKY,(109,109,103)),
    'desert': PALETTE.get(DESERT,(211,177,80)),
    'swamp': PALETTE.get(SWAMP,(76,101,56)),
    'mud': (147,112,72),
    'shore': PALETTE.get(SHORE,(211,192,131)),
    'river': (38,145,196),
    'water': WATER_COLORS[4],
}
TERRAIN_CHART_ORDER = ('grass','mountain','desert','swamp','mud','shore','river','water')
MINERAL_COLORS = {'coal':(55,55,55),'iron':(255,148,0),'gold':(235,202,35),'gems':(206,0,0),'sulfur':(196,178,92)}
AGRI_COLORS = {'wheat':(235,205,75),'vine':(165,85,185),'rice':(80,205,110)}

DRY_GRASS = 24
TERRAIN_ID_GROUPS = {
    'grass_green': (16,), 'grass_dry': (24,),
    'rock_open': (17, 32, 33, 34), 'snow': (35, 128, 129),
    'desert': (20, 64, 65), 'swamp': (21, 80, 81), 'mud': (23, 144, 145),
    'shore': (48,), 'river': (96, 97, 98, 99), 'water': tuple(range(8)),
}
RESOURCE_IDS = {'coal':0x10,'iron':0x20,'gold':0x30,'gems':0x40,'sulfur':0x50}

TERRAIN_NAMES_I18N={
    'de':{'grass':'Gras','mountain':'Gebirge','desert':'Wüste','swamp':'Sumpf','mud':'Schlamm','shore':'Küste','river':'Fluss','water':'Wasser'},
    'es':{'grass':'Hierba','mountain':'Montaña','desert':'Desierto','swamp':'Pantano','mud':'Barro','shore':'Costa','river':'Río','water':'Agua'},
}
MINERAL_NAMES_I18N={
    'fr':{'coal':'Charbon','iron':'Fer','gold':'Or','gems':'Gemmes','sulfur':'Soufre'},
    'en':{'coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gems','sulfur':'Sulfur'},
    'de':{'coal':'Kohle','iron':'Eisen','gold':'Gold','gems':'Edelsteine','sulfur':'Schwefel'},
    'es':{'coal':'Carbón','iron':'Hierro','gold':'Oro','gems':'Gemas','sulfur':'Azufre'},
}


def _t(lang,fr,en,de,es):
    return {'fr':fr,'en':en,'de':de,'es':es}.get(lang,en)


def _compress_ids(ids):
    vals=sorted(set(int(v) for v in ids))
    if not vals:return '—'
    parts=[];start=prev=vals[0]
    for v in vals[1:]:
        if v==prev+1:prev=v;continue
        parts.append(str(start) if start==prev else f'{start}–{prev}');start=prev=v
    parts.append(str(start) if start==prev else f'{start}–{prev}')
    return ', '.join(parts)


def _id_line(kind, ids, fr=True, lang=None):
    lang=lang or ('fr' if fr else 'en')
    label={
        'terrain':_t(lang,'Terrain','Terrain','Gelände','Terreno'),
        'object':_t(lang,'Objet','Object','Objekt','Objeto'),
        'resource':_t(lang,'Ressource','Resource','Ressource','Recurso'),
    }[kind]
    vals=tuple(ids) if isinstance(ids,(tuple,list,range,set)) else (ids,)
    return f'{label} ID' + ('s' if len(set(vals))>1 else '') + f' : {_compress_ids(vals)}'


def _resource_id_line(name, rid, fr=True, lang=None):
    # Minerals are family values in the resource byte; display both decimal and hex.
    return f'{name} : ID {int(rid)} (0x{int(rid):02X})'


def _font_candidates(bold=False):
    if bold:
        return (r'C:\Windows\Fonts\segoeuib.ttf',r'C:\Windows\Fonts\arialbd.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    return (r'C:\Windows\Fonts\segoeui.ttf',r'C:\Windows\Fonts\arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/System/Library/Fonts/Supplemental/Arial.ttf')


def _font(size=14,bold=False):
    for candidate in _font_candidates(bold):
        if Path(candidate).exists():
            try:return ImageFont.truetype(candidate,size=size)
            except OSError:pass
    for candidate in ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf','arialbd.ttf' if bold else 'arial.ttf'):
        try:return ImageFont.truetype(candidate,size=size)
        except OSError:pass
    return ImageFont.load_default()


def _fmt(v):
    if isinstance(v,float) and not float(v).is_integer():return f'{v:,.1f}'
    return f'{int(round(float(v))):,}'


def _lerp(a,b,t):
    return tuple(int(round(x+(y-x)*t)) for x,y in zip(a,b))


def _gradient_colors(n,start,end):
    if n<=1:return [start]
    return [_lerp(start,end,i/(n-1)) for i in range(n)]

def _three_color_value(value,lo,mid,hi,low=(220,60,45),middle=(235,190,55),high=(45,170,75)):
    value=float(value);lo=float(lo);mid=float(mid);hi=float(hi)
    if hi<=lo:return high if hi>0 else low
    mid=max(lo,min(hi,mid))
    if value<=mid:
        span=max(1e-9,mid-lo);return _lerp(low,middle,(value-lo)/span)
    span=max(1e-9,hi-mid);return _lerp(middle,high,(value-mid)/span)

def _three_color_series(values,low=(220,60,45),middle=(235,190,55),high=(45,170,75),zero_floor=True):
    vals=[float(v) for v in values]
    if not vals:return []
    lo=0.0 if zero_floor else min(vals);hi=max(vals);mid=float(sorted(vals)[len(vals)//2])
    return [_three_color_value(v,lo,mid,hi,low,middle,high) for v in vals]


def _number_text(d,xy,text,font,anchor=None):
    """Chart value text: always white with a thin black outline for stable contrast."""
    kw={'fill':(248,248,248),'font':font,'stroke_width':1,'stroke_fill':(10,10,10)}
    if anchor:kw['anchor']=anchor
    d.text(xy,str(text),**kw)


def _vertical_chart(groups,title,width=900,height=520,dark=True,y_label=None,show_total=True,footer_note=None,legend_override=None,return_regions=False):
    """Vertical category chart with collision-aware external value annotations."""
    theme=CHART_THEME['dark' if dark else 'light'];bg,fg,muted,grid,axis=(theme[k] for k in ('bg','fg','muted','grid','axis'))
    im=Image.new('RGB',(width,height),bg);d=ImageDraw.Draw(im);regions=[]
    title_font=_font(18,True);label_font=_font(11);value_font=_font(10);small_font=_font(9)
    d.text((24,16),title,fill=fg,font=title_font)
    if not groups:
        d.text((24,65),'—',fill=muted,font=label_font);return (im,regions) if return_regions else im
    left=78;right=28;top=64;bottom=104
    plot_w=max(20,width-left-right);plot_h=max(20,height-top-bottom)
    totals=[sum(max(0,float(seg[0])) for seg in g['segments']) for g in groups]
    maxv=max(totals) or 1.0;max_axis=maxv*1.10
    for step in range(6):
        y=top+plot_h-round(plot_h*step/5);d.line((left,y,left+plot_w,y),fill=grid,width=1)
        tick=max_axis*step/5;txt=_fmt(tick);bbox=d.textbbox((0,0),txt,font=value_font)
        d.text((left-10-(bbox[2]-bbox[0]),y-(bbox[3]-bbox[1])//2),txt,fill=muted,font=value_font)
    d.line((left,top,left,top+plot_h),fill=axis,width=1);d.line((left,top+plot_h,left+plot_w,top+plot_h),fill=axis,width=1)
    if y_label:d.text((16,42),y_label,fill=muted,font=small_font)
    n=len(groups);slot=plot_w/max(1,n);bar_w=max(9,min(68,int(slot*0.56)))
    for i,g in enumerate(groups):
        cx=left+slot*(i+0.5);x0=int(cx-bar_w/2);x1=int(cx+bar_w/2);ybase=top+plot_h;total=totals[i]
        stacked=len([1 for seg in g['segments'] if float(seg[0])>0])>1
        external=[]
        for seg in g['segments']:
            value,color,seg_label=seg[:3];segment_details=list(seg[3]) if len(seg)>3 and seg[3] else []
            value=max(0,float(value))
            if value<=0:continue
            h=max(1,int(plot_h*value/max_axis));ytop=ybase-h;d.rectangle((x0,ytop,x1,ybase),fill=color)
            group_label=str(g.get('tooltip_label') or g.get('pair_label') or g.get('label') or '').strip()
            tooltip_label=str(seg_label or group_label or title).strip()
            if group_label and seg_label and group_label != seg_label: tooltip_label=f'{group_label} · {seg_label}'
            details_map=g.get('tooltip_details') or {};details=segment_details or list(details_map.get(seg_label, details_map.get('', [])))
            regions.append({'bbox':(x0,ytop,x1,ybase),'label':tooltip_label,'value':_fmt(value),'unit':str(y_label or '').strip(),'details':details})
            if stacked:
                txt=_fmt(value);bb=d.textbbox((0,0),txt,font=small_font);tw=bb[2]-bb[0]
                if h>=18 and tw<=bar_w-4:
                    _number_text(d,(int(cx),int((ytop+ybase)/2)),txt,small_font,anchor='mm')
                else:
                    external.append({'y':int((ytop+ybase)/2),'txt':txt,'color':color,'anchor_y':int((ytop+ybase)/2)})
            ybase=ytop
        # Place tiny-segment annotations in alternating side lanes and resolve vertical collisions.
        if external:
            external.sort(key=lambda e:e['y']);min_gap=13
            low=top+7;high=top+plot_h-7
            ys=[]
            for e in external:
                yy=max(low,min(high,e['y']));yy=max(yy,(ys[-1]+min_gap) if ys else low);ys.append(yy)
            overflow=ys[-1]-high
            if overflow>0:ys=[max(low,y-overflow) for y in ys]
            # final upward pass if the shift created a collision at the top
            for j in range(len(ys)-2,-1,-1):ys[j]=min(ys[j],ys[j+1]-min_gap)
            # DEV_9: always use the left annotation lane. Alternating left/right
            # made two neighboring bars point labels toward each other on dense charts.
            for e,yy in zip(external,ys):
                tx=x0-7
                d.line((x0-1,e['anchor_y'],x0-4,e['anchor_y'],tx+2,yy),fill=e['color'],width=1)
                _number_text(d,(tx,yy),e['txt'],small_font,anchor='rm')
        if show_total and total>0:
            _number_text(d,(int(cx),max(top+6,int(ybase)-8)),_fmt(total),value_font,anchor='ms')
        # Optional in-plot opponent annotation (keeps crowded x-axis labels short).
        if g.get('top_annotation'):
            ay=max(top+8,int(ybase)-28);ann=str(g['top_annotation']);sw=g.get('top_swatch')
            if sw:
                # DEV_9_R2: make the arrow clearly visible as an arrow, not a thin dash.
                # Keep the semantic order as requested: arrow -> opponent color -> opponent label.
                arrow='→';arrow_font=_font(15,True)
                aw=d.textbbox((0,0),arrow,font=arrow_font)[2];tw=d.textbbox((0,0),ann,font=small_font)[2]
                totalw=aw+4+8+4+tw;sx=int(cx-totalw/2)
                # Align the arrow's visual center with the 8px opponent-color square.
                ab=d.textbbox((0,0),arrow,font=arrow_font);ah=ab[3]-ab[1]
                arrow_y=ay-int(ah/2)-ab[1]
                _number_text(d,(sx,arrow_y),arrow,arrow_font);sx+=aw+4
                d.rectangle((sx,ay-4,sx+7,ay+3),fill=sw,outline=(15,15,15));sx+=12
                d.text((sx,ay-7),ann,fill=fg,font=small_font)
            else:d.text((int(cx),ay),ann,fill=fg,font=small_font,anchor='ms')
        label=str(g.get('label',''));swatches=g.get('swatches') or [];ylab=top+plot_h+11
        rank=g.get('medal_rank')
        if rank in (1,2,3):
            # Compact emoji-like podium label: '#'+medal replaces '#1/#2/#3'.
            medal=((218,172,35),(190,195,202),(176,112,64))[rank-1]
            ribbon=((230,72,62),(100,145,215))
            hash_font=_font(11);hash_w=d.textbbox((0,0),'#',font=hash_font)[2];icon_w=14
            sx=int(cx-(hash_w+3+icon_w)/2);d.text((sx,ylab-1),'#',fill=fg,font=hash_font);mx=sx+hash_w+3+icon_w//2;my=ylab+5
            # Two short ribbons and a round medal, kept entirely inside the x-label band.
            d.polygon((mx-5,my-5,mx-1,my-1,mx-4,my+7,mx-7,my+5),fill=ribbon[0])
            d.polygon((mx+5,my-5,mx+1,my-1,mx+4,my+7,mx+7,my+5),fill=ribbon[1])
            d.ellipse((mx-6,my-7,mx+6,my+5),fill=medal,outline=(45,45,45))
            d.text((mx,my-1),str(rank),fill=(25,25,25),font=_font(7,True),anchor='mm')
            label=''
        if len(swatches)==1:
            sf=_font(9);bb=d.textbbox((0,0),label,font=sf);tw=bb[2]-bb[0];sx=int(cx-(tw+13)/2);d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=swatches[0],outline=(20,20,20));d.text((sx+12,ylab-1),label,fill=fg,font=sf)
        elif len(swatches)==2:
            sf=_font(9);parts=label.split('→');p1=parts[0].strip();p2=parts[1].strip() if len(parts)>1 else '';w1=d.textbbox((0,0),p1,font=sf)[2];w2=d.textbbox((0,0),p2,font=sf)[2];totalw=8+4+w1+12+8+4+w2;sx=int(cx-totalw/2);d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=swatches[0],outline=(20,20,20));sx+=12;d.text((sx,ylab-1),p1,fill=fg,font=sf);sx+=w1+3;d.text((sx,ylab-1),'→',fill=muted,font=sf);sx+=9;d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=swatches[1],outline=(20,20,20));sx+=12;d.text((sx,ylab-1),p2,fill=fg,font=sf)
        elif label:
            bb=d.textbbox((0,0),label,font=label_font);shown=label
            if bb[2]-bb[0]>slot*0.92:
                sf=_font(9);bb2=d.textbbox((0,0),label,font=sf)
                if bb2[2]-bb2[0]<=slot*0.96:d.text((int(cx-(bb2[2]-bb2[0])/2),ylab),label,fill=fg,font=sf);shown=None
                else:shown=label[:max(3,int(len(label)*slot*0.86/max(1,bb[2]-bb[0])))]+'…'
            if shown:
                bb=d.textbbox((0,0),shown,font=label_font);d.text((int(cx-(bb[2]-bb[0])/2),ylab),shown,fill=fg,font=label_font)
        if g.get('pair_label'):
            pcx=cx+slot/2;pl=str(g['pair_label']);sw=g.get('pair_swatch');bb=d.textbbox((0,0),pl,font=small_font);tw=bb[2]-bb[0];sx=int(pcx-(tw+(13 if sw else 0))/2)
            if sw:d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=sw,outline=(20,20,20));sx+=12
            d.text((sx,ylab-1),pl,fill=fg,font=small_font)
    legend=legend_override if legend_override is not None else []
    if legend_override is None:
        for g in groups:
            for seg in g['segments']:
                _v,c,l=seg[:3]
                if l and (l,c) not in legend:legend.append((l,c))
    if legend:
        x=left;y=height-29
        for label,color in legend[:8]:
            d.rectangle((x,y,x+10,y+10),fill=color);x+=14;d.text((x,y-2),label,fill=muted,font=small_font);x+=d.textbbox((0,0),label,font=small_font)[2]+14
            if x>width-170:break
    if footer_note:
        note=str(footer_note);bb=d.textbbox((0,0),note,font=small_font);d.text((width-28-(bb[2]-bb[0]),height-31),note,fill=muted,font=small_font)
    return (im,regions) if return_regions else im

def _paired_ab_chart(metrics,title,width=900,height=520,dark=True,return_regions=False):
    """One compact row per metric: label | A bar with value inside | B bar with value inside."""
    theme=CHART_THEME['dark' if dark else 'light'];bg,fg,muted,grid=(theme[k] for k in ('bg','fg','muted','grid'))
    im=Image.new('RGB',(width,height),bg);d=ImageDraw.Draw(im);regions=[]
    title_font=_font(18,True);label_font=_font(12);value_font=_font(10,True);small=_font(9)
    d.text((24,16),title,fill=fg,font=title_font)
    if not metrics:
        d.text((24,65),'—',fill=muted,font=label_font);return (im,regions) if return_regions else im
    left=155;right=28;top=68;bottom=24;plot_w=width-left-right;row_h=max(34,min(58,(height-top-bottom)//len(metrics)))
    half=(plot_w-18)//2
    d.text((left+half//2-6,48),'A',fill=muted,font=small);d.text((left+half+18+half//2-6,48),'B',fill=muted,font=small)
    for i,(label,av,bv,segments_a,segments_b) in enumerate(metrics):
        y=top+i*row_h;h=max(18,row_h-12);maxv=max(float(av),float(bv),1.0)
        d.text((16,y+max(0,(h-12)//2)),label,fill=fg,font=label_font)
        for side,(value,segs) in enumerate(((av,segments_a),(bv,segments_b))):
            bx=left+side*(half+18);bw=int(half*float(value)/maxv)
            if value>0:
                cursor=bx
                side_name='A' if side==0 else 'B'
                if segs:
                    total=sum(float(seg[0]) for seg in segs) or 1
                    for j,seg in enumerate(segs):
                        sv,c=seg[0],seg[1];seg_label=str(seg[2]).strip() if len(seg)>2 else '';details=list(seg[3]) if len(seg)>3 and seg[3] else []
                        sw=bw-cursor+bx if j==len(segs)-1 else int(bw*float(sv)/total)
                        x2=cursor+max(1,sw);d.rectangle((cursor,y,x2,y+h),fill=c)
                        tip_label=f'{side_name} · {label}' + (f' · {seg_label}' if seg_label else '')
                        regions.append({'bbox':(cursor,y,x2,y+h),'label':tip_label,'value':_fmt(sv),'unit':'','details':details});cursor=x2
                else:
                    d.rectangle((bx,y,bx+bw,y+h),fill=(65,135,220) if side==0 else (230,145,55))
                    regions.append({'bbox':(bx,y,bx+bw,y+h),'label':f'{side_name} · {label}','value':_fmt(value),'unit':''})
                txt=_fmt(value);bb=d.textbbox((0,0),txt,font=value_font)
                tx=bx+max(4,(bw-(bb[2]-bb[0]))//2);d.text((tx,y+(h-(bb[3]-bb[1]))//2),txt,fill=(248,248,248),font=value_font)
            d.rectangle((bx,y,bx+half,y+h),outline=grid,width=1)
    return (im,regions) if return_regions else im


def _simple_groups(items,colors=None):
    colors=colors or [(60,150,85)]*len(items)
    return [{'label':label,'segments':[(value,colors[i%len(colors)],'')]} for i,(label,value) in enumerate(items)]



def build_ab_metrics(a,b,fr=True,lang=None):
    """Build compact A/B comparison rows with semantic segment composition."""
    lang=lang or ('fr' if fr else 'en');fr=lang=='fr';tr=lambda a,b,c,d:_t(lang,a,b,c,d)
    def ore_segments(st):
        return [(st['resources']['minerals'][key]['stock'],MINERAL_COLORS[key],MINERAL_NAMES_I18N[lang][key],[_resource_id_line(MINERAL_NAMES_I18N[lang][key],RESOURCE_IDS[key],fr,lang)]) for key in ('coal','iron','gold','gems','sulfur')]

    def forest_segments(st):
        v=st['vegetation']
        return [(v['adult_wood_trees'],(45,125,60),tr('Arbres adultes','Adult trees','Ausgewachsene Bäume','Árboles adultos'),[_id_line('object',(68,69,70,71,72,73,74,75,76,77,80,81),fr,lang)]),(v['families']['palm'],(155,175,65),tr('Palmiers','Palms','Palmen','Palmeras'),[_id_line('object',(78,79),fr,lang)]),(v['saplings'],(105,205,90),tr('Pousses','Saplings','Setzlinge','Retoños'),[_id_line('object',(84,),fr,lang)])]

    def water_segments(st):
        g=st['general'];ids=[_id_line('terrain',TERRAIN_ID_GROUPS['water'],fr,lang)];return [(g.get('ocean_cells',0),WATER_COLORS[5],tr('Mer','Ocean','Meer','Océano'),ids),(g.get('inland_water_cells',0),WATER_COLORS[1],tr('Lacs','Lakes','Seen','Lagos'),ids)]

    def mountain_segments(st):
        g=st['general'];return [(g.get('mountain_non_snow_cells',0),PALETTE.get(ROCKY,(109,109,103)),tr('Roche','Rocky','Fels','Roca'),[_id_line('terrain',TERRAIN_ID_GROUPS['rock_open'],fr,lang)]),(g.get('snow_family_cells',0),(220,222,218),tr('Neige','Snow','Schnee','Nieve'),[_id_line('terrain',TERRAIN_ID_GROUPS['snow'],fr,lang)])]

    def agri_segments(st):
        ag=st['agriculture'];return [(ag['wheat'],AGRI_COLORS['wheat'],tr('Blé','Wheat','Weizen','Trigo'),[_id_line('object',range(85,94),fr,lang)]),(ag['vine'],AGRI_COLORS['vine'],tr('Vigne','Vine','Weinreben','Vid'),[_id_line('object',range(94,103),fr,lang)]),(ag['rice'],AGRI_COLORS['rice'],tr('Riz','Rice','Reis','Arroz'),[_id_line('object',range(103,111),fr,lang)])]

    specs=[
        (tr('Terre','Land','Land','Tierra'),lambda st:st['general']['land_cells'],lambda st:[(st['general']['land_cells'],PALETTE.get(GRASS,(72,148,69)),tr('Cases terrestres','Land cells','Landzellen','Celdas terrestres'))]),
        (tr('Eau','Water','Wasser','Agua'),lambda st:st['general']['water_cells'],water_segments),
        (tr('Montagne','Mountain','Gebirge','Montaña'),lambda st:st['general']['mountain_cells'],mountain_segments),
        (tr('Ressources forestières','Forestry resources','Forstressourcen','Recursos forestales'),lambda st:sum(seg[0] for seg in forest_segments(st)),forest_segments),
        (tr('Stock pierre','Stone stock','Steinvorrat','Reserva de piedra'),lambda st:st['building_stones']['stock_total'],lambda st:[(st['building_stones']['stock_total'],(125,125,120),tr('Pierre','Stone','Stein','Piedra'),[_id_line('object',range(115,128),fr,lang)])]),
        (tr('Stock minier','Mining stock','Mineralvorrat','Reservas minerales'),lambda st:sum(seg[0] for seg in ore_segments(st)),ore_segments),
        (tr('Stock poisson','Fish stock','Fischvorrat','Reserva de peces'),lambda st:st['resources']['fish_stock'],lambda st:[(st['resources']['fish_stock'],WATER_COLORS[2],tr('Poisson','Fish','Fisch','Pez'),[_id_line('resource',range(1,16),fr,lang)])]),
        (tr('Agriculture','Agriculture','Landwirtschaft','Agricultura'),lambda st:sum(seg[0] for seg in agri_segments(st)),agri_segments),
    ]
    rows=[]
    for label,value_fn,segment_fn in specs:
        av,bv=value_fn(a),value_fn(b)
        rows.append((label,av,bv,segment_fn(a) if segment_fn else None,segment_fn(b) if segment_fn else None))
    return rows

def render_stats_chart(stats,chart_key='terrain_families',lang='fr',dark=True,width=900,height=520,compare_stats=None,return_regions=False):
    lang=lang if lang in CHART_LABELS else 'en';labels=CHART_LABELS[lang];fr=lang=='fr';tr=lambda a,b,c,d:_t(lang,a,b,c,d);title=labels.get(chart_key,chart_key)
    if chart_key=='terrain_families':
        by_key={r['key']:r for r in stats['terrain']['families']};g=stats['general'];groups=[]
        for key in TERRAIN_CHART_ORDER:
            r=by_key.get(key)
            if not r:continue
            name=TERRAIN_NAMES_I18N.get(lang,{}).get(key,r['name_fr' if fr else 'name_en'])
            if key=='grass':
                green=g.get('green_grass_cells',r['cells']);dry=g.get('dry_grass_cells',0)
                green_label=tr('Herbe verte','Green grass','Grünes Gras','Hierba verde');dry_label=tr('Herbe sèche','Dry grass','Trockenes Gras','Hierba seca')
                groups.append({'label':name,'segments':[(green,TERRAIN_COLORS['grass'],green_label),(dry,(177,157,82),dry_label)],
                               'tooltip_details':{green_label:[_id_line('terrain',TERRAIN_ID_GROUPS['grass_green'],fr,lang)],dry_label:[_id_line('terrain',TERRAIN_ID_GROUPS['grass_dry'],fr,lang)]}})
            elif key=='water':
                sea=tr('Mer','Ocean','Meer','Océano');lakes=tr('Lacs','Lakes','Seen','Lagos');detail=[_id_line('terrain',TERRAIN_ID_GROUPS['water'],fr,lang)]
                groups.append({'label':name,'segments':[(g.get('ocean_cells',r['cells']),WATER_COLORS[5],sea),(g.get('inland_water_cells',0),WATER_COLORS[1],lakes)],'tooltip_details':{sea:detail,lakes:detail}})
            elif key=='mountain':
                rock=tr('Roche','Rocky','Fels','Roca');snow=tr('Neige','Snow','Schnee','Nieve')
                groups.append({'label':name,'segments':[(g.get('mountain_non_snow_cells',r['cells']),PALETTE.get(ROCKY,(109,109,103)),rock),(g.get('snow_family_cells',0),(220,222,218),snow)],'tooltip_details':{rock:[_id_line('terrain',TERRAIN_ID_GROUPS['rock_open'],fr,lang)],snow:[_id_line('terrain',TERRAIN_ID_GROUPS['snow'],fr,lang)]}})
            else:
                ids=TERRAIN_ID_GROUPS.get(key,())
                groups.append({'label':name,'segments':[(r['cells'],TERRAIN_COLORS[key],'')],'tooltip_details':{'':([_id_line('terrain',ids,fr,lang)] if ids else [])}})
        return _vertical_chart(groups,title,width,height,dark,tr('cases','cells','Zellen','celdas'),return_regions=return_regions)
    if chart_key=='mineral_stock':
        groups=[]
        for key,v in stats['resources']['minerals'].items():
            base=MINERAL_COLORS[key];snow=_lerp(base,(235,235,235),0.58)
            mineral_name=MINERAL_NAMES_I18N[lang][key];open_label=tr('Libre','Open','Frei','Libre');snow_label=tr('Sous neige','Snow-covered','Unter Schnee','Bajo nieve')
            groups.append({'label':mineral_name,'segments':[(v.get('open_stock',v['stock']),base,open_label),(v.get('snow_covered_stock',0),snow,snow_label)],
                           'tooltip_details':{open_label:[_resource_id_line(mineral_name,RESOURCE_IDS[key],fr,lang),_id_line('terrain',TERRAIN_ID_GROUPS['rock_open'],fr,lang)],snow_label:[_resource_id_line(mineral_name,RESOURCE_IDS[key],fr,lang),_id_line('terrain',TERRAIN_ID_GROUPS['snow'],fr,lang)]}})
        legend=[(MINERAL_NAMES_I18N[lang][k],MINERAL_COLORS[k]) for k in ('coal','iron','gold','gems','sulfur')]
        note=tr('Teinte claire = sous neige','Lighter shade = snow-covered','Heller Farbton = unter Schnee','Tono claro = bajo nieve')
        return _vertical_chart(groups,title,width,height,dark,tr('stock','stock','Vorrat','reserva'),footer_note=note,legend_override=legend,return_regions=return_regions)
    if chart_key=='building_stones':
        rows=[r for r in stats['building_stones']['states'] if r['anchors']>0];colors=[]
        for r in rows:
            u=r['units_each'];colors.append(_three_color_value(u,0,6,12,low=(220,60,45),middle=(235,190,55),high=(45,170,75)))
        items=[]
        for r in rows:
            u=r['units_each'];lab=(f'{u} '+tr('pierres','stones','Steine','piedras')) if u>1 else (tr('1 pierre','1 stone','1 Stein','1 piedra') if u==1 else tr('Épuisé','Exhausted','Erschöpft','Agotado'))
            items.append((lab,r['anchors']))
        groups=_simple_groups(items,colors)
        for group,row in zip(groups,rows):group['tooltip_details']={'':[_id_line('object',(row['object_id'],),fr,lang)]}
        return _vertical_chart(groups,title,width,height,dark,tr('piles','piles','Haufen','pilas'),return_regions=return_regions)
    if chart_key=='forestry':
        v=stats['vegetation'];items=[(tr('Arbres adultes','Adult trees','Ausgewachsene Bäume','Árboles adultos'),v['adult_wood_trees']),(tr('Palmiers','Palms','Palmen','Palmeras'),v['families']['palm']),(tr('Pousses','Saplings','Setzlinge','Retoños'),v['saplings'])]
        groups=_simple_groups(items,[(45,125,60),(155,175,65),(105,205,90)])
        ids=((68,69,70,71,72,73,74,75,76,77,80,81),(78,79),(84,))
        for group,obj_ids in zip(groups,ids):group['tooltip_details']={'':[_id_line('object',obj_ids,fr,lang)]}
        return _vertical_chart(groups,title,width,height,dark,tr('objets','objects','Objekte','objetos'),return_regions=return_regions)
    if chart_key=='height':
        h=stats['height'].get('land_distribution',stats['height']['distribution']);keys=('p10','p25','median','p75','p90','p95','p99','max');names=tuple(tr(a,b,c,d) for a,b,c,d in [('P10 bas','P10 low','P10 niedrig','P10 bajo'),('P25 bas','P25 low','P25 niedrig','P25 bajo'),('Médiane','Median','Median','Mediana'),('P75 haut','P75 high','P75 hoch','P75 alto'),('P90 haut','P90 high','P90 hoch','P90 alto'),('P95 haut','P95 high','P95 hoch','P95 alto'),('P99 haut','P99 high','P99 hoch','P99 alto'),('Maximum','Maximum','Maximum','Máximo')]);items=[(names[i],float(h[k])) for i,k in enumerate(keys)]
        return _vertical_chart(_simple_groups(items,_gradient_colors(len(items),(226,236,220),(92,88,79))),title,width,height,dark,tr('hauteur','height','Höhe','altura'),return_regions=return_regions)
    if chart_key=='agriculture':
        ag=stats['agriculture'];items=[(tr('Blé','Wheat','Weizen','Trigo'),ag['wheat']),(tr('Vigne','Vine','Weinreben','Vid'),ag['vine']),(tr('Riz','Rice','Reis','Arroz'),ag['rice'])]
        groups=_simple_groups(items,[AGRI_COLORS['wheat'],AGRI_COLORS['vine'],AGRI_COLORS['rice']])
        ids=(range(85,94),range(94,103),range(103,111))
        for group,obj_ids in zip(groups,ids):group['tooltip_details']={'':[_id_line('object',obj_ids,fr,lang)]}
        return _vertical_chart(groups,title,width,height,dark,tr('cases','cells','Zellen','celdas'),return_regions=return_regions)
    if chart_key=='nearest_starts':
        rows=stats['players']['nearest_start'];vals=[r['distance'] for r in rows];colors=_three_color_series(vals,zero_floor=False);groups=[]
        for i,r in enumerate(rows):
            opp=r.get('nearest_player');lab=f"P{r['player']}"
            g={'label':lab,'segments':[(r['distance'],colors[i],'')],'swatches':[PLAYER_COLORS[(r['player']-1)%len(PLAYER_COLORS)]]}
            if opp:
                g['top_annotation']=f"P{opp}";g['top_swatch']=PLAYER_COLORS[(opp-1)%len(PLAYER_COLORS)]
            groups.append(g)
        return _vertical_chart(groups,title,width,height,dark,'HEX',return_regions=return_regions)
    if chart_key in ('player_trees_r30','player_stone_r30','player_fish_r30'):
        key={'player_trees_r30':'trees','player_stone_r30':'stone','player_fish_r30':'fish'}[chart_key];raw=[]
        def metric(m):
            if key=='trees':return int(m.get('adult_trees',0)+m.get('saplings',0))
            return int(m.get('building_stone_stock',0) if key=='stone' else m.get('fish_stock',0))
        for row in stats.get('players',{}).get('local_resources',[]):
            near=metric(row['radii'].get('50',{}));total100=metric(row['radii'].get('100',{}));far=max(0,total100-near);raw.append((row['player'],near,far,total100))
        basecols=_three_color_series([r[3] for r in raw],zero_floor=True);groups=[]
        for i,(player,near,far,total) in enumerate(raw):
            c=basecols[i];groups.append({'label':f'P{player}','swatches':[PLAYER_COLORS[(player-1)%len(PLAYER_COLORS)]],'segments':[(near,c,'0–50 HEX'),(far,_lerp(c,(245,245,245),0.34),'50–100 HEX')]})
        note=tr('Foncé : 0–50 HEX · clair : 50–100 HEX','Dark: 0–50 HEX · light: 50–100 HEX','Dunkel: 0–50 HEX · hell: 50–100 HEX','Oscuro: 0–50 HEX · claro: 50–100 HEX')
        return _vertical_chart(groups,title,width,height,dark,tr('stock','stock','Vorrat','reserva') if key!='trees' else tr('arbres','trees','Bäume','árboles'),footer_note=note,legend_override=[],return_regions=return_regions)
    if chart_key=='player_mining_r40':
        groups=[]
        for row in stats.get('players',{}).get('local_resources',[]):
            r50=row['radii'].get('50',{}).get('minerals',{});r100=row['radii'].get('100',{}).get('minerals',{})
            near=[];far=[]
            for key in ('coal','iron','gold','gems','sulfur'):
                a=int(r50.get(key,{}).get('stock',0));b=max(0,int(r100.get(key,{}).get('stock',0))-a);label=MINERAL_NAMES_I18N[lang][key];color=MINERAL_COLORS[key]
                near.append((a,color,f'0–50 HEX · {label}',[_resource_id_line(label,RESOURCE_IDS[key],fr,lang)]));far.append((b,color,f'50–100 HEX · {label}',[_resource_id_line(label,RESOURCE_IDS[key],fr,lang)]))
            pnum=row['player'];groups.append({'label':'','segments':near,'pair_label':f'P{pnum}','tooltip_label':f'P{pnum}','pair_swatch':PLAYER_COLORS[(pnum-1)%len(PLAYER_COLORS)]});groups.append({'label':'','segments':far,'tooltip_label':f'P{pnum}'})
        legend=[(MINERAL_NAMES_I18N[lang][k],MINERAL_COLORS[k]) for k in ('coal','iron','gold','gems','sulfur')]
        note=tr('Barre gauche : 0–50 HEX · droite : 50–100 HEX','Left bar: 0–50 HEX · right: 50–100 HEX','Linker Balken: 0–50 HEX · rechter: 50–100 HEX','Barra izquierda: 0–50 HEX · derecha: 50–100 HEX')
        return _vertical_chart(groups,title,width,height,dark,tr('stock','stock','Vorrat','reserva'),footer_note=note,legend_override=legend,return_regions=return_regions)
    if chart_key in ('mountain_components','lake_components','river_components'):
        if chart_key=='mountain_components':vals=[r['cells'] for r in stats.get('spatial',{}).get('mountains',{}).get('components',[])[:20]]
        elif chart_key=='lake_components':vals=sorted(stats.get('hydrology',{}).get('inland_water_sizes',[]),reverse=True)[:20]
        else:vals=[r['cells'] for r in stats.get('hydrology',{}).get('river_details',[])[:20]]
        items=[(f'#{i+1}',v) for i,v in enumerate(vals)];base={'mountain_components':((75,75,72),(175,175,170)),'lake_components':((20,85,160),(125,205,245)),'river_components':((20,105,175),(115,210,235))}[chart_key]
        groups=_simple_groups(items,_gradient_colors(len(items),base[0],base[1]))
        for i,g in enumerate(groups[:3]):g['medal_rank']=i+1
        return _vertical_chart(groups,title,width,height,dark,tr('cases','cells','Zellen','celdas'),return_regions=return_regions)
    if chart_key=='ab_summary':
        if not(compare_stats and len(compare_stats)==2 and all(compare_stats)):return _paired_ab_chart([],title,width,height,dark,return_regions=return_regions)
        a,b=compare_stats
        return _paired_ab_chart(build_ab_metrics(a,b,fr=fr,lang=lang),title,width,height,dark,return_regions=return_regions)
    return _vertical_chart([],title,width,height,dark,return_regions=return_regions)
