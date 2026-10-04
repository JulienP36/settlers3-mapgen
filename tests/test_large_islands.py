import numpy as np
import pytest
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.map_data.constants import WATER_IDS, HEX6
from s3mapgen.map_data.hexgrid import component_labels

@pytest.mark.parametrize('mode,side,players,seed', [
 ('legacy',384,4,2026093003), ('upgraded',384,4,2026093004),
 ('legacy',512,4,2026093005), ('legacy',768,4,2026093006),
 ('legacy',384,8,2026093007), ('legacy',768,20,2026093008),
 ('upgraded',768,20,42),
])
def test_islands_have_independent_starts_and_native_features(mode,side,players,seed,monkeypatch):
 from s3mapgen.generation.generators.legacy import native_terrain as legacy
 from s3mapgen.generation.generators.upgraded import native_terrain as upgraded
 def forbidden(*args,**kwargs):
  raise AssertionError('Grandes îles must not construct discarded Classic relief')
 for engine in (legacy,upgraded):
  for name in ('_seed_coarse_relief','_refine_relief','_sculpt_candidate','_consume_sculpture_markers'):
   monkeypatch.setattr(engine,name,forbidden)
 monkeypatch.setattr(legacy,'_build_native_relief',forbidden)
 result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(players,seed,mode=mode,archetype='large_islands',side=side)
 state=result.state
 labels,n=component_labels(~np.isin(state.terrain,WATER_IDS))
 assert n==players
 assert len({int(labels[y,x]) for x,y in state.starts})==players
 sizes=np.bincount(labels.ravel())[1:]
 assert sizes.min()/sizes.max()>=0.65
 assert all(v.passed for v in result.validations if v.hard), result.validations
 features=state.metadata['large_island_features']
 assert all(row['mountain_cells']>0 and row['swamp_cells']>0 and row['river_cells']>0 for row in features)
 assert state.metadata['large_island_topology']['post_island_native_relaxation_passes']>0
 # Regression: R7 could run hundreds of cells around a coastal height-1 belt.
 # Check the committed terrain, including native continuations and cleanup.
 low_rivers=np.isin(state.terrain,[96,97,98,99])&(state.height<=2)
 low_labels,low_count=component_labels(low_rivers)
 if low_count:
  assert np.bincount(low_labels.ravel())[1:].max()<64
 # No single-cell strait: separate final land components stay apart even after coast transitions.
 for dr,dc in HEX6:
  a=labels[max(0,dr):side+min(0,dr),max(0,dc):side+min(0,dc)]
  b=labels[max(0,-dr):side+min(0,-dr),max(0,-dc):side+min(0,-dc)]
  assert not np.any((a>0)&(b>0)&(a!=b))

def test_islands_reject_mirror_before_generation():
 with pytest.raises(ValueError,match='miroir'):
  MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(4,1,mode='legacy',archetype='large_islands',side=384,mirror_mode=1)


def test_macro_preview_builds_the_selected_number_of_separate_islands():
 from s3mapgen.generation.archetypes.previews import generate_archetype_preview
 from s3mapgen.generation.archetypes.profiles import default_archetype_profile
 for players in (2,4,8):
  preview=generate_archetype_preview(default_archetype_profile('large_islands'),384,2026093009,players=players)
  assert preview.mass.mass_count==players
  assert np.array_equal(preview.source_noise,preview.noise)
  assert np.all(preview.source_noise[preview.island_mask==0]==-30)

@pytest.mark.parametrize('base_mode,seed', [('legacy',2026093051),('upgraded',2026093052)])
def test_custom_large_islands_keeps_the_independent_island_contract(base_mode,seed):
 from s3mapgen.generation.custom import build_custom_config
 config=build_custom_config(base_mode,'large_islands')
 result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
  4,seed,mode='custom',archetype='large_islands',side=384,custom_config=config,
 )
 assert all(v.passed for v in result.validations if v.hard)
 assert all(v.passed for v in result.validations if v.rule_id.startswith('ISLAND_'))

