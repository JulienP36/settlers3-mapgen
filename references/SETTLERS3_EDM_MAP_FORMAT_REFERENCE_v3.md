# Settlers III `.EDM` / `.MAP` — Binary Format Reference v3

> **CANONICAL REVERSE-ENGINEERING REFERENCE — READ BEFORE ANY FILE WRITE**
>
> Companion: `SETTLERS3_MAPGEN_REFERENCE_v10.md`.
> This file documents **how the binary format works**; MapGen documents **what to generate**.
>
> Status: **CONFIRMED** = experimentally validated; **STRONG** = repeatedly observed/used; **PARTIAL** = usable structure with unknown fields; **TODO** = not established.

## 1. Header and checksum

**CONFIRMED:** tested files use version `10 / 0x0A`.

| Offset | Size | Meaning |
|---:|---:|---|
| `0x00` | 4 | checksum, little-endian uint32 |
| `0x04` | 4 | format version, little-endian uint32 |
| `0x08...` | variable | prefix / structured parts |

Parts do not have to begin at one hard-coded offset: scan and validate candidates.

**Checksum (CONFIRMED):** offsets `0..7` are excluded; process little-endian DWORDs from offset 8.

```python
c = 0
for pos in range(8, (len(data)//4)*4, 4):
    v = uint32_le(data[pos:pos+4])
    c = ((c >> 31) | ((((c << 1) & 0xffffffff) ^ v) & 0xffffffff)) & 0xffffffff
```

After every modification write `c` at offset 0.

## 2. Structured parts and encryption

**CONFIRMED generic known-part header:**

```text
uint32_le part_type
uint32_le total_size
byte[total_size - 8] encrypted_payload
```

Known useful types:

| Type | Meaning | Status |
|---:|---|---|
| 2 | PlayerInfo | PARTIAL |
| 6 | Area/grid | CONFIRMED |
| 7 | Settlers | CONFIRMED structure |
| 8 | Buildings | PARTIAL |
| 9 | Starting Resources | PARTIAL |

Do not assume these are all file parts.

**CONFIRMED rolling encryption/decryption.** Initial key = part type.

Decrypt:
```python
k = part_type & 0xff
for cipher in payload:
    plain = cipher ^ k
    out.append(plain)
    k = ((k << 1) & 0xff) ^ plain
```

Encrypt:
```python
k = part_type & 0xff
for plain in payload:
    out.append(plain ^ k)
    k = ((k << 1) & 0xff) ^ plain
```

The rolling key is updated from **plaintext**.

**Safe write rule:** decrypt known parts, preserve unknown bytes and payload sizes, re-encrypt in place, recalculate checksum, then re-read/validate.

**CONFIRMED terminal alignment variant (2026-08-26):** two supplied editor-written EDM files end with the normal terminal part `type=0, total_size=8`, followed by respectively one opaque byte (`03`) and three opaque bytes (`01 00 00`). Both complete files are DWORD-aligned and have exact checksums. A read-only importer may therefore accept **1–3 opaque bytes after that terminal part only** when the complete file length is divisible by four. Do not assign semantics to those bytes, accept a tail without the terminal part, or silently discard such a tail during reconstruction. Detailed evidence: `SETTLERS3_EDM_TERMINAL_PADDING_20260826.md`.

## 3. Area — part type 6

**CONFIRMED payload:**
```text
uint32_le side
Cell cells[side * side]
```

Each Cell = exactly **6 bytes**. Payload length = `4 + side*side*6`; total part size = `12 + side*side*6`.

Row-major cell offset:
```python
4 + ((y * side + x) * 6)
```

Maximum map size encountered/used here: **768×768**.

### Correct cell layout — CONFIRMED

| byte | meaning |
|---:|---|
| 0 | height/elevation |
| 1 | terrain/area |
| 2 | object ID |
| 3 | player claim |
| 4 | accessibility/occupation |
| 5 | ground resource |

```text
[height, terrain, object_id, claim, accessibility, resource]
```

**Historical trap:** one obsolete writer revision swapped height/terrain. Do not reuse that layout.

## 4. Height

**CONFIRMED/STRONG:** height is byte 0; practical editor ceiling observed = **225**. Native/editor experiments observed orthogonal neighbor deltas up to about **12**.

A byte-valid height combination is not automatically visually/gameplay-valid. Terrain topology also matters.

## 5. Terrain IDs

**CONFIRMED editor IDs:**

| ID | Terrain |
|---:|---|
| 0..7 | Water Levels 1..8 |
| 16 | Grass |
| 32 | Rocky Terrain |
| 48 | Shore |
| 64 | Desert |
| 80 | Swamp |
| 96..99 | River Width 1..4 |
| 128 | Snow |
| 144 | Mud |

