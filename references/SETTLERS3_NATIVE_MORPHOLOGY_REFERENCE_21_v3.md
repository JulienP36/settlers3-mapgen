# Settlers III — Native Terrain Morphology Reference v3

> **CANONICAL MORPHOLOGY REFERENCE — 21 native SAVs — 2026-08-17**
>
> Corpus: 7 sizes (`384, 448, 512, 576, 640, 704, 768`) × 3 player-density configurations (`4P`, `8P`, native maximum). Connectivity is evaluated on the confirmed Settlers III HEX6 neighbourhood.
>
> This document supersedes `SETTLERS3_NATIVE_MORPHOLOGY_REFERENCE_21_v1.md` and v2 for terrain-shape generation.

## 1. Absolute generation invariants

- **Fish:** only Water terrain IDs `0..7`. Never place fish on River terrain IDs `96..99`.
- **Mud:** measured from native maps but disabled in the current Continental profile.
- **Mountains:** generate a coherent full mountain-family mask first; no Grass/Desert/Swamp/Water/River holes are allowed inside a massif. Snow and Snow transitions may occupy internal Rocky areas.
- **Desert / Swamp:** generate coherent family masks, then paint transitions. Accidental enclosed Grass holes are not native-like and must be removed.
- **Generation order:** continent → mountain family (locked) → lakes/water → surface biomes → rivers → resources → decorations → starts.

## 2. 768×768 principal targets

Three native 768 saves (4P / 8P / 20P) are the primary target when generating a 768 map.

| Family | Mean map % | Significant components ≥20 | Native aggregate contour target |
|---|---:|---:|---:|
| Water | 20.215% | 30.7 | perimeter/√area ≈ 72.53 |
| Desert | 3.108% | 50.7 | ≈ 101.40 |
| Swamp | 0.365% | 27.7 | ≈ 108.61 |
| Rivers | 1.491% | 215.7 | ≈ 381.01 |
| Full Mountain | 14.213% map ≈ 17.814% land | 22.0 | highly seed-dependent because a few huge ranges dominate |
| Rocky32 | 9.584% map ≈ 12.012% land | 19.3 | internal Snow makes Rocky alone appear holey |
| Snow family | 2.410% map ≈ 3.021% land | 12.3 | internal to mountain systems |

## 3. Micro-components are a real native feature

A major correction versus earlier generator attempts: native maps contain many components smaller than 20 cells. They are not the same thing as holes. They are separate tiny patches and strongly affect visual contour complexity.

### Native 768 micro-component counts

| Family | 4P small count / area | 8P small count / area | 20P small count / area | Typical target |
|---|---:|---:|---:|---:|
| Desert | 327 / 436 | 259 / 354 | 253 / 335 | ~280 components / ~375 cells |
| Swamp | 216 / 678 | 215 / 596 | 217 / 637 | ~216 components / ~637 cells |
| Water | 18 / 47 | 49 / 205 | 49 / 196 | ~39 components / ~149 cells |
| Full Mountain | 58 / 170 | 24 / 57 | 47 / 194 | ~43 components / ~140 cells |

This explains why generating only the ≥20-cell regions makes Desert/Swamp look too smooth even if their percentage and large-zone count are correct.

**Rule:** large zones and micro-zones must be generated separately. Micro-zones are external independent components, never holes punched into a larger zone.

## 4. Hole statistics — critical

Across the complete 21-map corpus:

- Desert-family component hole-ratio p90 = **0**.
- Swamp-family component hole-ratio p90 = **0**.
- River component hole-ratio p90 = **0**.
- Full Mountain-family components contain very little true hole area.
- Rocky32 alone can have large apparent holes because Snow-family terrain is embedded inside the full massif.

Therefore a visual `Rocky32` mask is not the correct object to test for mountain coherence. Test the union `17/33/32/34/35/129/128`, then verify that any internal non-Rocky cells belong to the Snow family.

## 5. Native 768 mountain examples

### 4-player seed
- Full Mountain area: **87,393 cells**.
- Significant components: **22**.
- Largest ranges: `45,307`, `13,084`, `11,373`, `11,000`, then much smaller systems.
- Small components: `58`, totaling only `170` cells.

### 8-player seed
- Full Mountain area: **81,800 cells**.
- Significant components: **18**.
- Largest ranges: `24,527`, `19,627`, `13,683`, `9,931`, `6,995`, ...

### 20-player seed
- Full Mountain area: **82,376 cells**.
- Significant components: **26**.
- Largest ranges: `20,713`, `14,666`, `14,605`, `11,723`, `8,322`, ...

**Interpretation:** native mountains do not use one uniform range size. A seed may contain one enormous system plus several secondary ranges, or distribute the same overall mountain area among more medium systems. The generator should sample a *distribution of systems*, not place 20 similarly sized blobs.

## 6. Component shape signature over all 21 saves

| Family | median component area | median perimeter/√area | median bbox fill | median elongation | p90 true hole ratio |
|---|---:|---:|---:|---:|---:|
| Desert | 193.5 | 13.36 | 0.469 | 1.84 | 0.0000 |
| Swamp | 33.0 | 11.51 | 0.454 | 1.89 | 0.0000 |
| Rivers | 30.0 | 22.27 | 0.147 | 3.82 | 0.0000 |
| Full Mountain | 306.0 | 12.02 | 0.418 | 2.35 | 0.0153 |
| Rocky32 | 298.5 | 10.98 | 0.388 | 2.47 | 0.3484 |
| Snow | 571.0 | 11.72 | 0.427 | 2.40 | 0.0143 |

