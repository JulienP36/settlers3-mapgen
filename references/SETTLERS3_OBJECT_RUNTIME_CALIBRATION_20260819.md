# Settlers III — Runtime object calibration — 2026-08-19

Controlled visual calibration from the 256×256 unknown-object test maps, extended with binary analysis of the eight `Save 768 10P offensive (1)..(8)` long-play SAV snapshots.

## Scope

This reference intentionally distinguishes:
- static/editor object IDs already confirmed in `s3_object_ids_confirmed.csv`;
- internal/runtime object-state IDs which should not be emitted by the procedural map generator as ordinary static decorations without further evidence;
- runtime terrain/object fields observed in played SAVs.

## Tree-like internal variants

User visual identification:

| ID | Visual equivalence | Status |
|---:|---|---|
| 73 | resembles Elm 2 | internal/tree variant, exact semantics unknown |
| 74 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 75 | resembles Birch 2 | internal/tree variant, exact semantics unknown |
| 76 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 77 | resembles Birch 2 | internal/tree variant, exact semantics unknown |
| 80 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 81 | resembles Birch 2 | internal/tree variant, exact semantics unknown |

These IDs are visually identified as tree-family variants but are not added to the normal static tree pool yet.

## IDs 82 / 83 — PRESENT BUT STILL SEMANTICALLY UNKNOWN

Controlled editor calibration rendered IDs `82` and `83` invisibly, including a dedicated retry on Terrain28.

Long-play SAV analysis proves they are nevertheless present:
- byte-14 ID82: exactly 3 cells in every offensive snapshot;
- byte-14 ID83: exactly 3 cells in every offensive snapshot;
- coordinates remain fixed across all eight snapshots;
- dynamic cell byte7 is `0` at all six positions in all snapshots;
- their runtime terrain is initially mainly Terrain28 and progressively returns to Grass16 at several coordinates.

Therefore `82/83` are real persistent technical/static IDs, not unused values, but their exact visual/gameplay semantics remain unresolved. Their invisibility persists even when manually placed on Terrain28, so future work should decode them from SAV/runtime context rather than more static visual calibration.

## Wheat growth/runtime states — IDENTIFIED FAMILY

IDs `85..93` form a coherent **9-state wheat family/cycle**.

- `85..91`: successive wheat growth states.
- `92`: mature / harvestable wheat.
- `93`: **chaume** — post-harvest cut straw/stubble lying on the ground, temporary state before disappearing.

The family identification is visually confirmed.

### Long-play binary confirmation

In the offensive SAV series, dynamic cell **byte7** contains the wheat stages `85..93`. They are overwhelmingly associated with runtime **Terrain22**.

Dynamic wheat-state counts by snapshot:

| snapshot | wheat byte7 85..93 |
|---:|---:|
| 1 | 1048 |
| 2 | 957 |
| 3 | 923 |
| 4 | 772 |
| 5 | 628 |
| 6 | 461 |
| 7 | 380 |
| 8 | 332 |

The strong decline is consistent with abandoned/uncared-for agriculture progressively disappearing during long play.

## Grape/vine growth/runtime states — IDENTIFIED FAMILY

IDs `94..102` form a coherent **9-state grape/vine family/cycle**.

- `94..101`: successive vine/grape states.
- `102`: ninth vine-family state; visually resembles `94`.

All IDs `94..102` are considered identified as members of the grape/vine family.

### Long-play binary confirmation and 102/94 cycle evidence

Dynamic cell byte7 contains all vine stages `94..102`; they are overwhelmingly associated with runtime Terrain22.

Dynamic vine-state counts by snapshot:

| snapshot | vine byte7 94..102 | ID94 | ID102 |
|---:|---:|---:|---:|
| 1 | 254 | 29 | 33 |
| 2 | 247 | 28 | 34 |
| 3 | 230 | 15 | 22 |
| 4 | 205 | 22 | 31 |
| 5 | 168 | 17 | 26 |
| 6 | 150 | 22 | 18 |
| 7 | 160 | 18 | 21 |
| 8 | 269 | 33 | 26 |

Across consecutive snapshots at identical coordinates, direct vine-state transitions include:
- `102 -> 94`: 27 observed transitions;
- `94 -> 102`: 5 observed transitions;
- `98 -> 102`: 45 observed transitions;
- `102 -> 95`: 23;
- `102 -> 96`: 53;
- `102 -> 97`: 27;
- `102 -> 98`: 13.

Snapshots are far enough apart that intermediate stages may be skipped, so this is not a frame-by-frame transition graph. However, the repeated `102 -> 94/95/96/...` observations strongly support a cyclic persistent-vine interpretation rather than treating `102` as a terminal/destruction state.

## Rice growth/runtime states — IDENTIFIED FAMILY

IDs `103..110` are identified as members of the **rice growth/runtime family**.

