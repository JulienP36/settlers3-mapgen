# Settlers III MapGen v1.2

## Current status

The v1 GUI is intentionally kept simple and stable. v1.2 activates the second generation mode: **Upgraded**.

### Generation modes
- **Legacy** — native-faithful baseline / reverse-engineering mode.
- **Upgraded** — project custom/balanced rules recovered from checkpoints and long-play references.
- **Custom** — reserved, not implemented yet.

### Archetypes
- **Continental** — implemented.
- Large Islands / Small Islands — reserved for later.

## Start architecture
Starts are placed early, immediately after the macro layout, and their technical zones are reserved before later hydrology/objects. Late passes must adapt around starts rather than trying to fit starts into a finished map.

## Upgraded 768 profile
See `references/SETTLERS3_UPGRADED_RULE_MATRIX_v1.md`. The profile includes the custom fish/mineral stock rules, start bonuses, micro-water rule, river fixes, Snow rule, wood/SmallTree84, Building Stone footprint/stock, decorations and Upgraded-specific validators.

## Important morphology note
For this first executable Upgraded iteration, Continental 768 intentionally uses the canonical validated resourcepass-v8 terrain/height checkpoint as its local morphology reference. This prevents another accidental reimplementation of already validated shapes. Generalized fresh Upgraded morphology is the next terrain-generation task.

## Windows
First run: `install_and_run.bat` or `install_python_and_run.bat`. Later: `run_gui.bat`.

## Validation
Program validators are regression guards, not substitutes for the official Settlers III editor/game.
