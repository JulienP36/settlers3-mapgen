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

## Current state — v2.0 DEV_8

DEV8 is published on the `dev` branch from the R86 candidate. It closes the
Archetype work: the main selector shows “Custom” after an effective profile
edit, then returns to the named profile when one is selected. The full
recovery references remain in the local hand-off archive and are excluded
from GitHub. All 641 regression tests pass.

DEV9 is next, including the Great Islands archetype and the remaining work in
`TODO_MAPGEN.md`.

### R55 — previews and providers for Continental Custom

R55 fixes the framing of fusion and mask thumbnails: the absolute envelope of
the native-calibrated Continental profile is now reduced from the real map
side to the 128² thumbnails. Fusions no longer look zoomed out, and masks can
no longer reintroduce influence into the ocean frame. Historical percentage
profiles keep their previous behavior.

R54 added `hybrid_fbm`, `turbulence`, `worley_f1`, `worley_f2`, and
`worley_f2_minus_f1`. R55 adds `heterogeneous_fbm` and
`ridged_multifractal`, available as the primary source, a fusion, or a mask
source in the **Archetype** tab. These are exploration building blocks; the
named R53 composition remains exactly unchanged and no geometry is drawn by
hand.

## Continental Custom R53 preset — noise composition

R53 keeps the genuinely independent Continental Custom preset:
`Continental Custom R53 — fBm + warp + ridges`. It starts with an autonomous
fBm field, applies a light `domain_warp` blend (`15%`), then a low-strength
additive `ridged` fusion (`12%`). These are exactly the sources, operations and
settings visible in the **Archetype** tab; no drawing, shape template or hidden
geometry code is embedded in the preset.

Its outer domain is now calibrated against the measured native envelope: the
frame and transition use absolute cells, so the surrounding ocean no longer
grows proportionally with map size. The Continental land mass therefore keeps
an extent close to the native profile.

In the application, choose **Custom**, **Continental**, then the preset in the
**Base profile** selector on the **Archetype** tab. The primary source and both
fusions remain editable in that same tab. Native Continental remains available
as the reference profile, and the Legacy/Upgraded code paths are unchanged.

`python tools/qualify_continental_custom.py` replays the preset across
`384/512/768`, three seeds and mirror modes `0/3`, then runs the Legacy-based
Custom route for player cases `2/4/max`. Hard gates cover validations, exact
start count, uniqueness and map bounds. `startable_mass` remains a soft
diagnostic; Windows and in-game visual validation are the next step.

## Recent history — v2.0 DEV_8_R50 / manual-mask qualification

R50 adds deterministic qualification for the drawable/imported mask provider.
`python tools/qualify_manual_masks.py` covers the representative sizes
`384/512/768`, three seeds (`20260920/21/22`) and all four native mirror
modes by default. The report checks signal reproducibility, effect on the
complete preview, coverage stability, variation outside the mask and the
native water border. `--mask path/to/image.png` qualifies an imported image
with the same 64×64 grayscale resampling used by the editor. This remains
diagnostic tooling and does not change generation.

## Recent history — v2.0 DEV_8_R49 / drawable masks

R49 keeps the independent mask stack and its generic spatial contract, and adds
the `Freehand` provider. Each slot can open a 64×64 grid to paint or erase a
grayscale influence, import an image, and export the mask as PNG. The grid is
resampled through the shared size, position, rotation and softness controls;
the operation modulates the complete field after fusions while preserving
variation outside the mask. The editor window now follows the dark theme
correctly. New archetypes still start with zero active fusions.

## Recent history — v2.0 DEV_8_R42 / resizable workspace

R42 keeps R40's four explicit setting families and also makes the core group
collapsible, while leaving it open by default. Source and fusion thumbnails
deliberately remain fixed at 128², as in R40, until a dedicated future slice.
The header stays anchored to the top when the sash moves, and Session /
Comparison keeps its historical two-position responsive reflow. A second
vertical sash adjusts the space between the header and the map/tabs workspace,
and its position is remembered.

## Recent history — v2.0 DEV_8_R41 / first adaptive workspace

R41 briefly made the noise thumbnails adaptive; R42 removes that behavior at
the user's request without changing their calculation or placement.

## Recent history — v2.0 DEV_8_R40 / collapsible setting groups

R40 grouped every noisemap source's settings into four explicit families:
core, output transforms, remapping, and coordinates. Core settings remained
visible, while the three advanced groups could be collapsed independently.

## Recent history — v2.0 DEV_8_R39 / focused archetype ergonomics

R39 keeps the global archetype reset and adds only two local resets, disabled
until their block is modified: morphology/relief source/thresholds, then the
fusion editor. The resets update controls and previews in place without
clearing the visible view, and no reset button is added to each fusion. Fusion
cards also separate their header, parameter and action grids so long fields no
longer shift the rows below them.

## Recent history — v2.0 DEV_8_R38 / advanced noise remapping

