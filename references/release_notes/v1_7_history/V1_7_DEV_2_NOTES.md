# Settlers III MapGen v1.7 DEV_2 — Stats cache & chart polish

Date: 2026-08-20
Status: DEV

## Scope
- Session-only LRU cache for derived map statistics. Stats are computed once per map state and reused across history loads and A/B toggles.
- Correct adult-tree semantics from validated profiles: IDs 68–77 and 80–81 are adult trees; IDs 73–77 and 80–81 remain species-neutral until exact visual names are locked.
- Object 84 is exposed as Pousse d’arbre / Tree sapling.
- Terrain-family transitions are included in family totals. Mud family = terrain IDs 23, 144, 145.
- Horizontal charts with Unicode-capable system fonts and a centralized palette definition.

## Terrain chart order
Herbe → Montagne → Désert → Marais → Boue → Rivage → Rivière → Eau.

## Validation
- 42 pytest tests PASS.
- Real 768×768 / 10-player SAV stats smoke PASS.
- 7 charts rendered in French with accents.
- Protected v1.5 generator/config/library hashes unchanged.
