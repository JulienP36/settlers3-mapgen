# Settlers III Map Generator — Canonical Generation Reference v15

> **CANONICAL RULES. MUST BE READ VIA `SETTLERS3_PREGEN_READ_FIRST.md` BEFORE EVERY GENERATION OR MODIFICATION.**
>
> Checkpoint date: **2026-08-18**
>
> Canonical source of truth for generation/gameplay rules.
>
> Binary format: `SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md`  
> SAV decoding: `SETTLERS3_SAV_FORMAT_REFERENCE_v1.md`  
> Continental profile: `SETTLERS3_CONTINENTAL_PROFILE_REFERENCE_v1.md`

## 1. Objective / current phase

Generate playable Settlers III `.EDM` maps with native-like procedural geography.

Current archetype: **Continental**.

The 768×768 reference lineage has reached a strong accepted state. The next phase is not another 768 redesign: it is the **multi-size × multi-player-count validation matrix**.

After that matrix passes:
1. mark **Continental v1 validated**;
2. build **program/generator v1 with GUI**;
3. then add additional archetypes.

## 2. Source/visual policy

- Never use imaginary/generated artwork for this project.
- Every preview must be a deterministic rendering of actual EDM/MAP/SAV bytes.
- Unknown binary/object semantics stay unknown until calibrated.
- Native SAVs are empirical source material for static generator outputs.

## 3. Binary safety

- EDM/MAP version `10 / 0x0A`.
- Area cell = `[height, terrain, object_id, claim, accessibility, resource]`.
- Preserve unknown parts/bytes.
- Rolling-XOR encode modified payloads correctly.
- Recalculate checksum.
- Invalid start coordinates can produce `C0000005`.
- Player start selection/revalidation happens at the end.

## 4. Grid topology

Canonical topology is HEX6:

```text
(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)
```

Use HEX6 for:
- components;
- terrain-family depth;
- transitions;
- river connectivity;
- water/coast distance where topology matters;
- start-neighbour slope checks.

## 5. Current generation order

The Snow rule changes the order compared with older checkpoints.

1. Generate outer continent/ocean.
2. Add satellite islands.
3. Generate inland lakes.
4. Generate full Mountain-family masks **without Snow**.
5. Generate Desert and Swamp family masks.
6. Generate rivers.
7. Derive Mountain/Desert/Swamp transitions from HEX6 family depth.
8. Derive Shore and water levels from actual water geometry.
9. Generate the heightmap.
10. Rebuild Snow **from mountain relief/summits** and paint `32→35→129→128`.
11. Generate mineral resources, including allowed continuation under Snow.
12. Generate fish as coastal/riparian sprinkle.
13. Generate pure decorations.
14. Generate adult trees / SmallTree84 / Building Stones / palms.
15. Select and revalidate starts.
16. Run all topology/resource/object/start/checksum validators.

## 6. Terrain morphology — validated/locked

Validated forms:
- continent;
- Desert;
- Swamp;
- mountains;
- lakes;
- rivers.

Mountain Snow is now governed by relief rather than a separate independent morphology stamp.

Detailed references:
- `SETTLERS3_NATIVE_MORPHOLOGY_REFERENCE_21_v3.md`
- `SETTLERS3_NATIVE_TERRAIN_TRANSITIONS_21_v2.md`
- `SETTLERS3_SNOW_SUMMIT_REFERENCE_v1.md`

Current Continental choice:
- Mud disabled.
- Swamp ~native baseline ×1.30.

## 7. Transition invariants

```text
Grass16 -> 17 -> 33 -> Rocky32
Rocky32 -> 35 -> 129 -> Snow128
Grass16 -> 20 -> 65 -> Desert64
Grass16 -> 21 -> 81 -> Swamp80
Shore48 -> Water0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7
```

Required:
- coherent family mask first;
- no interior Grass circles in mountains;
- no accidental Desert/Swamp holes;
- no meaningless one-cell core speckles;
- no Shore singletons;
- 0 illegal transition-neighbour contacts.

## 8. Hydrology

768 reference:
- Water ≈ 20.2% map.
- Inland micro-water bins about `28 / 6 / 5` for `1–4 / 5–9 / 10–19`.
- Significant lake forms remain native-like and irregular.

Simple-river target:
`16 / 18 / 22 / 29 / 35 / ~40 / ~54.5` at p10/p25/p50/p75/p90/p95/p99.

