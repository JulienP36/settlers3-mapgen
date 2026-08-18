# Settlers III MapGen v1 — release validation

Date: 2026-08-18

## Smoke matrix

- 768×768 / 4P / seed `2026081901`: **28/28 validations PASS**.
- 768×768 / 20P / seed `2026081902`: **28/28 validations PASS**.
- EDM binary export checksum: **PASS**.
- GUI module import: **PASS**.

## Hard checks currently enforced

- Water height/accessibility.
- Outer-frame bathymetry gradient.
- No inland Water components 1–4.
- River connection, stop-at-first-Water, length cap.
- Fish nonzero, Water-only, no River, actual Shore48 distance <=12, no map-edge-derived fish.
- Exact mineral family cell counts.
- No ordinary objects on Mountain.
- Adult tree quota range and Grass legality.
- Swamp decorations are Reeds only.
- SmallTree84 exact pool.
- Building Stone footprint, spacing, anchor quota, stock quota and Grass legality.
- Static start validity.

## Important

Passing these validators means the **program has applied its encoded rules consistently**. It does not replace official Settlers III editor/game validation. In particular, 20P metadata and exact remaining object hitboxes still need continued game-side testing.