R38 adds independent advanced remapping to every autonomous source: black/white
points to expand or narrow the input range, hard or softened low/high
thresholds, output floor/ceiling clamps, and an asymmetric response curve.
These controls run before the finite frame, remain neutral by default, and are
available independently on the primary source and every fusion. They can make
relief flatter, stepped, more concentrated, or deliberately asymmetric without
introducing an implicit mask.

R37 adds independent coordinate transforms to every autonomous source: X/Y
offset, independent X/Y scale, X/Y repetition and X/Y symmetry. They run before
the R36 output remaps, remain bounded by the finite inner rectangle, and are
available independently on the primary source and every fusion. Identity
defaults preserve R36 profiles.

R36 keeps R35's exact preview behavior and adds provider-independent output
transformations to every autonomous source: inversion, absolute value, gamma,
and terracing with adjustable blending. The noisemap editor help now sits in
its title, and identity defaults preserve existing profiles.

R34 fixes Solo so it isolates only an already-enabled fusion in the preview,
keeps the primary source, and never changes the profile used by real
generation. A disabled or zero-strength fusion can no longer be re-enabled by
that button.

When macro smoothing is disabled, the preview now goes directly to the exact
calculation without running or displaying an intermediate indicative pass.
Native refinement remains active; only `_relax_relief` is omitted from this
fast preview. Toggling the option also invalidates any previous calculation
immediately, so an obsolete result cannot overwrite the selected state. Each
fusion thumbnail is now 128²; action buttons are placed after all setting rows,
and the “Primary source” thumbnail shows the relief source before fusion while
“Noise / height” remains the composed view.

R33 makes the fusion stack directly editable from each card: move a slot up
or down, duplicate a fusion, delete it, or isolate its effect in a Solo
preview. Solo never changes the profile used by real generation; it disables
the other fusions only in the preview copy.

R32 moves the three main views to a single 1080p-friendly row at the top of the
tab. The fusion count is configurable from zero to six without losing hidden
slot settings. The primary source and every fusion have a raw 128² thumbnail
computed directly from their provider without running the macro pipeline. R31
still guarantees consistency between indicative and exact passes and greys out
settings the selected source does not consume.

R30 continues R29, which replaces the shape-preset direction with an actual noisemap editor. The
primary source can use Native Legacy, white, Value, Perlin, Simplex, fBm,
Billow, Ridged, Worley or Domain Warp noise. Up to six autonomous sources
can be fused using replace, blend, add, subtract, multiply, minimum or maximum.
Every source exposes frequency, octaves, lacunarity, gain, rotation, stretch,
bias, contrast, warp and seed offset. The domain remains a finite inner
rectangle with configurable margin and edge transition.

