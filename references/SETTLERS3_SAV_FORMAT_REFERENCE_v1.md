# Settlers III `.SAV` — Binary Format Reference v1

> **CANONICAL REVERSE-ENGINEERING REFERENCE — 2026-08-17**
>
> Calibration triplet:
> - `S3_SAV_Calibration_Rich_4P_768x768.edm`
> - `S3_SAV_Calibration_Rich_4P_768x768.map`
> - `S3_SAV_Calibration_Rich_4P_768x768.sav`
>
> This document records only findings directly supported by the calibration triplet.
> `CONFIRMED` means structurally or byte-for-byte established; `STRONG` means strongly
> supported but semantics are not yet completely decoded; `TODO` remains unknown.

## 1. Header and checksum

**CONFIRMED**

- `.SAV` format version at offset `0x04` is `11 / 0x0B`.
- The checksum at offset `0x00` uses the **same checksum algorithm as EDM/MAP**:
  offsets `0..7` are excluded and little-endian DWORDs are processed starting at offset 8.

For the calibration SAV:

- stored checksum = `0x1DA6AFE5`
- recomputed checksum with the EDM/MAP algorithm = `0x1DA6AFE5`

Therefore the checksum algorithm is shared across tested EDM/MAP v10 and SAV v11.

## 2. Sequential part structure

**CONFIRMED**

Unlike the conservative EDM/MAP scanner, this SAV can be parsed sequentially from offset 8 as:

```text
uint32_le part_type
uint32_le total_size
byte[total_size - 8] encrypted_payload
```

Starting at offset 8 and advancing by `total_size` parses the complete calibration SAV
without gaps and ends exactly at EOF.

The same rolling XOR algorithm used for EDM/MAP successfully decrypts SAV parts:

```python
k = part_type & 0xff
for cipher in payload:
    plain = cipher ^ k
    out.append(plain)
    k = ((k << 1) & 0xff) ^ plain
```

The low byte of the full part type is therefore sufficient as the initial rolling key.

## 3. Main map grid — type `...0003`

**CONFIRMED**

The calibration SAV contains exactly **768 grid parts**, one for each map column.

Part types are:

```text
0x00000003
0x00010003
0x00020003
...
0x02FF0003
```

Interpretation:

```text
part_type = (x << 16) | 3
```

Each grid part has:

```text
total_size  = 18440 bytes
payload     = 18432 bytes
            = 768 * 24
```

Therefore:

- maximum-size 768 map = 768 column parts;
- each column contains 768 cells;
- each SAV map cell = **24 bytes**;
- chunk index / high 16 bits = `x`;
- position inside payload = `y`;
- to compare with normal row-major EDM/MAP arrays, the extracted SAV grid must be transposed.

Cell payload offset inside one decrypted type-3 part:

```python
cell_offset = y * 24
```

## 4. SAV cell layout — decoded fields

Current 24-byte cell layout:

```text
byte  0  TODO
byte  1  TODO
byte  2  TODO
byte  3  TODO
byte  4  height                         CONFIRMED
byte  5  TODO
byte  6  runtime terrain                CONFIRMED
byte  7  TODO / dynamic object state    PARTIAL
byte  8  runtime player claim           STRONG
byte  9  TODO
byte 10  TODO
byte 11  TODO (zero in calibration)
byte 12  TODO (zero in calibration)
byte 13  TODO
byte 14  base/static object ID           CONFIRMED
byte 15  TODO (zero in calibration)
byte 16  TODO
byte 17  ground resource                 CONFIRMED
byte 18  TODO
byte 19  TODO (zero in calibration)
byte 20  TODO
byte 21  TODO
byte 22  TODO
byte 23  TODO
```

### Byte 4 — height

**CONFIRMED**

Compared with the exported MAP height grid:

- identical cells: `589770 / 589824`
- differing cells: `54`
- agreement: `99.9908447%`

All 54 changed height cells are localized around the four player start positions.
This means the runtime initialization modifies a very small start-area footprint.

### Byte 6 — runtime terrain

**CONFIRMED field, runtime-modified values**

Compared with MAP terrain:

- identical cells: `562883 / 589824`
- differing cells: `26941`
- agreement: `95.4323663%`

Almost all differences are **water-level changes** among terrain IDs `0..7`.
Only 131 non-water terrain changes occur:

```text
Grass 16 -> runtime terrain 28 : 131 cells
```

Those 131 cells form four small clusters centered on the four player starts:

```text
(619, 549)
(333, 688)
(100, 143)
(493, 119)
```

Cluster sizes are about 32–33 cells per player.