**CONFIRMED transition chains from editor calibration:**
```text
Grass 16 -> 20 -> 65  -> Desert 64
Grass 16 -> 17 -> 33  -> Rocky 32
Grass 16 -> 21 -> 81  -> Swamp 80
Grass 16 -> 23 -> 145 -> Mud 144

Grass 16 -> 17 -> 33 -> Rocky 32 -> 35 -> 129 -> Snow 128
```

Snow therefore uses Rocky support.

### Critical topology update — CONFIRMED

Historical prototypes used Manhattan and later Chebyshev/8-neighbour dilation to approximate terrain bands. Those approaches were useful during early reverse engineering but are **obsolete for the current generator**.

Current component, transition and river topology uses the confirmed Settlers III **HEX6** neighbourhood:

```text
(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)
```

Generate a coherent family mask first, then assign transition IDs from **HEX6 depth inside the mask**:

```text
Mountain:
depth 1 -> 17
depth 2 -> 33
depth >=3 -> Rocky32

Snow inside Rocky:
depth 1 -> 35
depth 2 -> 129
depth >=3 -> Snow128
```

The old orientation-sensitive 2×2 motif checks may be retained as historical regression tests, but **HEX6 neighbour legality and family coherence are now the primary validation**.

## 6. Ground resource byte

**CONFIRMED:** byte 5 encodes mountain resource family in the high nibble and quantity in low nibble (`0..15`).

| high nibble | resource |
|---:|---|
| `0x10` | Coal |
| `0x20` | Iron Ore |
| `0x30` | Gold |
| `0x40` | Gems |
| `0x50` | Sulfur |

Preserve family while changing quantity:
```python
new = (old & 0xF0) | quantity
```

**Fish:** fish occupy the `0x00` family. A validated water-cell test changed `0x0F -> 0x0E`, visibly changing fish quantity while remaining accepted. Thus zero high nibble does **not** by itself mean “no resource”; inspect low nibble/context.

## 7. Object byte / accessibility

**CONFIRMED:** byte 2 = object ID; byte 4 = accessibility/occupation.

Validated conservative behavior:
- trees `68,69,70,71,72,78,79,84` -> accessibility 1
- Building Stone `115..126` -> 1
- Building Stone 13 (`127`) -> 0
- reefs `111..114` -> 1
- many decorations -> often 0, but use calibration evidence

Validated object removal for several families:
```text
object_id = 0
accessibility = 0
```

Important mapped subset:
```text
1..8    Big Stone 1..8
9..12   Stone 1..4
13..20  Border Stone 1..8
21..28  Small Stone 1..8
29..33  Wreck 1..5
34      Grave
35..37  Small Plant 1..3
38..40  Toadstool 1..3
41..42  Tree Stump 1..2
43..44  Dead Tree 1..2
45..48  Cactus 1..4
49      Skeleton
50..52  Small Flower 1..3
53..56  Small Bush 1..4
57..61  Bush 1..5
62..67  Reed 1..6
68      Birch 1
69      Birch 2
70      Elm 1
71      Elm 2
72      Oak
78      Palm 1
79      Palm 2
84      Small Tree
111..114 Reefs (very small -> very big)
115..127 Building Stone 1..13
```

**STRONG:** objects have collision/accessibility footprints beyond the anchor cell. Do not infer placement legality merely because neighboring `object_id` bytes are zero. Use calibration-map spacing.

## 8. Claim byte

**CONFIRMED/PARTIAL:** Area byte 3 = player claim. Observed writer interpretation: `0..7` parties; `255` none/unclaimed. Full semantics remain incomplete.

## 9. PlayerInfo — part 2

**CONFIRMED structure / PARTIAL semantics:** payload is a multiple of **45 bytes**.

Each 45-byte entry begins:
```text
+0  uint32_le nation
+4  uint32_le start_x
+8  uint32_le start_y
+12 byte[33] unknown/preserve
```

Known nation values:
```text
0 Romans
1 Egyptians
2 Asians
3 Amazons
255 Free choice
```

Conservative writes modify only first 12 bytes and preserve remaining 33.

Coordinates inside the map do not guarantee gameplay validity: surrounding blocking objects can produce `Invalid startposition for player N`.

## 10. Settlers — part 7

**CONFIRMED structure:**
```text
uint32_le count
count * {
    uint8 party
    uint8 settler_type
    uint16_le x
    uint16_le y
}
```
Payload length = `4 + count*6`.