Rivers:
- true HEX6 connected;
- all reach water;
- mostly Width1;
- curved/branched;
- never fish-bearing.

## 9. Heightmap

Canonical native statistics:
`SETTLERS3_NATIVE_HEIGHTMAP_REFERENCE_21_v3.md`.

Rules:
- adjacent same-family HEX6 p99 around 5;
- strong medium/large-scale relief amplitude;
- land rises away from coast;
- mountain height rises with massif depth;
- do not flatten starts artificially.

The current 768 geometry/relief lineage is accepted as the working baseline.

## 10. Snow — accepted

Generate only after the heightmap.

Canonical algorithm:
`SETTLERS3_SNOW_SUMMIT_REFERENCE_v1.md`.

768 calibration:
```text
massif relative percentile = 80
absolute minimum H = 135
valid mountain depth >=4
final Snow-family cells = 11618 (~1.970% map)
```

Snow may be less on a map if the relief does not justify more. Do not force a surface percentage.

## 11. Minerals — 100% validated

Validated choice: **v7 no-gap**.

- accessible Rocky32 occupancy ≈ 80.08%;
- ore can exist below Snow;
- family shares:
  Coal 50.186%, Iron 21.564%, Gold 14.417%, Gems 5.446%, Sulfur 8.388%;
- many small solid mildly-ovoid elementary blobs;
- elementary size roughly 18–105 cells;
- no internal holes/singletons;
- **no forced empty line/moat** between blobs;
- blobs may touch/merge naturally.

768 elementary count calibration:
`500 / 240 / 165 / 75 / 100` for Coal/Iron/Gold/Gems/Sulfur.

## 12. Fish — 100% validated

Uniform sprinkle, not patches:

```text
HEX shore distance 1–3   -> 68%
4–6   -> 55%
7–9   -> 40%
10–12 -> 24%
>12   -> 0
```

- Water0..7 only.
- River96..99 always 0.
- Independent/random placement across the whole coastline/lake-rim band.

## 13. Resource objects

Detailed custom profile:
`SETTLERS3_CONTINENTAL_PROFILE_REFERENCE_v1.md`.

### Adult trees
- confirmed IDs68..72;
- custom target = native adult baseline ×1.30;
- 768: `1352`;
- mixed small loose forests + scatter.

### Small Tree84
- separate bonus = 30% adults;
- 768: `406`;
- heavily participates in forests.

### Building Stones
- anchors near native density;
- stock units = `127-object_id`;
- target real stock = native stock ×1.30;
- 768: `1683 anchors / 14160 units`;
- loose clusters + scattered.

## 14. Decorations

Current decoration profile is validated and locked:
- Stone1..28 roughly native /10;
- terrain-support legality strict;
- swamp decoration slightly boosted;
- ~10–12 reefs on 768, open-ocean/nonblocking;
- no ordinary decor/resource objects on Rocky.

## 15. Starts

Choose after blockers/resources.

Current 768 working starts:
```text
P1 (152,449)
P2 (590,578)
P3 (383,104)
P4 (383,578)
```

Candidate filter:
- Grass center;
- strong local Grass/buildability;
- no immediate object blockers;
- conservative immediate HEX slope (`max |dH|<=4`, sum six `|dH|<=14`);
- reasonable resource access;
- no rigid geometric symmetry.

## 16. Current canonical binary checkpoint

`S3_Continental_4P_768x768_seed_2026081801_resourcepass_v8_relief_snow.edm`

It contains:
- validated no-gap minerals from v7 unchanged;
- validated fish unchanged;
- validated wood profile;
- +30% real Building Stone stock profile;
- accepted relief-derived summit Snow;
- current four starts;
- checksum valid.

## 17. Next validation matrix

Native sizes:
```text
384 -> max 8 players
448 -> max 11
512 -> max 15
576 -> max 19
640 -> max 20
704 -> max 20
768 -> max 20
```

For each size:
- generate multiple fresh seeds;
- test at least a low player count, 8 players where legal, and the native maximum;
- verify starts after final blockers;
- inspect geography/resource scaling;
- run static validators;
- test editor/game.

Custom 256/320 may be tested separately after native-size matrix.

## 18. Continental v1 exit criteria

Declare Continental v1 validated only when:
- morphology generalizes across native sizes;
- resources scale sensibly;
- Snow remains summit-logical;
- fish remains shore-useful;
- starts are accepted across tested player counts;
- no transition/object legality regressions/crashes.

