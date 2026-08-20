# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-20**
>
> This file is intentionally updated in place. Older dated `SETTLERS3_SNAPSHOT_*` files are historical checkpoints and must not be mistaken for the current project state.

## 1. Repository / branches

Permanent branch model:

- `main` = STABLE only;
- `rc` = current Release Candidate under validation;
- `dev` = current development and frequent recovery checkpoints.

Current branch state at snapshot creation:

- `main` → v1.6 STABLE lineage, commit `1ed1626492bb0df476d7f01f5528689fcdfb2a01`;
- `rc` → same v1.6 STABLE baseline, no v1.7 RC promoted yet;
- latest functional v1.7 code checkpoint before this documentation refresh: `39ca722d698f8b306c2732353d5b17aadc6bbea6` (`dev: checkpoint v1.7 DEV_3 stats and release updater`).

Use the current tip of `dev` as the authoritative development state; do not assume the SHA above remains the tip after documentation/checkpoint updates.

Only the three permanent branches should normally remain. Temporary branches must be audited before deletion.

## 2. Published stable state

Current published STABLE: **v1.6**.

Canonical local package produced/validated:

`SETTLERS3_MAPGEN_V1_6_STABLE_20260820.zip`

SHA-256:

`8b4da63d73c2dd6b9e32e555b47c77c9e06e87eae76016a7717c49a400a5b3a8`

v1.6 STABLE validation:

- 32 automated tests PASS at release checkpoint;
- dark/light UI validated;
- generation engine v1.5 preserved;
- Git tag `v1.6` and GitHub Release published.

The updater must use GitHub Releases only; DEV/RC branches are not update channels.

## 3. Protected generation engine

Generation baseline: **v1.5 validated/stable**.

Reference seed/map lineage:

`S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`

Protected SHA-256 values:

- `s3mapgen/generator_v15.py` — `3bbc9180719ebfae2bc37b29d81025731dc821e861c7b0e66894f7460f296090`
- `s3mapgen/generator.py` — `1b73f2536c6db75dfb3856a1667d0b619d3462d9c0efa14f406c78a05556be77`
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

Rule: Stats/UI/tooling work must not modify these files. If a hash changes unexpectedly, investigate before checkpointing.

## 4. Current development — v1.7 DEV_3

Current development focus: **GIGA Statistics / analysis tooling**, not generation changes.

Implemented by DEV_1 → DEV_3:

- structured statistics analysis for imported/generated maps;
- exact Terrain ID and Object ID counts;
- terrain families with transitions aggregated;
- Mud/Boue family included (`23/144/145`);
- mining statistics including occupied cells, real stock and percentiles;
- Building Stones `115..127` analysis with `127 = 0` exploitable stock;
- vegetation statistics separating adult trees and object ID84 saplings;
- hydrology/fish, agriculture/runtime SAV data, relief/height percentiles and start-distance statistics;
- JSON/CSV export;
- graph view and PNG export;
- graph orientation changed to horizontal bars;
- Unicode-capable chart font fallback for French accents;
- logical terrain-family graph ordering;
- dedicated Stats session cache to avoid recomputation during history/A/B switching;
- conservative `update_latest_release.bat` + PowerShell helper, querying GitHub Releases only and downloading STABLE ZIPs into `updates/` without automatic install.

Current automated suite at DEV_2/DEV_3 checkpoint: **42 tests PASS**.

Protected v1.5 hashes were verified unchanged after Stats/updater work.

## 5. Object/terrain semantics currently important

### Tree sapling ID84

Object ID `84` is visually and behaviorally identified as a **tree sapling / pousse d'arbre** that later grows into a tree.

Rules:

- user-facing text must say `Pousse d'arbre` / `Tree sapling`, not `SmallTree84`;
- it remains a separate pool from adult-tree quota;
- implementation may still use ID84 internally;
- design structures should allow additional sapling types later if discovered.

### Adult trees

