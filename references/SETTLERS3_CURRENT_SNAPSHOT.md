# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — READ AFTER `PROJECT_WORKFLOW.md` WHEN RESUMING WORK.**
>
> Last refreshed: **2026-08-21 — v1.7 STABLE**

## Repository model
`main` = STABLE, `rc` = candidate under validation, `dev` = active development/checkpoints.

## Stable baseline
- v1.6 STABLE published.
- Generation engine v1.5 remains validated/locked.
- Reference lineage: `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- Protected hashes are listed in root `PROJECT_WORKFLOW.md` and must remain unchanged.

## v1.7 current stable release — STABLE
v1.7 is the Stats/Graphs foundation release. DEV_10_R2 was user-validated and synchronized exactly to `dev` at commit `536b757` before DEV_11 work.

DEV_11 final pre-RC scope (R2 adds only the A/B Land tooltip wording fix + roadmap persistence):
- Dry/Yellow Grass Terrain ID24 is no longer hidden in Other terrain: analytical Grass = Green Grass ID16 + Dry Grass ID24.
- Terrain Families graph segments Grass exactly like Mountain/Water, with Green/Dry legend and contextual terrain IDs.
- Graph tooltips expose contextual IDs where meaningful: terrain IDs for terrain-family segments, Object IDs for forestry/building-stone/agriculture categories, resource IDs for minerals/fish. Global mining additionally reports the actual open-rock vs Snow-family terrain IDs for the hovered segment.
- Nearby generic resource charts intentionally remain uncluttered; nearby mining reports mineral resource IDs because the segments already distinguish mineral type.
- Statistics remains a structured user-facing FR/EN surface while retaining its technical/debug role.
- Stats schema v7.
- Future ideas are recorded in `TODO_MAPGEN.md`: DE/ES, two configurable proximity radii, histogram/radial-profile/optional chart variants, native-corpus boxplots, and uncertain long-range geometry/radar ideas.

DEV_11_R2 is the final feature DEV. RC_1 contained release-hygiene corrections only; after Windows validation, it was promoted to v1.7 STABLE with no feature changes.

## Object semantics
ID84 = `Pousse d’arbre` / `Tree sapling`. Never expose `SmallTree84` as user-facing name. Adult IDs with unresolved exact species remain generic adult trees.

## Immediate next step
- DEV_11_R2 user validation is complete and exact `dev` sync is at commit `5b04aa5`.
- Global pre-RC review completed: only stale release-title/documentation references were found and corrected in RC_1.
- v1.7 STABLE is frozen. New work belongs to the post-v1.7 TODO / v1.8 track.
- After user validation, promote to v1.7 STABLE, then update the full recovery checkpoint before post-v1.7 work.

## After v1.7
- Do a short, selected TODO/UI pass without starting another large Stats release.
- **v1.8 target:** workflow tools around generation, especially Batch Generation (initially up to 4 maps), with direct A/B assignment and architecture reusable for later analysis.
- Then return strongly to the core generator: Continental multi-size 384 → 448 → 512 → 576 → 640 → 704 → 768, using the v1.7 Stats/Graphs foundation as calibration/debug tooling.
- **Multi-map comparison 3+ is planned at very high probability**, but deliberately after a major generator pass; it should become a dedicated analysis bench rather than overloading the existing A/B UX.
- **Modifiers / Modificateurs remain explicitly planned** as a later generator feature for strong/fun controlled variations; Batch + Stats + future multi-map comparison should make Modifier tuning and comparison much more powerful.
- Version numbers after v1.8 remain flexible: do not force v1.9 vs v2.0 until the actual generator scope is known.
- Immediately after v1.7 STABLE, perform a small **GitHub discoverability/publication** pass: repository About/Topics, an English README entry point while preserving French, natural Settlers III / Settlers 3 / Siedler III + EDM/MAP/SAV terminology, and a proper STABLE GitHub Release. This is discoverability hygiene for interested players, not a marketing campaign. Community outreach remains optional.

## Recovery
1. read `PROJECT_WORKFLOW.md`;
2. read this snapshot;
3. read `TODO_MAPGEN.md`;
4. inspect latest DEV/RC notes and repository tip;
5. if touching generation, read `references/SETTLERS3_PREGEN_READ_FIRST.md`;
6. verify protected hashes/tests before packaging or promotion.