Then begin the GUI program v1.
\n\n# 19. Checkpoint 384 start-first — VALIDÉ (2026-08-18)\n\n## 19.1 Référence binaire validée\n\nFichier canonique de ce jalon :\n\n`S3_Continental_4P_384x384_seed_2026081820_startfirst_v8_P1swampfix.edm`\n\nValidation utilisateur :\n- les 4 positions de départ sont valides dans l'éditeur ;\n- aucun crash `c0000005` en `View Map in-game` ;\n- forme du continent avec mer extérieure réduite validée ;\n- répartition start-first des joueurs validée ;\n- mini-marais bonus par joueur validés ;\n- bonus petite forêt + petit cluster de Building Stone par joueur validés après adoption du clustering normal ;\n- marais globaux plus nombreux, plus petits et mieux répartis validés ;\n- correctif final : suppression du composant de marais global de 19 cellules qui commençait à 4 HEX de P1.\n\n## 19.2 Architecture start-first verrouillée\n\nOrdre cible pour les prochaines tailles :\n1. générer la forme principale du continent / mer extérieure ;\n2. choisir les starts sur cette géographie en maximisant la dispersion / fair-play ;\n3. réserver seulement les contraintes techniques nécessaires aux starts, sans créer de disques de Grass visibles ;\n4. générer montagnes, biomes, hydrologie et relief autour des starts ;\n5. générer ressources globales puis compléter localement l'économie des starts ;\n6. placer objets / décorations en dernier, avec nettoyage technique proche du start.\n\nLes starts ne doivent plus être recherchés seulement à la fin d'une map déjà terminée. Ils deviennent une contrainte structurante de génération.\n\n## 19.3 Règles start validées sur 384 / 4P\n\n- Empreinte runtime native exacte : 33 cellules, entièrement Grass.\n- Relief local conservateur : amplitude de l'empreinte <= 10 ; voisinage immédiat conforme aux bornes déjà utilisées (`max |dH|<=4`, somme <=14).\n- Eau suffisamment éloignée ; les starts validés de la lignée stable sont dans un ordre de grandeur ~35–46 HEX de l'eau.\n- Objets statiques : nettoyage technique proche du start ; la dernière version validée conservait 0 objet dans r8 / zone technique immédiate.\n- Ne pas nettoyer le terrain en disque autour d'un joueur : aucune zone ne doit sembler découpée à l'emporte-pièce.\n- Montagnes / biomes / ressources peuvent exister à proximité tant qu'ils ne rendent pas le start invalide.\n\n## 19.4 Bonus économie de départ\n\nChaque start reçoit, EN PLUS du pool global :\n- une petite forêt proche ;\n- un petit cluster de Building Stone proche.\n\nCes bonus doivent utiliser la même logique d'espacement / clustering que les forêts et piles de pierres normales de la map. Ne pas faire de blobs ultra-serrés qui ignorent les hitboxes.\n\nLes ressources doivent rester naturelles et non symétriques ; l'objectif est l'équilibre des opportunités, pas une copie miroir.\n\n## 19.5 Marais\n\nDirection validée :\n- plus de petits marais distribués sur toute la map ;\n- réduire les très gros composants ;\n- mini-zone de marais bonus garantie à proximité raisonnable de chaque start pour le mana chinois ;\n- les marais bonus sont validés ;\n- les marais globaux ne doivent PAS entrer dans la zone technique proche des starts.\n\nCause du dernier `invalid position` de P1 : un composant de marais global de 19 cellules commençait à distance HEX 4. Aucun objet n'était présent sur ce composant. Après suppression de ce seul marais global, la map est entièrement validée.\n\nRègle à généraliser :\n**marais global interdit dans la zone technique locale d'un start ; seul le marais bonus contrôlé peut être présent dans le voisinage prévu.**\n\n## 19.6 Eau / marge / heightmap verrouillés pour la suite\n\n- Mer extérieure réduite par rapport aux anciennes Matrix A : forme validée.\n- Ne pas réduire les lacs pour gagner de la terre.\n- Zéro micro-étang 1–4 cellules.\n- Aucun lac / rivière ne remplace une montagne.\n- Marge océanique native construite dans la géographie, pas appliquée par découpe droite après coup.\n- Bathymétrie : Shore -> Water0 -> ... -> Water7, bord profond Water7.\n- Toutes les cellules Water0..7 à hauteur 0.\n- Pente HEX globale plafonnée à 5 dans la lignée stable.\n\n## 19.7 Prochaine étape\n\nReprendre la matrice native de tailles UNE MAP À LA FOIS, en commençant par :\n\n`448 x 448`\n\nPuis : 512, 576, 640, 704, 768.\n\nÀ chaque taille : priorité aux starts, stabilité éditeur / jeu, scaling naturel des couches et conservation des règles verrouillées ci-dessus.\n


