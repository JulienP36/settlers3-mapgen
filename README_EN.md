# Settlers III MapGen

[Français](README.md) · **English**

> Experimental procedural map generator and analysis workbench for **The Settlers III**, built from reverse engineering of `.EDM`, `.MAP` and `.SAV` files, measurements of the native generator, and repeated validation in the official editor and in-game.

> **Development transparency:** this project is conceived, directed, tested and validated by its human owner, with substantial **ChatGPT / OpenAI implementation assistance**, especially for backend development, technical analysis and reverse-engineering tools.

## Project overview

Settlers III MapGen aims to generate, inspect and eventually edit Settlers III maps through a reproducible and controlled workflow.

Its three long-term generation modes are:

- **Legacy**, the native-inspired reference and reverse-engineering baseline;
- **Upgraded**, the validated gameplay and safety rules accumulated by the project;
- **Custom**, a future user-configurable mode that will retain critical safeguards.

Map archetypes describe macro geography independently from generation modes. Continental is currently implemented; Large Islands and Small Islands are reserved for later development.

Every map preview is a deterministic rendering of actual generated or imported map data. The project does not use invented map artwork.

## Application screenshots

### Generation and Viewer

![Legacy 768×768 generation and Starts view in the Viewer](docs/screenshots/v1_8_generation_viewer.png)

*An actual generated map in parallelogram projection with all four player start areas.*

### Statistics

![Heatmap and Statistics report for a generated map](docs/screenshots/v1_8_statistics.png)

*Detailed terrain, resource, hydrology, elevation, player-start and ID inventories.*

### Charts

![Resources view and mining-stock chart](docs/screenshots/v1_8_charts.png)

*The Resources view paired with the semantic mining-stock chart, including snow-covered deposits.*

### Batch generation

![Four-map Batch generation with real previews and cache states](docs/screenshots/v1_8_batch.png)

*Four sequential tasks with real previews; the blue status deliberately demonstrates cache reuse for an identical configuration.*

## Current state — validated v1.9 DEV_3 / stable v1.5 engine

The protected v1.5 engine remains the validated generation checkpoint and must not change without an explicit engine reason. The latest published stable application is v1.7, which added the Statistics and Charts analysis foundation above that engine.

The current v1.8 development line adds workflow, accessibility and production tooling:

- Legacy and Upgraded Continental 768×768 generation;
- `.EDM`, `.MAP` and read-only `.SAV` imports;
- validated 768×768 `.EDM`/`.MAP` export and unchanged source `.SAV` copying;
- Global, Starts, Territories, Initial mask, Elevation, Resources, Paths, Crops and Heatmap views;
- structured statistics, full Terrain/Object ID inventories and interactive charts;
- light/dark themes, square/parallelogram projections, zoom, drag and exact cell inspection;
- French, English, German and Spanish interfaces with persistent live switching;
- a session-only map history with a hard 4/8/12/16 capacity, manual visual ordering, persistent-for-session `M` locks and A/B comparison slots;
- sequential Batch generation for one to four independently configured maps;
- grouped map and chart exports;
- configurable shortcuts and dynamic help.

DEV_11 closed the publication/maintainability pass. v1.9 DEV_1 fixed imports
for valid EDM files carrying terminal DWORD-alignment bytes; both supplied
failing files load on Windows. DEV_3 now consolidates the demonstrated player
SAV data, direct initial-mask field, confirmed object/terrain catalogues and
vegetation charts without changing the protected v1.5 engine.

## Install and run on Windows

For the first source-based launch:

```bat
install_and_run.bat
```

If Python is not installed yet:

```bat
install_python_and_run.bat
```

For later launches:

```bat
run_gui.bat
```

The main Python dependencies are NumPy, SciPy and Pillow. A separate installation-free Windows x64 package was proven feasible during DEV_9 and will return during the v1.8 Release Candidate phase.

## Important limits

- Generation is currently calibrated only for Continental 768×768.
- Sizes other than 768 may be shown in the UI but are not ready for generation.
- The project has no `.SAV` writer. Imported saves are read for supported data and may only be copied unchanged.
- The native initial territory mask is read directly from type-3 byte 8 of an
  immediate SAV when the confirmed signature is present; no start-based shape
  reconstruction is used. EDM/MAP claim-less sources remain neutral in that
  view.
- The partial `.EDM` import failure was fixed and Windows-validated in v1.9 DEV_1. The parser accepts only the confirmed terminal DWORD-alignment case and keeps reconstruction paths strict.
- Current seeds produce only three base morphologies, then rotations and occasional mirrors. The seed/RNG audit and objective diversification are planned for v1.10.
- Automated validators are regression guards; they do not replace validation in the official editor, View Map, a runtime `.SAV`, or long-play.

## Translation status

French and English are the reviewed reference languages. German and Spanish were produced automatically and only partially reviewed, so community corrections from competent speakers are welcome.

## Technical documentation

- [Concise contributor instructions](AGENTS.md)
- [Project architecture](docs/ARCHITECTURE.md)
- [Debugging and validation](docs/DEBUGGING.md)
- [GitHub publication checklist](docs/GITHUB_PUBLICATION.md)
- [Mandatory pre-generation reference](references/SETTLERS3_PREGEN_READ_FIRST.md)
- [Validated v1.5 rules](references/SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md)
- [EDM/MAP format reference](references/SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md)
- [SAV format reference](references/SETTLERS3_SAV_FORMAT_REFERENCE_v1.md)
- [Roadmap](TODO_MAPGEN.md)

## Validation model

The project uses a layered validation hierarchy:

1. parser, checksums and automated regressions;
2. official editor validation;
3. View Map and in-game smoke testing;
4. runtime `.SAV` inspection;
5. long-play validation.

The source package can validate its bundled runtime resources without opening the GUI:

```text
python run_gui.py --self-test
```

See [Debugging and validation](docs/DEBUGGING.md) for the full maintenance workflow.
