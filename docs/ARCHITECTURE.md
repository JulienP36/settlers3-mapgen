# Settlers III MapGen — Architecture

This guide describes the current runtime without redefining the native rules under audit. v2.0 DEV_5 continues from the validated DEV_2 reset: obsolete Legacy generators remain removed, while the native Legacy v1 reconstruction stays in its own package beside the isolated Upgraded compatibility path. Before changing generation or binary-map behavior, follow the routed reading rules in `references/SETTLERS3_PREGEN_READ_FIRST.md`.

## Architectural boundary

The application is deliberately split into a protected generation core and an evolving UI/tooling shell.

- **Generation:** `s3mapgen/generation/`, with the native Legacy v1 and
  Upgraded compatibility paths isolated from one another.
- **Shared map data:** `s3mapgen/map_data/` owns the byte constants, `MapState`,
  HEX6 geometry and EDM/MAP/SAV binary boundary. It depends on neither the
  application nor generation.
- **Analysis and rendering:** `application/analysis/` and
  `application/rendering/`.
- **Desktop application:** `s3mapgen/application/`, history helpers, caches, preferences, shortcuts and export planning.
- **Entrypoints and packaging:** `run_gui.py`, `application/runtime.py`, `package_runtime.py` and `tools/package_source.py`.

The hashes and exact protected paths are canonical in `PROJECT_WORKFLOW.md`.

## Runtime entrypoints

| Entrypoint | Purpose |
|---|---|
| `run_gui.bat` | Normal Windows source launch. |
| `run_gui.py` | Selects the normal GUI runtime. |
| `run_gui.py --self-test` | Imports the real GUI dependency chain and validates required runtime resources without opening a window. |
| `run_cli.py` | Legacy command-line entrypoint; not the primary v1.8 user workflow. |
| `tools/package_source.py` | Builds and validates a deterministic source ZIP. |

`application.runtime.App` is the composition root. It injects the validated
mode-dispatching `generation.MapGenerator` facade into the desktop application.

## Current application composition

The numbered GUI filenames and the later temporary window inheritance chain
have both been removed. Composition is explicit and named by responsibility:

1. `application.shell.ShellWindow` — sole Tk foundation and base report tabs;
2. feature controllers — Viewer, Analysis, Exports, Imports, Shortcuts, Batch,
   History, Settings, Theme, Language, Tasks and application workflows;
3. `application.main_window.MainWindow` — controller composition and remaining
   responsive shell layout;
4. `application.runtime.App` — sole public application root and the only place
   constructing the validated generator.

Current follow-up hotspots after DEV_2:

- `application/main_window.py`: about 370 lines of cohesive construction,
  responsive layout, feedback and top-level state initialization;
- `application/shell/foundation.py`: shared Tk state/body only; it no longer
  constructs disposable header controls before the active header;
- `generation/generators/upgraded/`: an independent copy of the native terrain
  pipeline plus the retained Upgraded content routines; it never dispatches
  through `generation/generators/legacy/`;
- `generation/archetypes/continental.py`: neutral Continental context and
  six-channel state assembly; it does not own native resource or object rules;
- `generation/generators/legacy/`: the native Legacy implementation, split into
  terrain, global content, starts/transition handling, profile and validators;
- `generation/facade.py`: dispatches each mode to its own generator package;
- `application/history/controller.py` and `application/batch/controller.py`:
  the two largest UI subsystem controllers; both are already isolated from the
  main window and can be subdivided by window/state responsibility later.

Since R5, `s3mapgen/` itself contains only package metadata and version data.
Dependency direction is enforced by tests:

1. `map_data` imports neither `application` nor `generation`;
2. `generation` may use `map_data` but never `application`;
3. `application` may orchestrate both lower layers.

These measurements identify investigation targets, not pre-approved deletions.

### Generation ownership

The Continental archetype owns only macro-geographic context and neutral state
assembly. Legacy and Upgraded each own a complete generation pipeline. The
Upgraded copy starts from the native terrain sequence and then applies only
its explicit differences: calibrated minerals, fish, trees/decorations and
building stones, with Mud disabled. Player-start objects/resources, settlers
and SAV writing remain outside the current MAP/EDM generation scope.

