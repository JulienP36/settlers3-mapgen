# Settlers III `.SAV` — Binary Format Reference v2 Long-Play

> **CANONICAL REVERSE-ENGINEERING REFERENCE — 2026-08-18**
>
> This document extends `SETTLERS3_SAV_FORMAT_REFERENCE_v1.md` with a chronological corpus of 16 saves from the same 768×768 / 10-player game.
> Saves 1–8 are pre-offensive. Saves 9–16 cover the offensive phase. Save 16 is the state immediately after the game announced victory while allowing continued solo play.
>
> Analysis performed with assistance from ChatGPT. Only observations supported by the supplied SAV bytes are promoted here; unknown runtime fields remain unknown.

## 1. Corpus integrity

All 16 files:

- are SAV version 11;
- validate with the shared EDM/MAP/SAV rolling checksum;
- parse sequentially from offset 8 to EOF;
- contain exactly 838 sequential parts;
- contain a complete 768×768 runtime grid using 768 type-3 column parts;
- use 24 bytes per runtime cell.

The files grow from 22,214,329 bytes in save 1 to 46,603,259 bytes in save 16, demonstrating that large dynamic SAV parts grow substantially during play even though the map grid dimensions stay constant.

## 2. Runtime cell layout — confidence update

```text
byte  0  TODO
byte  1  TODO
byte  2  TODO
byte  3  TODO
byte  4  height                         CONFIRMED
byte  5  TODO
byte  6  runtime terrain                CONFIRMED
byte  7  object-related dynamic state   PARTIAL
byte  8  runtime player claim           CONFIRMED
byte  9  TODO
byte 10  TODO
byte 11  TODO
byte 12  TODO
byte 13  TODO
byte 14  runtime/static-object slot      CONFIRMED FIELD, MUTABLE DURING PLAY
byte 15  TODO
byte 16  navigation/walkability         CONFIRMED by prior runtime calibration
byte 17  ground resource                CONFIRMED, MUTABLE DURING PLAY
byte 18  TODO
byte 19  TODO
byte 20  TODO
byte 21  TODO
byte 22  TODO
byte 23  TODO
```

### Important correction to v1 wording for byte 14

At initial MAP→SAV calibration, byte 14 matched the MAP object byte exactly on every cell. The 16-save series proves that this field is **not an immutable archival copy** once gameplay progresses.

Between save 1 and save 16, byte 14 changes on 2,440 cells. Observed transitions include:

- Small Tree `84` becoming adult/tree-family IDs such as `68`, `69`, `70`, `72`, `73`, `75`;
- adult trees becoming `0` after removal;
- Building Stone states progressing to `127` / exhausted;
- many `0 -> object` transitions associated with runtime construction/growth/activity.

Therefore the safe interpretation is:

> byte 14 is the runtime cell's static/base-object slot and equals the MAP object ID at initialization, but the slot is gameplay-mutable.

Do not treat byte 14 as an immutable copy of the original MAP after the game has started.

## 3. Byte 8 — player claim/territory is now CONFIRMED

The chronological territory evolution makes the semantics unambiguous.

Save 1 begins with the generator's initial claims:

```text
P1  3500
P2  3500
P3  3500
P4  3500
P5  3500
P6  4000
P7  3500
P8  3500
P9  3500
P10 3500
unclaimed 554324
```

By save 8, immediately before the offensive phase, the claims are:

```text
P1 59146
P2 58631
P3 34290
P4 15627
P5 55411
P6 33639
P7 45533
P8 74377
P9 27796
P10 17180
unclaimed 168194
```

The human player is claim value `0` / P1: during the offensive phase large areas owned by other claim values are transferred to value `0`.

Notable eliminations visible directly in byte 8:

- save 8 → 9: P6 (`claim=5`) goes from 33,639 cells to 0; 33,639 cells transition `5 -> 0`;
- save 11 → 12: P3 and P4 (`claim=2` and `3`) go to 0;
- save 12 → 13: P9 (`claim=8`) reaches 0;
- save 13 → 14: P7 and P10 (`claim=6` and `9`) reach 0;
- save 15 → 16: every remaining enemy claim disappears and all claimed territory belongs to P1 / value `0`.