Many settler IDs are decoded in writer code (Carrier 0, Digger 1, Builder 2, Woodcutter 3, Stonecutter 4, Miner 10, Fisherman 17, etc.). Unmapped IDs are not automatically invalid.

## 11. Buildings — part 8

**PARTIAL:**
```text
uint32_le count
count * {
    uint8 party
    uint8 building_type
    uint16_le x
    uint16_le y
    byte[6] tail
}
```
Payload length = `4 + count*12`.

Trailing six bytes remain incompletely decoded. Preserve them verbatim. Do not synthesize new records until dependencies are understood.

## 12. Starting Resources — part 9

This is distinct from Area ground resources.

**PARTIAL:**
```text
uint32_le count
count * {
    uint16_le x
    uint16_le y
    uint8 resource_type
    uint8 quantity
    byte[2] tail
}
```
Payload length = `4 + count*8`.

Tail is commonly observed as `FE 00`, but **preserve it verbatim** rather than treating that as a universal rule.

## 13. `.EDM` vs `.MAP`

**CONFIRMED:** the same conservative Area reader/writer, rolling part cipher and checksum logic have successfully modified supplied `.EDM` and `.MAP` files. A generated EDM was exported through the editor to MAP and successfully run in-game.

**PARTIAL:** do not claim EDM and MAP are byte-for-byte identical or contain identical parts/order. Safe statement: their tested structured-part mechanisms and Area representation are shared sufficiently for the same conservative writer.

Prefer `.EDM` as generation/test artifact, then editor inspection/export and game test.

## 14. Known failure modes

### Editor accepts, game crashes
This happened (`Structured Exception c0000005`). Editor acceptance is not sufficient. One dangerous experiment placed normal Stone objects on Rocky Terrain. Unsupported object×terrain combinations may crash despite rendering.

### See-through terrain holes
Grass/Rock and Rock/Snow junctions can be structurally readable but visually broken. The key discovered cause was invalid diagonal 2×2 transition topology from 4-direction dilation, not merely height delta.

### Invalid start
A structurally valid coordinate can fail gameplay validation because trees/objects block surrounding cells.

### Size-changing writes
Current writer is safest with unchanged known-part payload sizes. Adding/removing records is a different reverse-engineering problem.

## 15. Conservative reader

```text
1. Read bytes.
2. Read version at offset 4; currently require 10.
3. Validate checksum.
4. Scan from offset 8 for plausible known part headers.
5. Check total_size bounds.
6. Decrypt candidate using part_type key.
7. Validate payload shape.
8. Require one unambiguous Area.
9. Decode known parts only after validation.
10. For read-only EDM/MAP import, accept 1–3 final opaque bytes only after `type=0, total_size=8` and only when the complete file is DWORD-aligned.
10. Preserve all unknown data.
```

Validators:
```text
Area:       len == 4 + side*side*6
PlayerInfo: len % 45 == 0
Settlers:   len == 4 + count*6
Buildings:  len == 4 + count*12
Resources:  len == 4 + count*8
```

## 16. Conservative writer

```text
1. Start from known-good template/existing file.
2. Modify decrypted known payloads only.
3. Preserve unknown tails/bytes.
4. Keep payload sizes unchanged unless explicitly supported.
5. Re-encrypt each changed part using its part type.
6. Inject at original offsets.
7. Recalculate checksum.
8. Save to a NEW file.
9. Re-read and verify checksum/version/part lengths/coordinates.
10. Run generated-terrain topology checks.
11. Open in S3 editor.
12. Test in actual game.
```

Never overwrite the only calibration/reference copy.

## 17. Confidence ledger

### CONFIRMED / safe foundation
- version 10
- checksum algorithm
- known generic part header
- rolling XOR part cipher
- Area type 6 and exact grid layout
- six Area cell bytes in corrected order
- main terrain IDs and listed editor transition IDs
- currently calibrated object IDs
- mineral family nibble + quantity nibble
- fish quantity behavior
- PlayerInfo stride 45 + first 3 DWORDs
- Settler 6-byte records
- Building 12-byte stride + first 6 decoded bytes
- Starting Resource 8-byte stride + first 6 decoded bytes
- conservative writer works on tested MAP and EDM
- post-write checksum requirement
- terminal `type=0 / size=8` followed by 1–3 opaque DWORD-alignment bytes in the two supplied EDM samples

### STRONG / continue testing
- accessibility semantics for every object/state
- complete object collision footprints
- height/slope limits across every terrain
- complete settler/building/resource ID tables
- complete object×terrain legality matrix
- all differences between EDM and MAP

