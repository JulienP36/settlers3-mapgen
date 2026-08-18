# Settlers III — Native Procedural Generator Reference v2

> **CANONICAL EMPIRICAL REFERENCE — COMPLETE 21-SAVE CORPUS — 2026-08-17**
>
> Purpose: record what the original Settlers III procedural generator actually produces, measured from native `.SAV` files. This is the principal behavioral reference for the custom MapGen engine. Binary SAV/EDM/MAP serialization is documented separately.

## 1. Corpus

The corpus now contains the complete requested **21 native saves**:
- sizes: `384, 448, 512, 576, 640, 704, 768`;
- one 4-player generation per size;
- one 8-player generation per size;
- one native-maximum generation per size (`8, 11, 15, 19, 20, 20, 20`).

For 384×384 the 8-player series and max series both contain 8 players, so they are statistically separate seeds but indistinguishable by player count alone.

All 21 SAVs use version 11, validate with the known checksum, parse sequentially to EOF, and expose one type-3 runtime-grid column per map column. Static-generation analysis uses height byte 4, runtime terrain byte 6 normalized with `28 -> Grass16`, static object byte 14, resource byte 17 and runtime claim byte 8.

## 2. Strongest native parameters

- **Effective ocean margin:** mean **40.26 cells**, σ=2.56, range 36.84–47.72. The 384 trio validates rather than refutes the constant-absolute-margin model.
- **Full mountain footprint:** **17.71% of land** on average, σ=0.223. This remains one of the most stable native proportions.
- **Inner mountain family:** **16.16% of land**; Rocky32 core **11.85%**; snow family **2.99%**.
- **Rocky mineral occupancy:** **53.00%**, σ=1.38, range 50.63–55.77. Roughly 47% of Rocky32 is intentionally empty.
- **Static-object density:** **12.26 objects / 1000 land cells**.
- **Grass relief target:** median orthogonal slope = 2 on all 21 maps; p90 is normally 5 (one 384 seed gives 4); p99 = 5 throughout. Perfectly flat 3×3 Grass patches are essentially absent.

## 3. Size scaling

| Size | samples | Water % map | effective margin | full mountain % land | Rocky mineralized % | Desert % | Swamp % | Mud % | Rivers % | objects/1000 land |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 384 | 3 | 38.23 | 41.10 | 17.31 | 53.21 | 2.84 | 0.267 | 0.246 | 3.42 | 11.22 |
| 448 | 3 | 32.46 | 39.92 | 17.70 | 53.20 | 3.72 | 0.548 | 0.528 | 2.50 | 12.28 |
| 512 | 3 | 29.67 | 41.36 | 17.70 | 52.92 | 3.71 | 0.416 | 0.474 | 2.43 | 12.14 |
| 576 | 3 | 25.39 | 39.24 | 17.86 | 53.71 | 3.41 | 0.533 | 0.646 | 2.13 | 12.44 |
| 640 | 3 | 22.92 | 39.05 | 17.75 | 52.00 | 3.95 | 0.498 | 0.557 | 2.03 | 12.38 |
| 704 | 3 | 21.49 | 40.12 | 17.86 | 53.79 | 4.20 | 0.440 | 0.740 | 1.95 | 12.67 |
| 768 | 3 | 20.22 | 41.01 | 17.82 | 52.16 | 3.90 | 0.458 | 0.434 | 1.87 | 12.68 |

### Ocean rule

The 384 samples are decisive: their mean water share is much higher than on large maps, but their derived absolute ocean margin remains near the same ~40-cell scale. Therefore **do not use one fixed water percentage across map sizes**. Generate a large land body constrained by a roughly constant absolute navigable-ocean envelope, with stochastic local deviations and irregular coastline morphology.

### River scaling

The 384 trio has **3.14–3.60% of land as river**, clearly above the large-map regime. River percentage decreases with size: the generator appears closer to an absolute/linear-count process than a pure area-density process. Our generator should therefore not simply multiply land area by one fixed river percentage.