At save 16:

```text
claim 0   430327 cells
claim 1..9     0 cells
claim 255 159497 cells
```

The final 15→16 transition contains exactly 60,698 changed claim cells:

```text
claim 1 -> 0 : 57545
claim 4 -> 0 :  2574
claim 7 -> 0 :   495
255 -> 0      :    84
```

This is decisive evidence that byte 8 is the runtime ownership/territory field.

## 4. Byte 17 — mineral depletion observed directly

The source map used for this long-play has no fish in any of the 16 saves, so this corpus cannot validate fish economy. Fish occupancy and quantity are zero throughout.

Minerals, however, deplete progressively and remain in the same resource-family encoding established previously.

Save 1 → save 16:

| Resource | occupied cells | quantity | quantity consumed |
|---|---:|---:|---:|
| Coal | 28,375 → 27,298 | 226,887 → 212,501 | 14,386 (6.34%) |
| Iron | 12,202 → 11,726 | 97,241 → 90,369 | 6,872 (7.07%) |
| Gold | 8,164 → 8,087 | 66,048 → 64,837 | 1,211 (1.83%) |
| Gems | 3,098 → 3,022 | 24,924 → 23,533 | 1,391 (5.58%) |
| Sulfur | 4,745 → 4,745 | 38,096 → 38,096 | 0 (0%) |

Observed byte-17 transitions are predominantly decrementing low-nibble quantities, for example `18 -> 17`, `19 -> 18`, followed eventually by transitions to `0` when a deposit cell is exhausted.

This independently confirms that byte 17 is the live ground-resource field, not merely a static copy.

## 5. Building Stone runtime evidence

Using the established Building Stone family `115..126`, with remaining stock `127 - object_id`:

```text
save 1 : 1742 anchors / 14690 stock units
save 6 : 1742 anchors / 14687 stock units
save 7 : 1669 anchors / 14075 stock units
save 16: 1614 anchors / 13614 stock units
```

The series contains direct transitions from active Building Stone IDs to `127`, including `115 -> 127` and `121 -> 127` between save 1 and save 16.

This strengthens the existing interpretation of Building Stone object IDs as depletion/fill states and explains why byte 14 must be considered runtime-mutable.

## 6. Small Tree 84 growth is directly visible

Counts across the long-play:

```text
save 1 : Small Tree84 = 393, adult trees 68..72 = 1461
save 8 : Small Tree84 = 291, adult trees 68..72 = 1489
save 16: Small Tree84 = 223, adult trees 68..72 = 1516
```

Direct byte-14 transitions from save 1 to save 16 include:

```text
84 -> 72 : 16 cells
84 -> 69 : 14
84 -> 70 : 14
84 -> 75 : 13
84 -> 73 : 12
84 -> 68 : 11
84 -> 0  : 21
```

The exact full tree growth-state machine remains TODO, but this corpus directly confirms that object `84` participates in growth into multiple tree-family states during gameplay.

## 7. Runtime terrain byte 6

Water remains structurally stable across all 16 saves:

```text
Water0..7 cells = 123555 in every save
```

The runtime terrain value `28`, previously seen only around freshly initialized starts, expands massively during normal play:

```text
save 1 :   333 cells
save 2 : 10505
save 5 : 40135
save 7 : 75647
save 8 : 75622
save 16: 35893
```

In tested saves, terrain-28 cells are associated with claimed territory rather than unclaimed wilderness. However, this corpus alone does **not** isolate the exact gameplay meaning of terrain 28. It should continue to be normalized to Grass16 only when extracting a static-like terrain view, and its precise runtime semantics remain TODO.

Other runtime terrain IDs also change during play. Therefore SAV byte 6 must not be treated as an immutable reconstruction of the original MAP terrain.

## 8. Dynamic byte 7

Byte 7 changes on thousands of cells between consecutive saves and contains many object-like values. It frequently changes together with gameplay activity while byte 14 changes much less often.

The chronological corpus therefore reinforces the v1 conclusion:

> byte 7 is object-related dynamic state, but its exact semantics are not yet decoded.

It must remain separate from byte 14.

## 9. Key temporal transitions

