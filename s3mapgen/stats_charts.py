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
    # headroom for total label
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
            if stacked:
                txt=_fmt(value);bb=d.textbbox((0,0),txt,font=small_font)
                if h>=18 and bb[2]-bb[0] <= bar_w-4:
                    d.text((int(cx-(bb[2]-bb[0])/2),int((ytop+ybase-(bb[3]-bb[1]))/2)),txt,fill=(20,20,20) if sum(color)>470 else (245,245,245),font=small_font)
                else:
                    # Never hide a non-zero segment: annotate it just outside the bar.
                    ym=int((ytop+ybase)/2);tx=x1+7
                    d.line((x1+1,ym,x1+5,ym),fill=color,width=1);d.text((tx,ym-6),txt,fill=fg,font=small_font)
            ybase=ytop
        if show_total and total>0:
            txt=_fmt(total);bb=d.textbbox((0,0),txt,font=value_font);d.text((int(cx-(bb[2]-bb[0])/2),max(top,int(ybase)-17)),txt,fill=fg,font=value_font)
        label=str(g['label']);swatches=g.get('swatches') or []
        if len(swatches)==2:
            sf=_font(9);parts=label.split('→');p1=parts[0].strip();p2=parts[1].strip() if len(parts)>1 else ''
            ylab=top+plot_h+10;w1=d.textbbox((0,0),p1,font=sf)[2];w2=d.textbbox((0,0),p2,font=sf)[2];totalw=8+4+w1+12+8+4+w2
            sx=int(cx-totalw/2);d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=swatches[0],outline=(20,20,20));sx+=12;d.text((sx,ylab-1),p1,fill=fg,font=sf);sx+=w1+3;d.text((sx,ylab-1),'→',fill=muted,font=sf);sx+=9;d.rectangle((sx,ylab+1,sx+7,ylab+8),fill=swatches[1],outline=(20,20,20));sx+=12;d.text((sx,ylab-1),p2,fill=fg,font=sf);continue
        bb=d.textbbox((0,0),label,font=label_font);shown=label
        if bb[2]-bb[0] > slot*0.92:
            short_font=_font(9);bb=d.textbbox((0,0),label,font=short_font)
            if bb[2]-bb[0] <= slot*0.96:
                d.text((int(cx-(bb[2]-bb[0])/2),top+plot_h+10),label,fill=fg,font=short_font);continue
            shown=label[:max(5,int(len(label)*slot*0.90/max(1,bb[2]-bb[0])))]+'…'
        bb=d.textbbox((0,0),shown,font=label_font);d.text((int(cx-(bb[2]-bb[0])/2),top+plot_h+10),shown,fill=fg,font=label_font)
    # legend only for actually named segment labels when there is more than one semantic segment
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



