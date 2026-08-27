# Settlers III MapGen — v1.9 DEV_2 architecture inventory

> Static inventory and behavior-preserving restructuring plan.
>
> Baseline inspected on 2026-08-26 from `dev` at commit `44dfb08`.
> This document does not approve a generation-rule or binary-format change.

## 1. Verified baseline

- Branch: `dev`, clean and synchronized with `origin/dev` at `44dfb08`.
- Runtime version: `1.9 DEV_1`; protected generation engine version: `1.5`.
- Automated baseline: `236 passed`.
- The five protected hashes match `PROJECT_WORKFLOW.md`.
- No active `DEV_CANDIDATE_NOTES.md` exists.
- Normal GUI entrypoint: `run_gui.py` -> `gui_v16_runtime.main()`.
- Normal CLI entrypoint: `run_cli.py` -> `cli.main()`.

## 2. Runtime layers

### 2.1 GUI composition

The current GUI is a five-level runtime chain:

1. `gui.App` creates the original Tk shell and an `engine.MapGenerator`.
2. `gui_v14.App` adds preferences, themes, projection and navigation.
3. `gui_v15.App` replaces the export workflow.
4. `gui_v16.App` adds the current application surface.
5. `gui_v16_runtime.App` replaces the generator with the protected
   `generator_v15.MapGenerator`.

The four `App` classes contain 256 distinct method names. `gui_v16.App` alone
contains 245 methods and overrides 26 inherited names. Its 3168 lines include:

- 338 lines of catalogues, labels, palettes and ID display tables;
- Tk image helpers and the `ColorMenuSelect` widget;
- main-window construction, responsive layout and task/status feedback;
- language, theme and preference orchestration;
- Statistics/Graphs coordination and two export centres;
- session history, cache roles, A/B comparison and the History Center;
- Batch creation, queue execution, thumbnails and large previews;
- viewer rendering, projection, zoom/pan and cell inspection;
- shortcut capture, validation and help.

Important coupling points:

- importing `gui_v16` mutates the `VIEWS` dictionary owned by `gui`;
- later classes assume many widget/state attributes created by earlier classes;
- runtime generator injection happens only after the inherited GUI constructor
  has already created the older `engine.MapGenerator`;
- compatibility imports expose GUI constants and methods directly to tests;
- 17 test modules inspect the literal source of `gui_v16.py`; several others
  import its tables or call methods on partially constructed `App` objects.

The source-text assertions preserved historical UI decisions, but they are a
refactoring obstacle: moving unchanged code can fail tests without changing
runtime behavior.

### 2.2 Generation composition

There are three generator classes, not two independent runtime engines:

1. `engine.MapGenerator` (770 lines) owns the complete base pipeline,
   `GenerationOutput`, common placement logic and validation.
2. `generator.MapGenerator` (776 lines) subclasses it and overrides 18 methods
   for the audited Legacy/Upgraded split and Continental morphology library.
3. `generator_v15.MapGenerator` (235 lines) subclasses `generator.MapGenerator`
   and applies the final v1.5 mineral, decoration and validation refinements.

Only `generator_v15.MapGenerator` is selected by the production GUI runtime and
CLI. `gui.App` still constructs `engine.MapGenerator` during initialization,
before the runtime wrapper replaces it.

`generator.py` and `generator_v15.py` are both covered by baseline hashes.
Although `engine.py` is not listed as a protected file, changing it can change
inherited production behavior. These hashes are regression alarms, not a ban
on intentional restructuring.

Conclusion: merging, renaming or deleting generator layers is not a blind
cleanup, but it is authorized as part of the v1.9 restructuring. The current
inheritance, output identity and runtime construction must first be
characterized. After a behavior-identical migration is proven, the canonical
paths and hashes are updated to protect the new stable architecture.

### 2.3 Responsibility-based modules already present

These modules have coherent boundaries and should remain separate unless later
evidence proves otherwise:

