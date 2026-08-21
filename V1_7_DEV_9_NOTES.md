# Settlers III MapGen — v1.7 DEV_9

DEV_9 is a deliberately small polish pass following the DEV_8 user review. The validated v1.5 generation engine is unchanged.

## Changes
- Dense tiny-segment value annotations now always use the left lane; no automatic left/right alternation.
- Nearby mining (`0–50` / `50–100 HEX`) excludes ore covered by the Snow family. Global mining Stats keep the full outside-snow / under-snow decomposition.
- Nearest-opponent annotation order is now `→ [opponent color] Pn`; no redundant current-player label is added inside the plot.
- Component podium labels use a compact `# + medal` treatment for ranks 1–3, replacing `#1/#2/#3`; ranks 4+ remain numeric.
- Stats schema bumped to v5 because local mining semantics changed.

## Validation
- 61 automated tests PASS.
- Real 768×768 / 10-player SAV chart smoke PASS.
- Protected v1.5 engine/profile/library files remain byte-for-byte unchanged.
