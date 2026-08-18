# Settlers III MapGen v1.3.2 — Release validation

Date: 2026-08-19

## Scope of this patch
- Harden start selection for official-editor acceptance: naturally clear Grass halo, greater Water clearance and strict static-object clearance.
- Keep all later object/resource passes outside the protected start halo, including full Building Stone footprints.
- Make inner Snow terrains `129/128` non-walkable through static accessibility, matching the runtime behavior observed on standard/native maps.
- Rebuild Swamp transition chains systematically as `Grass16 -> 21 -> 81 -> 80`, including start mini-swamps.
- Add hard validators for start clearances, Snow accessibility, and Desert/Swamp/Snow transition chains.
- Consolidate the old text TODO into `TODO_MAPGEN.md` and record the requested future UI/statistics work.

## Automated checks performed
- Python module compilation: PASS.
- Legacy 4P generation: completed with no HARD validator failure.
- Upgraded 4P generation: completed with no HARD validator failure.
- Upgraded 20P generation: completed with no HARD validator failure.
- Targeted regression tests: 5 focused generator tests PASS (Upgraded 4P, Upgraded 20P, Legacy 4P, editor-safe start halos, Snow/Swamp hardening).
- `SNOW_ACCESS`: enforced by a HARD validator.
- `SWAMP_TRANSITIONS`: enforced by a HARD validator.
- Start terrain/water/object halos: enforced by HARD validators.

## External validation still required
The three gameplay/editor corrections remain **candidate fixes** until validated in the official tools:
- repeated editor acceptance of generated starts;
- soldiers unable to enter full/inner Snow;
- visual inspection confirming no missing Swamp connector textures.

A static PASS is a non-regression guard, not a replacement for editor/game validation.