## 7. 768 continent morphology

Mean across the three native 768 saves:

- Land: **79.785%** of map.
- Main continent: **99.769%** of all land.
- Significant satellite islands ≥20: **7.0**.
- Main-continent perimeter/√area: **26.210**.
- Main-continent bbox fill: **0.879**.
- Mean internal water/lake holes in the main land mask: ~**12,694 cells**.

### Multiscale coastline curve

After progressively smoothing the native main-continent mask:

- scale 0: `26.210`
- scale 1: `23.804`
- scale 2: `21.258`
- scale 4: `18.341`
- scale 8: `14.010`
- scale 16: `10.161`

A faithful continent should match the *curve*, not just raw perimeter. Excess high-frequency edge noise can match scale 0 while looking wrong; an over-smooth superellipse can match area but fails every intermediate scale.

## 8. Data-driven generation method now preferred

For native-faithful Continental generation:

1. Use native component masks as a **morphology library**.
2. Reuse shapes only through translation and HEX6-preserving transforms (180° and axial transpose variants), optionally with very small continuous deformation for the outer continent.
3. Never rescale components aggressively: rescaling was observed to destroy native perimeter/bbox signatures.
4. Large components are sampled separately from micro-components.
5. Full Mountain stamps are hole-filled before placement; filled cells become Rocky32.
6. Surface biome stamps are hole-filled before placement.
7. River components preserve their native thin/branching shape and must be anchored to Water.
8. The global continent is derived from a filled native outer silhouette with a low-amplitude continuous deformation; inland lakes and satellite islands are then reassembled independently.

## 9. Decorations while morphology is calibrated

- Resource objects are not being retuned in this phase.
- Pure decorative stone IDs `1..28`: use **one tenth** of the native observed quantities.
- Other pure decoration families keep the measured native frequency/support rules.
- Reefs `111..114`: approximately **10–12 on 768**, dispersed in open border-connected ocean, with wide local water around each reef so ships can always bypass them.

## 10. Current resource lock

Resource parameters are frozen while terrain morphology is being tuned:

- accessible Rocky32 mining occupancy target ~80%; Snow-covered geology is allowed to contain ore but is excluded from accessible-balance accounting;
- ore-family proportions remain locked to the previously validated values;
- ore is clustered, not isolated pixels;
- fish only Water0..7, never River96..99;
- resource-object generation is not part of the current morphology pass.


## 11. User validation checkpoint — morphology is now LOCKED

After the native-shape and transition-cleanup passes, the user explicitly validated the **forms** of:

- global continent;
- deserts;
- inland lakes;
- rivers;
- mountain systems;
- snow systems;
- swamps.

These shapes are now **locked**. Future work should not remodel these families unless a new test exposes a specific defect.

The subsequent transition cleanup was also judged very good and is now part of the canonical morphology/transition pipeline.

## 12. Hydrology refinement after morphology validation

### Inland water / mini-ponds

The validated large lake forms are retained.

Size-matched analysis of the three native 768 saves showed the following mean counts of inland-water components:

```text
1–4 cells:  ~27.67 / map
5–9 cells:   6.00 / map
10–19 cells: 5.00 / map
```

The pre-refinement candidate had too many `1–4` cell ponds (`47`). The refinement target is therefore approximately the native 768 distribution, without changing the already validated major lakes.

Current refined candidate:

```text
1–4 cells: 28
5–9 cells: 6
10–19 cells: 5
```

Significant lakes remain in the native 768 range.

### River lengths

For **simple, non-branching river components** in the native 768 corpus:

```text
p10  ≈ 16
p25  ≈ 18
p50  ≈ 22
p75  ≈ 29
p90  ≈ 35
p95  ≈ 39.75
p99  ≈ 54.5
max  ≈ 70
```

The current refinement shortened only overlong inland ends while preserving rare long-tail rivers.

Refined candidate profile is approximately:

```text
p50 ≈ 22
p75 ≈ 29
p90 ≈ 35
p95 ≈ 40
```

This is now the preferred 768 river-length target.

## 13. Current Continental-profile deviations from native

These deviations are intentional/current:

- **Mud = 0**, even though native maps generate Mud.
- Swamp volume has been experimentally increased by about **30%** versus the earlier working swamp volume. Current tested candidate is around **0.49% of map** versus native 768 mean **0.365%**.
- Decorative stone IDs `1..28` use **1/10** of native observed quantity.
- Reefs `111..114`: about **10–12** on 768, sparse and ship-bypass-safe.
- Small Tree 84 is a custom bonus pool, not a native-density target.

## 14. Latest size-768 morphology checkpoint

`S3_Continental_4P_768x768_seed_2026081734_resources_rebalanced.edm` currently measures approximately:

```text
Water      20.215% map
Desert      3.041% map
Swamp       0.490% map   (experimental +30%-ish profile)
Rivers      1.488% map
Mountain   15.062% map
Snow        2.489% map
Rocky32    10.386% map
```

The geometry itself is considered strong; future new-seed tests are intended to verify **robustness/generalization**, not to reopen the already validated shape model by default.