---

## Post-checkpoint experiments — 2026-08-18

### Large Islands 384×384 / 4P

Prototype:
`S3_LargeIslands_4P_384x384_seed_2026081820_prototype_v1b.edm`

Result:
- Island sizes and shapes are already highly promising.
- Terrain balance between islands is poor and must be redesigned per island.
- P1 and P4 starts are invalid, likely from static objects too close to the start.
- No in-game crash.
- No dedicated profile exists yet. This section is the retained prototype
  evidence; create and validate a dedicated reference before implementing
  Large Islands.

### Continental 768×768 / 10P scale stress-test

Test:
`S3_Continental_10P_768x768_scale_stresstest_20260818.edm`

Positive validation:
- All 10 starts are valid in the editor.
- No in-game crash.
- The recent start-placement / player-initialization approach therefore scales promisingly to 10 players.

Important: this map is NOT a new canonical Continental baseline.
It regressed on previously locked geography/hydrology rules.

Mandatory Continental rules that must never be lost:
- No inland water components of 1–4 cells.
- Removed micro-pond water is redistributed into already-existing lakes larger than 4 cells.
- Do not create a new lake solely to compensate for removed micro-pond water.
- Native outer-ocean bathymetry remains Shore → Water0 → Water1 → … → Water7 toward deep sea.
- No shallow-water gradient at the external map edge; outer edge/rings remain deep Water7.
- Preserve the validated native ocean margin / keep the continent sufficiently far from the map edge.
- Preserve every other locked rule from the validated 384 start-first checkpoint unless explicitly superseded later.

Interpretation:
The 768/10P experiment validates start robustness and non-crashing player initialization at scale, not the geography of that stress-test.

---

## Continental 768×768 / 10P — validated short-form reference

Canonical tested file:
`S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v2_final.edm`

Status:
- 10/10 starts valid in the official editor.
- No crash in-game / View Map.
- User validates the map visually as "tout est nickel".
- This is the strongest **short-form** large-scale validation so far.

### Rules proven together on this 768/10P

- Start-first architecture scales to 10 players.
- Player placement remains globally dispersed/fair-play.
- No circular Grass clearing around starts.
- Static-object safety around starts is enforced while terrain remains natural.
- Start bonus resources remain **outside the global quota**.
- Start bonus forest + Building Stone volume is now **+50%** versus the original 384 bonus rule.
- Start bonus clusters use ordinary loose cluster spacing, not tightly packed hitbox-ignoring blobs.
- Each start has a clearly visible controlled mini-swamp bonus.
- Global swamps stay out of the technical local start zone.
- Global swamps are numerous, small and distributed.
- Desert decorative objects use **×2** the previous quota.
- Swamp decorative objects use **×2** the previous quota.
- No inland ponds/lakes of 1–4 cells.
- Removed micro-pond cells are redistributed only by growing existing lakes >4 cells.
- No compensation lake is created solely for removed micro-pond water.
- Bathymetry is Shore → Water0 → Water1 → … → Water7 toward deep water.
- External map edge remains deep Water7; no shallow edge gradient.
- Ocean margin is preserved.
- Do not clip a continent with a straight post-generation safety strip. Repel/generate the contour naturally inside the margin so the coastline remains irregular.
- Water0..7 height = 0.
- Global HEX-neighbor height delta <= 5.
- No mountain/water overlap.
- No fish on Rivers.
- No normal/decor/resource objects on Rocky.
- Preserve all other checkpoint-384 start-first rules unless explicitly superseded.

### Long-game validation pending

The user will:
1. use **Export Game Map File**,
2. play the resulting map as a normal game,
3. continue the match until victory,
4. provide a detailed gameplay report.

If completed successfully, record that as **long-form end-to-end validation**. It is a higher-confidence validation tier than editor-start checks, View Map, and short in-game smoke tests.

Do not label this map as long-game validated until that full playthrough report arrives.