**STRONG inference:** terrain ID `28` is a runtime/start-area terrain state created when
the game initializes the players. Exact gameplay meaning remains TODO.

### Byte 14 — object ID

**CONFIRMED**

Byte 14 matches the MAP object byte **exactly on all 589824 cells**.

```text
SAV cell byte 14 == MAP Area cell byte 2
```

This includes calibrated trees, Building Stones and decorative objects.

Therefore byte 14 is the static/base object ID field in the runtime cell.

### Byte 17 — ground resource

**CONFIRMED**

Byte 17 corresponds to the MAP ground-resource byte.

Agreement:

```text
588755 / 589824 = 99.8187595%
```

All observed differences are in the zero-high-nibble water/fish family.
No mineral-family mismatch was observed in this calibration.

Therefore:

- Coal / Iron / Gold / Gems / Sulfur survive MAP -> SAV directly in byte 17.
- Fish quantities are already dynamically modified during initial game startup/save.

### Byte 8 — runtime claim

**STRONG**

MAP input claim was entirely `255` / unclaimed.

SAV byte 8 contains:

```text
255 : 575324 cells
0   : 3500
1   : 3500
2   : 3500
3   : 4000
```

This is strongly consistent with player territory/claim initialization.
Exact claim semantics and the reason per-player counts vary between maps remain
TODO; the direct 4P triplet below provides a second observed distribution.

### Direct initial-mask confirmation — supplied 4P immediate save

**CONFIRMED for the supplied triplet**

The follow-up triplet
`S3_Continental_Legacy_4P_768x768_seed_2026081901_MapGenV1_8.{edm,map,sav}`
settles the storage question without any geometric reconstruction:

- the generated EDM Area claim byte is `255` on all `589824` cells;
- the editor-exported MAP Area claim byte is also `255` on all `589824` cells;
- the SAV captured immediately at game start contains the complete claim raster
  in type-3 **byte 8**, with counts `P1=3500`, `P2=3500`, `P3=4000`,
  `P4=4000`, and `574824` unclaimed cells.

The four original starts read from the native type-6 block are
`(652,652)`, `(424,46)`, `(54,324)` and `(212,710)`.  Copying the byte-8
coordinates directly gives the exact per-player masks; the first two have a
`71×71` bounding box and the latter two a `77×77` bounding box.  No radius,
shape table, wrapping, interpolation or nearest-start assignment is involved.

The reader therefore exposes this raster only when the strict observed
immediate-save signature is present (each active player has 3500 or 4000 cells
and no other claim value occurs).  Later SAVs continue to expose byte 8 as the
current runtime claim raster, but are not labelled as an initial mask when that
signature has evolved.

## 5. SAV type-6 player block

**CONFIRMED structure on the current native corpus; semantics deliberately
limited**

The tested type-6 payload is exactly `84 + 20×328 = 6644` bytes. The native
record offsets are:

```text
record +0   uint32  active flag (1 human / 2 computer for active slots; 0 unused)
record +4   uint32  repeated race/faction code candidate
record +16  uint32  original start X
record +20  uint32  original start Y
```

The current reader uses the active flag and the two coordinates to recover
starts. The race/faction value is exported as a candidate numeric field only;
no tribe name, effective player colour, mana current value or mana maximum is
assigned from the remaining opaque bytes. The validated viewer colour shown in
reports is the slot palette, not a value decoded from this block.

An older synthetic unit fixture uses a `96 + 20×328` layout with contiguous
`<player_id,start_x,start_y>` tuples. The reader accepts that fixture for
backwards compatibility but does not treat it as native SAV evidence.

## 6. Static versus runtime copies

Several SAV cell bytes appear to duplicate or transform map information.

Important distinction established by calibration:

- byte 14 is the exact static/base object ID;
- byte 7 contains many object-like values but is **not** an exact copy and therefore
  likely represents a runtime/dynamic object state;
- byte 6 is terrain but water depth and start-area terrain are modified by runtime;
- byte 17 is resource but fish quantities are runtime-active;
- byte 4 is height with only a tiny start-area runtime adjustment.

Do not overwrite the exact/static field with a guessed dynamic counterpart.

## 7. Additional large grid-like parts

The sequential SAV parser also finds later large parts.

### Type 70 / `0x46`

**CONFIRMED structure, semantics TODO**

```text
total_size  = 2,359,304
payload     = 2,359,296
            = 589,824 * 4
```

Thus type 70 stores exactly **4 bytes per map cell**.

In the immediate calibration save, every decoded DWORD is zero.

