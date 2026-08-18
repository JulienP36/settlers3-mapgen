# Settlers III MapGen v1.3.1 — Release validation

Date: 2026-08-18

## Scope of this patch
- Fix GUI preview crash caused by a missing `PIL.Image` import.
- Refresh README with a complete project presentation and current v1.3.1 status.
- No modification to Legacy or Upgraded generation rules/configuration.

## Targeted automated checks
- `tests/test_gui_regressions.py`: **PASS**.
- `s3mapgen` compileall: **PASS**.
- GUI module import: **PASS**.
- `Image.Resampling.NEAREST` available: **PASS**.
- Package version: `1.3.1`.

## Existing generation regression suite
A full `pytest -q` run was started in the execution environment. Five tests completed successfully before the environment timeout; no failure was observed before timeout. This patch does not modify the generation engine, profiles, resources, objects, starts or validators.

The previous v1.2/v1.3 generation validation remains the latest completed generation validation:
- Upgraded 4P HARD validators: PASS.
- Upgraded 20P HARD validators: PASS.
- Legacy generation: PASS.
- 20P Upgraded sample: 35/35 validators PASS.

## External validation still required
- User-side Windows GUI generation/preview smoke after this crash fix.
- Official editor/game validation remains required for generated maps as before.