---

# 20. LONG-PLAY SUPERSEDING RULES — 2026-08-18

> This section **supersedes conflicting older statements in this file**.
> The long-play has higher gameplay evidential value than short-form editor/View Map validation.

## 20.1 Current long-play lineage

Played MAP:
`1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v3_water_access_fix.map`

Current playthrough facts:
- Water walkability bug was fixed and runtime-validated.
- The played v3 map contains **zero fish**; the user intentionally continues the game without restarting.
- Therefore the current long-play is valid for geography, terrain, expansion, construction, wood, stones, minerals, rivers, accessibility and general AI behavior, but **not for fish economy**.
- A v4 fish-restored EDM/MAP exists for future generation/testing.

## 20.2 Water accessibility — HARD RUNTIME RULE

For every future EDM/MAP:
- `Water0..7 -> Area accessibility = 1`.
- Shore remains ordinary/passable unless an object blocks it.
- Rivers remain ordinary/passable unless an object blocks them.
- Reefs remain blocking according to their object calibration.
- After export, an immediate SAV sanity check should show runtime water walkability blocked.

This rule was validated in a real game: soldiers no longer walk on water.

## 20.3 Fish — HARD GENERATION + STOCK RULE

Spatial fish footprint:
- Water0..7 only.
- River96..99 always zero.
- Keep the validated coastal distribution.
- No fish beyond HEX12 from Shore.
- On the current 768 reference geometry, the spatial baseline is **32,313 fish-bearing cells**.
- Fish must be generated/rebuilt **after the final hydrology/coast/lake pass**.
- A future map with `fish_cells == 0` is an automatic generation failure.

New long-play stock rule:
- **Do not increase fish-bearing cell count.**
- Increase fish quantity per already fish-bearing cell by about **+30%**.
- Quantity is the low nibble `1..15`; target operation is approximately `round(q*1.30)` with saturation at `15`.
- If clipping prevents a true +30% total stock increase, report the achieved increase rather than changing spatial coverage.

## 20.4 Minerals — +30% STOCK, SAME OCCUPANCY

For future maps:
- Keep the existing mineralized-cell footprint/occupancy.
- Keep ore family in the high nibble.
- Increase low-nibble quantity per mineralized cell by about **+30%**, capped at `15`.
- Do not increase mountain area or mineralized-cell count to reach this stock increase.
- Preserve the current Coal/Iron/Gold/Gems/Sulfur family composition unless explicitly retuned later.
- Report achieved total-stock increase after saturation.

## 20.5 Rivers — orphan cleanup and size-dependent practical cap

After all lake/micro-water cleanup:
- Every River96..99 component/system must touch a valid Water0..7 body.
- Remove orphan river systems.
- Run this validator **after** deletion/redistribution of inland Water components 1..4.

Practical simple-river maximum by map size, calibrated from native p99:
- 384 -> **44**
- 448 -> **47**
- 512 -> **48**
- 576 -> **49**
- 640 -> **47**
- 704 -> **53**
- 768 -> **55**

Native absolute maxima (outliers only, never routine targets):
- 384 -> 46
- 448 -> 62
- 512 -> 51
- 576 -> 52
- 640 -> 52
- 704 -> 64
- 768 -> 70

Preserve the currently accepted river shapes/meandering:
- HEX6 only;
- map path one cell wide;
- River1..4 provide visual variation;
- straight-run practical ceiling ~3, absolute native corpus max 4;
- no 120/180-degree simple-path corners.

## 20.6 Building Stones — FOOTPRINT BUG FOUND IN LONG PLAY

Building Stone IDs:
- `115..126` active/minable stages;
- `127` exhausted/final stage.

Known calibrated accessibility/occupation footprint around anchor `X`:

```text
1 1 .
1 X 1
. 1 1
```

Seven occupied/accessibility cells total.

The current long-play map incorrectly serialized almost all Building Stones with accessibility active on the anchor only, rather than the complete 7-cell footprint.

Observed gameplay consequence:
- Several stones existed visually but could not be harvested.
- User-reported anchors included `(494,126)`, `(482,104)`, `(492,139)`.
- The issue also appears potentially across AI territories: many untouched stones coexist with already harvested stones in the same claims.
- Crucial controlled observation: stone anchor `(492,139)` was initially runtime stage `120`, could not be harvested while a building was adjacent, then after demolition of that adjacent building it advanced to runtime stage `125`.
- This strongly supports footprint overlap with building occupation/pathfinding as the cause.

