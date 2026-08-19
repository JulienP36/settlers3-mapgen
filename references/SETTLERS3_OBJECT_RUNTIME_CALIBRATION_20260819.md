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

These IDs are visually identified as tree-family variants but are not added to the normal static tree pool yet.

## Unknown / invisible

- `82`, `83`: no visible object in the controlled editor calibration on tested supports/heights. Exact role remains unknown; defer to future binary/runtime analysis.

## Wheat growth/runtime states — IDENTIFIED FAMILY

IDs `85..93` form a coherent **9-state wheat family/cycle**.

- `85..91`: successive wheat growth states.
- `92`: mature / harvestable wheat.
- `93`: **chaume** — post-harvest cut straw/stubble lying on the ground, temporary state before disappearing.

The family identification is considered visually confirmed. Exact timing/duration of intermediate stages remains a runtime-mechanics detail, not an object-ID ambiguity.

## Grape/vine growth/runtime states — IDENTIFIED FAMILY

IDs `94..102` form a coherent **9-state grape/vine family/cycle**.

- `94..101`: successive vine/grape states.
- `102`: ninth vine-family state; visually resembles `94`.

All IDs `94..102` are considered identified as members of the grape/vine family. The precise runtime transition semantics between `102` and `94` remain open. A plausible explanation is the vineyard-specific behavior where vines persist after harvest and re-enter an early growth state without requiring replanting, but this mechanical interpretation is not yet binary-confirmed.

## Rice growth/runtime states — IDENTIFIED FAMILY

IDs `103..110` are considered identified as members of the **rice growth/runtime family**.

Rice normally grows on Swamp terrain. Exact stage ordering and terrain/runtime coupling can be refined later from a live SAV, but the family identification itself is retained as confirmed visual information.

## Generator decisions

- Do not deliberately generate IDs `73..110` as ordinary decorative/static objects in Upgraded.
- Keep the already-confirmed static tree pool (`68..72`, `78`, `79`, `84`) unchanged.
- Keep `82/83` as unresolved runtime/technical IDs.
- Treat `85..93` as wheat runtime states, including `93 = chaume`.
- Treat `94..102` as grape/vine runtime states; only the exact `102 -> 94` cycle semantics remain unresolved.
- Treat `103..110` as rice runtime states.
- Future SAV/live-game analysis should correlate crop object-state IDs with terrain IDs underneath them, especially cultivated/fallow terrain for wheat and rice-on-Swamp behavior.