def build_ab_metrics(a,b,fr=True):
    """Build compact A/B comparison rows with semantic segment composition."""
    def ore_segments(st):
        return [(st['resources']['minerals'][key]['stock'],MINERAL_COLORS[key]) for key in ('coal','iron','gold','gems','sulfur')]

    def forest_segments(st):
        v=st['vegetation']
        return [(v['adult_wood_trees'],(45,125,60)),(v['families']['palm'],(155,175,65)),(v['saplings'],(105,205,90))]

    def water_segments(st):
        g=st['general'];return [(g.get('ocean_cells',0),WATER_COLORS[5]),(g.get('inland_water_cells',0),WATER_COLORS[1])]

    def mountain_segments(st):
        g=st['general'];return [(g.get('mountain_non_snow_cells',0),PALETTE.get(ROCKY,(109,109,103))),(g.get('snow_family_cells',0),(220,222,218))]

    def agri_segments(st):
        ag=st['agriculture'];return [(ag['wheat'],AGRI_COLORS['wheat']),(ag['vine'],AGRI_COLORS['vine']),(ag['rice'],AGRI_COLORS['rice'])]

    specs=[
        ('Terre' if fr else 'Land',lambda st:st['general']['land_cells'],lambda st:[(st['general']['land_cells'],PALETTE.get(GRASS,(72,148,69)))]),
        ('Eau' if fr else 'Water',lambda st:st['general']['water_cells'],water_segments),
        ('Montagne' if fr else 'Mountain',lambda st:st['general']['mountain_cells'],mountain_segments),
        ('Ressources forestières' if fr else 'Forestry resources',lambda st:sum(v for v,_ in forest_segments(st)),forest_segments),
        ('Stock pierre' if fr else 'Stone stock',lambda st:st['building_stones']['stock_total'],lambda st:[(st['building_stones']['stock_total'],(125,125,120))]),
        ('Stock minier' if fr else 'Mining stock',lambda st:sum(v for v,_ in ore_segments(st)),ore_segments),
        ('Stock poisson' if fr else 'Fish stock',lambda st:st['resources']['fish_stock'],lambda st:[(st['resources']['fish_stock'],WATER_COLORS[2])]),
        ('Agriculture',lambda st:sum(v for v,_ in agri_segments(st)),agri_segments),
    ]
    rows=[]
    for label,value_fn,segment_fn in specs:
        av,bv=value_fn(a),value_fn(b)
        rows.append((label,av,bv,segment_fn(a) if segment_fn else None,segment_fn(b) if segment_fn else None))
    return rows

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
        v=stats['vegetation'];items=[(('Arbres adultes' if fr else 'Adult trees'),v['adult_wood_trees']),(('Palmiers' if fr else 'Palms'),v['families']['palm']),(('Pousses' if fr else 'Saplings'),v['saplings'])]
        return _vertical_chart(_simple_groups(items,[(45,125,60),(155,175,65),(105,205,90)]),title,width,height,dark,'objets' if fr else 'objects')
    if chart_key=='height':
        h=stats['height'].get('land_distribution',stats['height']['distribution']);keys=('p10','p25','median','p75','p90','p95','p99','max');names=(('P10 bas','P25 bas','Médiane','P75 haut','P90 haut','P95 haut','P99 haut','Maximum') if fr else ('P10 low','P25 low','Median','P75 high','P90 high','P95 high','P99 high','Maximum'));items=[(names[i],float(h[k])) for i,k in enumerate(keys)]
        return _vertical_chart(_simple_groups(items,_gradient_colors(len(items),(226,236,220),(92,88,79))),title,width,height,dark,'hauteur' if fr else 'height')
    if chart_key=='agriculture':
        ag=stats['agriculture'];items=[(('Blé' if fr else 'Wheat'),ag['wheat']),(('Vigne' if fr else 'Vine'),ag['vine']),(('Riz' if fr else 'Rice'),ag['rice'])]
        return _vertical_chart(_simple_groups(items,[AGRI_COLORS['wheat'],AGRI_COLORS['vine'],AGRI_COLORS['rice']]),title,width,height,dark,'cases' if fr else 'cells')
    if chart_key=='nearest_starts':
        rows=stats['players']['nearest_start'];vals=[r['distance'] for r in rows];colors=_three_color_series(vals,zero_floor=False);groups=[]
        for i,r in enumerate(rows):
            opp=r.get('nearest_player');lab=f"P{r['player']} → P{opp}" if opp else f"P{r['player']}"
            g={'label':lab,'segments':[(r['distance'],colors[i],'')]}
            if opp:g['swatches']=[PLAYER_COLORS[(r['player']-1)%len(PLAYER_COLORS)],PLAYER_COLORS[(opp-1)%len(PLAYER_COLORS)]]
            groups.append(g)
        return _vertical_chart(groups,title,width,height,dark,'HEX')
    if chart_key in ('player_trees_r30','player_stone_r30','player_fish_r30'):
        key={'player_trees_r30':'trees','player_stone_r30':'stone','player_fish_r30':'fish'}[chart_key];raw=[]
        def metric(m):
            if key=='trees':return int(m.get('adult_trees',0)+m.get('saplings',0))
            return int(m.get('building_stone_stock',0) if key=='stone' else m.get('fish_stock',0))
        for row in stats.get('players',{}).get('local_resources',[]):
            near=metric(row['radii'].get('50',{}));total100=metric(row['radii'].get('100',{}));far=max(0,total100-near);raw.append((row['player'],near,far,total100))
        basecols=_three_color_series([r[3] for r in raw],zero_floor=True);groups=[]
        for i,(player,near,far,total) in enumerate(raw):
            c=basecols[i];groups.append({'label':f'P{player}','segments':[(near,c,'0–50 HEX'),(far,_lerp(c,(245,245,245),0.34),'50–100 HEX')]})
        return _vertical_chart(groups,title,width,height,dark,'stock' if key!='trees' else ('arbres' if fr else 'trees'))
    if chart_key=='player_mining_r40':
        groups=[]
        for row in stats.get('players',{}).get('local_resources',[]):
            r50=row['radii'].get('50',{}).get('minerals',{});r100=row['radii'].get('100',{}).get('minerals',{})
            near=[];far=[]
            for key in ('coal','iron','gold','gems','sulfur'):
                a=int(r50.get(key,{}).get('stock',0));b=max(0,int(r100.get(key,{}).get('stock',0))-a);label=stats['resources']['minerals'][key]['name_fr' if fr else 'name_en'];color=MINERAL_COLORS[key]
                near.append((a,color,label));far.append((b,color,label))
            groups.append({'label':f"P{row['player']} A",'segments':near});groups.append({'label':f"P{row['player']} B",'segments':far})
        return _vertical_chart(groups,title,width,height,dark,'stock · A≤50 / B 50–100')
    if chart_key in ('mountain_components','lake_components','river_components'):
        if chart_key=='mountain_components':vals=[r['cells'] for r in stats.get('spatial',{}).get('mountains',{}).get('components',[])[:20]]
        elif chart_key=='lake_components':vals=sorted(stats.get('hydrology',{}).get('inland_water_sizes',[]),reverse=True)[:20]
        else:vals=[r['cells'] for r in stats.get('hydrology',{}).get('river_details',[])[:20]]
        items=[(f'#{i+1}',v) for i,v in enumerate(vals)];base={'mountain_components':((75,75,72),(175,175,170)),'lake_components':((20,85,160),(125,205,245)),'river_components':((20,105,175),(115,210,235))}[chart_key]
        return _vertical_chart(_simple_groups(items,_gradient_colors(len(items),base[0],base[1])),title,width,height,dark,'cases' if fr else 'cells')
    if chart_key=='ab_summary':
        if not(compare_stats and len(compare_stats)==2 and all(compare_stats)):return _paired_ab_chart([],title,width,height,dark)
        a,b=compare_stats
        return _paired_ab_chart(build_ab_metrics(a,b,fr=fr),title,width,height,dark)
    return _vertical_chart([],title,width,height,dark)
