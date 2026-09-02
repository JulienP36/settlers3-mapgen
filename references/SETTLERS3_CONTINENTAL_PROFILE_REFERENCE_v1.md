# Settlers III — Continental Profile Reference v1

> **Current validated/accepted gameplay-generation profile — checkpoint 2026-08-18**
>
> This file contains the custom Continental choices layered on top of the native-generator morphology references.

## 1. Status

Validated/locked or accepted on the current 768 reference lineage:

- continent morphology;
- mountains;
- Desert;
- Swamp;
- lakes;
- rivers;
- terrain-transition cleanup;
- micro-terrain cleanup;
- Shore/water logic;
- decorative objects;
- adult wood + Small Tree84 profile;
- fish distribution;
- mineral distribution (v7 no-gap);
- summit-derived Snow (v8 accepted).

Next phase: **multi-size × multi-player-count validation**.

## 2. Continental terrain choices

- Mud: disabled.
- Swamp: current profile uses roughly native baseline × 1.30.
- Terrain families must be generated as coherent full-family masks.
- No Grass holes/circles inside mountains.
- No meaningless one-cell core terrain speckles.
- Shore only belongs to real sea/lake rims.
- Rivers use HEX6 connectivity and must connect to water.

## 3. Hydrology — 768 calibration

Native-like inland-water micro counts:

```text
1–4 cells  ≈ 28
5–9 cells  ≈ 6
10–19      ≈ 5
```

Simple river length target:

```text
p10 16
p25 18
p50 22
p75 29
p90 35
p95 ~40
p99 ~54.5
rare max ~70
```

## 4. Fish — 100% validated

Fish is a **uniform random sprinkle along all usable shores**, not correlated patches.

Rules:

```text
Water terrain only: IDs 0..7
River96..99: always 0 fish
HEX distance to shore/land >12: 0 fish
```

Validated 768 band occupancies:

```text
distance 1–3  : 68%
distance 4–6  : 55%
distance 7–9  : 40%
distance 10–12: 24%
distance >12  : 0%
```

On the accepted 768 lineage:

```text
total fish cells = 32313
deep fish = 0
fish on rivers = 0
```

Sampling must be independent/uniform within each distance band. Do not generate coherent fish zones.

## 5. Minerals — 100% validated v7 no-gap

Resource families:

```text
0x10 Coal
0x20 Iron
0x30 Gold
0x40 Gems
0x50 Sulfur
```

Family shares remain:

```text
Coal   50.186%
Iron   21.564%
Gold   14.417%
Gems    5.446%
Sulfur  8.388%
```

Accessible Rocky32 occupancy target:

```text
~80.08%
```

Ore may continue under Snow; Snow-covered ore is excluded from accessible-Rocky statistics.

### Validated geometry

Generate many **small elementary blobs**:

- solid/full;
- compact;
- mildly ovoid;
- modest variation in elongation/orientation;
- no internal holes;
- no singleton resource pixels;
- **no forced one-cell empty moat** between blobs;
- blobs may touch/merge naturally.

768 elementary-blob calibration before natural merging:

```text
Coal   ~500 elementary blobs
Iron   ~240
Gold   ~165
Gems    ~75
Sulfur ~100
```

Typical elementary size:

```text
roughly 18–105 cells
```

Connected components after touching can be larger. The no-gap version is the one explicitly validated by the user.

Validated 768 resource-cell totals:

```text
Coal   28375
Iron   12202
Gold    8164
Gems    3098
Sulfur  4745
```

Low-nibble quantity distribution remains native-like (`1..15`) and total resource stock must be preserved when only geometry is changed.

### Test de forme sans étirement

Le profil DEV_3 conserve exactement la version **v7 sans trou** et ne change
que le facteur de forme des blobs : `blob_aspect_min = 1.0` et
`blob_aspect_max = 1.0`. La priorité de croissance est désormais évaluée dans
l’espace compensé de la projection (`X=2x-y`, `Y=2y`) : les blobs sont ainsi
plus ronds dans l’aperçu parallélogramme, tandis que la projection reste une
option de rendu indépendante et ne modifie pas les données de la carte.

