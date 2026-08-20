# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-20 — v1.7 DEV_4 preparation**

This file is updated in place. Dated `SETTLERS3_SNAPSHOT_*` files are historical and are not the current state.

## Repository / branches
Permanent model: `main` = STABLE, `rc` = candidate under validation, `dev` = current development/checkpoints.
At the start of DEV_4: `main` and `rc` remain on the v1.6 STABLE lineage; `dev` contains v1.7 Stats/tooling work. Use the actual current tip of `dev` as authoritative.

## Stable engine
Generation engine v1.5 is validated and locked. Reference map lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
Protected hashes are listed in root `PROJECT_WORKFLOW.md`; all five still match after DEV_4.

## v1.6 STABLE
UI/tooling checkpoint validated. GitHub Release v1.6 published. The updater intentionally follows only GitHub `releases/latest`, not DEV/RC/main.

## v1.7 current work — Stats
DEV_1 introduced structured map statistics, JSON/CSV export and initial charts.
DEV_2 added Stats caching, horizontal charts, Unicode-capable fonts, terrain-family ordering, Mud, transition-family accounting and corrected adult-tree counting.
DEV_3 added conservative latest-STABLE updater.

### DEV_4 additions
- local per-player analysis in real HEX radii 10/20/30/40;
- adult trees, tree saplings, Building Stone anchors + real stock, fish cells + stock, mountain/desert/swamp/water cells per radius;
- per-mineral nearby cell counts + real stock;
- advanced component analysis for mountains, deserts, swamps, forests and mineral blobs: size, HEX perimeter, bbox, centroid, compactness and approximate elongation;
- richer river component statistics;
- charts for nearby trees R30, stone stock R30, fish stock R30, mining stock R40 and mountain access R40;
- charts for largest mountain/lake/river components;
- A/B Stats comparison chart using cached statistics for both slots;
- Stats schema version 2 and extended CSV player-local exports.

Real SAV smoke: 768×768 / 10 players parses and produces advanced Stats. Initial uncached advanced analysis is heavier than DEV_2 (~5 s on the current test environment), but A/B/history reuse the Stats LRU and do not recompute cached states.

## Object semantics
User-facing name for object ID84 is **Pousse d’arbre / Tree sapling**, not `SmallTree84`. It is distinct from adult-tree quotas and the data model must allow future additional sapling types.
Adult-tree IDs validated/classified for Stats include 68–77 and 80–81; exact species names for 73–77/80–81 remain unresolved and must not be invented.

## Current Stats priorities / next work
- refine/extend object-ID nomenclature from existing calibrated references;
- comparison A/B tables/deltas, not only graph;
- distributions/percentiles and richer reports for blobs/massifs/lakes/rivers/clusters;
- per-player agriculture/claims where runtime SAV supports it;
- native-corpus comparisons and reference bands;
- later chart palette redesign (palette is centralized already).

After the Stats pass: Continental multi-size validation 384 → 448 → 512 → 576 → 640 → 704 → 768, then v2.0 executable milestone.
