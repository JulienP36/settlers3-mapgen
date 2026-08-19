# Settlers III — Runtime object calibration — 2026-08-19

Controlled visual calibration from the 256×256 unknown-object test maps.

## Scope

This reference intentionally distinguishes:
- static/editor object IDs already confirmed in `s3_object_ids_confirmed.csv`;
- internal/runtime object-state IDs which should not be emitted by the procedural map generator as ordinary static decorations without further evidence.

## Tree-like internal variants

User visual identification:

| ID | Visual equivalence | Status |
|---:|---|---|
| 73 | resembles Elm 2 | internal/tree variant, exact semantics unknown |
| 74 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 75 | resembles Birch 2 | internal/tree variant, exact semantics unknown |
| 76 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 77 | resembles Birch 2 | internal/tree variant, exact semantics unknown |
| 80 | resembles Birch 1 | internal/tree variant, exact semantics unknown |
| 81 | resembles Birch 2 | internal/tree variant, exact semantics unknown |

These IDs are not added to the normal static tree pool yet.

## Unknown / invisible

- `82`, `83`: no visible object in the controlled editor calibration on tested supports/heights. Exact role remains unknown; defer to future binary/runtime analysis.

## Wheat growth/runtime states

IDs `85..93` form a coherent **9-state wheat cycle**.

- `85..91`: successive growth states (exact ordinal naming not yet locked beyond visual progression).
- `92`: mature / harvestable wheat.
- `93`: post-harvest state — cut straw/stubble lying on the ground, temporary fallow-like state before disappearing.

These are runtime crop states, not ordinary static map decorations.

## Grape/vine growth/runtime states

IDs `94..102` form a coherent **9-state grape/vine cycle**.

- `94..101`: successive vine states.
- `102`: ninth state, visually resembles the first state (`94`).

Interpretation to test later: this may reflect the vineyard gameplay cycle where vines persist and return to an early growth state after harvest instead of requiring replanting. This interpretation is plausible but not yet treated as binary-confirmed semantics.

## Rice growth/runtime states

IDs `103..110` correspond to **rice growth/runtime states**.

Rice normally grows only on Swamp terrain, so these IDs should be rechecked later in a controlled Swamp or live-game context to establish exact stage ordering and any terrain coupling.

## Generator decisions

- Do not deliberately generate IDs `73..110` as ordinary decorative/static objects in Upgraded.
- Keep the already-confirmed static tree pool (`68..72`, `78`, `79`, `84`) unchanged.
- Keep `82/83` as unresolved runtime/technical IDs.
- Treat `85..110` as runtime agriculture-state families for analysis/statistics, not static object families.
- Future SAV/live-game analysis should correlate crop object-state IDs with terrain IDs underneath them, especially wheat field/fallow terrain and rice-on-Swamp behavior.
