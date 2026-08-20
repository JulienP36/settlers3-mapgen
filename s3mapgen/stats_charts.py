from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .preview import PALETTE, WATER_COLORS
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
        'player_trees_r30':'Arbres proches — R30','player_stone_r30':'Stock pierre proche — R30','player_fish_r30':'Stock poisson proche — R30','player_mining_r40':'Stock minier proche — R40',
        'mountain_components':'Taille des massifs','lake_components':'Taille des lacs','river_components':'Taille des rivières','ab_summary':'Comparaison A/B',
    },
    'en': {
        'terrain_families':'Terrain families','mineral_stock':'Mining stock','building_stones':'Building stone stock',
        'forestry':'Forestry resources','height':'Land height distribution','agriculture':'Agriculture','nearest_starts':'Nearest opponent distance',
        'player_trees_r30':'Nearby trees — R30','player_stone_r30':'Nearby stone stock — R30','player_fish_r30':'Nearby fish stock — R30','player_mining_r40':'Nearby mining stock — R40',
        'mountain_components':'Mountain sizes','lake_components':'Lake sizes','river_components':'River sizes','ab_summary':'A/B comparison',
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


def _vertical_chart(groups,title,width=900,height=520,dark=True,y_label=None,show_total=True):
    """Vertical category chart. Each group is {'label': str, 'segments': [(value,color,label), ...]}.
    Segments are stacked, category labels are on X, numeric scale on Y.
    """
    theme=CHART_THEME['dark' if dark else 'light'];bg,fg,muted,grid,axis=(theme[k] for k in ('bg','fg','muted','grid','axis'))
    im=Image.new('RGB',(width,height),bg);d=ImageDraw.Draw(im)
    title_font=_font(18,True);label_font=_font(11);value_font=_font(10);small_font=_font(9)
    d.text((24,16),title,fill=fg,font=title_font)
    if not groups:
        d.text((24,65),'—',fill=muted,font=label_font);return im
    left=78;right=28;top=64;bottom=92
    plot_w=max(20,width-left-right);plot_h=max(20,height-top-bottom)
    totals=[sum(max(0,float(v)) for v,_c,_l in g['segments']) for g in groups]
    maxv=max(totals) or 1.0
    max_axis=maxv*1.10
    for step in range(6):
        y=top+plot_h-round(plot_h*step/5)
        d.line((left,y,left+plot_w,y),fill=grid,width=1)
        tick=max_axis*step/5
        txt=_fmt(tick);bbox=d.textbbox((0,0),txt,font=value_font)
        d.text((left-10-(bbox[2]-bbox[0]),y-(bbox[3]-bbox[1])//2),txt,fill=muted,font=value_font)
    d.line((left,top,left,top+plot_h),fill=axis,width=1);d.line((left,top+plot_h,left+plot_w,top+plot_h),fill=axis,width=1)
    if y_label:d.text((16,42),y_label,fill=muted,font=small_font)
    n=len(groups);slot=plot_w/max(1,n);bar_w=max(10,min(68,int(slot*0.62)))
    for i,g in enumerate(groups):
        cx=left+slot*(i+0.5);x0=int(cx-bar_w/2);x1=int(cx+bar_w/2)
        ybase=top+plot_h
        total=totals[i]
        stacked=len([1 for value,_color,_label in g['segments'] if float(value)>0])>1
        for value,color,seg_label in g['segments']:
            value=max(0,float(value))
            if value<=0:continue
            h=max(1,int(plot_h*value/max_axis));ytop=ybase-h
            d.rectangle((x0,ytop,x1,ybase),fill=color)
            if stacked and h>=18:
                txt=_fmt(value);bb=d.textbbox((0,0),txt,font=small_font)
                if bb[2]-bb[0] <= bar_w-4:d.text((int(cx-(bb[2]-bb[0])/2),int((ytop+ybase-(bb[3]-bb[1]))/2)),txt,fill=(20,20,20) if sum(color)>470 else (245,245,245),font=small_font)
            ybase=ytop
        if show_total and total>0:
            txt=_fmt(total);bb=d.textbbox((0,0),txt,font=value_font);d.text((int(cx-(bb[2]-bb[0])/2),max(top,int(ybase)-17)),txt,fill=fg,font=value_font)
        label=str(g['label']);bb=d.textbbox((0,0),label,font=label_font);shown=label
        if bb[2]-bb[0] > slot*0.92:
            short_font=_font(9);bb=d.textbbox((0,0),label,font=short_font)
            if bb[2]-bb[0] <= slot*0.96:
                d.text((int(cx-(bb[2]-bb[0])/2),top+plot_h+10),label,fill=fg,font=short_font);continue
            shown=label[:max(5,int(len(label)*slot*0.90/max(1,bb[2]-bb[0])))]+'…'
        bb=d.textbbox((0,0),shown,font=label_font);d.text((int(cx-(bb[2]-bb[0])/2),top+plot_h+10),shown,fill=fg,font=label_font)
    legend=[]
    for g in groups:
        for _v,c,l in g['segments']:
            if l and (l,c) not in legend:legend.append((l,c))
    if len(legend)>1 and len(legend)<=8:
        x=left;y=height-26
        for label,color in legend:
            d.rectangle((x,y,x+10,y+10),fill=color);x+=14;d.text((x,y-2),label,fill=muted,font=small_font);x+=d.textbbox((0,0),label,font=small_font)[2]+14
            if x>width-160:break
    return im


def _paired_ab_chart(metrics,title,width=900,height=520,dark=True):
    """One compact row per metric: label | A bar with value inside | B bar with value inside."""
    theme=CHART_THEME['dark' if dark else 'light'];bg,fg,muted,grid=(theme[k] for k in ('bg','fg','muted','grid'))
    im=Image.new('RGB',(width,height),bg);d=ImageDraw.Draw(im)
    title_font=_font(18,True);label_font=_font(12);value_font=_font(10,True);small=_font(9)
    d.text((24,16),title,fill=fg,font=title_font)
    if not metrics:
        d.text((24,65),'—',fill=muted,font=label_font);return im
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
                if segs:
                    total=sum(float(v) for v,_c in segs) or 1
                    for j,(sv,c) in enumerate(segs):
                        sw=bw-cursor+bx if j==len(segs)-1 else int(bw*float(sv)/total)
                        d.rectangle((cursor,y,cursor+max(1,sw),y+h),fill=c);cursor+=max(1,sw)
                else:d.rectangle((bx,y,bx+bw,y+h),fill=(65,135,220) if side==0 else (230,145,55))
                txt=_fmt(value);bb=d.textbbox((0,0),txt,font=value_font)
                tx=bx+max(4,(bw-(bb[2]-bb[0]))//2);d.text((tx,y+(h-(bb[3]-bb[1]))//2),txt,fill=(248,248,248),font=value_font)
            d.rectangle((bx,y,bx+half,y+h),outline=grid,width=1)
    return im


def _simple_groups(items,colors=None):
    colors=colors or [(60,150,85)]*len(items)
    return [{'label':label,'segments':[(value,colors[i%len(colors)],'')]} for i,(label,value) in enumerate(items)]


def render_stats_chart(stats,chart_key='terrain_families',lang='fr',dark=True,width=900,height=520,compare_stats=None):
    labels=CHART_LABELS['en' if lang=='en' else 'fr'];fr=lang!='en';title=labels.get(chart_key,chart_key)
    if chart_key=='terrain_families':
        by_key={r['key']:r for r in stats['terrain']['families']};g=stats['general'];groups=[]
        for key in TERRAIN_CHART_ORDER:
            r=by_key.get(key)
            if not r:continue
            name=r['name_fr' if fr else 'name_en']
            if key=='water':
                groups.append({'label':name,'segments':[(g.get('ocean_cells',r['cells']),WATER_COLORS[5],'Mer' if fr else 'Ocean'),(g.get('inland_water_cells',0),WATER_COLORS[1],'Lacs' if fr else 'Lakes')]})
            elif key=='mountain':
                groups.append({'label':name,'segments':[(g.get('mountain_non_snow_cells',r['cells']),PALETTE.get(ROCKY,(109,109,103)),'Roche' if fr else 'Rocky'),(g.get('snow_family_cells',0),(220,222,218),'Neige' if fr else 'Snow')]})
            else:groups.append({'label':name,'segments':[(r['cells'],TERRAIN_COLORS[key],'')]})
        return _vertical_chart(groups,title,width,height,dark,'cases' if fr else 'cells')
    if chart_key=='mineral_stock':
        groups=[]
        for key,v in stats['resources']['minerals'].items():
            base=MINERAL_COLORS[key];snow=_lerp(base,(235,235,235),0.58)
            groups.append({'label':v['name_fr' if fr else 'name_en'],'segments':[(v.get('open_stock',v['stock']),base,'Accessible' if fr else 'Open'),(v.get('snow_covered_stock',0),snow,'Sous neige' if fr else 'Snow-covered')]})
        return _vertical_chart(groups,title,width,height,dark,'stock')
    if chart_key=='building_stones':
        rows=[r for r in stats['building_stones']['states'] if r['anchors']>0];colors=[]
        for r in rows:
            u=r['units_each'];t=(12-u)/12
            colors.append(_lerp((45,170,75),(230,55,45),t))
        items=[]
        for r in rows:
            u=r['units_each'];lab=(f'{u} pierres' if fr else f'{u} stones') if u>1 else (("1 pierre" if fr else '1 stone') if u==1 else ('Épuisé' if fr else 'Exhausted'))
            items.append((lab,r['anchors']))
        return _vertical_chart(_simple_groups(items,colors),title,width,height,dark,'piles' if fr else 'piles')
    if chart_key=='forestry':
        v=stats['vegetation'];items=[(('Pousses' if fr else 'Saplings'),v['saplings']),(('Arbres adultes' if fr else 'Adult trees'),v['adult_wood_trees']),(('Palmiers' if fr else 'Palms'),v['families']['palm'])]
        return _vertical_chart(_simple_groups(items,[(105,205,90),(45,125,60),(155,175,65)]),title,width,height,dark,'objets' if fr else 'objects')
    if chart_key=='height':
        h=stats['height'].get('land_distribution',stats['height']['distribution']);keys=('p10','p25','median','p75','p90','p95','p99','max');items=[(k.upper(),float(h[k])) for k in keys]
        return _vertical_chart(_simple_groups(items,_gradient_colors(len(items),(226,236,220),(92,88,79))),title,width,height,dark,'hauteur' if fr else 'height')
    if chart_key=='agriculture':
        ag=stats['agriculture'];items=[(('Blé' if fr else 'Wheat'),ag['wheat']),(('Vigne' if fr else 'Vine'),ag['vine']),(('Riz' if fr else 'Rice'),ag['rice'])]
        return _vertical_chart(_simple_groups(items,[AGRI_COLORS['wheat'],AGRI_COLORS['vine'],AGRI_COLORS['rice']]),title,width,height,dark,'cases' if fr else 'cells')
    if chart_key=='nearest_starts':
        items=[(f"P{r['player']}",r['distance']) for r in stats['players']['nearest_start']];vals=[v for _,v in items];lo=min(vals) if vals else 0;hi=max(vals) if vals else 1
        colors=[_lerp((215,55,45),(50,170,75),0 if hi==lo else (v-lo)/(hi-lo)) for _,v in items]
        return _vertical_chart(_simple_groups(items,colors),title,width,height,dark,'HEX')
    if chart_key in ('player_trees_r30','player_stone_r30','player_fish_r30'):
        key={'player_trees_r30':'trees','player_stone_r30':'stone','player_fish_r30':'fish'}[chart_key];items=[]
        for row in stats.get('players',{}).get('local_resources',[]):
            m=row['radii'].get('30',{})
            value=int(m.get('adult_trees',0)+m.get('saplings',0)) if key=='trees' else int(m.get('building_stone_stock',0) if key=='stone' else m.get('fish_stock',0))
            items.append((f"P{row['player']}",value))
        vals=[v for _,v in items];lo=min(vals) if vals else 0;hi=max(vals) if vals else 1;colors=[_lerp((220,70,50),(45,170,75),0 if hi==lo else (v-lo)/(hi-lo)) for _,v in items]
        return _vertical_chart(_simple_groups(items,colors),title,width,height,dark,'stock' if key!='trees' else ('arbres' if fr else 'trees'))
    if chart_key=='player_mining_r40':
        groups=[]
        for row in stats.get('players',{}).get('local_resources',[]):
            m=row['radii'].get('40',{});segs=[]
            for key,v in m.get('minerals',{}).items():segs.append((v['stock'],MINERAL_COLORS.get(key,(100,100,100)),stats['resources']['minerals'][key]['name_fr' if fr else 'name_en']))
            groups.append({'label':f"P{row['player']}",'segments':segs})
        return _vertical_chart(groups,title,width,height,dark,'stock')
    if chart_key in ('mountain_components','lake_components','river_components'):
        if chart_key=='mountain_components':vals=[r['cells'] for r in stats.get('spatial',{}).get('mountains',{}).get('components',[])[:20]]
        elif chart_key=='lake_components':vals=sorted(stats.get('hydrology',{}).get('inland_water_sizes',[]),reverse=True)[:20]
        else:vals=[r['cells'] for r in stats.get('hydrology',{}).get('river_details',[])[:20]]
        items=[(f'#{i+1}',v) for i,v in enumerate(vals)];base={'mountain_components':((160,160,155),(75,75,72)),'lake_components':((105,190,240),(20,85,160)),'river_components':((90,195,225),(20,105,175))}[chart_key]
        return _vertical_chart(_simple_groups(items,_gradient_colors(len(items),base[0],base[1])),title,width,height,dark,'cases' if fr else 'cells')
    if chart_key=='ab_summary':
        if not(compare_stats and len(compare_stats)==2 and all(compare_stats)):return _paired_ab_chart([],title,width,height,dark)
        a,b=compare_stats
        def ore_total(st):return sum(v['stock'] for v in st['resources']['minerals'].values())
        metrics=[]
        raw=[('Terre' if fr else 'Land',a['general']['land_cells'],b['general']['land_cells']),('Montagne' if fr else 'Mountain',a['general']['mountain_cells'],b['general']['mountain_cells']),('Arbres adultes' if fr else 'Adult trees',a['vegetation']['adult_trees_including_palms'],b['vegetation']['adult_trees_including_palms']),('Stock pierre' if fr else 'Stone stock',a['building_stones']['stock_total'],b['building_stones']['stock_total']),('Stock minier' if fr else 'Mining stock',ore_total(a),ore_total(b)),('Stock poisson' if fr else 'Fish stock',a['resources']['fish_stock'],b['resources']['fish_stock'])]
        for label,av,bv in raw:metrics.append((label,av,bv,None,None))
        return _paired_ab_chart(metrics,title,width,height,dark)
    return _vertical_chart([],title,width,height,dark)