### Save 8 → 9 — first supplied offensive transition

Changed runtime-grid cells include:

```text
byte 6  terrain     8680
byte 7  dynamic     4663
byte 8  claim      40316
byte 14 object        44
byte 17 resource     601
```

The dominant claim change is:

```text
claim 5 -> 0 : 33639 cells
```

This is a clean territory-elimination signature.

### Save 15 → 16 — victory-state transition

Changed runtime-grid cells include:

```text
byte 6  terrain    21583
byte 7  dynamic     3024
byte 8  claim      60698
byte 14 object       270
byte 17 resource     362
```

All remaining enemy claim values disappear in this interval. This makes the pair particularly valuable for future search for the explicit game-over/victory flag in non-grid parts.

## 10. Non-grid dynamic parts

All saves retain 838 sequential parts, but several large dynamic parts change payload size during the game. The map grid itself remains fixed-size.

The 15→16 pair shows changes in many non-grid parts, including types `0`, `1`, `2`, `4`, `6`, `7`, `8`, `9`, `0x0A` through `0x17`, `0x1C`, `0x33`, `0x38`, `0x3A`, `0x3B`, `0x3F` through `0x43`, etc.

A tiny type `0x3B` part has a 5-byte payload. Its first four bytes remain:

```text
01 00 00 00
```

while byte 4 varies across saves and is `00` in save 16. Because that byte also takes unrelated values in earlier saves (`0x26`, `0x04`, `0xB0`, `0x3C`, `0xB7`), it is **not yet safe to call it a victory flag**. It is merely a candidate field worth isolating with controlled victory/no-victory pairs.

## 11. Safe static-like extraction from an arbitrary SAV

For MapGen visualization/import, the established conservative extraction remains:

```text
height        = byte 4
terrain       = byte 6, with runtime terrain 28 normalized to Grass16 for static-like display
claim         = byte 8
object        = byte 14
resource      = byte 17
```

Important caveat after this long-play analysis:

- `terrain`, `object`, `claim`, and `resource` are live runtime state;
- a late-game SAV is **not** a byte-perfect copy of the original MAP;
- byte 14 can contain grown, depleted, removed, or newly created objects;
- byte 17 contains remaining resources after consumption;
- byte 8 contains current territory, not original starts only.

The import GUI should therefore label SAV-derived views as runtime state rather than original-map reconstruction.

## 12. Confidence ledger after the 16-save corpus

### CONFIRMED

- SAV v11 framing/checksum/decryption from v1
- 24-byte type-3 runtime cells
- byte 4 = height
- byte 6 = runtime terrain
- byte 8 = runtime player claim/territory
- byte 14 = runtime static/base-object slot, identical to MAP object at initialization but mutable afterward
- byte 16 = runtime navigation/walkability from prior calibration
- byte 17 = live ground resource
- mineral low-nibble quantities deplete in byte 17
- Building Stone state/stock evolves through byte 14
- Small Tree84 grows into tree-family object states
- water-cell count in this game remains constant across all 16 supplied saves
- all 16 supplied SAVs parse to EOF and have valid checksums

### STRONG / PARTIAL

- byte 7 = object-related dynamic state
- runtime terrain 28 is a claimed-area gameplay terrain state; exact meaning remains unresolved

### TODO

- explicit victory/game-over flag
- exact game tick/time location
- exact byte-7 semantics
- precise terrain-28 gameplay semantics
- player state structures and defeat flags
- buildings/settlers/inventory structures
- diplomacy/teams
- fog/visibility
- RNG state
- safe SAV writer

## 13. Next targeted experiments

The 16-save time series replaces the old generic TODO "compare multiple saves from the same game" — that experiment is now complete.

The highest-value controlled follow-ups are now narrower:

1. save immediately before and immediately after the victory notification with as little elapsed game time as possible;
2. one controlled Building Stone extraction step with no other actions;
3. one controlled Small Tree84 growth observation if timing can be isolated;
4. one controlled terrain-28 creation/removal event;
5. one controlled fish consumption pair on a fish-enabled map.

These pairs would let us assign semantics to currently dynamic-but-unknown parts with much less ambiguity than broad long-play diffs.
