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

## Current state — v2.0 DEV_2 / native Legacy reconstruction

The `v2.0 DEV_1` generation was validated and published on GitHub. DEV_2 now
starts from a clean boundary: the old procedural Legacy generator, its
profiles, helpers and derived libraries are removed, together with the former
Legacy v1.5 path that did not provide usable generation. Legacy remains a
reserved mode in the UI and API, but generation is explicitly disabled while
the native reconstruction is completed.

The only generation engine retained is the **Upgraded** compatibility path,
calibrated for Continental 768×768. Its rules, profile, validators and
references remain separated and protected. The Continental archetype continues
to own macro shape; the future Legacy generator will define its own relief,
terrain, hydrology, resources, objects, starts and validation layers from the
native audit.

Minerals were compared before removal: the former generator had a globally
similar family mix to the native SAV corpus, but its deposits were much too
fragmented in component count and size. Those quotas and heuristics are not
carried forward as rules. The reproducible comparison is recorded in
`references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

DEV_2 is therefore dedicated to rebuilding the native Legacy core and then
defining Continental v1. The generator audit is the source of truth; no
provisional behavior should be described as exact until it is validated against
maps produced by the game.

The validated GUI and tooling remain available: read-only EDM/MAP/SAV import,
scaffolded 768 EDM/MAP export, analysis and inspection views, statistics,
charts, history, A/B comparison, Batch generation, themes and FR/EN/DE/ES
locales. Previews remain deterministic renders of real data or identified
outputs of the retained engine.

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

- Legacy generation/preview is currently disabled during the native rebuild.
  The retained Upgraded generator is calibrated for Continental 768×768, and
  EDM/MAP export still requires its validated scaffold.
- The project has no `.SAV` writer. Imported saves are read for supported data and may only be copied unchanged.
- The native initial territory mask is read directly from type-3 byte 8 of an
  immediate SAV when the confirmed signature is present; no start-based shape
  reconstruction is used. EDM/MAP claim-less sources remain neutral in that
  view.
- The partial `.EDM` import failure was fixed and Windows-validated in v1.9 DEV_1. The parser accepts only the confirmed terminal DWORD-alignment case and keeps reconstruction paths strict.
- The native Legacy audit and implementation are still in progress; no
  provisional procedural rule is treated as an exact game rule.
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
