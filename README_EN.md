# Settlers III MapGen

[Français](README.md) · **English**

> Experimental procedural map generator and analysis workbench for **The Settlers III**, built from reverse engineering of `.EDM`, `.MAP` and `.SAV` files, measurements of the native generator, and repeated validation in the official editor and in-game.

> **Development transparency:** this project is conceived, directed, tested and validated by its human owner, with substantial **ChatGPT / OpenAI implementation assistance**, especially for backend development, technical analysis and reverse-engineering tools.

## Project overview

Settlers III MapGen aims to generate, inspect and eventually edit Settlers III maps through a reproducible and controlled workflow.

Its three long-term generation modes are:

- **Legacy**, the native-inspired reference and reverse-engineering baseline;
- **Upgraded**, the validated gameplay and safety rules accumulated by the project;
- **Custom**, a user-configurable laboratory mode that retains critical safeguards.

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

## Current state — v2.0 DEV_7 / Custom generator finish

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
Upgraded reefs. The DEV_6_R61 application foundation reprises R57's lake shapes and
depths, strengthens the shoreline to two native-style rings, and rebuilds each
bonus river with the local native system (9x9 filter, relief fan, HEX6 markers
and backtracking) without searching for existing water as a destination.
Accidental junctions remain possible when geometry causes them, but no
lake-to-sea route is sought; normal bonus systems use River96 throughout.
R58 caps the bonus-lake radius at `16 HEX6` and the maximum target at `6`
rivers per lake without changing the validated R57 tracer. A water threshold of
`0` now explicitly disables the native-water proximity filter; positive values
keep the configured exclusion radius. Compact per-player and global metadata
counters record attempts, accepts and rejection causes.
Tower water clearance remains 20 HEX across the full lake/river footprint,
even without forced placement. It places
“Distribution” between “Shape” and “Common radius”, and preserves derived
radius/total/core values when the allocation mode changes; it reprises R53
functionally. R60 now compacts the lake/river panel into four columns,
shortens the native-water avoidance label, and keeps each shape list directly
beside its label. R61 replaces that label with “Native-water check radius” and
aligns every lake/river control in one vertical column. Generation logic
remains the R59 behavior. DEV_7 publishes the Custom-generator UX finish; the
next tranche is Custom archetypes. The semantic sections remain Minerals, Fish,
Trees, Building Stones, Decorations and detailed start-bonus controls, dynamic
translations, profiles
derived from presets, a configuration fingerprint in the cache,
Generator/Archetype tabs, and an extensible start-bonus registry. Minerals
expose the three Legacy/Upgraded/Random-pixels algorithms, occupancy, distribution, size
variation and average resource; Fish expose global fill or uniform placement
inside a configurable coastal band, falling back to global fill when the
requested band exceeds the available shore. Technical profile details are hidden
from the UI. Selected settings are applied
to the Upgraded content pass and to the Legacy resource bridge, without
modifying a profile through Custom editing. The Upgraded base profile now uses
the requested 52.5 / 22.5 / 15 / 5 / 5 mineral split, which its equivalent
Custom preset inherits automatically. **Random pixels** places compatible
cells uniformly in one pass without forming deposits, including through the
actual interleaved resource view exported by the map state. Upgraded and its
equivalent Custom configuration now share the exact mineral and fish routines
when their parameters are identical. Successive Custom edits keep the existing
controls and focus, and Charts → View linking is enabled by default.