The DEV_2 closing audit also reviewed the short modules and public entrypoints.
Their small size is not accidental fragmentation: they hold package APIs,
paths, profile loading, catalogues or isolated controller boundaries. Merging
them would either reverse a dependency or return unrelated state to the main
window. Batch and History remain large but should only be split together with
behavioral widget coverage for their Tk host-state contracts.

## Main data flows

### Generation

1. The GUI converts visible selections into a `GenerationCacheKey`.
2. A real cache hit reuses `GenerationOutput`; otherwise the protected generator runs synchronously.
3. `GenerationOutput` contains a `MapState`, validations and a stage log.
4. The result is displayed, analysed, rendered and offered to the session history.
5. Export uses the validated 768 scaffold as a deliberately test-oriented
   envelope for every currently supported native size; editor/game validation
   is still required for sizes outside 768×768.

### EDM/MAP import

1. `application.imports.ImportController.import_file()` selects `read_area()` and
   `read_starts()` from `map_data/binary.py`.
2. The parser decrypts parts, finds a compatible Area part and constructs `MapState`.
3. The current UI wraps the imported state in `GenerationOutput` without pretending generation validators were run.
4. `application.history.HistoryController` registers the result in the common session history using a content digest and source format.

### SAV import

1. `read_sav_state()` accepts the confirmed version-11 read-only path.
2. Supported static/runtime arrays, player starts and real claims are exposed through `MapState` and metadata.
3. Export may copy the original SAV unchanged; it never synthesizes a new SAV.

### Preview and analysis

`MapState.area` is the shared six-channel byte array.
`application/rendering/preview.py` derives deterministic raster layers, while
`application/analysis/core.py` derives structured statistics.
`SessionStatsCache` keys results by state identity so imported and generated
maps use the same analysis path.

## MapState channels

| Index | Property | Meaning |
|---:|---|---|
| 0 | `height` | Height byte. |
| 1 | `terrain` | Terrain ID. |
| 2 | `objects` | Static object ID. |
| 3 | `claim` | Territory/player claim; `255` is unclaimed in the current model. |
| 4 | `accessibility` | Accessibility byte. |
| 5 | `resources` | Resource ID/state byte. |

The model exposes views over one NumPy array. Code must avoid assuming that copying one property creates an independent map.

## History and protection semantics

`SessionGenerationCache` owns the real LRU eviction order and enforces a hard capacity. The GUI separately owns visual ordering and four contextual/manual roles:

- `V`: currently displayed map;
- `A` and `B`: comparison slots;
- `M`: explicit manual lock.

All four roles protect their attached outputs from ordinary eviction. Simple generation is the specific visible exception for a formerly displayed map: the new result becomes the Viewer automatically, so `V` moves to it before history retention is resolved. The previous Viewer may then be evicted if capacity is full and every other retained output remains protected. `M` is the persistent-for-session choice when a user wants a map to remain protected independently from Viewer navigation.

Visual order must not be used as LRU order. The pure rules live in
`application/history/order.py`; GUI navigation and A/B assignment are
observational and must not reorder the history.

## Runtime paths and user data

`application/paths.py` distinguishes source mode from PyInstaller mode:

- bundled resources are resolved from the repository root or `_MEIPASS`;
- source exports go to the repository `output/` directory;
- portable executable exports go beside the executable;
- persistent settings are handled separately by `preferences.py` under the user application-data location.

Self-tests must not write user settings or modify map resources.

## Safe change rules

- Add tests around behavior before flattening the remaining application chain.
- Keep `map_data`, generation, rendering, analysis and UI responsibilities separate.
- Do not add a second Batch generator or a second settings format.
- Do not infer unknown Terrain/Object IDs or unsupported binary structures.
- Do not mutate protected engine/config/data files without an explicit engine task.
- Do not use invented map imagery; previews and screenshots must come from actual generated or imported data.
- Update the living snapshot after every explicitly validated DEV stage and every RC/STABLE release.