Future mandatory placement rules:
1. Reserve/serialize the full 7-cell Building Stone footprint.
2. Reject stone-footprint vs stone-footprint collision.
3. Reject stone-footprint vs tree/decor/object collision.
4. Prevent building placement/occupation from overlapping the stone footprint.
5. Keep the footprint on legal ordinary terrain.
6. Validate real harvestability in controlled gameplay before declaring the corrected implementation final.
7. Start-bonus Building Stones must obey the exact same footprint rules as global stones.

Do not reduce stone supply merely to hide the bug; fix collision semantics.

## 20.7 Small Tree84 — LONG-PLAY VALIDATED

Long-play initial map contained **393 Small Tree84 anchors** in the analyzed lineage.

Advanced runtime analysis:
- `SmallTree84` still present as runtime ID84: **0**.
- The overwhelming majority evolved into tree runtime IDs or disappeared.
- Under the user-approved criterion, disappearance counts as successful growth followed by felling.
- 390/393 (~99.24%) fell cleanly into grown-tree/disappeared behavior; only 3 runtime states were atypical and none remained stuck as ID84.

Therefore:
- **Small Tree84 is validated for the current bonus-placement method.**
- Continue using it as a separate bonus pool.
- It does **not** replace the adult-tree quota.
- Do not generate unresolved IDs73..77/80..81 directly merely because SmallTree84 can evolve into related runtime tree states.

## 20.8 Final hydrology/resource order — HARD PRE-EXPORT CHECK

Recommended final pass:
1. finalize Water/Lakes;
2. remove inland Water components 1..4;
3. redistribute removed water only into existing lakes >4;
4. finalize Rivers;
5. remove orphan Rivers;
6. enforce size-specific practical river maximum;
7. rebuild Shore/bathymetry;
8. force Water0..7 height=0;
9. force Water0..7 accessibility=1;
10. rebuild Fish **after all hydrology changes**;
11. apply fish +30% quantity-per-cell rule;
12. apply mineral +30% quantity-per-cell rule;
13. serialize full object accessibility footprints, especially Building Stones;
14. run starts/object/terrain/topology/resource validators;
15. checksum;
16. export MAP;
17. immediate SAV runtime sanity checks.

## 20.9 Long-play validation hierarchy

Validation confidence tiers:
1. static parser/checksum;
2. official editor load;
3. View Map / smoke test;
4. immediate SAV runtime inspection;
5. long-play intermediate SAV analysis;
6. victory/end-to-end long-play.

A rule confirmed in long-play overrides an older assumption from a short-form/static-only test when they conflict.



---

## 24. Generator hardening after long-play — 2026-08-19

Latest explicit validation supersedes older start/accessibility details where they conflict.

### 24.1 Editor-safe starts

The exact native 33-cell Grass footprint and slope rules remain mandatory, but they are not sufficient for editor acceptance.
Generation must additionally select starts that already possess a conservative natural safety halo:

- no non-Grass terrain within the configured editor terrain halo;
- Water farther than the configured water halo;
- no static object within the configured object halo after all object passes;
- Building Stone validation applies to the complete 7-cell footprint, not only to its anchor;
- do **not** manufacture visible circular Grass clearings to satisfy these rules.

Current 768 conservative calibration: terrain halo 10 HEX, Water halo 20 HEX, object halo 14 HEX. These values are intentionally conservative and remain subject to official-editor validation.

### 24.2 Snow accessibility

Long-play on a generated map showed soldiers could cross full Snow, unlike standard native behavior. Native runtime SAV observations show the inner Snow family (`129`, `128`) in the non-walkable runtime navigation state, while the generated long-play retained the walkable mountain state.

Static generator rule: set accessibility = 1 on `Snow129` and `Snow128`, analogous to the validated Water accessibility correction. Keep `RockSnow35` as the outer traversable transition unless later native calibration proves otherwise.

### 24.3 Swamp transitions

All Swamp terrain must be derived from a coherent family mask and repainted by HEX depth:

```text
depth 1 -> Grass/Swamp transition 21
depth 2 -> Swamp transition 81
depth >=3 -> Swamp core 80
```

This applies to global Swamps and start bonus mini-Swamps. Manual independent painting of IDs `21/81/80` is forbidden. A hard validator must reject any illegal Swamp transition edge.