| Area | Modules | Assessment |
|---|---|---|
| Map model/formats | `model.py`, `binary.py` | Clear shared representation and binary boundary. |
| Rendering | `preview.py` | Deterministic renderer; large but cohesive. |
| Analysis | `stats_analysis.py`, `stats_charts.py`, `stats.py` | Analysis and raster charts are distinct; `stats.py` is a compatibility facade. |
| Session state | `session_cache.py`, `history_order.py` | Cache ownership and pure visual-order rules are correctly separated. |
| Preferences/input | `preferences.py`, `shortcuts.py` | Persistent settings and shortcut normalization are coherent. |
| Export planning | `export_center.py` | Small, pure and independently tested. |
| Platform/runtime | `app_paths.py`, `native_titlebar.py`, `package_runtime.py` | Separate filesystem, Windows and package concerns. |
| Generation vocabulary | `modes.py`, `archetypes.py`, `rules.py`, `profile.py` | Small but real domain concepts; size alone is not a reason to merge them. |
| Geometry | `hexgrid.py`, `morphology.py` | Reusable generation/analysis primitives. |

Potential compatibility shims to review later are `stats.py`,
`gui_v15_runtime.py` and the versioned GUI modules. They must not be removed
until all imports, packaged files and documented entrypoints have migrated.

## 3. Main architectural risks

1. **Behavior hidden in inheritance.** Moving an override can change method
   resolution or which inherited callback is bound during construction.
2. **State hidden on `self`.** History, Batch, preview and dialog code exchange
   state through many implicit attributes rather than explicit interfaces.
3. **Import-time mutation.** `gui_v16` changes `gui.VIEWS`, so import order is
   observable.
4. **Source-shaped tests.** Literal-source assertions can confuse structural
   movement with a regression.
5. **Protected generator inheritance.** An apparently local `engine.py` cleanup
   can alter v1.5 output through subclass dispatch.
6. **Display tables duplicated across layers.** Terrain/object names exist in
   GUI and Stats code. They must not be consolidated before the Data Mapping
   evidence is complete.
7. **Runtime/package compatibility.** `run_gui.py`, self-test, PyInstaller and
   source packaging explicitly name current modules.

## 4. Target architecture and context budget

The target is not a renamed monolith. It is a set of stable responsibility
packages that can be inspected and changed independently without loading the
whole application into working context.

```text
s3mapgen/
  ui/
    app.py                       final Tk composition root
    state.py                     explicit session/window state contracts
    shell/
      layout.py                  main window and responsive regions
      theme.py                   styles, palettes and native title bars
      feedback.py                task progress, status and feedback
      settings.py                settings tab and persistence orchestration
    viewer/
      controller.py              view selection, zoom/pan and invalidation
      inspector.py               source-cell inspection
    history/
      controller.py              cache roles, visual order and A/B links
      window.py                  History Center widgets and actions
      preview.py                 history thumbnails and large preview
    batch/
      controller.py              requests, queue, cancellation and results
      window.py                  Batch form and row state
      preview.py                 Batch thumbnails and large preview
    analysis/
      controller.py              Stats/Graphs UI coordination
      charts_tab.py              chart selection, refresh and tooltip regions
    exports/
      map_dialog.py              map export centre
      stats_dialog.py            statistics/chart export centre
    shortcuts/
      controller.py              bindings, capture and validation
      help_dialog.py             localized help window
    i18n/
      common.py                  shared labels and fallback helpers
      shell.py                   main-window and settings texts
      history.py                 history/comparison texts
      batch.py                   Batch texts
      exports.py                 export texts
      shortcuts.py               shortcut/help texts
    widgets/
      selectors.py               `ColorMenuSelect`
      icons.py                   deterministic Pillow/Tk icons
      tooltips.py                shared tooltip behavior
  generation/
    runtime.py                   one public protected-generator factory
```

The exact number of files is driven by responsibilities and dependency edges,
not by an arbitrary line quota. Small files are desirable when each one owns a
real concept, transformation, widget or state machine. A 50–150-line module is
not considered too small when its public contract is clear and it can be read,
tested and changed independently.

Related modules are grouped in a named package as soon as they form a coherent
family. Package boundaries should make future targeted reading obvious:
working on `ui/history/preview.py` must not require opening Batch, export or
shortcut implementations. Conversely, unrelated helpers are not collected in
generic `utils.py` or `helpers.py` dumping grounds.

Practical rules:

- one file per cohesive responsibility, even when the result is short;
- one directory per family of two or more cooperating responsibilities;
- explicit dependency direction between packages;
- minimal `__init__.py` files that expose only the intended public surface;
- domain-specific names instead of numbered, `misc`, `common` or catch-all
  modules, except for genuinely shared vocabulary;
- tests mirror the production families (`tests/ui/history/`,
  `tests/ui/batch/`, `tests/generation/`, and so on) after migration;
- avoid files that only forward every symbol or split one operation across
  several locations without an independent contract.

