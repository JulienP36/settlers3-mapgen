# Settlers III MapGen — v1.7 DEV_8

DEV_8 is the focused polish pass from the DEV_7 user review. The validated v1.5 generation engine is unchanged.

## Implemented
- Fixed shifted letter shortcut binding on Windows/Tk: `Ctrl+Shift+T` and `Ctrl+Shift+C` now use uppercase keysyms, including AZERTY use-cases.
- Added a compact raster sun/moon theme toggle button.
- Reordered tabs so Statistics + Charts are adjacent, followed by Settings + Shortcuts.
- Chart data values now use stable white text with a thin black outline; axis-scale labels keep theme styling.
- Tiny non-zero segment values use alternating outside lanes, leader lines and vertical collision avoidance.
- Mining stock now has a concise snow-shading note and a clean mineral legend.
- Building Stone state colors now use an explicit red → yellow → green 3-point scale.
- Nearest-opponent chart uses compact player labels with player-color square; opponent square + arrow are shown inside the plot.
- Nearby Trees / Stones / Fish include player-color squares and a concise 0–50 / 50–100 legend note.
- Nearby Mining groups both radius bars under one centered player label + player-color square.
- Mountain / Lake / River component charts add lightweight top-3 medal markers only; semantic bar colors stay unchanged.
- DEV_7 validated height labels and A/B colors preserved.

## Validation
- 57 automated tests PASS.
- Real 768×768 / 10-player SAV chart smoke PASS.
- Protected v1.5 generation files remain unchanged.
