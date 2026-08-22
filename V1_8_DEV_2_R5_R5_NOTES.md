# v1.8 DEV_2_R5_R5

## UI header — Paint 3 baseline
- Paint 3 becomes the primary visual/layout reference.
- One stable functional header structure across widths; compact mode mostly adjusts widths and global controls.
- Generation grouping: Mode / Archetype / Modifiers, Generate / Generate batch…, then Size / Players / Seed / random / Copy seed and a tight Import / Export / PNG Preview cluster.
- `Generate batch…` reserves the future v1.8 Batch action slot and currently reports a feedback message only.
- Session / Comparison remains two-row and uses a more compact A/B cluster with dedicated clear buttons.
- History stays elastic but no longer drives the whole header width.
- Compact header tuned to fit the 900 px minimum window in Tk runtime tests.
- Wide mode restores comfortable selector widths.
- Language / Help / Theme remain horizontal when roomy and stack only in compact mode.
- No header PanedWindow/reparenting is used; Windows-stable R4 layout mechanics are preserved.

## Validation
- 82 pytest tests PASS.
- Generation smoke: 49 validations PASS.
- Binary checksum PASS.
- Protected generation/config/native-library hashes unchanged.
