# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-20 — v1.7 DEV_5**

This file is updated in place. Dated `SETTLERS3_SNAPSHOT_*` files are historical and are not the current state.

## Repository / branches
Permanent model: `main` = STABLE, `rc` = candidate under validation, `dev` = current development/checkpoints.
Only `main`, `dev`, `rc` remain. `main` and `rc` still point to the v1.6 STABLE lineage. `dev` is the active v1.7 branch.

A Git-checkout launch failure caused by mixed-version files was diagnosed and repaired on `dev`: the old `gui_v15.py` expected `SessionGenerationCache(max_items=...)` while the newer cache API uses `max_entries`. The exact DEV_5 `gui_v15.py` was restored and a fresh `fetch/reset` checkout was confirmed to launch by the user.

Important: the exact runnable DEV_5 package remains `SETTLERS3_MAPGEN_V1_7_DEV_5_20260820.zip` (SHA-256 `115d056edbb90a5fde988d923f0045ca3d531208df895d5df449cf2133f253fb`). The branch is launchable again, but a final byte-for-byte synchronization audit against the large DEV_5 source files is still pending because the GitHub connector cannot directly ingest arbitrary local files and the runtime currently cannot resolve github.com via direct Git. `TODO_MAPGEN.md` tracks this explicitly.

## Stable engine
Generation engine v1.5 is validated and locked. Reference map lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
Protected hashes are listed in root `PROJECT_WORKFLOW.md`; all five remain unchanged after DEV_5.

## v1.6 STABLE
UI/tooling checkpoint validated. GitHub Release v1.6 published. The updater intentionally follows only GitHub `releases/latest`, not DEV/RC/main.

## v1.7 current work — Stats
DEV_1 introduced structured map statistics, JSON/CSV export and initial charts.
DEV_2 added Stats caching, horizontal charts, Unicode-capable fonts, terrain-family ordering, Mud, transition-family accounting and corrected adult-tree counting.
DEV_3 added the conservative latest-STABLE updater.
DEV_4 added local player analysis in true HEX radii 10/20/30/40 plus advanced connected-component/blob analysis and first A/B Stats graphing.

### DEV_5 additions
- Stats schema v3;
- normal charts switched to vertical bars for user testing;
- water segmented as Ocean + Inland water;
- mountain segmented as non-snow mountain + snow family;
- mineral stock/cells segmented as outside snow + under snow;
- Building Stones labels expressed by real remaining stock, 12 stones → 1 stone → depleted;
- Vegetation renamed to Forestry resources / Ressources forestières;
- agriculture colors aligned with the Agriculture view;
- player-distance and nearby-resource gradients;
- nearby R40 mining chart segmented by mineral family;
- redundant nearby-mountain chart removed from the catalog;
- height chart based on land-height distribution rather than the mechanically-zero global minimum;
- A/B compact comparison: one metric per row, A and B bars side by side, each value centered in its own bar;
- analysis text areas read-only but selectable/copyable;
- Stats cache misses from history/comparison tied into loading feedback;
- exact invariants verify that segmented chart components sum to their totals.

Validation of the exact DEV_5 package: **49 automated tests PASS**, real **768×768 / 10-player SAV smoke PASS**, protected v1.5 hashes unchanged, ZIP integrity verified.

## Naming / cleanup
Historical module names such as `gui_v15.py`, `gui_v16.py`, runtimes and `generator_v15.py` are ambiguous. The intended naming convention is explicit `v1_5` / `v1_6`. This is recorded as a controlled future refactor because imports, tests and entry points must migrate atomically; do not casually rename protected/validated files in isolation.

## Object semantics
User-facing name for object ID84 is **Pousse d’arbre / Tree sapling**, not `SmallTree84`. It is distinct from adult-tree quotas and the data model must allow future additional sapling types.
Adult-tree IDs validated/classified for Stats include 68–77 and 80–81; exact species names for 73–77/80–81 remain unresolved and must not be invented.

## Current priorities / next work
1. complete the DEV_5 package ↔ `dev` byte-for-byte source synchronization audit;
2. continue Stats/UI feedback from DEV_5;
3. later recalibrate start-resource distances toward gameplay-oriented ranges around ~50/60 HEX and ~100 HEX rather than treating DEV_4 R30/R40 as canonical;
4. support imported SAV/EDM/MAP in A/B slots;
5. continue component distributions, native-corpus reference bands and exact known-ID nomenclature;
6. after Stats: Continental multi-size validation 384 → 448 → 512 → 576 → 640 → 704 → 768, then v2.0 executable milestone.
