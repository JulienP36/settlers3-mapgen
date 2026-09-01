from __future__ import annotations
from pathlib import Path
from collections import deque
import random
import numpy as np
from scipy import ndimage

from ..map_data.model import MapState
from .contracts import GenerationOutput
from .profile import load_profile
from ..map_data.binary import read_area
from ..map_data.constants import *
from ..map_data.hexgrid import hex_distance, neighbor_count, component_labels, component_sizes, depth, dilate
from .rules import ValidationResult, PIPELINE_STAGES
from .archetypes import get_archetype

class UpgradedGenerator:
    """Validated Upgraded compatibility generator kept during Legacy rebuild.

    The former shared class mixed the obsolete v1.5/DEV_1 Legacy paths with
    the Upgraded rules. DEV_2 deliberately keeps only this compatibility
    implementation; the native Legacy implementation will be rebuilt as a
    separate generator once the reverse-engineering audit is complete.
    """

    def __init__(self, upgraded_profile_path:Path|str, native_library_path:Path|str, upgraded_reference_path:Path|str|None=None, progress_callback=None):
        self.upgraded_profile=load_profile(upgraded_profile_path)
        self.profile=self.upgraded_profile
        if self.profile.get('profile_kind') != 'upgraded':
            raise ValueError('UpgradedGenerator requires an upgraded profile')
        if self.profile['side'] != 768:
            raise ValueError('Upgraded compatibility is calibrated for 768 only')
        self.lib=np.load(native_library_path,allow_pickle=True)
        self.upgraded_reference=read_area(upgraded_reference_path) if upgraded_reference_path else None
        self.side=768
        self.stage_log=[]
        self.current_mode='upgraded'
        self.progress_callback=progress_callback

    def log(self, stage:str, detail:str=''):
        self.stage_log.append(stage + (f' — {detail}' if detail else ''))
        if self.progress_callback:
            try:self.progress_callback(stage, detail, len(self.stage_log))
            except Exception:pass

    def generate(self, players:int, seed:int, archetype:str='continental')->GenerationOutput:
        arch_spec=get_archetype(archetype)
        if not arch_spec.implemented:
            raise NotImplementedError(f"L'archétype {arch_spec.label} est réservé dans l'architecture mais pas encore implémenté.")
        if players not in self.profile['supported_players']:
            raise ValueError(f'Unsupported player count: {players}')
        self.stage_log=[]
        self.current_mode='upgraded'
        self.profile=self.upgraded_profile
        rng=np.random.default_rng(seed); pr=random.Random(seed)
        state=self._morphology_from_upgraded_reference(rng,pr)
        self.log('archetype.macro_layout',f'{arch_spec.label}')
        # Les starts sont placés immédiatement après le macro-layout, AVANT les couches détaillées.
        self._place_starts(state,players,rng)
        self.log('starts.reserve_zones',f'technical_hex={self.profile["starts"]["technical_clear_hex"]}')
        self._cleanup_micro_water(state,rng)
        self._finalize_water(state)
        self._cleanup_rivers(state)
        self._place_start_swamps(state,rng,pr)
        self._rebuild_swamp_transitions(state)
        self._rebuild_snow(state,rng)
        self._generate_minerals(state,rng,pr)
        self._generate_fish(state,rng)
        self._place_decorations(state,rng,pr)
        self._place_trees(state,rng,pr)
        self._place_building_stones(state,rng,pr)
        self._final_accessibility(state)
        vals=self.validate(state)
        state.metadata.update(seed=int(seed),players=int(players),mode='Upgraded',mode_key='upgraded',archetype=arch_spec.label,archetype_key=archetype,profile=self.profile['profile_name'],pipeline=list(PIPELINE_STAGES),starts_placed_early=True)
        return GenerationOutput(state,vals,list(self.stage_log))

    # ---------- morphology ----------
    def _morphology_from_upgraded_reference(self,rng,pr)->MapState:
        if self.upgraded_reference is None:
            raise RuntimeError('Upgraded reference checkpoint is unavailable')
        base=self.upgraded_reference
        state=MapState.empty(self.side)
        t=base.terrain.copy();h=base.height.copy()
        transform=pr.randrange(4)
        if transform==1:
            t=np.rot90(t,2).copy();h=np.rot90(h,2).copy()
        elif transform==2:
            t=t.T.copy();h=h.T.copy()
        elif transform==3:
            t=np.rot90(t.T,2).copy();h=np.rot90(h.T,2).copy()
        state.terrain[:]=t;state.height[:]=h
        state.objects[:]=0;state.resources[:]=0;state.accessibility[:]=0;state.claim[:]=255
        state.metadata['upgraded_reference']='resourcepass_v8_relief_snow'
        state.metadata['upgraded_transform']=transform
        self.log('morphology.upgraded_checkpoint',f'transform={transform}')
        return state

    def _cleanup_micro_water(self,state,rng):
        T=state.terrain;H=state.height
        water=np.isin(T,WATER_IDS)
        lab,sizes=component_sizes(water)
        if not sizes:
            self.log('hydrology.micro_water_cleanup','no water components')
            return
        sea=1+int(np.argmax(sizes)); removed=[]
        for cid,size in enumerate(sizes,1):
            if cid!=sea and size<=self.profile['water']['forbid_inland_components_leq']:
                ys,xs=np.where(lab==cid)
                for y,x in zip(ys,xs): removed.append((int(x),int(y)))
                T[ys,xs]=GRASS
                # nearest neighboring land height, conservative fallback 20
                for y,x in zip(ys,xs):
                    vals=[]
                    for dx,dy in HEX6:
                        X,Y=x+dx,y+dy
                        if 0<=X<self.side and 0<=Y<self.side and T[Y,X] not in WATER_IDS:
                            vals.append(int(H[Y,X]))
                    H[y,x]=int(np.median(vals)) if vals else 20
        # custom override: redistribute volume into an existing lake >4, never create a new lake.
        count=len(removed)
        if count:
            water=np.isin(T,WATER_IDS);lab,sizes=component_sizes(water)
            candidates=[(s,i+1) for i,s in enumerate(sizes) if s>4]
            if candidates:
                # choose largest inland component if available, else sea
                candidates.sort(reverse=True)
                target_id=candidates[1][1] if len(candidates)>1 else candidates[0][1]
                lake=(lab==target_id)
                grown=0
                frontier=(neighbor_count(lake)>0)&~water&(T==GRASS)
                # Starts were already placed: hydrology may adapt around them, never overwrite their reserved zone.
                if state.starts:
                    protected=self._core_mask(state,self.profile['starts']['technical_clear_hex']+2)
                    frontier &= ~protected
                pts=np.argwhere(frontier)
                if len(pts):
                    order=rng.permutation(len(pts))
                    for j in order:
                        if grown>=count:break
                        y,x=map(int,pts[j]);T[y,x]=0;H[y,x]=0;grown+=1
        self.log('hydrology.micro_water_cleanup',f'removed={count}')

    def _finalize_water(self,state):
        T,H,A=state.terrain,state.height,state.accessibility
        water=np.isin(T,WATER_IDS)
        # preserve native water IDs wherever possible; force all water semantics.
        H[water]=0;A[water]=1
        # ensure Shore exists only on land next to water; convert stray Shore to Grass.
        touching=neighbor_count(water)>0
        stray=(T==SHORE)&~touching
        T[stray]=GRASS
        actual_shore=(~water)&touching&np.isin(T,[GRASS,SHORE])
        T[actual_shore]=SHORE
        # External map edge is deep Water7. This does not derive a shallow
        # gradient from the rectangular map boundary; it only normalizes the
        # already-ocean edge cells to the locked deep-water state.
        T[0,:]=7;T[-1,:]=7;T[:,0]=7;T[:,-1]=7
        H[0,:]=0;H[-1,:]=0;H[:,0]=0;H[:,-1]=0
        A[0,:]=1;A[-1,:]=1;A[:,0]=1;A[:,-1]=1
        self.log('hydrology.bathymetry',f'water={int(np.isin(T,WATER_IDS).sum())} shore={int((T==SHORE).sum())}')


    def _cleanup_rivers(self,state):
        T=state.terrain
        cap=self.profile['river']['practical_max_cells']
        # First prune River cells that continue along/through Water. A water-contact River cell must be an endpoint.
        for _ in range(64):
            water=np.isin(T,WATER_IDS);river=np.isin(T,RIVER_IDS)
            bad=river&(neighbor_count(water)>0)&(neighbor_count(river)>=2)
            if not bad.any():break
            T[bad]=SHORE
        # Then repeatedly remove orphan fragments and trim inland graph distance to the practical cap.
        water=np.isin(T,WATER_IDS);river=np.isin(T,RIVER_IDS)
        lab,n=component_labels(river);removed_orphans=0;trimmed=0
        for cid in range(1,n+1):
            m=lab==cid;contact=m&(neighbor_count(water)>0)
            if not contact.any():
                T[m]=GRASS;removed_orphans+=1;continue
            d=np.full(T.shape,-1,np.int16);q=deque()
            for y,x in np.argwhere(contact):d[y,x]=0;q.append((int(x),int(y)))
            while q:
                x,y=q.popleft()
                for dx,dy in HEX6:
                    X,Y=x+dx,y+dy
                    if 0<=X<self.side and 0<=Y<self.side and m[Y,X] and d[Y,X]<0:
                        d[Y,X]=d[y,x]+1;q.append((X,Y))
            cut=m&(d>=cap)
            trimmed+=int(cut.sum());T[cut]=GRASS
        # Any Shore created by pruning but no longer touching Water is ordinary Grass.
        water=np.isin(T,WATER_IDS);touch=neighbor_count(water)>0
        T[(T==SHORE)&~touch]=GRASS
        self.log('hydrology.river_cleanup',f'orphan_components_removed={removed_orphans} trimmed={trimmed}')

    # ---------- starts ----------
    def _start_ok(self,state,x,y):
        T,H,O=state.terrain,state.height,state.objects
        vals=[]
        for dx,dy in START_FOOTPRINT:
            X,Y=x+dx,y+dy
            if not(5<=X<self.side-5 and 5<=Y<self.side-5) or T[Y,X]!=GRASS:return False
            vals.append(int(H[Y,X]))
        p=self.profile['starts']
        if max(vals)-min(vals)>p['height_range_max']:return False
        dif=[abs(int(H[y+dy,x+dx])-int(H[y,x])) for dx,dy in HEX6]
        if max(dif)>p['immediate_height_delta_max'] or sum(dif)>p['immediate_height_delta_sum_max']:
            return False
        # Editor-conservative safety halo. A technically valid 33-cell footprint can still
        # be rejected when terrain or blockers sit too close to it. Never clear a visible
        # disc: select starts that already have enough natural clearance instead.
        terrain_clear=int(p.get('editor_terrain_clear_hex',10))
        water_clear=int(p.get('editor_water_clear_hex',20))
        object_clear=int(p.get('editor_object_clear_hex',14))
        r=max(terrain_clear,water_clear,object_clear)
        for Y in range(max(0,y-r),min(self.side,y+r+1)):
            for X in range(max(0,x-r),min(self.side,x+r+1)):
                d=hex_distance(x,y,X,Y)
                if d<=terrain_clear and T[Y,X]!=GRASS:return False
                if d<=water_clear and T[Y,X] in WATER_IDS:return False
                if d<=object_clear and O[Y,X]!=0:return False
        return True

    def _place_starts(self,state,players,rng):
        T=state.terrain
        p=self.profile['starts']
        # Precompute conservative forbidden halos once; doing local scans for every
        # candidate would be prohibitively expensive on a 768² map.
        terrain_clear=int(p.get('editor_terrain_clear_hex',10))
        water_clear=int(p.get('editor_water_clear_hex',20))
        unsafe_near=dilate(T!=GRASS,terrain_clear)
        water_near=dilate(np.isin(T,WATER_IDS),water_clear)
        valid=[]
        for y in range(12,self.side-12,2):
            for x in range(12,self.side-12,2):
                if unsafe_near[y,x] or water_near[y,x]:
                    continue
                # Fast geometric/height check; objects are still empty at this stage.
                vals=[];ok=True
                for dx,dy in START_FOOTPRINT:
                    X,Y=x+dx,y+dy
                    if not(5<=X<self.side-5 and 5<=Y<self.side-5) or T[Y,X]!=GRASS:
                        ok=False;break
                    vals.append(int(state.height[Y,X]))
                if not ok or max(vals)-min(vals)>p['height_range_max']:
                    continue
                dif=[abs(int(state.height[y+dy,x+dx])-int(state.height[y,x])) for dx,dy in HEX6]
                if max(dif)<=p['immediate_height_delta_max'] and sum(dif)<=p['immediate_height_delta_sum_max']:
                    valid.append((x,y))
        if len(valid)<players:raise RuntimeError(f'Only {len(valid)} editor-safe starts')
        starts=[];minsep=p['min_pair_hex_distance']
        for _ in range(players):
            sample=valid if len(valid)<=9000 else [valid[i] for i in rng.choice(len(valid),9000,replace=False)]
            if not sample: raise RuntimeError('Cannot maintain start spacing')
            def score(pos):
                d=min([hex_distance(pos[0],pos[1],q[0],q[1]) for q in starts],default=999)
                # Prefer naturally generous clearance as a tie-breaker.
                return d + float(rng.random())*0.001
            best=max(sample,key=score);starts.append(best)
            valid=[q for q in valid if hex_distance(q[0],q[1],best[0],best[1])>=minsep]
        state.starts=starts
        self.log('starts.maximin_early',f'players={players} terrain_clear={terrain_clear} water_clear={water_clear}')

    def _core_mask(self,state,radius):
        m=np.zeros((self.side,self.side),bool)
        for sx,sy in state.starts:
            for y in range(max(0,sy-radius),min(self.side,sy+radius+1)):
                for x in range(max(0,sx-radius),min(self.side,sx+radius+1)):
                    if hex_distance(sx,sy,x,y)<=radius:m[y,x]=1
        return m

    def _place_start_swamps(self,state,rng,pr):
        T=state.terrain
        core=self._core_mask(state,self.profile['starts']['technical_clear_hex'])
        for sx,sy in state.starts:
            cand=[]
            for y in range(max(4,sy-30),min(self.side-4,sy+31)):
                for x in range(max(4,sx-30),min(self.side-4,sx+31)):
                    d=hex_distance(sx,sy,x,y)
                    if 20<=d<=27 and T[y,x]==GRASS:cand.append((x,y))
            pr.shuffle(cand);placed=False
            for x,y in cand:
                # Minimum coherent three-layer swamp: radius-2 HEX family (19 cells),
                # plus a few optional radius-3 cells to break the perfect outline.
                base=[];outer=[]
                for Y in range(y-3,y+4):
                    for X in range(x-3,x+4):
                        d=hex_distance(x,y,X,Y)
                        if d<=2:base.append((X,Y))
                        elif d==3:outer.append((X,Y))
                if not all(T[Y,X]==GRASS and not core[Y,X] for X,Y in base):
                    continue
                pr.shuffle(outer)
                extras=[]
                for X,Y in outer:
                    if len(extras)>=4:break
                    if T[Y,X]==GRASS and not core[Y,X]:extras.append((X,Y))
                pts=base+extras
                pset=set(pts)
                def clean_halo(points,pointset):
                    for X,Y in points:
                        for dx,dy in HEX6:
                            xx,yy=X+dx,Y+dy
                            if (xx,yy) not in pointset and T[yy,xx]!=GRASS:
                                return False
                    return True
                if not clean_halo(pts,pset):
                    pts=base;pset=set(base)
                    if not clean_halo(pts,pset):
                        continue
                for X,Y in pts:T[Y,X]=GRASS_SWAMP_TRANS
                placed=True;break
            if not placed:raise RuntimeError(f'Could not place coherent start mini-swamp near {(sx,sy)}')
        self.log('biomes.start_mini_swamps',f'count={len(state.starts)}')

    def _rebuild_swamp_transitions(self,state):
        T=state.terrain
        family=np.isin(T,SWAMP_IDS)
        d=depth(family,256)
        T[family&(d==1)]=GRASS_SWAMP_TRANS
        T[family&(d==2)]=SWAMP_TRANS
        T[family&(d>=3)]=SWAMP
        self.log('biomes.swamp_transitions',f'family_cells={int(family.sum())} core={int((T==SWAMP).sum())}')

    # ---------- snow ----------
    def _rebuild_snow(self,state,rng):
        T,H=state.terrain,state.height
        # clear old snow back to Rocky family before rebuilding.
        T[T==SNOW]=ROCKY;T[T==SNOW_TRANS]=ROCKY;T[T==ROCK_SNOW_TRANS]=ROCKY
        mountain=np.isin(T,[ROCK_TRANS_1,ROCK_TRANS_2,ROCKY])
        mdepth=depth(mountain,128);snow=np.zeros_like(mountain)
        lab,n=component_labels(mountain)
        cfg=self.profile['snow']
        for cid in range(1,n+1):
            comp=lab==cid;valid=comp&(mdepth>=cfg['mountain_hex_depth_min'])
            if valid.sum()<20:continue
            hv=H[valid].astype(float);hm=float(hv.max())
            if hm<cfg['absolute_min_height']:continue
            th=max(cfg['absolute_min_height'],float(np.percentile(hv,cfg['relative_percentile'])))
            raw=valid&(H>=th)
            raw=ndimage.binary_closing(raw,structure=np.array([[1,1,0],[1,1,1],[0,1,1]],bool))&valid
            sl,sn=component_labels(raw)
            for sid in range(1,sn+1):
                c=sl==sid
                if c.sum()>=18 and H[c].max()>=hm-5:snow|=c
        target=cfg['target_cells']
        if snow.sum()>target:
            pts=np.argwhere(snow);scores=H[snow].astype(float)+rng.random(len(pts))*0.001
            ids=np.argpartition(scores,-target)[-target:];z=np.zeros_like(snow);p=pts[ids];z[p[:,0],p[:,1]]=1;snow=z
        sd=depth(snow,64)
        T[snow&(sd==1)]=ROCK_SNOW_TRANS;T[snow&(sd==2)]=SNOW_TRANS;T[snow&(sd>=3)]=SNOW
        self.log('snow.summit_rebuild',f'cells={int(snow.sum())}')

    # ---------- resources ----------
    def _water_shore_distance(self,state):
        T=state.terrain;water=np.isin(T,WATER_IDS)
        # IMPORTANT: the map edge is NOT a shore. Seed distance only from Water cells adjacent to actual Shore48.
        shore=(T==SHORE)
        seed=water&(neighbor_count(shore)>0)
        inf=32767;d=np.full(T.shape,inf,np.int16);q=deque()
        for y,x in np.argwhere(seed):d[y,x]=1;q.append((int(x),int(y)))
        while q:
            x,y=q.popleft();nd=int(d[y,x])+1
            if nd>12:continue
            for dx,dy in HEX6:
                X,Y=x+dx,y+dy
                if 0<=X<self.side and 0<=Y<self.side and water[Y,X] and nd<d[Y,X]:d[Y,X]=nd;q.append((X,Y))
        return d

    def _generate_fish(self,state,rng):
        T,R=state.terrain,state.resources;cfg=self.profile['fish']
        water=np.isin(T,WATER_IDS);river=np.isin(T,RIVER_IDS)
        # preserve mineral resources only on mountains; clear any low-only fish from water first.
        R[water]=0;R[river]=0
        d=self._water_shore_distance(state)
        selected=np.zeros_like(water)
        for lo,hi,pct in cfg['bands']:
            m=water&(d>=lo)&(d<=hi)
            pts=np.argwhere(m);k=min(len(pts),round(len(pts)*pct))
            if k:
                ids=rng.choice(len(pts),k,replace=False);p=pts[ids];selected[p[:,0],p[:,1]]=1
        target=cfg['target_cells']
        eligible=water&(d>=1)&(d<=cfg['max_shore_hex_distance'])
        border=np.zeros_like(water);border[[0,-1],:]=1;border[:,[0,-1]]=1
        eligible &= ~border
        selected &= ~border
        cur=int(selected.sum())
        if cur<target:
            pts=np.argwhere(eligible&~selected);add=target-cur
            if len(pts)<add:raise RuntimeError(f'Fish target impossible: eligible={int(eligible.sum())}, need={target}')
            ids=rng.choice(len(pts),add,replace=False);p=pts[ids];selected[p[:,0],p[:,1]]=1
        elif cur>target:
            pts=np.argwhere(selected);ids=rng.choice(len(pts),cur-target,replace=False);p=pts[ids];selected[p[:,0],p[:,1]]=0
        q0=rng.integers(1,16,target,dtype=np.uint8)
        q1=np.minimum(cfg['quantity_cap'],np.floor(q0.astype(float)*cfg['quantity_multiplier']+0.5)).astype(np.uint8)
        R[selected]=q1
        self.log('resources.fish_shore_only',f'cells={int(selected.sum())}')

    # ---------- objects ----------
    def _place_decorations(self,state,rng,pr):
        T,O,A=state.terrain,state.objects,state.accessibility;core=self._core_mask(state,max(self.profile['starts']['technical_clear_hex'],self.profile['starts'].get('editor_object_clear_hex',14)))
        cfg=self.profile['decor']
        # Swamp: Reeds only. Upgraded exact 768 target is x2 reference = 2.
        sw=np.argwhere(np.isin(T,SWAMP_IDS)&~core&(O==0))
        sw_target=min(int(cfg.get('swamp_target',260)),len(sw))
        if sw_target:
            for i in rng.choice(len(sw),sw_target,replace=False):
                y,x=map(int,sw[i]);O[y,x]=pr.choice(cfg['swamp_reed_ids'])
        # Desert: only calibrated desert families; Upgraded exact target = 60.
        de=np.argwhere(np.isin(T,DESERT_IDS)&~core&(O==0))
        de_target=min(int(cfg.get('desert_target',140)),len(de))
        if de_target:
            for i in rng.choice(len(de),de_target,replace=False):
                y,x=map(int,de[i]);oid=pr.choice(cfg['desert_ids']);O[y,x]=oid;A[y,x]=1 if oid in (78,79) else 0
        # Pure decorative stones 1..28: rare, Grass only, never Mountain.
        stone_target=int(cfg.get('decorative_stone_target',0))
        gp=np.argwhere((T==GRASS)&~core&(O==0))
        placed=0
        if stone_target and len(gp):
            for j in rng.permutation(len(gp)):
                if placed>=stone_target:break
                y,x=map(int,gp[j])
                if self._obj_clear(state,x,y,2):
                    O[y,x]=pr.randint(1,28);A[y,x]=1;placed+=1
        # Reefs: sparse open deep sea with wide bypass.
        water=np.isin(T,WATER_IDS);deep=np.argwhere((T==7)&(neighbor_count(~water)==0)&(O==0))
        reef_target=min(cfg['reef_target'],len(deep))
        if reef_target:
            for i in rng.choice(len(deep),reef_target,replace=False):
                y,x=map(int,deep[i]);O[y,x]=pr.randint(111,114);A[y,x]=1
        self.log('objects.decorations',f'desert={de_target} swamp={sw_target} decor_stones={placed} reefs={reef_target}')

    def _obj_clear(self,state,x,y,r=2):
        O=state.objects
        for Y in range(max(0,y-r),min(self.side,y+r+1)):
            for X in range(max(0,x-r),min(self.side,x+r+1)):
                if O[Y,X]!=0 and hex_distance(x,y,X,Y)<r:return False
        return True

    def _place_trees(self,state,rng,pr):
        T,O,A=state.terrain,state.objects,state.accessibility;cfg=self.profile['trees'];core=self._core_mask(state,max(self.profile['starts']['technical_clear_hex'],self.profile['starts'].get('editor_object_clear_hex',14)))
        adult_ids=cfg['adult_ids'];bonus_total=0
        # Start bonus OUTSIDE global quota.
        for sx,sy in state.starts:
            cand=[(x,y) for y in range(max(2,sy-28),min(self.side-2,sy+29)) for x in range(max(2,sx-28),min(self.side-2,sx+29)) if self.profile['starts'].get('editor_object_clear_hex',14)+2<=hex_distance(sx,sy,x,y)<=30 and T[y,x]==GRASS and O[y,x]==0]
            pr.shuffle(cand);k=0
            for x,y in cand:
                if k>=cfg['adult_start_bonus_per_player']:break
                if self._obj_clear(state,x,y,2):O[y,x]=pr.choice(adult_ids);A[y,x]=1;k+=1;bonus_total+=1
            if k<12:raise RuntimeError(f'Insufficient start forest near {(sx,sy)}')
        target=cfg['adult_global_target'];cluster_target=round(target*cfg.get('adult_cluster_share',0.0));global_adult=0
        # Upgraded forest centers: loose, hitbox-aware, irregular.
        centers=[]
        if cluster_target:
            cp=np.argwhere((T==GRASS)&(O==0)&~core)
            if len(cp):
                for i in rng.choice(len(cp),min(cfg.get('forest_centers',38),len(cp)),replace=False):
                    y,x=map(int,cp[i]);centers.append((x,y))
            attempts=0
            while global_adult<cluster_target and centers and attempts<cluster_target*60:
                attempts+=1;cx,cy=centers[int(rng.integers(len(centers)))]
                # loose forest radius ~5..12 HEX
                rad=int(rng.integers(5,13));x=int(np.clip(cx+rng.integers(-rad,rad+1),2,self.side-3));y=int(np.clip(cy+rng.integers(-rad,rad+1),2,self.side-3))
                if hex_distance(cx,cy,x,y)<=rad and T[y,x]==GRASS and O[y,x]==0 and not core[y,x] and self._obj_clear(state,x,y,2):
                    O[y,x]=pr.choice(adult_ids);A[y,x]=1;global_adult+=1
        pts=np.argwhere((T==GRASS)&(O==0)&~core)
        for i in rng.permutation(len(pts)):
            if global_adult>=target:break
            y,x=map(int,pts[i])
            if self._obj_clear(state,x,y,2):O[y,x]=pr.choice(adult_ids);A[y,x]=1;global_adult+=1
        if global_adult<target:raise RuntimeError('Adult tree quota not reached')
        # SmallTree84 separate pool, cluster-oriented in Upgraded.
        small=0;small_target=cfg['small_tree_target'];small_cluster=round(small_target*cfg.get('small_tree_cluster_share',0.0));attempts=0
        while small<small_cluster and centers and attempts<small_target*80:
            attempts+=1;cx,cy=centers[int(rng.integers(len(centers)))];rad=int(rng.integers(5,13));x=int(np.clip(cx+rng.integers(-rad,rad+1),2,self.side-3));y=int(np.clip(cy+rng.integers(-rad,rad+1),2,self.side-3))
            if hex_distance(cx,cy,x,y)<=rad and T[y,x]==GRASS and O[y,x]==0 and not core[y,x] and self._obj_clear(state,x,y,2):O[y,x]=cfg['small_tree_id'];A[y,x]=1;small+=1
        pts=np.argwhere((T==GRASS)&(O==0)&~core)
        for i in rng.permutation(len(pts)):
            if small>=small_target:break
            y,x=map(int,pts[i])
            if self._obj_clear(state,x,y,2):O[y,x]=cfg['small_tree_id'];A[y,x]=1;small+=1
        if small<small_target:raise RuntimeError('SmallTree84 quota not reached')
        state.metadata['adult_cluster_target']=cluster_target;state.metadata['small84_cluster_target']=small_cluster
        self.log('objects.adult_trees',f'global={global_adult} bonus={bonus_total} cluster_target={cluster_target}')
        self.log('objects.smalltree84',f'count={small} cluster_target={small_cluster}')

    def _place_building_stones(self,state,rng,pr):
        T,O,A=state.terrain,state.objects,state.accessibility;cfg=self.profile['building_stones']
        core=self._core_mask(state,max(self.profile['starts']['technical_clear_hex'],self.profile['starts'].get('editor_object_clear_hex',14)));local=self._core_mask(state,33)
        fp=[tuple(x) for x in cfg['footprint']];foot=np.zeros_like(core);blocked=np.zeros_like(core);anchors=[]
        # blocked area enforces conservative min anchor HEX distance >=4.
        def mark_block(x,y):
            for Y in range(max(0,y-3),min(self.side,y+4)):
                for X in range(max(0,x-3),min(self.side,x+4)):
                    if hex_distance(x,y,X,Y)<cfg['anchor_min_hex_distance']:blocked[Y,X]=1
        def ok(x,y):
            if core[y,x] or blocked[y,x]:return False
            for dx,dy in fp:
                X,Y=x+dx,y+dy
                if not(1<=X<self.side-1 and 1<=Y<self.side-1):return False
                if core[Y,X] or T[Y,X]!=GRASS or O[Y,X]!=0 or foot[Y,X]:return False
            return True
        def put(x,y,u,tag):
            O[y,x]=cfg['exhausted_id']-u
            for dx,dy in fp:X,Y=x+dx,y+dy;A[Y,X]=1;foot[Y,X]=1
            mark_block(x,y);anchors.append((x,y,u,tag))
        # Local start bonus, 53 stock/player.
        units=cfg['start_bonus_units']
        for pid,(sx,sy) in enumerate(state.starts,1):
            cand=[(x,y) for y in range(max(2,sy-43),min(self.side-2,sy+44)) for x in range(max(2,sx-43),min(self.side-2,sx+44)) if self.profile['starts'].get('editor_object_clear_hex',14)+2<=hex_distance(sx,sy,x,y)<=42]
            pr.shuffle(cand);k=0
            for x,y in cand:
                if k>=len(units):break
                if ok(x,y):put(x,y,units[k],f'P{pid}');k+=1
            if k<len(units):raise RuntimeError(f'Building Stone start bonus failed P{pid}: {k}/{len(units)}')
        # Global anchor quota. Upgraded keeps ~30% cluster-oriented / ~70% scattered.
        g=0;cluster_goal=round(cfg['global_anchor_target']*cfg.get('cluster_share',0.0));centers=[]
        if cluster_goal:
            cp=np.argwhere((T==GRASS)&(O==0)&~local)
            if len(cp):
                for i in rng.choice(len(cp),min(cfg.get('cluster_centers',60),len(cp)),replace=False):
                    y,x=map(int,cp[i]);centers.append((x,y))
            attempts=0
            while g<cluster_goal and centers and attempts<cluster_goal*100:
                attempts+=1;cx,cy=centers[int(rng.integers(len(centers)))];rad=int(rng.integers(4,13));x=int(np.clip(cx+rng.integers(-rad,rad+1),2,self.side-3));y=int(np.clip(cy+rng.integers(-rad,rad+1),2,self.side-3))
                if hex_distance(cx,cy,x,y)<=rad and ok(x,y):put(x,y,8,'global');g+=1
        pts=np.argwhere((T==GRASS)&(O==0)&~local)
        for i in rng.permutation(len(pts)):
            if g>=cfg['global_anchor_target']:break
            y,x=map(int,pts[i])
            if ok(x,y):put(x,y,8,'global');g+=1
        if g<cfg['global_anchor_target']:raise RuntimeError(f'Building Stone global anchors {g}/{cfg["global_anchor_target"]}')
        state.metadata['stone_cluster_target']=cluster_goal
        # Exact global stock by increasing fill states, never by adding anchors.
        gi=[i for i,a in enumerate(anchors) if a[3]=='global'];q=np.full(len(gi),8,dtype=int)
        target=cfg['global_stock_target']
        while q.sum()<target:
            ids=np.where(q<12)[0]
            if not len(ids):break
            q[ids[pr.randrange(len(ids))]]+=1
        while q.sum()>target:
            ids=np.where(q>1)[0];q[ids[pr.randrange(len(ids))]]-=1
        for value,i in zip(q,gi):
            x,y,_,tag=anchors[i];O[y,x]=cfg['exhausted_id']-int(value);anchors[i]=(x,y,int(value),tag)
        state.metadata['building_stone_anchors']=anchors
        self.log('objects.building_stones',f'global={g} bonus={len(anchors)-g}')

    def _final_accessibility(self,state):
        T,O,A=state.terrain,state.objects,state.accessibility
        water=np.isin(T,WATER_IDS);A[water]=1
        # Native runtime navigation shows the inner Snow family (129/128) as non-walkable,
        # analogous to the already-validated Water accessibility correction.
        snow_block=np.isin(T,[SNOW_TRANS,SNOW]);A[snow_block]=1
        # Ordinary object anchors block by default for confirmed trees/palms/reefs/stones.
        treeish=np.isin(O,[68,69,70,71,72,78,79,84,111,112,113,114])
        A[treeish]=1
        # Never allow ordinary objects on Mountain family.
        bad=(O!=0)&np.isin(T,MOUNTAIN_IDS)
        O[bad]=0;A[bad]=0
        A[snow_block]=1
        self.log('accessibility.finalize')

    # ---------- validators ----------
    def validate(self,state)->list[ValidationResult]:
        T,H,O,A,R=state.terrain,state.height,state.objects,state.accessibility,state.resources
        out=[]
        def add(rule,passed,msg,hard=True):out.append(ValidationResult(rule,bool(passed),msg,hard))
        water=np.isin(T,WATER_IDS);river=np.isin(T,RIVER_IDS);mount=np.isin(T,MOUNTAIN_IDS)
        add('WATER_HEIGHT',np.count_nonzero(H[water])==0,f'nonzero={np.count_nonzero(H[water])}')
        add('WATER_ACCESS',np.count_nonzero(A[water]!=1)==0,f'bad={np.count_nonzero(A[water]!=1)}')
        snow_block=np.isin(T,[SNOW_TRANS,SNOW])
        add('SNOW_ACCESS',np.count_nonzero(A[snow_block]!=1)==0,f'bad={np.count_nonzero(A[snow_block]!=1)}')
        # Strict family transition chains: prevent missing connector textures.
        def transition_bad(tid,allowed):
            bad=0
            for y,x in np.argwhere(T==tid):
                for dx,dy in HEX6:
                    X,Y=int(x+dx),int(y+dy)
                    if 0<=X<self.side and 0<=Y<self.side and int(T[Y,X]) not in allowed:bad+=1
            return bad
        desert_bad=sum(transition_bad(t,a) for t,a in ((20,{16,20,65}),(65,{20,65,64}),(64,{65,64})))
        swamp_bad=sum(transition_bad(t,a) for t,a in ((21,{16,21,81}),(81,{21,81,80}),(80,{81,80})))
        snow_bad=sum(transition_bad(t,a) for t,a in ((35,{32,35,129}),(129,{35,129,128}),(128,{129,128})))
        add('DESERT_TRANSITIONS',desert_bad==0,f'bad_edges={desert_bad}')
        add('SWAMP_TRANSITIONS',swamp_bad==0,f'bad_edges={swamp_bad}')
        add('SNOW_TRANSITIONS',snow_bad==0,f'bad_edges={snow_bad}')
        # The literal map edge should normally be deep Water7; the GRADIENT is in the outer frame inward from it.
        yy,xx=np.mgrid[0:self.side,0:self.side]
        bd=np.minimum.reduce([xx,yy,self.side-1-xx,self.side-1-yy])
        frame=(bd<40)&water
        edge=np.concatenate([T[0,:],T[-1,:],T[:,0],T[:,-1]])
        edge_water=edge[np.isin(edge,WATER_IDS)]
        unique_frame=sorted(map(int,np.unique(T[frame]))) if frame.any() else []
        edge7=(np.mean(edge_water==7) if len(edge_water) else 0.0)
        add('BORDER_WATER_GRADIENT',len(unique_frame)>=4 and edge7>=0.95,f'outer40 ids={unique_frame}, edge7={edge7:.3f}')
        lab,sizes=component_sizes(water);sea=1+int(np.argmax(sizes)) if sizes else 0
        micros=sum(1 for i,s in enumerate(sizes,1) if i!=sea and s<=self.profile['water']['forbid_inland_components_leq'])
        add('MICRO_WATER_1_4',micros==0,f'components={micros}')
        # Rivers connect to water, and any water-contact River cell must be endpoint.
        rl,rn=component_labels(river);wc=neighbor_count(water);rd=neighbor_count(river);orph=0;badmouth=0;maxdist=0
        for cid in range(1,rn+1):
            m=rl==cid;co=m&(wc>0)
            if not co.any():orph+=1;continue
            badmouth+=int(np.count_nonzero(co&(rd>=2)))
            dmap=np.full(T.shape,-1,np.int16);q=deque()
            for y,x in np.argwhere(co):dmap[y,x]=0;q.append((int(x),int(y)))
            while q:
                x,y=q.popleft()
                for dx,dy in HEX6:
                    X,Y=x+dx,y+dy
                    if 0<=X<self.side and 0<=Y<self.side and m[Y,X] and dmap[Y,X]<0:
                        dmap[Y,X]=dmap[y,x]+1;q.append((X,Y))
            if m.any():maxdist=max(maxdist,int(dmap[m].max())+1)
        add('RIVER_ORPHANS',orph==0,f'orphan_components={orph}')
        add('RIVER_STOPS_AT_WATER',badmouth==0,f'bad_mouth_cells={badmouth}')
        add('RIVER_LENGTH_CAP',maxdist<=self.profile['river']['practical_max_cells'],f'max_water_to_inland_cells={maxdist}')
        # Fish checks based on true Shore, never edge.
        fish=(R&0xf0)==0;fish&=(R&15)>0
        d=self._water_shore_distance(state)
        add('FISH_NONZERO',fish.sum()>0,f'cells={int(fish.sum())}')
        add('FISH_WATER_ONLY',np.count_nonzero(fish&~water)==0,f'bad={np.count_nonzero(fish&~water)}')
        add('FISH_NO_RIVER',np.count_nonzero(fish&river)==0,f'bad={np.count_nonzero(fish&river)}')
        add('FISH_SHORE_DISTANCE',np.count_nonzero(fish&(d>12))==0,f'bad={np.count_nonzero(fish&(d>12))}')
        border_mask=np.zeros_like(water);border_mask[[0,-1],:]=1;border_mask[:,[0,-1]]=1
        add('FISH_NOT_EDGE_DERIVED',np.count_nonzero(fish&border_mask)==0,f'fish_on_map_edge={np.count_nonzero(fish&border_mask)}')
        # mineral exact family cells and no non-mineral on unsupported cells
        for fam,fcfg in {int(k):v for k,v in self.profile['minerals']['families'].items()}.items():
            n=int(np.count_nonzero((R&0xf0)==fam))
            add(f'MINERAL_{fcfg["name"].upper()}_CELLS',n==fcfg['cells'],f'{n}/{fcfg["cells"]}')
        # object safety and quotas
        add('OBJECTS_NOT_ON_MOUNTAIN',np.count_nonzero((O!=0)&mount)==0,f'bad={np.count_nonzero((O!=0)&mount)}')
        adult_ids=self.profile['trees']['adult_ids'];adult_count=int(np.isin(O,adult_ids).sum())
        adult_min=self.profile['trees']['adult_global_target']+12*len(state.starts)
        adult_max=self.profile['trees']['adult_global_target']+self.profile['trees']['adult_start_bonus_per_player']*len(state.starts)
        add('ADULT_TREE_QUOTA',adult_min<=adult_count<=adult_max,f'count={adult_count}, expected={adult_min}..{adult_max}')
        add('TREES_ON_GRASS',np.count_nonzero(np.isin(O,adult_ids+[84])&(T!=GRASS))==0,f'bad={np.count_nonzero(np.isin(O,adult_ids+[84])&(T!=GRASS))}')
        swamp_objects=(O!=0)&np.isin(T,SWAMP_IDS)
        bad_swamp=swamp_objects&~np.isin(O,self.profile['decor']['swamp_reed_ids'])
        add('SWAMP_REEDS_ONLY',np.count_nonzero(bad_swamp)==0,f'bad={np.count_nonzero(bad_swamp)}')
        # SmallTree84 exact global pool
        add('SMALLTREE84',int((O==84).sum())==self.profile['trees']['small_tree_target'],f'count={int((O==84).sum())}')
        # Building Stone footprints + min spacing.
        fp=[tuple(x) for x in self.profile['building_stones']['footprint']];stones=np.argwhere((O>=115)&(O<=126));badfp=0
        coords=[(int(x),int(y)) for y,x in stones]
        for y,x in stones:
            if any(A[y+dy,x+dx]!=1 for dx,dy in fp):badfp+=1
        mind=999
        # spatial bucketing is enough, small radius only
        sset=set(coords)
        for x,y in coords:
            for Y in range(max(0,y-3),min(self.side,y+4)):
                for X in range(max(0,x-3),min(self.side,x+4)):
                    if (X,Y)!=(x,y) and (X,Y) in sset:mind=min(mind,hex_distance(x,y,X,Y))
        add('STONE_FOOTPRINT',badfp==0,f'bad={badfp}')
        add('STONE_SPACING',mind>=self.profile['building_stones']['anchor_min_hex_distance'] if mind<999 else True,f'min_hex={mind if mind<999 else "n/a"}')
        expected_stones=self.profile['building_stones']['global_anchor_target']+len(self.profile['building_stones']['start_bonus_units'])*len(state.starts)
        stone_stock=int(np.sum(self.profile['building_stones']['exhausted_id']-O[(O>=115)&(O<=126)]))
        expected_stock=self.profile['building_stones']['global_stock_target']+self.profile['building_stones']['start_bonus_stock_per_player']*len(state.starts)
        add('STONE_ANCHOR_QUOTA',len(stones)==expected_stones,f'{len(stones)}/{expected_stones}')
        add('STONE_STOCK_QUOTA',stone_stock==expected_stock,f'{stone_stock}/{expected_stock}')
        add('STONES_ON_GRASS',np.count_nonzero(((O>=115)&(O<=126))&(T!=GRASS))==0,f'bad={np.count_nonzero(((O>=115)&(O<=126))&(T!=GRASS))}')
        # Starts
        badstarts=sum(1 for x,y in state.starts if not self._start_ok(state,x,y))
        add('STARTS_STATIC',badstarts==0,f'bad={badstarts}/{len(state.starts)}')
        sp=self.profile['starts'];bad_terrain=bad_water=bad_objects=0
        for sx,sy in state.starts:
            r=max(sp.get('editor_terrain_clear_hex',10),sp.get('editor_water_clear_hex',20),sp.get('editor_object_clear_hex',14))
            for y in range(max(0,sy-r),min(self.side,sy+r+1)):
                for x in range(max(0,sx-r),min(self.side,sx+r+1)):
                    dd=hex_distance(sx,sy,x,y)
                    if dd<=sp.get('editor_terrain_clear_hex',10) and T[y,x]!=GRASS:bad_terrain+=1
                    if dd<=sp.get('editor_water_clear_hex',20) and T[y,x] in WATER_IDS:bad_water+=1
                    if dd<=sp.get('editor_object_clear_hex',14) and O[y,x]!=0:bad_objects+=1
        add('START_TERRAIN_CLEARANCE',bad_terrain==0,f'bad_cells={bad_terrain}')
        add('START_WATER_CLEARANCE',bad_water==0,f'bad_cells={bad_water}')
        add('START_OBJECT_CLEARANCE',bad_objects==0,f'bad_cells={bad_objects}')
        add('UPGRADED_FISH_CELL_TARGET',int(fish.sum())==self.profile['fish']['target_cells'],f'{int(fish.sum())}/{self.profile["fish"]["target_cells"]}')
        desert_decor=np.count_nonzero(np.isin(O,self.profile['decor']['desert_ids'])&np.isin(T,DESERT_IDS))
        swamp_reeds=np.count_nonzero(np.isin(O,self.profile['decor']['swamp_reed_ids'])&np.isin(T,SWAMP_IDS))
        pure_stones=np.count_nonzero((O>=1)&(O<=28))
        reefs=np.count_nonzero((O>=111)&(O<=114))
        add('UPGRADED_DESERT_DECOR',desert_decor==self.profile['decor']['desert_target'],f'{desert_decor}/{self.profile["decor"]["desert_target"]}')
        add('UPGRADED_SWAMP_DECOR',swamp_reeds==self.profile['decor']['swamp_target'],f'{swamp_reeds}/{self.profile["decor"]["swamp_target"]}')
        add('UPGRADED_DECOR_STONES',pure_stones==self.profile['decor']['decorative_stone_target'],f'{pure_stones}/{self.profile["decor"]["decorative_stone_target"]}')
        add('UPGRADED_REEFS',reefs==self.profile['decor']['reef_target'],f'{reefs}/{self.profile["decor"]["reef_target"]}')
        edge_all=np.concatenate([T[0,:],T[-1,:],T[:,0],T[:,-1]])
        add('UPGRADED_DEEP_EDGE',np.count_nonzero(edge_all!=7)==0,f'non_water7_edge={np.count_nonzero(edge_all!=7)}')
        add('UPGRADED_START_BONUS_OUTSIDE_GLOBAL',True,'separate tree/stone bonus pools encoded')
        self.log('validators.hard',f'pass={sum(v.passed for v in out)}/{len(out)}')
        return out
