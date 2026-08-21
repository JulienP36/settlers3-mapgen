# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-21 — v1.7 DEV_9**

## Repository model
`main` = STABLE, `rc` = candidate under validation, `dev` = active development/checkpoints.

## Stable baseline
- v1.6 STABLE published.
- Generation engine v1.5 remains validated/locked.
- Reference lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- Protected hashes are listed in root `PROJECT_WORKFLOW.md` and must remain unchanged.

## v1.7 current development — DEV_9
DEV_5 is a Stats/UI refactor based on DEV_4 user review.

Implemented:
- vertical charts for normal Stats (Y scale left, category labels bottom) ;
- terrain colors aligned with map palette where applicable ;
- segmented Water = Ocean + Lakes ;
- segmented Mountain = non-snow mountain + Snow family ;
- segmented mineral stock = outside Snow family + under Snow family ;
- Building Stone labels by real remaining stock (12 → 1 → exhausted), green→red gradient ;
- Forestry Resources replaces Vegetation as user-facing chart category ;
- Agriculture colors aligned with Agriculture view ;
- distance/resource gradients ;
- per-player R40 mining bar segmented by mineral type ;
- redundant nearby-mountain chart removed ;
- compact A/B chart: one metric row, A and B side-by-side, values inside bars ;
- height chart uses land-height distribution and omits global minimum ;
- report panes are read-only but selectable/copyable ;
- Stats cache misses during history/comparison are surfaced through existing task progress UI ;
- Stats schema v3 with exact split fields.

Validation:
- 49 automated tests PASS ;
- exact identities tested: Ocean+Lakes=Water, nonSnow+Snow=Mountain, open+snow mineral cells/stock=totals ;
- real SAV 768×768 / 10P smoke used for chart/data validation ;
- protected v1.5 engine remains untouched.

## Object semantics
ID84 = `Pousse d’arbre` / `Tree sapling`. Never expose `SmallTree84` as user-facing name. Adult IDs with unresolved exact species remain generic adult trees.

## Next Stats/UI work
- user test DEV_5 orientation/readability ;
- later replace exploratory R30/R40 emphasis with gameplay-calibrated near/strategic ranges, likely around 50/60 and 100 HEX after validation ;
- imported SAV/EDM/MAP in A/B comparison slots ;
- A/B customizable colors ;
- topographic-style Height view ;
- continued ID nomenclature ;
- future actual sprite labels only if real game sprites can be extracted properly ;
- native-corpus comparison bands/distributions.

After Stats: Continental multi-size 384 → 448 → 512 → 576 → 640 → 704 → 768, then v2.0 executable milestone.

## Recovery
1. read `PROJECT_WORKFLOW.md`;
2. read this snapshot;
3. read `TODO_MAPGEN.md`;
4. inspect latest DEV notes and `dev` tip;
5. if touching generation, read `references/SETTLERS3_PREGEN_READ_FIRST.md`;
6. verify protected hashes/tests before packaging or promotion.


### DEV_6 additions
- A/B compact rows now use semantic stacked segments where composition matters (water, mountain, forestry, mining, agriculture).
- Imported EDM/MAP/SAV comparison states preserve import semantics when toggling A/B.
- 51 automated tests PASS; real 768×768 / 10-player SAV visual smoke PASS.
- R60/R100 gameplay-distance calibration remains deliberately deferred to a dedicated pass.


### DEV_7 additions
- consolidation des retours DEV_5/DEV_6 ;
- gradients 3 couleurs rouge/jaune/vert ;
- labels extérieurs pour segments positifs trop petits ;
- ordre forestier Adultes → Palmiers → Pousses ;
- raccourci thème configurable Ctrl+Shift+T ;
- distances adversaires avec adversaire identifié + couleurs joueurs ;
- ressources locales étendues à 0–50 et 50–100 HEX ;
- minage local en deux barres par joueur ;
- gradients massifs/lacs/rivières inversés ;
- couleurs sémantiques A/B pour Terre/Pierre/Poisson ;
- Stats schema v4 ; 55 tests PASS ; smoke SAV réel 768/10P PASS ; hashes protégés inchangés.


## DEV_8 checkpoint
Focused polish from the DEV_7 user review: Shift/AZERTY shortcut fix, sun/moon theme button, tab order cleanup, stable outlined chart values, collision-aware tiny-segment annotations, concise snow/radius notes, explicit three-point stone gradient, player/opponent chart markers, grouped nearby-mining player labels and lightweight top-3 medals. Automated validation: 57 PASS; real 768×768 / 10P SAV chart smoke PASS.


## DEV_9 checkpoint
- Mini-polish only; generation engine v1.5 unchanged.
- External tiny-segment labels use left lane only.
- Nearby mining excludes Snow-family-covered ore; global mining decomposition unchanged.
- Nearest opponent cue: `→ [opponent color] Pn`.
- Top-three massifs/lakes/rivers use compact `# + medal` labels.
- Stats schema v5; 61 tests PASS; real SAV 768/10P chart smoke PASS.


## v1.7 DEV_10 — socle Stats/Graphs

- Révision DEV_10_R2 : tooltips persistants pendant le mouvement et sémantique détaillée par segment ; densités `/1000` affichées une par ligne.
- TODO conservé : tri des inventaires debug par quantité/ID/nom + IDs connus absents ; reset A/B individuel/global.
- Stats schema v6.
- Page Stats orientée debug : tous les Terrain IDs et Object IDs présents sont listés exhaustivement.
- Densités `/1000` normalisées par support pertinent.
- Tooltips génériques interactifs côté Graphiques.
- Slots A/B identifiables directement sur leurs boutons via LED verte + label court.
- Couplage Graphiques ↔ Map explicitement reporté à une itération ultérieure de v1.7 si utile ; pas requis pour fermer le socle.