### Type 65 / `0x41`

**CONFIRMED structure, semantics TODO**

```text
total_size  = 589,836
payload     = 589,828
            = 4 + 589,824
```

The decrypted payload begins with:

```text
uint32_le 16
```

followed by exactly one byte per map cell.

In this calibration:

```text
0 : 589822 cells
1 : 2 cells
```

Exact semantics remain unknown.

### Type 58 / `0x3A`

Large structured/dynamic part:

```text
total_size = 3,675,768
```

It is not a simple fixed one-byte / two-byte / four-byte per-cell grid.
Its decrypted header contains structured values and ASCII data.
Further decomposition is TODO.

## 8. Known part sequence landmarks

The calibration SAV parses completely into 820 sequential parts.

Early parts include:

```text
type 0
type 20
type 26
type 27
type 30
type 1
type 2
type 0x00010002
768 x type (... << 16) | 3
type 4
type 6
type 7
...
```

The 768 type-3 grid parts begin at file offset:

```text
35122
```

and end immediately before type 4 at:

```text
14197042
```

This entire region is therefore the main 24-byte-per-cell runtime map grid.

## 9. Calibration observations around player starts

The four PlayerInfo coordinates used by the MAP were retained:

```text
P1 (619,549)
P2 (333,688)
P3 (100,143)
P4 (493,119)
```

At game initialization:

- 54 height cells change, all near starts;
- 131 Grass cells become runtime terrain 28, all near starts;
- player claims appear in SAV byte 8;
- these changes happen without altering byte-14 static object IDs.

This gives a useful signature for future start-position reverse engineering.

## 10. Safe SAV reader baseline

A first conservative reader should:

```text
1. Read version; currently accept SAV version 11.
2. Validate checksum using the EDM/MAP checksum algorithm.
3. Starting at offset 8, parse part headers sequentially.
4. Require every total_size >= 8 and within file bounds.
5. Require final part to end exactly at EOF.
6. Decrypt payload using rolling XOR with initial key = part_type & 0xff.
7. Identify grid parts where (part_type & 0xffff) == 3.
8. Interpret high 16 bits as x.
9. Require one complete set of x columns for the map side.
10. Require each type-3 payload length == side * 24.
11. Decode cell y at payload[y*24:(y+1)*24].
12. Preserve every unknown byte and part exactly.
```

Do not write SAV files yet. Reading is sufficiently established; writing has not been
validated against the game.

## 11. Confidence ledger

### CONFIRMED

- SAV version 11 / `0x0B`
- same checksum algorithm as tested EDM/MAP
- sequential `type + total_size + encrypted_payload` part framing
- same rolling XOR decryption principle
- complete file parses sequentially to EOF
- 768 type-3 grid parts on 768×768 calibration
- type-3 part high 16 bits encode map column x
- each SAV runtime cell is exactly 24 bytes
- byte 4 = height
- byte 6 = runtime terrain
- byte 14 = exact MAP/static object ID
- byte 17 = ground resource
- minerals preserved in byte 17
- fish are dynamically changed
- type 70 = exact 4-byte-per-cell payload
- type 65 = 4-byte prefix + exact 1-byte-per-cell payload
- type-6 player payload on the native corpus = `84 + 20×328` bytes
- type-6 record `+0` active flag and `+16/+20` original start coordinates

### STRONG

- byte 8 = runtime player claim/territory
- terrain 28 around starts is a player-start/runtime terrain state
- byte 7 is an object-related dynamic field
- type-6 record `+4` is a repeated race/faction-code candidate, not a proven name

### TODO

- semantic meaning of cell bytes 0..3, 5, 7, 9..13, 15..16, 18..23
- exact meaning of terrain 28
- exact meaning of type 65 and type 70 grids
- decode type 58 and remaining dynamic parts
- settlers/buildings runtime records
- opaque player-state fields beyond the confirmed type-6 offsets
- fog/visibility
- game tick/time and RNG state
- teams/diplomacy
- stock/resources/inventory
- safe SAV writing
- compare multiple saves from the same game at controlled time deltas

## 12. Next recommended calibration experiments

To decode dynamic fields efficiently, create controlled SAV pairs from the **same MAP**:

1. save immediately after load;
2. move one settler, save again;
3. cut exactly one tree, save again;
4. mine/use exactly one fish or mineral quantity, save again;
5. construct exactly one building, save again;
6. reveal a previously unseen area if fog-of-war data is present;
7. take/lose a small territory area.

Binary diffs between such paired SAVs will isolate dynamic parts far more efficiently
than comparing unrelated games.
