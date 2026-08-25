# Settlers III MapGen — Architecture

This guide describes the current v1.8 runtime without redefining the validated generation rules. Before changing generation or binary-map behavior, read `references/SETTLERS3_PREGEN_READ_FIRST.md` and every reference it requires.

## Architectural boundary

The application is deliberately split into a protected generation core and an evolving UI/tooling shell.

- **Protected engine:** `s3mapgen/generator_v15.py`, its compatibility wrapper, the two validated profiles and the native static library.
- **Map representation and formats:** `s3mapgen/model.py` and `s3mapgen/binary.py`.
- **Analysis and rendering:** `stats_analysis.py`, `stats_charts.py` and `preview.py`.
- **Session/UI tooling:** `gui_v16.py`, history helpers, caches, preferences, shortcuts and export planning.
- **Entrypoints and packaging:** `run_gui.py`, `gui_v16_runtime.py`, `package_runtime.py` and `tools/package_source.py`.

The hashes and exact protected paths are canonical in `PROJECT_WORKFLOW.md`.

## Runtime entrypoints

| Entrypoint | Purpose |
|---|---|
| `run_gui.bat` | Normal Windows source launch. |
| `run_gui.py` | Selects the normal GUI runtime. |
| `run_gui.py --self-test` | Imports the real GUI dependency chain and validates required runtime resources without opening a window. |
| `run_cli.py` | Legacy command-line entrypoint; not the primary v1.8 user workflow. |
| `tools/package_source.py` | Builds and validates a deterministic source ZIP. |

`gui_v16_runtime.App` is the composition root. It injects the protected v1.5 `MapGenerator` into the current v1.8 UI.

## GUI inheritance chain

The current interface evolved incrementally and therefore retains a compatibility inheritance chain:

1. `gui.App` — original generation/import/export shell;
2. `gui_v14.App` — themes, projection, navigation and persisted settings;
3. `gui_v15.App` — stable v1.5 export shell;
4. `gui_v16.App` — current analysis, Batch, history, translations and production tooling;
5. `gui_v16_runtime.App` — binds the protected v1.5 generator and runtime resources.

This structure is historical, not a recommendation to add another layer for every release. A future flattening must preserve behavior with tests before removing compatibility methods.

## Main data flows

### Generation

1. The GUI converts visible selections into a `GenerationCacheKey`.
2. A real cache hit reuses `GenerationOutput`; otherwise the protected generator runs synchronously.
3. `GenerationOutput` contains a `MapState`, validations and a stage log.
4. The result is displayed, analysed, rendered and offered to the session history.
5. Export uses validated scaffolds only when the map size and requested format are supported.

### EDM/MAP import

1. `gui.App.import_file()` selects `read_area()` and `read_starts()` from `binary.py`.
2. The parser decrypts parts, finds a compatible Area part and constructs `MapState`.
3. The current UI wraps the imported state in `GenerationOutput` without pretending generation validators were run.
4. `gui_v16.App` registers the result in the common session history using a content digest and source format.

### SAV import

1. `read_sav_state()` accepts the confirmed version-11 read-only path.
2. Supported static/runtime arrays, player starts and real claims are exposed through `MapState` and metadata.
3. Export may copy the original SAV unchanged; it never synthesizes a new SAV.

### Preview and analysis

`MapState.area` is the shared six-channel byte array. `preview.py` derives deterministic raster layers, while `stats_analysis.py` derives structured statistics. `SessionStatsCache` keys results by state identity so imported and generated maps use the same analysis path.

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

Visual order must not be used as LRU order. The pure rules live in `history_order.py`; GUI navigation and A/B assignment are observational and must not reorder the history.

## Runtime paths and user data

`app_paths.py` distinguishes source mode from PyInstaller mode:

- bundled resources are resolved from the repository root or `_MEIPASS`;
- source exports go to the repository `output/` directory;
- portable executable exports go beside the executable;
- persistent settings are handled separately by `preferences.py` under the user application-data location.

Self-tests must not write user settings or modify map resources.

## Safe change rules

- Add tests around behavior before refactoring the historical GUI chain.
- Keep parsing, rendering, analysis and UI responsibilities separate.
- Do not add a second Batch generator or a second settings format.
- Do not infer unknown Terrain/Object IDs or unsupported binary structures.
- Do not mutate protected engine/config/data files without an explicit engine task.
- Do not use invented map imagery; previews and screenshots must come from actual generated or imported data.
- Update the living snapshot after every explicitly validated DEV stage and every RC/STABLE release.