## 4. Terrain/biome proportions — 21-map means

- Desert family: **3.676%**, range 2.244–4.765.
- Swamp family: **0.452%**, range 0.116–0.669.
- Mud family: **0.518%**, range 0.133–0.849.
- River terrain: **2.332%**, range 1.552–3.605.
- Inland water: **1.698%**, range 0.198–4.176.

These are distributions, not fixed quotas. Desert/Swamp/Mud fluctuate substantially between seeds. Mountains are far more stable and should be treated as the stronger structural target.

## 5. Minerals

Mean Rocky32 occupancy over all 21 maps: **53.00%**.

Pooled composition of all decoded native Rocky minerals:
- Coal: **50.19%** (174,500 cells)
- Iron: **21.56%** (74,978 cells)
- Gold: **14.42%** (50,127 cells)
- Gems: **5.45%** (18,936 cells)
- Sulfur: **8.39%** (29,164 cells)

The five quantity values continue to use low-nibble quantities 1..15 with an approximately flat distribution and mean near 8. This supports generating quantity independently from family, rather than making richer minerals systematically lower quantity.

**MapGen policy:** native composition is the default calibration. Any gameplay-driven rebalance must be an explicit archetype/profile deviation, not silently called 'native'.

## 6. Rivers

Pooled river-width composition:
- Width 1: **81.22%**
- Width 2: **15.94%**
- Width 3: **2.50%**
- Width 4: **0.35%**

Width 1 overwhelmingly dominates. Higher widths should appear as sparse local widening, not as equally common river classes.

## 7. Relief

- Grass↔Grass orthogonal slope median: **2** on every map.
- p90: normally **5**, with one 384 seed at 4.
- p99: **5** on all 21 maps.
- Rare maxima are not suitable generation targets; they can include special topology/runtime effects.
- Native plains are rolling rather than flat; exact-flat 3×3 Grass patches are effectively zero.

This means our earlier custom median≈3 target was somewhat rougher than the native bulk distribution. A native-faithful profile should target median≈2, p90≈5, p99≈5 while still preserving larger-scale relief.

## 8. Player starts

All expected starts are recovered from `terrain28 ∩ claim` across the complete corpus.

Nearest-neighbor spacing is primarily player-density dependent, not geography dependent.

- 4 players: mean nearest-neighbor / side = **0.277** over 7 map(s); mean r25 Grass-like share = 85.94%.
- 8 players: mean nearest-neighbor / side = **0.188** over 8 map(s); mean r25 Grass-like share = 84.09%.
- 11 players: mean nearest-neighbor / side = **0.169** over 1 map(s); mean r25 Grass-like share = 81.04%.
- 15 players: mean nearest-neighbor / side = **0.129** over 1 map(s); mean r25 Grass-like share = 84.71%.
- 19 players: mean nearest-neighbor / side = **0.136** over 1 map(s); mean r25 Grass-like share = 86.20%.
- 20 players: mean nearest-neighbor / side = **0.136** over 3 map(s); mean r25 Grass-like share = 85.37%.

The 384×384 4-player seed is notably denser than the larger 4-player seeds, showing that a single universal 4P ratio is insufficient near the minimum map size. Use a player-count + available-land candidate optimizer, not rigid polygons.

Across all maps/start positions, the map-level mean r25 Grass-like share averages **84.87%**. Native starts therefore do not require sterile all-Grass circles; nearby mountain, biome, water and river terrain is normal.

## 9. Static objects

Mean density: **12.26 / 1000 land cells**.

The earlier 18-map observation remains: object IDs 73–77 and 80–81 are very frequent in native output but are not yet correctly named in our editor object table. They should be calibrated before trying to reproduce native decorative-object distributions exactly. Small Tree 84 and Reefs 111–114 were absent from the 18-map large-size analysis; the 384 additions do not justify changing that conclusion without explicit per-ID validation.

## 10. Geography independence from player count

