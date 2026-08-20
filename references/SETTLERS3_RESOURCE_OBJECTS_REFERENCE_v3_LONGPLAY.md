# Settlers III — Resource Objects Reference v3 — Long-play update

Date: 2026-08-18
Status: **canonical resource-object supplement**
Read from: `SETTLERS3_PREGEN_READ_FIRST.md`

## 1. Adult trees
- Keep the validated current adult-tree quota/profile.
- Temperate adult generation uses confirmed IDs68..72.
- Other adult-tree IDs may exist and must be counted as adult trees once identified/validated even if their exact species label remains unresolved.
- Object ID84 is a **tree sapling / pousse d'arbre** and is separate from the adult-tree quota.

## 2. Tree sapling / pousse d'arbre — object ID84 — VALIDATED
Long-play result:
- Initial object ID84 sapling anchors analyzed: **393**.
- Runtime ID84 remaining in advanced save: **0**.
- 390/393 (~99.24%) evolved into tree-like runtime states or disappeared.
- Per user-approved interpretation, disappearance means the sapling successfully grew and was then felled.
- Therefore the current object ID84 sapling placement/use is **validated**.

Naming rule:
- User-facing UI, Stats and reports must use `Pousse d'arbre` / `Tree sapling` rather than `SmallTree84`.
- `ID84` may remain as an internal technical identifier in code/references where useful.
- Data structures should not assume ID84 is the only possible sapling type forever; additional sapling types may be added later if calibrated.

Generation rule:
- Continue current ID84 sapling bonus placement method.
- Keep saplings as a distinct bonus pool.
- Never subtract them from the adult-tree target.
- Do not invent exact species names for unresolved adult-tree IDs. Count them as adult trees until calibrated.

## 3. Building Stones — active IDs and stock
- Active/minable stages: `115..126`.
- Exhausted/final appearance: `127`.
- Stock units remain modeled as `127-object_id`.
- Keep global finite-stone supply and start bonus supply conceptually unchanged unless retuned explicitly.
- Start bonus stone is outside the global quota.

## 4. Building Stone footprint — CRITICAL CORRECTION

Calibrated footprint around anchor X:

```text
1 1 .
1 X 1
. 1 1
```

Seven occupied/accessibility cells.

Observed generator defect:
- Current long-play lineage typically serialized only the anchor as occupied/accessibility.
- This allows other runtime/building occupation to intrude on cells that should have been reserved for the stone.

Observed gameplay evidence:
- User reported non-harvestable stones near `(493,126)`, `(483,105)`, `(493,140)`.
- Actual anchors include `(494,126)`, `(482,104)`, `(492,139)`.
- In the latest controlled observation, `(492,139)` was stage120 while blocked by an adjacent building; after demolition of that building it advanced to stage125.
- This strongly supports footprint overlap/pathfinding/work-position conflict rather than corrupt stone ID/terrain.

Mandatory future algorithm:
1. Candidate stone anchor must be on legal ordinary terrain.
2. Build its complete 7-cell footprint.
3. All footprint cells must be in-bounds and legal.
4. Mark/serialize the required occupation/accessibility semantics on all footprint cells.
5. Reject collision with another stone footprint.
6. Reject collision with trees, decorations and other static objects.
7. Reject placement that would overlap technical start footprints.
8. Ensure later building-placement semantics cannot reuse those occupied cells.
9. Apply identical rules to start-bonus stones.
10. Validate in a controlled real game that a stone remains harvestable beside legal nearby construction.

Do not solve this by making stone fields artificially sparse. Native-like distance 3–4 between anchors can remain valid if footprints do not overlap.

## 5. Mineral stock — long-play adjustment
- Keep mineralized-cell footprint unchanged.
- Increase quantity low nibble by ~30%, cap15.
- Keep ore-family high nibble unchanged.
- Report achieved stock increase after clipping.

## 6. Fish stock — long-play adjustment
- Keep fish-bearing cell footprint unchanged.
- Fish Water0..7 only; River96..99 = 0.
- Increase fish quantity low nibble by ~30%, cap15.
- Rebuild fish only after final hydrology.
- `fish_cells == 0` is a hard generation failure.

## 7. Latest long-play files
- `slot 1(2).sav` — corrected-water beginning baseline.
- `slot 6.sav` / `slot 6(1).sav` — advanced analysis checkpoints.
- `slot 6(2).sav` — post-building-demolition observation.
- Latest save SHA-256: `0397cc782839a92ae7ef37b3bbd3bec3c4d5b520249c4e75610f9b6e3589ced9`