@pytest.mark.parametrize('side,players', [(384,2),(384,8),(512,15),(768,20)])
def test_balanced_masks_keep_target_land_and_real_channels(side,players):
 from s3mapgen.generation.archetypes.large_islands import build_island_masks
 from s3mapgen.map_data.hexgrid import distance_from
 labels,centers,mask,channel,_=build_island_masks(side,players,42)
 assert component_labels(labels>0)[1]==players
 assert .56 <= np.count_nonzero(labels)/labels.size <= .57
 sizes=np.bincount(labels.ravel())[1:]
 assert sizes.min()/sizes.max()>.97
 for n in range(1,players+1):
  other=(labels>0)&(labels!=n)
  assert distance_from(other)[labels==n].min()>=channel
  x,y=centers[n-1]
  assert labels[y,x]==n
 assert np.all(mask[labels==0]==0)
 assert np.array_equal(mask, np.where(labels>0,255,0))


def test_island_preview_exposes_the_actual_mask_and_independent_relief():
 from s3mapgen.generation.archetypes.previews import generate_archetype_preview
 from s3mapgen.generation.archetypes.profiles import default_archetype_profile
 p=generate_archetype_preview(default_archetype_profile('large_islands'),384,42,players=8)
 assert p.island_mask is not None and p.local_relief is not None
 assert np.array_equal(p.island_mask>0,p.macro!=0)
 assert np.all(p.local_relief[p.island_mask==0]==0)
 assert p.macro_relaxed
 assert .56<=np.count_nonzero(p.macro)/p.macro.size<=.57
 # The outer coast should remain a low gradual transition after native smoothing.
 from s3mapgen.map_data.hexgrid import distance_from
 land=p.macro!=0
 depth=distance_from(~land)
 outer=land&(depth<=3)
 # R13 adds at most two rounded units on the third coastal row;
 # the native HEX6 slope contract remains unchanged.
 assert int(p.noise[outer].max())<=12
 assert float(p.noise[outer].mean())<6
 # Lowlands extend beyond the immediate shoreline; high relief is inland.
 coastal=land&(depth<=10)
 assert int(p.noise[coastal].max())<=75
 assert float(p.noise[coastal].mean())<25
 mountains=land&(p.noise>=p.thresholds[1])
 assert int(depth[mountains].min())>=15
 near_shore=land&(depth<=5)
 assert int(p.noise[near_shore].max())<=24
 assert float(p.noise[near_shore].mean())<10
 assert np.mean(p.noise[near_shore]==1)<.4

 # Quantized contour lines are expected; broad constant-height interiors are not.
 interior=land&(depth>10)&(p.noise>=8)
 flat=np.ones(land.shape,dtype=bool)
 for dr,dc in HEX6:
  a=np.s_[max(0,dr):p.side+min(0,dr),max(0,dc):p.side+min(0,dc)]
  b=np.s_[max(0,-dr):p.side+min(0,-dr),max(0,-dc):p.side+min(0,-dc)]
  flat[a]&=p.noise[a]==p.noise[b]
 assert np.count_nonzero(flat&interior)/np.count_nonzero(interior)<.005


def test_large_island_preview_has_no_wide_quantized_coastal_belt():
 from s3mapgen.generation.archetypes.previews import generate_archetype_preview
 from s3mapgen.generation.archetypes.profiles import default_archetype_profile
 from s3mapgen.map_data.hexgrid import distance_from
 # R7's five first rows were all height 1 on this large-island seed.
 p=generate_archetype_preview(default_archetype_profile('large_islands'),768,2026093006,players=4)
 land=p.macro!=0
 near_shore=land&(distance_from(~land)<=5)
 assert np.mean(p.noise[near_shore]==1)<.4
 assert int(p.noise[near_shore].max())<=16


@pytest.mark.parametrize("engine_name", ["legacy", "upgraded"])
def test_explicit_island_source_keeps_native_river_policy_and_relaxation(engine_name):
 import importlib
 from s3mapgen.generation.archetypes.profiles import default_archetype_profile
 engine=importlib.import_module(f"s3mapgen.generation.generators.{engine_name}.native_terrain")
 profile=default_archetype_profile("large_islands")
 assert profile["morphology"]["relief_source"]=="large_islands"
 assert not engine._uses_noise_archetype_profile(profile)
 profile["morphology"]["native_relaxation_strength_percent"]=50
 assert engine._native_relaxation_strength_percent(profile)==50