Comparing the 4P, 8P and max-player series shows no strong systematic player-count effect on global water, mountain share or Rocky mineral occupancy. The dominant player-count effect is on start selection/spacing and local runtime initialization.

**Generation architecture consequence:**
1. generate macro geography independently of player placement;
2. generate mountains/biomes/water/rivers/resources/objects;
3. choose starts from the completed terrain with adaptive fairness;
4. only then perform local player-specific validation/adjustment without deforming the global map.

## 11. 384×384 validation details

### `384_4_joueurs(3).sav`
- players: 4; water 37.32%; effective margin 40.00;
- full mountain 17.41% land; inner mountain 16.03%; Rocky core 11.93%;
- Rocky mineralized 54.21%; Desert 3.33%; Swamp 0.309%; Mud 0.386%; Rivers 3.14%;
- objects 12.02/1000 land; start nearest-neighbor/side 0.169; r25 Grass-like 81.56%.

### `384_8_joueurs(2).sav`
- players: 8; water 37.66%; effective margin 40.40;
- full mountain 17.39% land; inner mountain 15.74%; Rocky core 11.48%;
- Rocky mineralized 50.63%; Desert 2.24%; Swamp 0.375%; Mud 0.133%; Rivers 3.51%;
- objects 10.40/1000 land; start nearest-neighbor/side 0.183; r25 Grass-like 72.12%.

### `384_8_joueurs (2)(2).sav`
- players: 8; water 39.71%; effective margin 42.92;
- full mountain 17.13% land; inner mountain 15.27%; Rocky core 10.80%;
- Rocky mineralized 54.79%; Desert 2.95%; Swamp 0.116%; Mud 0.218%; Rivers 3.60%;
- objects 11.23/1000 land; start nearest-neighbor/side 0.168; r25 Grass-like 72.91%.

The 384 data validate the mountain/mineral models but reveal stronger small-map river density and larger seed-to-seed variation in water and start spacing.

## 12. Recommended native-faithful MapGen defaults

These are **starting distributions**, not hard constants:
- ocean envelope: absolute effective margin centered near **40.26 cells**, then irregularized by archetype/size;
- full mountain footprint: about **17.71% of land**;
- Rocky32 mineral occupancy: about **53.00%**;
- pooled mineral family mix: Coal 50.19, Iron 21.56, Gold 14.42, Gems 5.45, Sulfur 8.39%;
- mineral quantity: approximately uniform 1..15;
- Desert around 3.68% land, but allow wide per-seed variation;
- Swamp around 0.452% land; Mud around 0.518% for a truly native profile;
- river widths heavily dominated by Width 1; river *percentage* should decrease with map size rather than stay constant;
- Grass slopes: median≈2, p90≈5, p99≈5; essentially no perfectly flat 3×3 plains;
- static objects around **12.26/1000 land cells**, but exact family mix waits for IDs 73–77/80–81 calibration;
- starts: adaptive statistical fairness after final geography; never fixed quadrants/polygons and never large sterile circles.

## 13. Confidence / limitations

**High confidence:** map-size water scaling, ~40-cell effective ocean margin, mountain share, Rocky mineral occupancy, mineral family composition, Grass bulk slope distribution, river width hierarchy, player-count effect on start spacing.

**Medium confidence:** exact biome quotas, lake-count scaling, object-family composition, fish density, exact coast-complexity distributions. These are noisy across 21 seeds and/or affected by runtime representation.

**Not inferred here:** hidden random-generator algorithm, exact procedural noise functions, exact placement order, exact seed transform, or dynamic settlers/buildings. Those are outside current MapGen scope.

## 14. Update rule

When additional native maps are supplied, append raw per-map measurements first, then recompute aggregate distributions. Never replace observed ranges with a single tuned constant without retaining the corpus statistics.

This v2 supersedes `SETTLERS3_NATIVE_GENERATOR_REFERENCE_v1.md` for native-generation behavior.