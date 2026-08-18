# Settlers III — Native Terrain Transition Rules (21 SAV) v2

> **CANONICAL TERRAIN-TRANSITION REFERENCE — 2026-08-17**
>
> Derived from the complete 21-save native corpus and validated in-game/editor on the current generated lineage. Connectivity and legality use the confirmed Settlers III **HEX6** neighbourhood:
>
> `(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)`
>
> This supersedes `SETTLERS3_NATIVE_TERRAIN_TRANSITIONS_21_v1.md`.

## 1. Strict transition chains

```text
Mountain:
Grass16 ↔ 17 ↔ 33 ↔ Rocky32

Snow, strictly inside the mountain:
Rocky32 ↔ 35 ↔ 129 ↔ Snow128

Desert:
Grass16 ↔ 20 ↔ 65 ↔ Desert64

Swamp:
Grass16 ↔ 21 ↔ 81 ↔ Swamp80

Water:
Shore48 ↔ Water0 ↔ 1 ↔ 2 ↔ 3 ↔ 4 ↔ 5 ↔ 6 ↔ 7
```

Mud exists natively (`23 ↔ 145 ↔ 144`) but is disabled in the current Continental profile.

## 2. Strong adjacency invariants

From the native corpus and cleanup validation:

- every generated `17` must be a real outer mountain transition and touch actual Grass16;
- `17` must never directly touch Rocky32: `33` is the required intermediate;
- `20` neighbors only `16/20/65`;
- `65` neighbors only `20/65/64`;
- `64` neighbors only `65/64`;
- `21` neighbors only `16/21/81`;
- `81` neighbors only `21/81/80`;
- `80` neighbors only `81/80`;
- `35` neighbors only `32/35/129`;
- `129` neighbors only `35/129/128`;
- `128` neighbors only `129/128`.

The current cleanup lineage achieved **0 transition-neighbour violations** for all of these chains.

## 3. Family-mask rule — critical

Never generate core and transition IDs as independent noise.

Correct algorithm:

1. create a coherent full-family binary mask;
2. fill accidental internal holes;
3. compute **HEX6 depth inside the family**;
4. paint transition/core IDs from depth.

Examples:

```text
Mountain family depth:
depth 1 -> 17
depth 2 -> 33
depth >=3 -> 32

Desert family:
depth 1 -> 20
depth 2 -> 65
depth >=3 -> 64

Swamp family:
depth 1 -> 21
depth 2 -> 81
depth >=3 -> 80
```

Snow is a second coherent family strictly inside the Rocky core:

```text
snow depth 1 -> 35
snow depth 2 -> 129
snow depth >=3 -> 128
```

## 4. No Swiss-cheese terrain

Validated correction:

- no Grass circles/pockets inside full mountain systems;
- no arbitrary Desert/Swamp/Water/River cells punching holes through a mountain;
- Desert and Swamp full-family masks must not contain accidental enclosed Grass holes;
- Snow may replace internal Rocky cells only through the legal `32→35→129→128` chain.

## 5. Micro-terrain cleanup

The native generator can create small **independent family components**, but it does not produce the huge number of one-cell **core-ID speckles** seen in early generated attempts.

Current policy:

- preserve legitimate native-style micro-components only when they are coherent complete transition structures;
- eliminate meaningless one-cell/near-one-cell `Rocky32`, `Desert64`, `Swamp80`, `Snow128` speckles;
- do not indiscriminately remove tiny transition IDs (`33/65/81/129`) when they are required to complete a legal HEX6 transition.

The validated cleanup reduced single-cell core artefacts to zero in the tested candidate.

## 6. Shore / water

- Shore48 is generated only from actual sea/lake geometry.
- No isolated Shore pixels in plains.
- Native 768 saves have zero one-cell Shore components.
- Water depth is derived from HEX6 distance to land; native 768 matches approximately:

```text
water_level = min(HEX_distance_to_land - 1, 7)
```

for roughly 99% of water cells.

At river mouths, tiny Shore fragments that are fully wedged between River/Water may be absorbed into the River rather than left as isolated beach pixels.

## 7. Rivers and family separation

Native 768 observations:

- Rivers may meet Grass16, Shore48 and shallow Water;
- Rivers do not directly cut through Mountain, Desert or Swamp families;
- all river cells use HEX6 connectivity;
- fish resource is **never** placed on terrain IDs `96..99`.

## 8. Validation checklist

Before accepting any generated EDM:

- `0` illegal HEX6 transition-neighbour violations;
- `0` interior mountain Grass pockets;
- `0` accidental full-family holes in Mountain/Desert/Swamp;
- `0` meaningless Snow128 micro-speckles;
- `0` Shore singletons;
- `0` fish/resource bytes on River96..99;
- transitions derived from masks, never independently painted.
