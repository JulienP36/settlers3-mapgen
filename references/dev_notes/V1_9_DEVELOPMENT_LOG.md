# Settlers III MapGen — v1.9 development log

## DEV_1 — tolerant EDM terminal padding

Validated on Windows: 2026-08-26  
Tracking: GitHub Issue #4

- Reproduced `Part scan did not end at EOF` on two real EDM files supplied by
  the project owner.
- Confirmed valid version-10 structures and checksums; the files retain one or
  three opaque bytes after the terminal `type 0 / size 8` part to reach DWORD
  alignment.
- Read-only EDM/MAP import now accepts only the confirmed 1–3-byte terminal
  alignment case. Scaffold reconstruction remains strict.
- Both original files load under Windows: 256×256/20 starts and 768×768/10
  starts.
- 236 pytest tests, 49 engine validations, binary checksum, extracted package
  self-test and five protected hashes passed.
- The protected v1.5 generation engine was not modified.

DEV_1 closes the urgent import defect. The main v1.9 scope is now internal
restructuring; Data Mapping is deliberately moved toward the end of v1.9.

## DEV_2_R1 — first responsibility packages (replaced candidate)

Awaiting Windows validation; this suffixed revision remains local.

- Added the stable `s3mapgen/ui/` package family.
- Extracted theme palettes, inspector labels, deterministic icons and
  `ColorMenuSelect` from `gui_v16.py` without changing their public values or
  runtime behavior.
- Added mirrored `tests/ui/` families and replaced source-location assertions
  for the moved primitives with ownership and behavior checks.
- Pixel comparisons against `44dfb08` passed for 24 selector cases and six
  magnifier states; extracted catalogues are value-identical.
- Windows startup failed because the remaining local theme-toggle drawing still
  referenced `ImageDraw` after its import had been removed. R1 is rejected and
  replaced; do not reuse its archive or extracted folder.

## DEV_2_R2 — corrected first responsibility packages (local candidate)

Validated on Windows by the project owner; this suffixed revision remains local
because the complete DEV_2 scope is still open.

- Restores the required `ImageDraw` import.
- Adds a headless behavioral regression that executes the complete
  `_refresh_theme_button_icon()` path.
- Adds reproducible Ruff development tooling and makes `F821` undefined-name
  validation mandatory during structural moves.
- Uses a distinct version and archive-root name to prevent confusion with R1.
- 244 tests, `ruff --select F821`, runtime self-test and five protected hashes
  pass.
- The tested application functionality works under Windows; continue with the
  next modular extraction.

## DEV_2_R3 — feature-scoped UI catalogues (validated local slice)

Windows startup validated by the project owner; this suffixed revision remains
local because DEV_2 continues.

- Extracts shell, viewer, Batch, History, export and shortcut translations into
  independent `s3mapgen/ui/i18n/` modules.
- Moves viewer option order and selector colors to `ui/viewer/options.py`.
- Keeps temporary identity-preserving exports from `gui_v16.py` during the
  wider migration.
- All 22 compared catalogues are value- and order-identical to the pre-move
  implementation when evaluated with the same current version metadata.
- Adds mirrored ownership, four-language key, formatting-placeholder and view
  option-order tests.
- `gui_v16.py` is reduced from 2982 to 2697 lines.
- 248 tests, Ruff `F821`, source/package self-tests and protected hashes pass.

## DEV_2_R4 — stable application/generation names and window subsystems

Validated under Windows by the project owner; this suffixed revision remains
local because DEV_2 continues.

- Replaces the active GUI chain with responsibility names under
  `s3mapgen/application/`: base, settings, export, main window and runtime.
- Removes the obsolete `gui_v15_runtime.py`; no `gui.py` or `gui_v*` module
  remains active or packaged.
- Moves the complete protected generator lineage to `s3mapgen/generation/` as
  `base.py`, `continental.py` and `validated.py`; CLI and GUI share the public
  `generation.MapGenerator` boundary.
- Proves generation identity against the extracted R3 candidate for Legacy 4P
  and Upgraded 20P: map bytes, starts, validations and stage logs all match.
- Extracts the complete Batch and History/comparison method families into
  `application/batch/controller.py` and `application/history/controller.py`.
- Reduces `application/main_window.py` to about 1560 lines; viewer, analysis,
  exports, shortcuts/help and final shell flattening remain to be extracted.
- Migrates entrypoints, package checks and tests to stable module paths with no
  compatibility facade carrying an obsolete version number.

## DEV_2_R5 — explicit root boundaries (validated local slice)