### TODO / unknown
- PlayerInfo bytes 12..44
- Building trailing 6 bytes
- Starting Resource trailing 2 bytes beyond observations
- full prefix/header semantics
- unlisted part types
- safe variable-length record creation/deletion
- hidden cross-part dependencies
- construction of a completely new file without template
- complete EDM↔MAP delta
- exact serialization rules for every terrain corner case

## 18. Required regression tests

The binary toolchain should maintain tests for:
- decrypt(encrypt(payload,type),type) roundtrip
- checksum against known reference
- Area detection in EDM and MAP
- exact Area length
- six-byte cell roundtrip
- terrain IDs
- resource family/quantity preservation
- PlayerInfo write preserving 33-byte tail
- Settler write
- Building write preserving 6-byte tail
- Starting Resource write preserving 2-byte tail
- no unintended output-size change
- post-write checksum
- byte-diff limited to intended encrypted parts + checksum
- acceptance of 1/2/3-byte terminal DWORD padding and rejection without the terminal part
- zero forbidden mountain 2×2 motifs on generated maps

## 19. Reference hierarchy

Always consult both:

1. **`SETTLERS3_EDM_MAP_FORMAT_REFERENCE.md`** — binary read/write truth.
2. **`SETTLERS3_MAPGEN_REFERENCE.md`** — validated generation/gameplay parameters.

Useful code lineage:
- `s3_map_writer.py`: minimal validated Area reader/writer.
- `s3_map_writer_v2.py`: parts 2/6/7/8/9 and conservative record edits.
- later `s3_map_writer_v*`: terrain/object calibration and experimental helpers.

Do not blindly trust stale code over validated findings. Example: an intermediate revision had height/terrain reversed.

## 20. Update rule

Whenever a binary discovery is validated:
1. reproduce it on controlled calibration data where possible;
2. label observation vs inference;
3. test EDM in editor;
4. test exported MAP in-game when relevant;
5. update **this file immediately**;
6. update MapGen reference too if generation behavior changes.

This file exists specifically so reverse-engineering knowledge is not lost between prototype iterations.


## 21. Engine-valid PlayerInfo start positions — CONFIRMED LESSON

**CONFIRMED by Seed `2026081402` diagnostics.**

A map can:
- open correctly in the editor;
- have valid checksum / Area structure;
- have apparently reasonable Grass terrain, slopes, objects and resources around the start;
- yet still crash in the game engine with `c0000005` solely because of the PlayerInfo start coordinates.

Diagnostic sequence:

- original Seed02 with generated starts `(177,60)` and `(27,84)` -> **engine crash**
- same seed with all rivers removed -> **same crash**
- same seed with objects removed -> **same crash**
- same seed with Area ground resources removed -> **same crash**
- same seed reduced to terrain + height only -> **same crash**
- same regenerated terrain with PlayerInfo starts replaced by known-good coordinates from Prototype 36f -> **valid in engine**
- full Seed02 restored with all original layers and only PlayerInfo starts replaced by `(207,69)` and `(204,192)` -> **valid in engine**

Therefore:
> The crash source was the generated PlayerInfo start coordinates, not terrain, heightmap, rivers, objects, accessibility or ground resources.

Important consequence:
- bounds checking is insufficient;
- “center cell is Grass and object-free” is insufficient;
- local Grass percentage, slope thresholds and object-clear radius used by the previous heuristic are insufficient;
- the engine applies an additional start-validity rule not yet decoded.

Until the exact rule is understood:
1. treat procedurally selected starts as **UNVALIDATED**;
2. do not use the old heuristic as a guarantee of engine validity;
3. prefer known-good start coordinates only when they are valid on the generated terrain, or test candidate starts experimentally;
4. keep PlayerInfo start validation as a separate reverse-engineering task.

**TODO:** identify the actual engine/editor condition behind start-position validation and encode it as a deterministic validator.


## 14. 2026-08-17 generation semantics update

### Fish versus River

Fish resource bytes are valid on Water `0..7`.

Current gameplay validation: **fish do not function on River terrain `96..99`**. Generated river cells must therefore have resource byte `0`.

### Building Stone depletion semantics

Object IDs `115..127` are the 13 visual/resource states of Building Stone.

User-confirmed depletion model:

```text
state = object_id - 114
remaining_stones = 13 - state = 127 - object_id
```

Thus:

```text
115 -> 12 stones remaining
...
126 -> 1
127 -> 0 / exhausted
```

This semantic is used by MapGen balance calculations; the binary object ID itself remains the stored state.

### Small Tree generation semantics

Object ID `84` is a separate custom bonus pool in current MapGen generation. It is not part of the native adult-tree (`68..72`) count used for density calibration.
