# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-21 — v1.7 DEV_7**

This file is updated in place. Dated `SETTLERS3_SNAPSHOT_*` files are historical and are not the current state.

## Repository / branches
Permanent model: `main` = STABLE, `rc` = candidate under validation, `dev` = current development/checkpoints. Only `main`, `dev`, `rc` remain. `main` and `rc` stay on the v1.6 STABLE lineage; `dev` is active v1.7 work.

Git checkout launch was repaired after mixed-version files caused `SessionGenerationCache(max_items=...)` / `max_entries` incompatibility. The branch is launchable again. The exact tested DEV package remains the canonical runnable checkpoint until the large-source byte-for-byte GitHub sync audit is completed.

## Stable engine
Generation engine v1.5 is validated and locked. Reference lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`. Protected hashes are listed in `PROJECT_WORKFLOW.md` and all five remain unchanged after DEV_7.

## v1.6 STABLE
UI/tooling checkpoint validated and GitHub Release published. Updater follows GitHub Releases only.

## v1.7 Stats progression
DEV_1 introduced structured Stats/JSON/CSV/charts. DEV_2 added Stats cache, Unicode fonts and corrected semantic groupings. DEV_3 added conservative updater. DEV_4 added true-HEX local player analysis and component/blob analysis. DEV_5 refactored chart orientation/segmentation/colors and read-only analysis panes. DEV_6 extended compact A/B with semantic stacked segments and preserved import semantics in A/B toggles.

### DEV_7 additions
- quantitative gradients standardized to red → yellow → green where appropriate;
- Building Stones gradient: full green → middle yellow → exhausted red;
- non-zero tiny stacked segments no longer silently lose their value: external connected labels are used when needed;
- Forestry order: Adult trees → Palms → Saplings;
- more descriptive short height labels;
- configurable `Ctrl+Shift+T` theme toggle;
- nearest-opponent chart now identifies the opponent and shows both player colors; min distance red, median zone yellow, max green;
- local analysis extended to HEX50 and HEX100 while retaining older radii internally for continuity;
- nearby Trees/Stones/Fish charts now show 0–50 and 50–100 segments;
- nearby Mining uses two bars/player: A ≤50 HEX, B 50–100 HEX, each segmented by mineral type;
- largest mountain/lake/river components are visually darkest;
- A/B Land/Stone/Fish now use semantic colors;
- Stats schema v4.

Validation: **55 automated tests PASS**, real **768×768 / 10-player SAV visual smoke PASS**, protected v1.5 hashes unchanged, ZIP integrity verified.

## Exact DEV_7 package
`SETTLERS3_MAPGEN_V1_7_DEV_7_20260821.zip`
SHA-256: `a045bea27adb42e3544f4d425cb339ac4d23daf83bf75dad2ccfa1bec7ce9079`

## Current next work
- user review of DEV_7;
- interactive graph tooltips as a later generalized graph capability;
- optional/disableable graph ↔ map-view synchronization;
- imported SAV/EDM/MAP in session history + configurable history capacity;
- PNG export sharpness/resolution;
- native-corpus comparison bands and remaining Stats analysis;
- controlled future rename `v15/v16` modules to explicit `v1_5/v1_6`;
- finish byte-for-byte audit/sync of GitHub large source files against the latest tested package.

After Stats: Continental multi-size validation 384 → 448 → 512 → 576 → 640 → 704 → 768, then v2.0 executable milestone.

## Recovery
1. read `PROJECT_WORKFLOW.md`;
2. read this snapshot;
3. read `TODO_MAPGEN.md`;
4. inspect latest DEV notes and `dev` tip;
5. if touching generation, read `references/SETTLERS3_PREGEN_READ_FIRST.md`;
6. verify protected hashes/tests before packaging or promotion.