Long-play SAV analysis gives an especially clean terrain correlation:
- dynamic byte7 rice IDs `103..110` are observed **exclusively on runtime Terrain21** in the eight offensive snapshots;
- Terrain21 count itself remains constant at 2364 cells across the series;
- dynamic rice-state count declines from 26 to 17 cells across snapshots.

This is strong empirical evidence that the live rice cycle is coupled to Terrain21 in this played map. Terrain21 is already part of the Swamp transition family (`Grass16 -> 21 -> 81 -> 80`), so future agriculture/runtime work must preserve the distinction between static swamp-family semantics and live rice use.

## Runtime Terrain22 — CULTIVATED/FIELD TERRAIN (STRONG)

Terrain22 was not part of the native static generator terrain catalogue but appears massively in the played offensive SAVs and is strongly correlated with wheat/vine runtime states.

Terrain22 counts:

| snapshot | Terrain22 cells |
|---:|---:|
| 1 | 5124 |
| 2 | 4751 |
| 3 | 4593 |
| 4 | 4000 |
| 5 | 3186 |
| 6 | 2382 |
| 7 | 2016 |
| 8 | 1783 |

This is a decline of about **65.2%** from snapshot 1 to 8.

Terrain22 decay between consecutive snapshots overwhelmingly returns to Grass16. Observed `22 -> 16` changes are:
`1015, 270, 943, 1009, 998, 443, 452` cells across the seven intervals.

Interpretation: Terrain22 is now a **strong candidate for cultivated/ploughed/field ground** created during agriculture and reverting to Grass when fields decay. Exact official game naming remains unknown and should not be invented.

## Runtime Terrain28 — PATH / TRAFFIC-WEAR TERRAIN (STRONG)

A dedicated editor calibration showed Terrain28 visually as path-like ground. This matches the user's known gameplay behavior: repeated settler traffic creates visible paths/tracks, and unused tracks can fade back into Grass.

The eight offensive SAVs strongly support that interpretation.

Terrain28 cell counts by snapshot:

| snapshot | Terrain28 cells |
|---:|---:|
| 1 | 73334 |
| 2 | 68075 |
| 3 | 66329 |
| 4 | 62714 |
| 5 | 58960 |
| 6 | 40351 |
| 7 | 36905 |
| 8 | 35893 |

Observed reversible Grass/28 transitions between consecutive snapshots:

| interval | Grass16 -> 28 | 28 -> Grass16 | 28 -> 28 |
|---|---:|---:|---:|
| 1 -> 2 | 6516 | 11783 | 61509 |
| 2 -> 3 | 2032 | 3779 | 64292 |
| 3 -> 4 | 6667 | 10276 | 56045 |
| 4 -> 5 | 1965 | 5728 | 56983 |
| 5 -> 6 | 4661 | 23281 | 35673 |
| 6 -> 7 | 1455 | 4898 | 35448 |
| 7 -> 8 | 9574 | 10575 | 26316 |

This bidirectional `16 <-> 28` behavior is exactly what is expected from traffic-wear paths that appear through use and fade when traffic stops. Snapshot-1 Terrain28 persistence also decays steadily: of 73334 initial cells, only 24043 are still Terrain28 by snapshot 8.

In snapshot 8, Terrain28 is overwhelmingly adjacent only to Terrain28 and Grass16, reinforcing that it is a Grass-derived runtime surface rather than a biome transition.

Decision: treat Terrain28 as **runtime path/traffic-wear terrain** with strong confidence. Do not generate it as static map geography; the game should create/remove it naturally from settler movement.

## Important SAV byte distinction

The played SAV series shows that crop stage tracking should focus on **runtime cell byte7**:
- byte7 carries dense, changing agricultural stage IDs `85..110`;
- byte14 can retain persistent/static object IDs at the same coordinates and should not be treated as the sole live growth-stage field in advanced SAV analysis.

This refines the earlier static-startup interpretation of byte14 as an exact MAP/static object copy: that statement remains useful for immediate-load/static correlation, but long-play crop/tree analysis must inspect byte7 as the primary dynamic object-state field.

## Generator decisions

- Do not deliberately generate IDs `73..110` as ordinary decorative/static objects in Upgraded.
- Keep the already-confirmed static tree pool (`68..72`, `78`, `79`, `84`) unchanged.
- Keep `82/83` unresolved but now mark them as **persistent observed technical/static IDs**, not absent/unused IDs.
- Treat `85..93` as wheat runtime states, including `93 = chaume`.
- Treat `94..102` as grape/vine runtime states; long-play evidence supports cyclic persistence after `102`.
- Treat `103..110` as rice runtime states strongly coupled to runtime Terrain21.
- Track Terrain22 explicitly in future SAV statistics as probable cultivated/field terrain.
- Treat Terrain28 as runtime path/traffic-wear terrain and let the engine create/remove it naturally.
- Do not add Terrain22 or Terrain28 to procedural static generation until a specific gameplay reason requires doing so.