Most orchestration modules should naturally remain in the low hundreds of
lines, but this is an observation target rather than a limit. Translations are
split by feature so changing Batch does not require loading all History,
export and shortcut catalogues.

The versioned GUI names are migration inputs, not part of the target:

- `gui.py`, `gui_v14.py`, `gui_v15.py` and `gui_v16.py` are removed after their
  responsibilities and imports have migrated;
- `gui_v15_runtime.py` and `gui_v16_runtime.py` are replaced by a stable
  application entrypoint;
- `run_gui.py`, packaging, self-test, documentation and tests then reference
  only the stable modules;
- no `gui_v17.py` or permanent `legacy_gui.py` facade is introduced.

Temporary compatibility re-exports may exist inside local `DEV_2_Rn`
candidates to keep each move testable. They must be gone from the final DEV_2
unless a demonstrated external compatibility contract requires one.

Controller extraction may initially use narrowly scoped mixins to preserve Tk
method binding. A mixin is acceptable only with a documented host-state
contract and a planned composition endpoint; merely splitting a monolith into
equally implicit files is not the target state.

The generator is not exempt from stable naming. Its restructuring is isolated
from the GUI moves because its validation gate is heavier, but the final target
must also remove `generator_v15.py` as an active version-numbered module. The
validated implementation is moved into responsibility-based modules under
`s3mapgen/generation/`; the old path disappears after deterministic equivalence
is demonstrated and every runtime/package reference has migrated.

## 5. Characterization gates before movement

Add behavior-oriented tests for the current contracts before changing module
locations:

- runtime entrypoint selects `generator_v15.MapGenerator`;
- current construction order and generator replacement are recorded;
- language catalogues keep the same keys and formatting placeholders;
- preference load/save/debounce and destruction flush remain identical;
- view selection, render options and cache invalidation remain identical;
- history `V/A/B/M`, visual order, hard capacity and eviction transitions;
- Batch request validation, capacity forecast, cancellation and result roles;
- map/statistics export capability and path planning;
- public imports currently used by tests remain available during migration.

Tests that inspect source text should then be replaced or narrowed as their
corresponding behavior gets direct coverage. Historical intent remains in the
development log and focused test names, not in required line placement.

## 6. Proposed DEV sequence

### DEV_2 — complete GUI modularization

DEV_2 is one large behavior-preserving restructuring stage. Its intermediate
steps remain local suffixed candidates; they are not separate published DEV
checkpoints.

#### DEV_2_R1 — characterization and low-coupling data

- Add the first characterization gates.
- Extract feature-scoped translations, palettes, icons, selectors and
  tooltips.
- Preserve public values, order, formatting placeholders and visual drawing.

#### DEV_2_R2 — shell and viewer

- Extract main layout, responsive behavior, theme, status/task feedback,
  preferences, viewer navigation and inspector.
- Replace import-time `VIEWS` mutation with explicitly owned catalogue data.

#### DEV_2_R3 — History and comparison

- Extract History Center, large preview and A/B/manual-role coordination.
- Keep `SessionGenerationCache` and `history_order.py` as independent owners of
  cache and pure ordering rules.
- Document the host-state contract and preserve the accepted `V` exception.

#### DEV_2_R4 — Batch

- Extract Batch form, request validation, queue state and preview surfaces.
- Reuse the same generation service/cache path; do not create a second Batch
  generator.
- Preserve all seed, cancellation, capacity and auto-display semantics.

#### DEV_2_R5 — analysis, exports and shortcuts

- Extract Stats/Graphs UI orchestration, map/statistics export dialogs,
  shortcut capture and help.
- Keep `preview.py`, `stats_analysis.py`, `stats_charts.py` and
  `export_center.py` as non-UI-domain services.

#### DEV_2_R6 — final composition and stable names

- Make `ui.app.App` the sole real GUI class.
- Make the normal entrypoint use stable application/generation boundaries.
- Remove the inherited `gui -> gui_v14 -> gui_v15 -> gui_v16` construction
  path and the duplicate temporary generator construction.
- Migrate all package, self-test, test and documentation imports.

#### DEV_2_R7 — cleanup candidate

- Verify zero remaining references to versioned GUI modules.
- Remove the six obsolete GUI/runtime files.
- Remove temporary re-exports and obsolete source-location assertions.
- Run the complete automated/package validation and prepare the Windows
  checklist for final DEV_2 validation.