Stats must include all currently validated adult-tree IDs used by the profiles. IDs whose exact species is not yet calibrated must be counted as adult trees without inventing species names.

Known Stats correction already applied: IDs `73..77` and `80..81` must not disappear from adult-tree totals simply because their species label is unresolved.

### Terrain families

Family statistics include transition cells, not just core terrain IDs.

Important aggregations currently locked for Stats:

- Desert: `20 + 65 + 64`;
- Swamp: `21 + 81 + 80`;
- Mud: `23 + 144 + 145`;
- Mountain family includes Rocky and its validated transition/snow chain;
- charts should display major families in an expected logical order rather than arbitrary ID/count order.

## 6. Current user feedback / pending refinements

Recent Stats feedback already addressed in DEV_2/DEV_3:

- A/B switching had slowed due to Stats recomputation → dedicated Stats cache added;
- missing adult-tree coverage → corrected without inventing species labels;
- graphs requested horizontal → done;
- French accents unsupported by chart font → Unicode-capable font fallback added;
- Mud missing from terrain-family graph → added;
- terrain families must include transitions → explicitly tested/locked.

Still pending or expected future refinement:

- complete nomenclature pass for known/unknown Object IDs, especially multiple adult-tree IDs;
- graph color redesign/palette pass;
- richer Stats UI and deeper spatial analysis;
- user visual/performance feedback on latest DEV after the above corrections.

## 7. Next Stats work

Planned next wave after current DEV feedback:

1. local player/start richness at HEX radii 10/20/30/40;
2. richer per-player balance comparison;
3. Stats A/B comparison tables and charts;
4. connected-component/blob analysis for Desert, Swamp, Mud, Rocky/Snow, forests, lakes and mineral clusters;
5. massif/lake/river size and morphology distributions;
6. density/percentile metrics and native-vs-MapGen comparison;
7. continue object/terrain nomenclature calibration without guessing unknown semantics.

Graphs are part of the current Stats phase, not postponed to a later unrelated version.

## 8. Longer roadmap

After the core Stats pass:

- Continental native-size validation one size at a time: `384 → 448 → 512 → 576 → 640 → 704 → 768`;
- validate starts, morphology, relief/snow, resources, objects, hydrology, quotas and editor/game stability at each size/player-count target;
- after complete Continental multi-size validation, prepare **v2.0** with first Windows executable/build pipeline;
- then Large Islands;
- then Small Islands.

## 9. SAV/runtime facts to preserve

For SAV v11 runtime type3 cells:

- cell size 24 bytes;
- byte6 terrain;
- byte7 current/runtime object;
- byte8 claim;
- byte14 static/persistent object;
- byte17 accessibility.

Agriculture/current-object analysis must use runtime byte7 where appropriate. Known agriculture groups include wheat `85..93`, vine `94..102`, rice `103..110`.

Original start territory reconstruction uses the player block / canonical native mask rather than an approximate ellipse.

## 10. Visual policy

Never use imaginary/generated Settlers III map images for project analysis or illustration.

Any map preview must be a deterministic rendering calculated from actual EDM/MAP/SAV data. Screenshots supplied by the user may be inspected directly.

## 11. Recovery checklist

When resuming after context loss:

1. checkout/inspect `dev`;
2. read root `PROJECT_WORKFLOW.md`;
3. read this file;
4. read `TODO_MAPGEN.md`;
5. inspect latest DEV notes and recent commits;
6. if touching generation, read `SETTLERS3_PREGEN_READ_FIRST.md` plus mandatory canonical references;
7. verify protected hashes and tests before risky changes;
8. continue from repository facts, not reconstructed chat memory.

## 12. Snapshot maintenance rule

Update this file whenever a meaningful checkpoint changes one or more of:

- current DEV/RC/STABLE status;
- branch strategy;
- validation/test status;
- protected baseline;
- newly locked semantics/rules;
- major known bugs or fixes;
- current next step/roadmap;
- files required for recovery.

Do **not** rewrite historical dated snapshots to look current. Keep those as historical evidence.