The **Legacy** engine now implements the Continental v1 native reconstruction:
relief, terrain, hydrology, objects, resources, starts and runtime metadata.
The **Upgraded** engine owns an independent copy of the native terrain
pipeline, calibrated for Continental 768×768 but generatable on every contract
size. It adds only its explicit
differences: v7 minerals, fish, trees/decorations and building stones, with no
Mud generation.
The Continental archetype supplies the macro-geographic context; it does not
apply a second sculpture over the native core.
DEV_5 keeps the provisional start-coordinate bridge, R36 corrects the forest
bonus in both Custom variants, R37 consolidates start forests and stones, and
R40 removes empty-cell bonus reservations while unifying the public route. Legacy and
Upgraded presets
start with bonuses disabled, each panel owns its activation switch, and the
forest defaults to `30` adult trees plus `20` saplings per player. Adults are
placed first, then saplings, with a common minimum of `3 HEX6`; the minimum
forest radius is derived from the requested population and spacing and may
expand automatically when terrain or collisions require it. The old forest
radius fields are ignored. R37 caps both adult and sapling requests at `100`,
caps global forests at `100` trees, and shares the sapling colour between map
and charts. Start stones default to `15` anchors per player, maximum `50`, with
an average quantity of `10`; their radius is derived automatically. R46 keeps
the R42 mini-swamp controls, generates an independent `Native` footprint for
each start with the same brush/expand/erode plan as global swamps, and adds a
strict staged path only when a start bonus is
active: the no-bonus path remains byte-identical to R42. Bonus terrain is written
after archetype-linked terrain and before global non-archetype families, then
bonus objects are written before all global objects; no bonus write is deleted
afterwards. R46 keeps R45's live written object halo for every active family,
including Legacy's native global pass, and keeps the complete stone footprint
protected. R45 also writes bonus forest adults before saplings. R42 replaces
the free mini-swamp cell count with an extensible shape list (`Native`, `Hexagon`)
and a bounded radius `1–16`; the hexagon scales with the radius and
`Native` reuses the global native swamp plan. Cell count is derived. R39 also
removes residual native stones when the global rate is `0%` and the local
bonus is disabled; bonus-stone stock uses the same law as the global stock. The object
switch permits grass-compatible objects on terrain IDs `18`, `19` and `24`,
but not rocky detail `34`, without erasing already placed objects; enabled bonuses
may use those cases. All five bonuses can be enabled in both public presets and
remain outside global quotas; a shared forced-spawn-at-a-greater-distance
option is active for every bonus, off by default, and falls back to the local
radius when disabled. R13 wires the
Custom Trees section into both engines: a relative base quota, saplings (global
pool or separate quota and placement), forests (share, average and variation),
and a relative maximum palm quota. The Upgraded default follows its active
profile, including `30%` of adult trees in forests; Legacy defaults to no forests
and no saplings. The Decorations section exposes an independent `0–500%`
appearance rate for each static family already recognized by the generator;
`100%` preserves the selected profile, while IDs and terrain/collision rules
remain internal. The DEV6 socle still awaits user validation, followed by the
Dev 7 Custom archetype and Dev 8 first modifiers.

Minerals were compared before removal: the former generator had a globally
similar family mix to the native SAV corpus, but its deposits were much too
fragmented in component count and size. Those quotas and heuristics are not
carried forward as rules. The reproducible comparison is recorded in
`references/history/minerals/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

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

The main Python dependencies are NumPy, SciPy and Pillow. A separate installation-free Windows x64 package was proven feasible during the historical v1.8 work and will return during a future Release Candidate phase.

## Important limits

- Native Legacy and Upgraded generation are available for the native map sizes. Sizes below
  384 and above 768 are deliberately exportable test candidates and are warned
  about in the feedback area. The active Upgraded engine is independent;
  768×768 is only its calibration reference, while
  proportional quotas are used outside that reference size. There is no active
  there is no active Upgraded v1.5 engine.
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
- [Reference index](references/REFERENCE_INDEX.md)
- [Mandatory pre-generation reference](references/SETTLERS3_PREGEN_READ_FIRST.md)
- [Current generation matrix](references/SETTLERS3_UPGRADED_RULE_MATRIX_CURRENT.md)
- [Historical long-play rules](references/SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md)
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

R58 keeps the R48 engine and R47's forced-centre search through D+34 and uses
rounded Upgraded-style organic mineral zones, equal/deposit-share/custom core surfaces, and per-mineral
average quantities inherited from or overriding the global setting. Every core
cell is mineralized; an impossible complete zone is skipped with a shortfall.
The Hexagon shape and historical radius controls remain compatible. The panel
now uses a compact `Mineral / Core / Average` matrix and disables radii, total
surface, or per-mineral surfaces according to the selected mode; prorata points
back to the global mineral shares. R50 adds the 16×16 coal/iron/gold sprites
and one common equal-mode radius (`1–16 HEX6`). R54 keeps R51's locked selectors,
read-only, keeps unused contextual fields disabled, places `HEX6`/`cells` units
beside their inputs, grays inactive mineral sprites, sets the swamp radius
maximum to `16 HEX6`, bounds each core to `1–820` cells, and makes the prorata
total dynamic (`820/1,640/2,460`) according to active minerals. OFF keeps R46 behavior.
Forests, stones and swamps are user-validated; mineral zones and the lake/river
still need separate validation. DEV6 remains a local candidate. Bonus lakes
use two shoreline rings, and bonus rivers use the native local construction
instead of a global distance route. R58 caps the lake radius at `16 HEX6` and
the maximum river target at `6` per lake.
