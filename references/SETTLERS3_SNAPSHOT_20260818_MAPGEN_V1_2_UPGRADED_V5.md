# Settlers III MapGen — Snapshot V5 — Upgraded activated

Date: **2026-08-18**
Program state: **MapGen v1.2**

This snapshot supersedes V4 for program/mode state. Long-play V2, PREGEN and subsystem references remain the detailed historical sources.

## 1. Axes

- **Archetype** = macro-form only.
- **Generation Mode** = local morphology, terrain zones, relief, detailed hydrology, resources, objects, balance, starts strategy, validators.

Working modes:
- **Legacy** — existing native-faithful baseline.
- **Upgraded** — recovered custom validated project profile.
- **Custom** — reserved/manual future mode.

Current implemented archetype: **Continental**. Large Islands / Small Islands remain reserved.

## 2. Starts remain structurally early

Canonical order remains:
1. MapConfig;
2. Archetype macro-layout;
3. mode prepares startable terrain;
4. **place starts early**;
5. reserve technical zones;
6. detailed terrain/hydrology around starts;
7. global resources;
8. local start balance/bonuses;
9. objects/decor;
10. final hydrology + fish;
11. validators;
12. export.

Late passes may not invalidate a reserved start.

## 3. Upgraded now active

Upgraded v1.2 encodes the recovered long-play/custom rules instead of falling back silently to Legacy. Main 768 locks:
- 0 micro-water 1–4;
- River stop-at-first-Water, no orphan, max55;
- Water H0/access1, external edge deep Water7;
- Fish final layer, true Shore only, <=HEX12, 32,313 cells, +30% qty/cell, no River, no map-edge derived fish;
- Minerals v7 no-gap, exact family occupied-cell totals, +30% qty/cell;
- Snow from relief/summits p80/H135/depth4;
- 1,352 adult trees global, loose forest clustering, start bonus separate;
- SmallTree84=406 separate validated pool;
- Building Stone 1,683 global anchors / 14,160 global units, 53 units/player bonus, 7-cell footprint, min anchor HEX4;
- desert decor=60; swamp Reeds=2; pure decorative Stones1..28=89; reefs=11;
- no ordinary objects on Mountain;
- start mini-swamp + forest + stone bonus outside global quota.

Detailed executable mapping: `SETTLERS3_UPGRADED_RULE_MATRIX_v1.md`.

## 4. Morphology recovery status

To avoid another regression, Upgraded v1.2 **does not invent a new local-shape generator**. Continental 768 currently uses the validated `S3_Continental_4P_768x768_seed_2026081801_resourcepass_v8_relief_snow.edm` terrain/height as its executable morphology reference, with safe HEX-compatible transforms, then rebuilds starts/resources/objects/final hydro according to Upgraded.

This is transitional. Next morphology task: convert the validated/custom component shapes into a generalized Upgraded shape library compatible with any archetype, without changing the recovered gameplay validators.

## 5. Validation

Program-side tests completed:
- Upgraded 4P: all HARD validators PASS.
- Upgraded 20P: all HARD validators PASS.
- 20 starts survive the complete late pipeline statically.
- Legacy still generates.
- Custom still fails explicitly instead of fallback.
- Upgraded sample 20P: **35/35 PASS**, EDM/MAP export produced.

Official editor/game validation remains required. Static PASS does not prove official start acceptance or runtime Stone hitbox correctness.

## 6. Non-regression rule

A validated mode rule must exist in code as config, pipeline behavior, validator and/or test. Do not rely on conversation memory alone.

## 7. Visual policy

No imaginary images. GUI/PNG previews are deterministic renders of actual generated map data only.
