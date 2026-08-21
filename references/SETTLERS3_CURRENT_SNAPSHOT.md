# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-21 — v1.7 DEV_11_R2 pre-RC**

## Repository model
`main` = STABLE, `rc` = candidate under validation, `dev` = active development/checkpoints.

## Stable baseline
- v1.6 STABLE published.
- Generation engine v1.5 remains validated/locked.
- Reference lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- Protected hashes are listed in root `PROJECT_WORKFLOW.md` and must remain unchanged.

## v1.7 current development — DEV_11_R2
v1.7 is the Stats/Graphs foundation release. DEV_10_R2 was user-validated and synchronized exactly to `dev` at commit `536b757` before DEV_11 work.

DEV_11 final pre-RC scope (R2 adds only the A/B Land tooltip wording fix + roadmap persistence):
- Dry/Yellow Grass Terrain ID24 is no longer hidden in Other terrain: analytical Grass = Green Grass ID16 + Dry Grass ID24.
- Terrain Families graph segments Grass exactly like Mountain/Water, with Green/Dry legend and contextual terrain IDs.
- Graph tooltips expose contextual IDs where meaningful: terrain IDs for terrain-family segments, Object IDs for forestry/building-stone/agriculture categories, resource IDs for minerals/fish. Global mining additionally reports the actual open-rock vs Snow-family terrain IDs for the hovered segment.
- Nearby generic resource charts intentionally remain uncluttered; nearby mining reports mineral resource IDs because the segments already distinguish mineral type.
- Statistics remains a structured user-facing FR/EN surface while retaining its technical/debug role.
- Stats schema v7.
- Future ideas are recorded in `TODO_MAPGEN.md`: DE/ES, two configurable proximity radii, histogram/radial-profile/optional chart variants, native-corpus boxplots, and uncertain long-range geometry/radar ideas.

DEV_11 is intended as the last feature DEV before a global v1.7 check and RC promotion if user validation passes.

## Object semantics
ID84 = `Pousse d’arbre` / `Tree sapling`. Never expose `SmallTree84` as user-facing name. Adult IDs with unresolved exact species remain generic adult trees.

## Immediate next step
- User-test DEV_11 specifically for Dry Grass segmentation, contextual tooltip IDs, and FR/EN Statistics behavior.
- If no blocker remains: run a global v1.7 release check, synchronize the validated DEV to `dev`, then enter the real `rc` branch phase.
- v1.7 RC is validation/fix-only: no new Stats/Graphs features unless a release blocker is found.

## After v1.7
- Do a short, selected TODO/UI pass without starting another large Stats release.
- **v1.8 target:** workflow tools around generation, especially Batch Generation (initially up to 4 maps), with direct A/B assignment and architecture reusable for later analysis.
- Then return strongly to the core generator: Continental multi-size 384 → 448 → 512 → 576 → 640 → 704 → 768, using the v1.7 Stats/Graphs foundation as calibration/debug tooling.
- **Multi-map comparison 3+ is planned at very high probability**, but deliberately after a major generator pass; it should become a dedicated analysis bench rather than overloading the existing A/B UX.
- **Modifiers / Modificateurs remain explicitly planned** as a later generator feature for strong/fun controlled variations; Batch + Stats + future multi-map comparison should make Modifier tuning and comparison much more powerful.
- Version numbers after v1.8 remain flexible: do not force v1.9 vs v2.0 until the actual generator scope is known.

## Recovery
1. read `PROJECT_WORKFLOW.md`;
2. read this snapshot;
3. read `TODO_MAPGEN.md`;
4. inspect latest DEV/RC notes and repository tip;
5. if touching generation, read `references/SETTLERS3_PREGEN_READ_FIRST.md`;
6. verify protected hashes/tests before packaging or promotion.