R8 completed the Windows validation of the restructured GUI. The unsuffixed
`v1.9 DEV_2` checkpoint is documented locally and will be pushed only after its
final package/title check.

### DEV_3 — generator-layer audit

- Record method ownership and `super()` dispatch across all three layers.
- Compare deterministic outputs, metadata, stage logs and validations for a
  fixed Legacy/Upgraded seed matrix.
- Split the pipeline into stable responsibility modules under
  `s3mapgen/generation/` and expose one explicit runtime/factory boundary.
- Remove the ambiguous `engine.py -> generator.py -> generator_v15.py`
  inheritance and versioned active filename without altering generated output.
- Migrate CLI, GUI, tests, package manifests and documentation, then remove the
  obsolete generator modules once reference scans and equivalence checks pass.
- Update `PROJECT_WORKFLOW.md` with the new canonical protected paths and hashes
  only after the restructured engine is validated.

### Later v1.9 DEV — remaining module/test cleanup, then Data Mapping

- Rename tests by subsystem only after the corresponding code settles.
- Remove proven-unused entrypoints/shims and update package manifests/docs.
- Audit small modules using responsibility and dependency evidence, not LOC.
- Begin Terrain/Object/SAV Data Mapping only after the restructuring is stable.

Later DEV numbers are planning labels, not promises. DEV_2 itself may use more
or fewer local `R` candidates, but its published endpoint remains the complete
stable-name GUI architecture rather than a partial versioned chain.

### Actual implementation update — R4/R8

The candidate order intentionally changed after Windows validation:

- R4 removed the numbered GUI/generator paths and extracted Batch plus History;
- R5 classified every remaining root module under `application/`,
  `generation/` or the shared lower-level `map_data/` package;
- R6 gives Viewer, Analysis/Graphs, Exports and Shortcuts/Help their own
  controller modules, removes obsolete main-window compatibility imports and
  organizes application tests by the same subsystem boundaries;
- R7 replaces the remaining `base_window -> settings_window -> export_window`
  inheritance with `application.shell.ShellWindow` and explicit Settings,
  Theme, Language, Imports, Tasks and workflow controllers;
- `application.main_window.MainWindow` is now the named controller composition,
  while `application.runtime.App` is the sole public root and generator factory;
- `application/main_window.py` is 398 lines, down from the 3168-line baseline,
  and the obsolete intermediate window files have been deleted;
- R8 removes the disposable foundation header/progress controls discovered by
  the test audit; `main_window.py` is now 372 lines and directly builds the sole
  active header.

### Closing audit — DEV_2

- Every short active module and both public entrypoints were traced through
  imports and callers. None is a merge candidate without weakening a real
  responsibility boundary.
- Tiny `__init__` modules intentionally define package APIs; `paths.py`,
  `profile.py`, i18n catalogues and the import controller each have independent
  ownership despite their low line count.
- Batch and History remain the largest GUI controllers. They are future
  subdivision candidates only after host-state expectations become behavioral
  widget tests; line count alone is not sufficient evidence.
- Root `AGENTS.md` becomes the compact automatic recovery entry point, while
  the workflow and living snapshot remain canonical detailed sources.

The responsibility target is unchanged; the suffix numbers in the proposal
above are historical planning labels only.

## 7. Validation contract for every extraction

1. Focused unit/characterization tests for the moved responsibility.
2. Ruff `F821` undefined-name validation after every import/dependency move.
3. Full pytest suite once for the candidate.
4. `run_gui.py --self-test` from source and extracted source ZIP.
5. Five protected hashes unchanged during GUI-only moves.
6. For generator restructuring: record the old hashes, run 49 engine
   validations, checksum and fixed deterministic output comparisons, then
   establish new canonical hashes after validation.
7. Windows checklist for the touched controls/dialogs plus a short general
   generation/import/export sanity pass.
8. No push of a suffixed `DEV_X_Rn`; publish only the validated unsuffixed DEV
   checkpoint with snapshot/TODO/log/changelog synchronized.

## 8. Explicit non-goals

- No generation-rule, morphology, resource, start or binary-format change.
- No Data Mapping during the first restructuring slices.
- No `gui_v17.py`.
- No version-numbered GUI module in the final DEV_2 architecture.
- No arbitrary micro-files that merely move implicit coupling elsewhere.
- No generator merge based only on similar method names or file sizes.
- No algorithm or output change hidden inside a structural generator move.
- No invented Terrain/Object ID knowledge.
- No imaginary or AI-generated Settlers III visual asset.
