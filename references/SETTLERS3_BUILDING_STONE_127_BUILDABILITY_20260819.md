# Settlers III — Building Stone 13 / ID127 buildability

Date: 2026-08-19
Status: **canonical correction**

## Confirmed gameplay semantics

- Building Stones `115..126` are active resource states and retain the validated 7-cell blocking/buildability footprint while stone remains.
- Building Stone `127` is the exhausted/empty visual state with **0 remaining stone units** (`127 - 127 = 0`).
- Native generation may include ID127 directly (768 corpus: roughly 20 anchors/map).
- **ID127 is buildable/passable for construction purposes:** once a stone pile reaches the exhausted state, buildings may be placed over it.
- Therefore ID127 must **not** retain the active Building Stone blocking footprint/accessibility reservation.
- ID127 still counts as a generated Building Stone anchor for visual/density/state-distribution statistics, but never contributes to exploitable stone stock.
- Upgraded start-bonus stone clusters remain well-filled active states only; do not place ID127 in start bonus clusters.

## Generator requirement

When a generated global Building Stone anchor is assigned state `127`:
1. keep object ID `127` at its anchor for the visual exhausted pile;
2. clear the active 7-cell Building Stone accessibility/buildability footprint for that anchor;
3. exclude it from active stone-stock totals;
4. keep it in total-anchor and state-distribution counts.

Validation should explicitly check that every generated ID127 has a buildable footprint, while IDs115..126 retain their blocking footprint.
