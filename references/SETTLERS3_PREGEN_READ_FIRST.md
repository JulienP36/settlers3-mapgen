# Settlers III MapGen — PREGEN READ FIRST

> **MANDATORY ENTRY POINT BEFORE EVERY MAP GENERATION, REGENERATION, PATCH OR EXPORT.**
>
> Project-wide workflow is defined in root `PROJECT_WORKFLOW.md` and current resumable state in `references/SETTLERS3_CURRENT_SNAPSHOT.md`.
>
> Do not generate a map from conversation memory alone.
> Before touching map bytes, read the canonical files below and reconcile the requested change against them.

## A. Mandatory files — always read

0. `../PROJECT_WORKFLOW.md` and `SETTLERS3_CURRENT_SNAPSHOT.md`
   - Project workflow, protected baseline, branch/checkpoint policy and current working state.

1. `SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md`
   - Master generation/gameplay rules.
   - Later sections supersede older conflicting sections.

2. `SETTLERS3_RESOURCE_OBJECTS_REFERENCE_v3_LONGPLAY.md`
   - Trees, object ID84 tree saplings, Building Stones, mineral/fish stock changes.
   - Contains the corrected 7-cell Building Stone footprint rule.

3. `SETTLERS3_NATIVE_MORPHOLOGY_REFERENCE_21_v3.md`
   - Native terrain/component morphology.

4. `SETTLERS3_NATIVE_TERRAIN_TRANSITIONS_21_v2.md`
   - Legal transition topology.

5. `SETTLERS3_NATIVE_HEIGHTMAP_REFERENCE_21_v3.md`
   - Relief/slope statistics.

6. `SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md`
   - Binary writer/checksum/Area semantics.

7. `SETTLERS3_SAV_FORMAT_REFERENCE_v2_LONGPLAY.md`
   - Runtime verification and 16-save long-play findings.
   - Keep `SETTLERS3_SAV_FORMAT_REFERENCE_v1.md` as the original calibration baseline.

8. `SETTLERS3_TODO_POSTCHECKPOINT_v4_LONGPLAY.md`
   - Current unresolved work. A TODO must never silently override a validated rule.

## B. Read when the feature is touched

- Snow -> `SETTLERS3_SNOW_SUMMIT_REFERENCE_v1.md`
- Continental quotas/profile -> `SETTLERS3_CONTINENTAL_PROFILE_REFERENCE_v1.md`
- Native generator statistics / player scaling -> `SETTLERS3_NATIVE_GENERATOR_REFERENCE_v2.md`
- River topology/length study -> `native_generator_rivers_starts_deep_dive_v4.txt`
- Large Islands -> `SETTLERS3_LARGE_ISLANDS_PROFILE_REFERENCE_v1.md`
- 21-SAV exact corpus validation -> `SETTLERS3_NATIVE_21_SAV_MANIFEST_SHA256.txt`
- Recent long-game history -> `SETTLERS3_SNAPSHOT_20260818_LONGPLAY_V2.md`

## C. Supersession policy

When files disagree:
1. explicit latest user validation/long-play finding;
2. `SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md`;
3. dedicated latest canonical reference for that subsystem;
4. native empirical corpus;
5. older checkpoint/reference only for history.

Never silently revive an old rule just because an older script/checkpoint contains it.

## D. Mandatory pre-generation checklist

Before generating:
- [ ] Confirm requested archetype, size, player count.
- [ ] Read all files in section A.
- [ ] Read feature-specific files in section B.
- [ ] Resolve any conflicts using section C.
- [ ] Verify native maximum players for requested size.
- [ ] Preserve deterministic seed/output reporting.
- [ ] Never use imaginary/image-generated Settlers III visuals.

Before export:
- [ ] checksum valid.
- [ ] all starts valid under current start rules, including editor terrain/water/object safety halos.
- [ ] 0 ordinary objects on Rocky.
- [ ] Water0..7 height=0.
- [ ] Water0..7 accessibility=1.
- [ ] Snow129/Snow128 accessibility=1.
- [ ] 0 illegal Desert/Swamp/Snow transition-neighbour contacts.
- [ ] 0 inland Water components size1..4.
- [ ] 0 orphan River components.
- [ ] river practical max obeys map-size cap.
- [ ] fish_cells > 0.
- [ ] 0 fish on Rivers.
- [ ] fish only within validated shore distance profile.
- [ ] fish quantity +30% per occupied cell rule applied, without increasing fish-cell count.
- [ ] mineral quantity +30% per occupied cell rule applied, without increasing mineralized-cell count.
- [ ] every Building Stone uses full 7-cell footprint and collision checks.
- [ ] Object ID84 tree saplings remain a separate bonus pool.
- [ ] start bonus forest/stone outside global quota; current bonus volume +50% vs original 384 rule.
- [ ] controlled mini-swamp guaranteed per player.
- [ ] desert decorations x2 and swamp decorations x2 current rule.
- [ ] no straight post-generation coastline clipping.
- [ ] generate deterministic preview only from real EDM/MAP/SAV if requested.

After export:
- [ ] load official editor/game.
- [ ] create immediate SAV when practical.
- [ ] verify water runtime non-walkability.
- [ ] verify fish presence.
- [ ] verify Building Stone footprints/harvestability in controlled test until correction is fully validated.

## E. Non-negotiable workflow rule

**No future generation is considered correctly started until this file has been consulted.**
