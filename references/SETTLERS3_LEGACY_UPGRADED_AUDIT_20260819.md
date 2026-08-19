# Settlers III MapGen — Legacy / Upgraded audit

Date: 2026-08-19
Status: **canonical mode-separation reference**

## 1. Architecture

- **Legacy**: reproduce the original Settlers III generator as closely as possible. Only bug/stability/start-validity fixes may deliberately improve native behavior.
- **Upgraded**: starts from the Legacy base, then applies explicit gameplay/aesthetic improvements.
- Macro morphology (continent, mountains, lakes and broad geography) may be shared.
- Future cross-cutting options are **modifiers**, not extra generator modes.

## 2. Common rules

- Starts are placed very early and protected from later passes. Current start placement is retained unless invalid/crashing seeds reappear.
- No artificial Grass circles or start flattening.
- Water/Snow accessibility fixes, valid metadata, Goods Default serialization and other stability fixes are common.
- Snow generation is common: `Rocky32 -> 35 (1 cell) -> 129 (1 cell) -> Snow128`.
- Terrain34 is a rare Rocky variant, valid only fully surrounded by Rocky32; it is not part of the Snow transition and may carry mineral resources.
- Fish remains coast-oriented in both modes as an intentional practical exception; no fish on Rivers.
- Reeds use native behavior in both modes; Swamp contains Reeds only.
- Small non-blocking vegetation (small plants, flowers, mushrooms/toadstools, bushes) uses native behavior in both modes.
- Desert content uses native behavior in both modes: Dead Trees 43..44, Cacti 45..48, Skeleton 49, Palms 78..79.
- Wrecks 29..33, Grave 34 object and Tree Stumps 41..42 use native behavior in both modes.
- Building Stone footprint/collision correctness is a shared bugfix.
- Building Stone resource states must stay visually/statistically varied; exact stock targets must never collapse all anchors to one object state.

## 3. Legacy-only/native behavior

- Minerals remain native-like; do not apply the Upgraded ore preset.
- Native 1..4-cell ponds are preserved.
- Rivers preserve native behavior; no custom trimming/cap pass.
- Mud is present according to native generation.
- Terrain24 yellow/dry Grass is generated using the already-derived native behavior.
- Swamp global amount remains native.
- Decorative stones 1..28 remain at native density.
- Reefs 111..114: **0 generated**.
- Tree pool uses the native full startup family `68..77 + 80..81`, with native proportions and volume.
- SmallTree84: **0 generated**.
- Building Stones use native density, stock and spatial behavior; no custom start bonus. State/remaining-stock values are varied approximately native-like while preserving the exact global stock target.
- No custom bonus swamp/forest/Building Stone package around starts.

## 4. Upgraded rules

### 4.1 Minerals

- Target about **90% of accessible Rocky** mineralized.
- Current empirical native family shares retained as calibration source, to be rounded later to deliberate simple ratios:
  - Coal 50.186%
  - Iron 21.564%
  - Gold 14.417%
  - Gems 5.446%
  - Sulfur 8.388%
- Geometry: validated **v7 no-gap** small solid compact blobs, no holes/singletons/forced empty moat; natural merging allowed.
- Quantity low nibble: about **+30%**, cap 15, mineral family unchanged.
- Ore may continue under Snow and on valid Terrain34.

### 4.2 Hydrology

- Remove inland Water components of 1..4 cells and redistribute their volume into existing larger lakes; never create replacement lakes solely to compensate.
- River trimming/cap is Upgraded-only and **size-scaled**.
- Native simple-path p99 by map size:
  - 384: 43.9
  - 448: 46.5
  - 512: 47.9
  - 576: 49.0
  - 640: 46.8
  - 704: 53.1
  - 768: 54.5
- Practical p99 fit for the Upgraded target: `river_p99_target(side) ~= 0.0245 * side + 34.7`.
- Treat this as a practical target, **not a strict absolute maximum**. Native rare tails reach about 46/62/51/52/52/64/70 cells respectively; allow occasional longer rivers up to a size-scaled rare-tail ceiling.
- Native topology constraints remain useful: straight runs normally <=3 and observed absolute max 4; turns use adjacent 60-degree HEX directions.

### 4.3 Biomes / objects

- Mud disabled.
- Swamp global amount about native x1.30; reeds themselves remain native-behavior.
- Terrain24 yellow Grass deliberately postponed for Upgraded. It is confirmed for future isolated integration, likely with the exact Legacy behavior.
- Decorative stones about native / 10.
- Reefs rare, open-water and navigation-safe (~10–12 on 768 as current working scale).
- Small non-blocking vegetation remains native-like, same as Legacy.
- Desert object behavior remains native-like, same as Legacy.

### 4.4 Trees / wood

- Base pool is the same native full tree family as Legacy: `68..77 + 80..81`.
- Palms 78..79 are harvestable trees and count toward wood quotas/statistics.
- Current Upgraded target: about **130% of the correct total native tree volume**, not merely 130% of IDs68..72.
- If visual tests become too forest-heavy, fallback is native/Legacy total volume while keeping the full ID pool.
- SmallTree84 remains a separate Upgraded bonus pool.
- Spatial behavior: mix small loose irregular forests with scattered trees.

### 4.5 Building Stones

- Same functional states 115..127 and `remaining = 127 - object_id`.
- Improved stock profile retained; spatial behavior mixes small clusters/fields with scattered anchors.
- Global Upgraded states must remain varied while being biased toward fuller stones; exact total stock is enforced by small per-anchor corrections, not by assigning one state to every anchor.
- Start bonus remains Upgraded-only and outside global quota.

### 4.6 Starts

- Early placement/protection architecture is common and currently considered stable.
- Mini-swamp, bonus forest and bonus Building Stones are Upgraded-only.
- Initial territory is modeled with a practical HEX radius of about **34** cells (consistent with the validated ~3500-cell starting territory). Bonus cluster centers sit on this boundary so the territory border passes through each cluster.
- **Bonus forest per player:** approximately one ordinary Upgraded forest-cluster volume, currently **41 adult trees + 21 SmallTree84**. This replaces the obsolete 15-tree sparse bonus. The cluster is loose/irregular, with the same overall scale as ordinary forest clusters.
- **Bonus Building Stone cluster per player:** **8 anchors**, matching the ordinary Upgraded cluster scale. Stones are deliberately well filled but still varied, with an exact target of **84 remaining stone units/player** (average 10.5/anchor, individual anchors constrained to 9..12 units).
- Bonus forests and stone clusters are outside the global quotas.

## 5. Future modifiers

Do not add a fourth generator called Barebone. Implement orthogonal modifiers combinable with Legacy or Upgraded.

Planned/possible modifiers:
- **Barebone**: remove only content that is purely cosmetic and has no gameplay function.
- **Forest density**: tune tree/forest density without changing the mode.
- **Starting crops** (experimental): pre-place wheat/vine/rice runtime-like content if technically sensible; investigate decay behavior first.
- Possible future mountain/realism modifier rather than silently diverging Upgraded Snow/mountain rules.

## 6. Explicit deferred items

- Integrate Terrain24 into Upgraded only in an isolated change/test.
- Validate the new Upgraded tree-volume calculation visually; revert volume to Legacy if too forest-heavy.
- Validate the new boundary-centered start forest/stone clusters on a freshly generated candidate before release promotion.
- Validate Building Stone state diversity visually/statistically in both Legacy and Upgraded.
- Validate all quotas/scaling across 384/448/512/576/640/704/768 rather than extrapolating blindly from 768.
- Validate desert/decorative multi-size scaling.