Validated under Windows by the project owner; this suffixed revision remains
local because DEV_2 continues.

- Leaves only `__init__.py` and `version.py` at the `s3mapgen/` root.
- Moves strict generation vocabulary and morphology under `generation/`.
- Moves application paths, rendering, analysis, exports, platform integration,
  settings, shortcuts, session caches, diagnostics and CLI under
  responsibility packages in `application/`.
- Introduces `map_data/` as the intentionally shared lower layer for byte
  constants, `MapState`, HEX6 geometry and EDM/MAP/SAV binary formats.
- Adds architecture tests enforcing `map_data` independence and forbidding
  generation-to-application dependencies.
- Removes the obsolete `stats.py` compatibility facade; the base window now
  calls the explicit analysis contract.
- Confirms exact Legacy 4P and Upgraded 20P identity against the Windows-
  validated R4 archive: map bytes, starts, validations and stage logs match.
- Records a mandatory end-of-restructuring audit of context costs and project
  instructions before Data Mapping begins.

## DEV_2_R6 — application subsystem controllers (validated local slice)

Validated under Windows by the project owner; the application and tested
functionality remain operational. This suffixed revision stays local because
DEV_2 continues.

- Extracts Viewer, Analysis/Graphs, Exports and Shortcuts/Help into dedicated
  controller modules while preserving method bodies and host-state contracts.
- Moves shortcut bindings into their own package instead of keeping them under
  generic settings.
- Reduces `application/main_window.py` from about 1560 to about 860 lines and
  removes 48 compatibility imports that no longer belong to its runtime role.
- Replaces version-history test filenames with functional packages mirroring
  Batch, Viewer, Exports, History, Shortcuts, Shell, Platform and Diagnostics.
- Keeps the protected generation and map-data layers untouched.

## DEV_2_R7 — explicit shell composition (validated local slice)

Validated under Windows by the project owner; the application and tested
functionality remain operational. This suffixed revision stays local while the
test-suite relevance audit closes DEV_2.

- Deletes `base_window.py`, `settings_window.py` and `export_window.py` after
  replacing their few active responsibilities with explicit controllers and a
  single `ShellWindow` Tk foundation.
- Eliminates the temporary generator instance formerly created during base
  construction; `application.runtime.App` is the only engine factory.
- Extracts Imports, Tasks, the application-level generation workflow,
  Settings, Theme and Language switching without moving engine rules out of
  the strict `generation/` package.
- Renames the composed class to `MainWindow` and reduces its file to about 400
  lines of cohesive shell layout/state glue.
- Adds architecture contracts preventing the removed window layers and second
  generator factory from returning.

## DEV_2_R8 — current test contracts and direct shell construction

Validated under Windows by the project owner; the application, direct header,
simple generation/progress and exercised features remain operational.

- Audits all 250 R7 cases by responsibility and implementation style.
- Removes five proven duplicates/stale version checks and two tests that only
  preserved a disposable legacy header workaround.
- Renames every test function that still encoded an old DEV/R milestone and
  prevents historical revision names from returning.
- Makes `ShellWindow` initialize shared state and the common body directly;
  `MainWindow` now builds the only active header instead of destroying an older
  one immediately after construction.
- Removes the hidden obsolete header progress bar and unused task-dialog
  compatibility state. Progress remains in the active map overlay and Batch
  rows.
- Current result: 243 passing cases, 0 historical names, 0 exact duplicate test
  bodies. 87 source-shaped contracts remain, principally for headless GUI
  layout/wiring; their behavioral replacement stays explicit follow-up work.

## DEV_2 — final architecture and context audit

Validated under Windows by the project owner on 2026-08-27. The final
unsuffixed checkpoint is approved for publication on `dev`.

- Audits every short runtime module and both public entrypoints by ownership,
  import direction and callers. None is an artificial fragment worth merging:
  the smallest modules are package APIs, path/profile boundaries, catalogues or
  isolated subsystem controllers.
- Keeps Batch and History as explicit future widget-test targets. Their size is
  real, but splitting them now would only redistribute implicit Tk host state.
- Adds a compact root `AGENTS.md` as the automatically discovered instruction
  entry point and requires it in source packages.
- Reduces recommended ChatGPT Project instructions to a short pointer toward
  repository-owned guidance and routes new tasks through only the current
  snapshot and relevant TODO/reference.
- Consolidates the runtime version as `1.9 DEV_2`; no functional code differs
  from the Windows-validated R8 candidate.
- Records the release decision: v1.8 remains DEV-only and no new RC/STABLE is
  published until the generator's real morphology/diversity is fixed in v1.10.