Editing the Archetype tab now customizes the archetype without switching the
Generator mode to Custom. The noisemap and its contribution render directly
on a live 192² grid without waiting for native relaxation; the exact macro map
continues in the background. Panels replace their images independently and in
place, with no blank frame. Detailed laboratory statistics were removed from
the UI in favor of useful controls. The macro-map smoothing pass can now be
disabled to iterate on noise faster; this preview-only setting does not alter
real map generation.

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
remains the R59 behavior. DEV_7 publishes the Custom-generator UX finish.
`DEV_8_R1` was validated and opened the Archetype tab with a declarative Continental macro
profile: an unchanged Custom copy reuses the same relief thresholds, while
edited thresholds affect its own generation. The live noise and five-class
macro-map previews, with square/parallelogram projection, adjustable display
size, noise reuse and adaptive sizing, with atomic final painting, signed noise
`-30 … 225`, full native generation without a resolution approximation and
resize-aware adaptive sizing, are part of the `DEV_8_R11` foundation. Preview work is
paused while the Archetype tab is inactive, then resumes with only the latest
useful request when the tab becomes active again; the last complete image stays
visible and the macro map reports the distribution of its five classes, warning
when one is absent. The Continental contract is also shown explicitly: relief
engine, noise family, signed range, derived shores, land-mass model and the
absence of micro-islands. Those fields stay locked until a real engine consumes
them; relief thresholds are checked against implicit native defaults across
multiple sizes and mirrors. Hexagons and detailed live generation in the
Generator remain deferred to v2.1. R9 also hardens Generator reflow callbacks
after tab reconstruction and wheel detection over Tk's transient combobox
popdown menus. R10 adds connected-land diagnostics to the preview and records
the actual grass mass carrying provisional starts, without changing generated
maps. R11 adds the first real Custom morphology controls: spatial shape scale
and relief contrast. At `100%`, native output remains unchanged; the same fields
feed the previews and both native-derived engines. R17 keeps the two optional,
stackable procedural layers but makes them semantic relief components: the
implemented role is `land_relief`, and each layer uses an explicit `add` or
`subtract` blend. They are applied before native normalization, sculpture and
relaxation, only to existing land cells; native water cells, including the
outer border, remain protected. R17 does not yet create lakes or a new
water/land mask. R46 now adds an independent parametric mask stack with soft
modulation outside each shape; drawn/imported masks and specialized roles
remain future extensions.
R12 separates the noise-map display path: the signed native field is shown as
soon as raw relief generation completes, before sculpture and final relaxation,
while the exact macro map continues in the background. Raw fields are cached
independently from morphology, and mirror copies plus the water border are
reapplied in the same order as the native preview. Shape scale is capped at
`100%` so water remains around the map. The native `_relax_relief` pass remains
unchanged in real generation; it repairs local height gaps until stable before
terrain classification and is bypassed only by the fast noise-map display.
R13 also derives an indicative five-class macro raster immediately from that
same fast field. It is clearly marked as provisional, then replaced by the
exact macro map when sculpture and `_relax_relief` finish; exact statistics are
hidden during this interim state. Real Legacy/Upgraded generation remains
unchanged in output. R14 speeds up the exact ordered relaxation loop while
preserving its corrections and `uint8` result, substantially reducing waits at
sizes `704+` without approximating the final preview. R15 gives the visible
progress one global scale: `0–15%` for the indicative field, `15–95%` for the
exact calculation, and `100%` only after the final render; resize callbacks can
no longer complete or rewind it prematurely. R17 keeps the optional, stackable
and deterministic procedural noise layers but makes them semantic relief
components: `land_relief` with an explicit `add` or `subtract` blend. Disabled
by default, they leave native output unchanged; when enabled, they modify
existing land before native normalization and relaxation, while native water
cells remain protected and the unchanged native-field cache is bypassed.
R24 corrects the R23 regression in the laboratory's third preview: image 1
shows the selected relief source, while image 3 shows only the raw layer
contribution in red/blue. The source-versus-Legacy delta and the composed field
remain separate in the diagnostic report.
R25 removes the flash during re-previews by replacing images inside their
existing panels and adds raw land share plus P10/P50/P90 heights to help
compare providers.
R26 keeps the last complete triptych visible throughout recalculation: the
indicative phase is no longer painted, and noise/height, macro and raw
contribution are prepared before being replaced together only when the exact
preview is complete. Errors or invalid values keep the previous view. No noise
provider, noise setting or Legacy/Upgraded generation path changes; the next
roadmap step is the target matrix and reproducible qualification of the
existing providers.
R27 adds that matrix for Continental, Large Islands and Small Islands, covering
native sizes `384–768`, player cases `2 / 4 / maximum`, and mirrors `0 / 3`.
The new `python tools/qualify_archetypes.py` command compares existing providers
using the actual macro preview: land/water share, outer border, dominant mass,
coast contact and mountain/snow relief. This first pass intentionally stops at
macro preview; starts, buildability, resources, detailed hydrology and
editor/game validation remain later gates. The default run passes `12/12`;
mirror 3 exposes one existing native case at `384²` with `0.23%`
mountain/snow (`11/12`), while the independent providers pass `9/9`. This
diagnostic remains open for the next step.

R22 replaces the rejected R21 post-generation envelope: each provider is
generated directly inside a finite inner rectangle with low boundary
conditions carried by the noise itself; the area outside the frame is water.
There is no corrective layer stacked after generation, shapes are not cropped
at the domain edge, and dynamic previews calculate fewer cells.

R20 corrected the R19 boundary mistake: changing the noise now replaces the
complete raw elevation matrix, including its water, instead of preserving the
Legacy coast and land mask. Three independent providers are available:
`fractal_fbm`, `warped_fbm` and `ridged_fbm`. The native engine then consumes
that field and applies its own normalization, macro shaping, relaxation and
classification. `native_legacy` remains the default and its output is guarded
by binary parity. Optional layers target the selected source's `source_land`
domain, so they cannot silently reintroduce the Legacy coast. The laboratory
separates the reference field, active source, source delta and layer
contributions. R20 does not yet claim specialized lake or water roles.

R18 makes each component contract inspectable: source, role, mask, stage, blend
and order. The completed preview exposes the native field before composition,
the composed field and a contribution map where red raises relief and blue
lowers it; the statistics list affected cells and delta bounds. R17 profile keys
are migrated without changing their meaning. R18 still does not replace the
Legacy source or create lakes.
The semantic sections remain Minerals, Fish,
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
remain internal. The DEV6 foundation and DEV7 UX finish are published; DEV8
now continues with the Custom archetype editor.

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

To reproduce the first provider qualification:

```text
python tools/qualify_archetypes.py --output qualification.json
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
still need separate validation. At that point, DEV7 was published and DEV8_R1 remained a local
candidate. Bonus lakes
use two shoreline rings, and bonus rivers use the native local construction
instead of a global distance route. R58 caps the lake radius at `16 HEX6` and
the maximum river target at `6` per lake.
