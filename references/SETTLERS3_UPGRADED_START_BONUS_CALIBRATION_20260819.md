# Settlers III MapGen — Upgraded start bonus calibration

Date: 2026-08-19
Status: **locked working calibration after Legacy/Upgraded audit**

## Scope

This calibration applies only to **Upgraded**. Legacy receives no custom start resource package.

Starts remain placed early and protected by later passes. The bonus package remains outside global quotas and must not reshape the natural terrain into artificial Grass circles.

## Bonus forest

- Keep **15 mature/adult trees per player** as the explicit Upgraded start bonus.
- IDs are selected from the full native adult tree pool `68..77 + 80..81` using the Upgraded/native-derived weighting.
- The bonus is deliberately not increased after the global wood recalibration: Upgraded already generates about 130% of the correct native adult-tree volume plus the separate SmallTree84 pool, and global vegetation can also occur around the start outside the technical exclusion halo.
- Goal: a visibly useful small local forest without turning each start into an artificial dense wood ring.

## Building Stones

- Keep **5 Building Stone anchors per player**.
- Recalibrate every anchor to the fullest active state: `115`, i.e. **12 remaining stone units**.
- Therefore the explicit start bonus is **5 × 12 = 60 stone units per player**.
- This replaces the historical mixed stock `12 + 11 + 10 + 10 + 10 = 53`.
- The 60 units are outside the global Upgraded Building Stone stock quota.
- Full 7-cell footprint/collision validation remains mandatory.
- Placement stays as a small loose cluster/field near the start, outside the technical object-clearance zone.

## Mini-swamp

- One coherent visible mini-swamp per Upgraded start remains unchanged.
- It is separate from the global Swamp budget.

## Final Upgraded start package

Per player:

- 15 mature/adult bonus trees;
- 5 full Building Stones = 60 remaining units;
- 1 coherent mini-swamp;
- all outside global quotas;
- natural terrain preserved, no artificial Grass disc.

Revisit only if future multi-size calibration or editor/in-game tests show crowding, invalid starts, or excessive local advantage.