Cette variante validée peut être comparée à la forme ovale précédente sans
toucher aux quotas, aux quantités ni à la règle no-gap.

Le test DEV_3 utilise le nom court natif **Patch d’herbe rocheuse** pour le
terrain ID `34`. Il appartient à la famille Montagne et possède une teinte
jaune/olive discrète, distincte du cœur Roche dans les aperçus.

## 6. Snow — accepted relief/summit rule

Canonical detailed reference:
`SETTLERS3_SNOW_SUMMIT_REFERENCE_v1.md`.

Accepted 768 calibration:

```text
relative massif percentile = 80
absolute minimum height = 135
valid mountain HEX depth >=4
Snow cells = 11618 = 1.970% map
```

Snow is rebuilt from relief after the heightmap. It is **not** translated from old shapes.

## 7. Adult wood — validated

Confirmed adult tree IDs:

`68..72`

The custom Continental profile is **native adult-tree baseline × 1.30**.

For 768:

```text
native baseline ≈ 1040 adults
Continental adult target = 1352
```

Distribution:

- mixed small loose forests + scattered trees;
- forests must remain non-blocking / hitbox-aware;
- adult-cluster share calibration ≈ 44%;
- 38 small forest centers on the accepted 768 test;
- forest total object count roughly median 23, p90 32, max 36.

### Small Tree84

Separate bonus pool:

```text
SmallTree84 = 30% of adult-tree target
```

For 768:

```text
1352 adults -> 406 Small Tree84
```

Small Tree84 participates heavily in forest clusters but never replaces adult quota.

Accepted calibration:

```text
SmallTree84 cluster-oriented share ≈ 76%
```

## 8. Building Stones — current locked working profile

States:

```text
115 -> 12 units remaining
...
126 -> 1
127 -> 0 / exhausted
```

Formula:

```text
remaining = 127 - object_id
```

Anchor count stays near native density; increase **real stone stock by +30%**, mostly by fuller states rather than simply adding more blocking objects.

768 accepted working values:

```text
anchors = 1683
native stock baseline ≈ 10892 units
Continental stock = 14160 units (+30.004%)
```

Distribution:

- ~30% cluster-oriented;
- ~70% scattered;
- around 60 loose stone-cluster centers on 768;
- typical cluster ~8 anchors, p90 ~12, max ~14;
- balance players by actual stone units, not anchor count.

## 9. Decorations — validated

- Keep current decoration profile unchanged unless a new size exposes a scaling problem.
- Decorative Stones1..28 ≈ native observed amount / 10.
- Swamp decoration slightly boosted.
- Reefs: ~10–12 on 768, sparse, open-sea, nonblocking.
- No decorative/stone objects on Rocky terrain.
- Decoration legality always wins over quota.

## 10. Starts

Select/revalidate after final terrain, resources and blocking objects.

Known current accepted working coordinates on the 768 lineage:

```text
P1 (152,449)
P2 (590,578)
P3 (383,104)
P4 (383,578)
```

Important start lesson:

- fixed mountain distance is not a validity rule;
- native starts may be very close to mountains;
- immediate relief and local buildability matter.

Conservative candidate filter currently used:

```text
immediate HEX6 max |dH| <= 4
sum of six immediate |dH| <= 14
high local Grass fraction
no objects in immediate start core
reasonable resource opportunity
```

Do not flatten terrain around starts.

## 11. Scaling to other sizes

During the validation matrix:

- shape/morphology counts follow native size-specific references;
- adult-tree target = native adult density/target for that size × 1.30;
- SmallTree84 = 30% adult target;
- Building Stone anchor density follows native; real stock target = native stock density × 1.30;
- fish distance bands stay in **absolute HEX cells**;
- elementary mineral blob size should stay broadly absolute (gameplay-scale), while blob count scales with total ore area;
- Snow logic stays relief-based, initially using the accepted 768 thresholds.

Do not assume a scaling rule is validated until the multi-size tests pass.
