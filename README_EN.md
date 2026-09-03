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

![Legacy 768×768 generation and start markers in the Viewer](docs/screenshots/v1_8_generation_viewer.png)

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

## Current state — v2.0 DEV_5 / Upgraded finishing pass

The `v2.0 DEV_1` generation was validated and published on GitHub. `DEV_2` was
the validated native reset checkpoint, and `DEV_3` is now the validated and
published checkpoint: the old procedural Legacy
generator and its derived libraries were removed and replaced by a separate
native-inspired v1 port. The Upgraded engine is now rebuilt as an independent
copy of that pipeline. DEV_4 adds temporary Charts → View linking, keeps the
A/B comparison tooltip-only, fixes the non-768 export dialog, unlocks all
three mirror modes for Upgraded, and exposes Upgraded on every native contract
size; 768 keeps its calibrated quotas while other sizes use proportional
quotas so they remain generatable. No contract size is blocked as “untested”;
warnings remain informational. **Start markers** now offer Tiny, Normal and
Large, plus Hidden, in every view, Batch and History; a separate option shows
the start circles everywhere as well.
DEV_5 restores the Upgraded content around starts: Legacy-shaped static
objects, mini-forests, tree/stone bonuses and mini-swamps, while keeping
Upgraded reefs.

The **Legacy** engine now implements the Continental v1 native reconstruction:
relief, terrain, hydrology, objects, resources, starts and runtime metadata.
The **Upgraded** engine owns an independent copy of the native terrain
pipeline, calibrated for Continental 768×768 but generatable on every contract
size. It adds only its explicit
differences: v7 minerals, fish, trees/decorations and building stones, with no
Mud generation.
The Continental archetype supplies the macro-geographic context; it does not
apply a second sculpture over the native core.
DEV_5 keeps the provisional start-coordinate bridge, but restores the tree,
building-stone and mini-swamp bonuses around those coordinates. The next
planned steps are Dev 6 Custom generator, Dev 7 Custom archetype and Dev 8
first modifiers.

Minerals were compared before removal: the former generator had a globally
similar family mix to the native SAV corpus, but its deposits were much too
fragmented in component count and size. Those quotas and heuristics are not
carried forward as rules. The reproducible comparison is recorded in
`references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

The native reference port is present in DEV_2 for sizes 256, 320, 384, 448, 512,
576, 640, 704, 768, 832, 896, 960 and 1024. Mirror modes are Long axis,
Short axis and Both. The generator audit remains the source of truth; extended
exports still require validation in the community editor/game.

DEV_3 continues this base with the validated projection-compensated mineral
blob shape, the validated short name for terrain ID `34` (**Rocky grass patch**),
and distinct map/chart rendering for that terrain.

The validated GUI and tooling remain available: read-only EDM/MAP/SAV import,
scaffold-based EDM/MAP export for all native sizes, analysis and inspection views, statistics,
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

- Native Legacy and Upgraded generation are available for the native map sizes. Sizes below
  384 and above 768 are deliberately exportable test candidates and are warned
  about in the feedback area. Upgraded remains calibrated against Continental
  768×768, while proportional quotas are used outside that reference size.
- The project has no `.SAV` writer. Imported saves are read for supported data and may only be copied unchanged.
- Known SAV limitation: some imports may display reef IDs on land, probably due
  to an incorrect decoder mapping; this is explicitly deferred.
- The native initial territory mask is read directly from type-3 byte 8 of an
  immediate SAV when the confirmed signature is present; no start-based shape
  reconstruction is used. EDM/MAP claim-less sources remain neutral in that
  view.
- The partial `.EDM` import failure was fixed and Windows-validated in v1.9 DEV_1. The parser accepts only the confirmed terminal DWORD-alignment case and keeps reconstruction paths strict.
- The native Legacy audit and implementation are complete for the demonstrated
  generation contract; opaque runtime format tables remain explicitly open.
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
