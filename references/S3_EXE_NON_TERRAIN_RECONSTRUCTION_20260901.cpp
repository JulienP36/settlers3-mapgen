/*
 * Settlers III - transcription comportementale progressive
 *
 * Source : S3.EXE, SHA-256
 * 25a6de6703ea3f9d88537aa309192ff0399b81f8a1221f40a222f36dc6be37a6
 *
 * This is NOT the original source and is not intended to compile as-is.
 * It records behavior recovered from the i386 disassembly. Names are
 * deliberately descriptive; PARTIAL/TODO comments mark semantics that are
 * not yet safe to turn into generator rules.
 */

#include <cstdint>
#include <cstddef>
#include <algorithm>
#include <utility>
#include <vector>

// Behavioral interfaces. The real runtime types are not reconstructed here.
struct NativeStartSlot;
struct NativeWorld;
bool native_4d99e0(
    NativeWorld&, int x, int y, int pattern_kind,
    int player_slot_or_context, int variant);
void native_place_start_batch(
    NativeWorld&, int player, int x, int y,
    int type_or_mode, int count_or_value, int profile);
std::uint16_t native_prng16(NativeWorld&);
std::pair<int, int> native_offset(NativeWorld&, unsigned index);
bool native_terrain_family_match(
    NativeWorld&, int x, int y, std::uint8_t source_terrain);
bool native_static_object_footprint_free(
    NativeWorld&, int x, int y,
    unsigned accessibility_mode, unsigned collision_variant);
void native_mark_static_object_footprint(
    NativeWorld&, int x, int y, unsigned accessibility_mode);

// 0x4FEB40/0x4FEB70. The same generator is used by terrain and by later
// party-layer routines, but the orchestrator explicitly seeds it again at
// 0x53CE55 before starting players/entities. Arithmetic is intentionally kept
// at 16 bits, matching the i386 instructions.
struct NativePrngState {
    std::uint16_t a;
    std::uint16_t b;
    std::uint16_t c;
};

void native_seed_prng(NativePrngState& state, std::uint32_t input) {
    const std::uint16_t seed = static_cast<std::uint16_t>(input);
    state.a = seed;
    state.b = static_cast<std::uint16_t>(seed + 1000);
    state.c = static_cast<std::uint16_t>(seed + 2000);
}

std::uint16_t native_prng_step(NativePrngState& state) {
    const std::uint16_t output = static_cast<std::uint16_t>(state.a + state.b)
        ^ state.c;
    const std::uint16_t next_c = static_cast<std::uint16_t>(state.c + state.b);
    const std::uint16_t next_b = static_cast<std::uint16_t>(
        (static_cast<std::uint32_t>(state.b ^ next_c) >> 1)
        | (static_cast<std::uint32_t>(state.b ^ next_c) << 15));
    state.a = output;
    state.b = next_b;
    state.c = static_cast<std::uint16_t>(
        (static_cast<std::uint32_t>(next_c) >> 1)
        | (static_cast<std::uint32_t>(next_c) << 15));
    return output;
}

// 0x516530. The runtime bank is generated once per world context. It is not
// a chunk grid: it is a deterministic ordering of hexagonal offsets reused by
// start selection, resource placement and structured footprints.
struct NativeHexOffset {
    std::int32_t dx;
    std::int32_t dy;
    std::int32_t ring_marker;
    std::int32_t orientation;
};

// Raw normal Continental start pattern, key 15 (pattern_kind 0x0F,
// profile 0), extracted from file offset 0x2AA174 + 15*0x960 + 20*4.
// The stream is deliberately kept as uint32_t: negative offsets are native
// two's-complement words and the 0x8000000[0-3] values are interpreter
// controls, not coordinates.  It decodes to exactly 33 coordinate pairs.
constexpr std::uint32_t kNormalContinentalPatternWords[] = {
    0x80000000u,
    0xFFFFFFFFu, 0xFFFFFFFEu, 0x00000000u, 0xFFFFFFFEu,
    0xFFFFFFFFu, 0xFFFFFFFFu, 0x00000000u, 0xFFFFFFFFu,
    0x00000001u, 0xFFFFFFFFu, 0xFFFFFFFFu, 0x00000000u,
    0x00000000u, 0x00000000u, 0x00000001u, 0x00000000u,
    0x00000002u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x00000001u, 0x00000001u, 0x00000002u, 0x00000001u,
    0x00000001u, 0x00000002u, 0x00000002u, 0x00000002u,
    0x00000002u, 0x00000003u, 0x80000001u, 0x00000003u,
    0x00000002u, 0x80000002u,
    0xFFFFFFFEu, 0xFFFFFFFDu, 0xFFFFFFFFu, 0xFFFFFFFDu,
    0x00000000u, 0xFFFFFFFDu, 0x00000001u, 0xFFFFFFFEu,
    0x00000002u, 0xFFFFFFFFu, 0x00000003u, 0x00000000u,
    0x00000003u, 0x00000001u, 0x00000003u, 0x00000003u,
    0x00000003u, 0x00000004u, 0x00000002u, 0x00000004u,
    0x00000001u, 0x00000003u, 0x00000000u, 0x00000002u,
    0xFFFFFFFFu, 0x00000001u, 0xFFFFFFFEu, 0x00000000u,
    0xFFFFFFFEu, 0xFFFFFFFFu, 0x00000004u, 0x00000002u,
    0xFFFFFFFEu, 0xFFFFFFFEu, 0x80000003u,
};

constexpr std::size_t kNormalContinentalPatternWordCount =
    sizeof(kNormalContinentalPatternWords)
    / sizeof(kNormalContinentalPatternWords[0]);
static_assert(kNormalContinentalPatternWordCount == 70);

std::vector<NativeHexOffset> native_build_hex_offset_bank() {
    struct Candidate {
        std::uint32_t metric;
        std::int32_t x;
        std::int32_t y;
    };

    std::vector<Candidate> candidates;
    candidates.reserve(5000);

    std::int32_t x = 1;
    std::int32_t y = 0;
    for (unsigned i = 0; i < 5000; ++i) {
        const std::int32_t d = 2 * x - y;
        const std::uint64_t metric64 =
            2500ull * static_cast<std::uint64_t>(d) * d
            + 7569ull * static_cast<std::uint64_t>(y) * y;
        candidates.push_back({static_cast<std::uint32_t>(metric64), x, y});

        ++y;
        if (y == x) {
            y = 0;
            ++x;
        }
    }

    std::vector<NativeHexOffset> bank;
    bank.reserve(1 + 3333 * 6);
    bank.push_back({0, 0, 0, 0});

    std::int32_t ring = 1;
    for (unsigned group = 0; group < 3333; ++group) {
        unsigned selected = 0;
        for (unsigned i = 1; i < candidates.size(); ++i) {
            // The native comparison is strict, so ties retain the first
            // candidate in enumeration order.
            if (candidates[i].metric < candidates[selected].metric) {
                selected = i;
            }
        }

        const Candidate candidate = candidates[selected];
        candidates[selected].metric = 0x7FFFFFFFu;

        const std::int32_t cx = candidate.x;
        const std::int32_t cy = candidate.y;
        const std::int32_t offsets[6][2] = {
            { cx,     cy     },
            { cx - cy, cx    },
            {-cy,     cx - cy},
            {-cx,    -cy     },
            { cy - cx, -cx   },
            { cy,     cy - cx},
        };
        const bool rotated = 2 * cy > cx;
        const std::int32_t orientations[6] =
            {0, 1, 2, 3, 4, 5};
        for (unsigned i = 0; i < 6; ++i) {
            const unsigned orientation = rotated ? (i + 1) % 6 : i;
            bank.push_back({
                offsets[i][0], offsets[i][1], ring,
                orientations[orientation],
            });
        }

        if (cy == 0) {
            ++ring;
        }
    }
    return bank;
}

struct NativeAreaCell {
    std::uint8_t height;
    std::uint8_t terrain;
    std::uint8_t static_object;
    std::uint8_t claim;
    std::uint8_t accessibility;
    std::uint8_t ground_resource;
};

struct RuntimeCell {
    // The native runtime has a 0x18-byte cell stride. Only fields used by the
    // audited paths are named here.
    std::uint16_t dynamic_entity; // runtime +0x67444
    std::uint16_t associated_link; // runtime +0x67446, semantics PARTIAL
    std::uint8_t height;           // runtime +0x67448
    std::uint8_t terrain;          // runtime +0x6744A
    std::uint8_t object;           // runtime +0x6744B
    std::uint8_t claim;            // runtime +0x6744C
    std::uint8_t flags_a;          // runtime +0x6744D / nearby state
    std::uint8_t accessibility;    // runtime +0x6744E
    std::uint8_t loader_flag;      // runtime +0x6744F
    std::uint16_t object_word;     // runtime +0x67452
    std::uint8_t auxiliary;        // runtime +0x67454
    std::uint8_t resource;         // runtime +0x67455
};

// 0x51AD40, called by 0x5166D0. This is a behavioral transcription of the
// initial ground-mineral pass; it is deliberately kept separate from entity
// allocation and from the later simulation-time resource writers.
struct NativeMineralRule {
    std::uint8_t resource_base;
    unsigned density;
};

void native_place_ground_minerals(NativeWorld& world, int side) {
    constexpr NativeMineralRule rules[] = {
        {0x50, 30},  // 0x5189D4: sulfur
        {0x40, 20},  // 0x5189DF: gems
        {0x30, 60},  // 0x5189EA: gold
        {0x20, 100}, // 0x5189F5: iron
        {0x10, 300}, // 0x518A03: coal
    };

    const unsigned tiles = static_cast<unsigned>((side + 63) >> 6);
    for (const NativeMineralRule& rule : rules) {
        const unsigned batches =
            (tiles * tiles * rule.density) >> 3;
        for (unsigned batch = 0; batch < batches; ++batch) {
            // The native helper uses PRNG16 * side here, unlike the start and
            // object helpers which use (side - 2) and add one.
            const int center_x =
                (static_cast<unsigned>(native_prng16(world)) * side) >> 16;
            const int center_y =
                (static_cast<unsigned>(native_prng16(world)) * side) >> 16;
            const unsigned tries =
                (native_prng16(world) & 0x3F) + 0x20;
            const unsigned threshold =
                (native_prng16(world) & 0x7FFF) + 0x8000;

            for (unsigned attempt = 0; attempt < tries; ++attempt) {
                const auto [dx, dy] = native_offset(world, attempt);
                const int x = center_x + dx;
                const int y = center_y + dy;
                if (x < 1 || x >= side - 1 || y < 1 || y >= side - 1) {
                    continue;
                }

                RuntimeCell& cell = world.cell(x, y);
                const std::uint8_t terrain_class =
                    static_cast<std::uint8_t>(cell.terrain & 0xF0);
                if (terrain_class != 0x20 && terrain_class != 0x80) {
                    continue;
                }
                if (cell.resource != 0) {
                    continue;
                }
                if (native_prng16(world) >= threshold) {
                    continue;
                }

                cell.resource = static_cast<std::uint8_t>(
                    rule.resource_base + (native_prng16(world) % 15) + 1);
            }
        }
    }
}

// 0x518A08, initial fish pass. The pointer walk is the native (side-1) by
// (side-1) traversal and has no wraparound.
void native_place_initial_fish(NativeWorld& world, int side) {
    for (int x = 0; x < side - 1; ++x) {
        for (int y = 0; y < side - 1; ++y) {
            RuntimeCell& cell = world.cell(x, y);
            if ((cell.terrain & 0xF0) != 0 || cell.resource != 0) {
                continue;
            }
            if (native_prng16(world) <= 0x9C40) {
                continue;
            }
            cell.resource = static_cast<std::uint8_t>(
                native_prng16(world) & 0x0F);
        }
    }
}

// 0x51B010 and 0x51B1A0. These helpers write the static-object byte directly,
// not an entity slot. `attempt_shift` is 1 for 0x51B010 and 4 for 0x51B1A0;
// the two native routines do not have the same density divisor.
void native_place_static_object_group(
    NativeWorld& world,
    std::uint8_t source_terrain,
    std::uint8_t object_min,
    std::uint8_t object_max,
    unsigned density,
    unsigned accessibility_mode,
    unsigned collision_variant,
    unsigned attempt_shift) {
    const unsigned tiles = static_cast<unsigned>((world.side() + 63) >> 6);
    const unsigned attempts = (tiles * tiles * density) >> attempt_shift;
    for (unsigned i = 0; i < attempts; ++i) {
        const int x =
            ((static_cast<unsigned>(native_prng16(world))
              * (world.side() - 2)) >> 16) + 1;
        const int y =
            ((static_cast<unsigned>(native_prng16(world))
              * (world.side() - 2)) >> 16) + 1;
        if (!world.in_bounds(x, y)) {
            continue;
        }
        if (!native_terrain_family_match(
                world, x, y, source_terrain)) {
            continue;
        }
        if (!native_static_object_footprint_free(
                world, x, y, accessibility_mode, collision_variant)) {
            continue;
        }

        RuntimeCell& cell = world.cell(x, y);
        const auto picked = object_min == object_max
            ? object_min
            : static_cast<std::uint8_t>(
                object_min + ((static_cast<unsigned>(native_prng16(world))
                               * (object_max - object_min + 1)) >> 16));
        cell.object = picked;
        // The native helper optionally marks the center or center+six-neighbor
        // footprint with access bit 0x01. Exact neighbor adapters are TODO.
        native_mark_static_object_footprint(
            world, x, y, accessibility_mode);
    }
}

// Exact call families observed in 0x5166D0. A range in the fixed table means
// that 0x51B010 is called once for every ID in that interval; only the ranged
// table delegates ID selection to 0x51B1A0.
struct NativeStaticObjectCall {
    std::uint8_t source_terrain;
    std::uint8_t object_min;
    std::uint8_t object_max;
    unsigned density;
    unsigned accessibility_mode;
    unsigned collision_variant;
};

constexpr NativeStaticObjectCall kNativeFixedStaticObjectCalls[] = {
    {0x10, 0x01, 0x01, 1, 2, 1},
    {0x10, 0x02, 0x0C, 1, 0, 0},
    {0x10, 0x0D, 0x14, 1, 0, 2},
    {0x30, 0x1D, 0x1E, 5, 2, 0},
    {0x30, 0x1F, 0x1F, 5, 0, 0},
    {0x30, 0x20, 0x21, 5, 2, 0},
    {0x10, 0x22, 0x22, 1, 2, 1},
    {0x10, 0x15, 0x1C, 1, 0, 0},
    {0x10, 0x23, 0x29, 1, 0, 0},
    {0x10, 0x2A, 0x2A, 1, 2, 0},
    {0x40, 0x2B, 0x2C, 3, 1, 2},
    {0x40, 0x2D, 0x2F, 6, 1, 1},
    {0x40, 0x30, 0x30, 6, 0, 0},
    {0x40, 0x31, 0x31, 3, 0, 0},
    {0x10, 0x32, 0x3D, 1, 0, 0},
    {0x50, 0x3E, 0x43, 150, 0, 0},
    {0x10, 0x44, 0x4D, 1, 1, 2},
    {0x40, 0x4E, 0x4F, 1, 1, 2},
    {0x10, 0x50, 0x51, 9, 1, 2},
    {0x10, 0x73, 0x7E, 1, 2, 1},
    {0x10, 0x7F, 0x7F, 1, 0, 0},
};

constexpr NativeStaticObjectCall kNativeRangedStaticObjectCalls[] = {
    {0x10, 0x44, 0x45, 0x0B, 1, 2},
    {0x10, 0x46, 0x47, 0x0B, 1, 2},
    {0x10, 0x48, 0x49, 0x0B, 1, 2},
    {0x10, 0x4A, 0x4B, 0x0B, 1, 2},
    {0x10, 0x4C, 0x4D, 0x0B, 1, 2},
    {0x40, 0x4E, 0x4F, 0x0B, 1, 2},
    {0x10, 0x50, 0x51, 0x0B, 1, 2},
    {0x10, 0x73, 0x7E, 0x37, 2, 1},
};

// 0x4FD540 consumes type-9 records in eight-byte steps. The last byte is not
// read by the loader loop shown in the binary; that does not prove it is unused
// elsewhere.
struct NativeType9Record {
    std::uint16_t x;
    std::uint16_t y;
    std::uint8_t field4;
    std::uint8_t field5;
    std::uint8_t field6;
    std::uint8_t field7_unread_here;
};

// 0x504420 stores only the following observed projection in its 0x0E-byte
// registry entry. The intervening bytes and the link/update branch remain
// deliberately opaque.
struct NativeType9RegistryProjection {
    std::uint8_t field0_from_record4; // entry +0x00
    std::uint8_t opaque_1_to_4[4];     // entry +0x01..+0x04
    std::uint8_t field5_from_record5;  // entry +0x05
    std::uint8_t opaque_6_to_7[2];     // entry +0x06..+0x07
    std::uint8_t field6_from_record6;  // entry +0x08
    std::uint8_t opaque_9;             // entry +0x09
    std::uint16_t x;                   // entry +0x0A
    std::uint16_t y;                   // entry +0x0C
};

void native_materialize_type9_record(
    NativeWorld& world, const NativeType9Record& raw) {
    std::uint8_t field4 = raw.field4;
    if (raw.field5 == 0 && raw.field6 == 0) {
        field4 = 0xFF;
    }

    // The exact cell lookup is known: the loader tests runtime +0x6744F before
    // choosing the allocation path. These named methods stand for the two
    // branches at 0x4FD540; their internal tables are not reconstructed here.
    if (!world.type9_cell_loader_flag_is_clear(raw.x, raw.y)) {
        return;
    }
    if (raw.field6 != 0) {
        world.allocate_type9_entry(
            raw.x, raw.y, field4, raw.field5, raw.field6);
    } else {
        world.link_or_update_type9_entry(
            raw.x, raw.y, field4, raw.field5);
    }
}

// 0x4FD540, Area/type 6 materialization.
void native_materialize_area(
    RuntimeCell* runtime,
    const NativeAreaCell* area,
    std::uint32_t side,
    const std::uint8_t* party_map) {
    for (std::uint32_t y = 0; y < side; ++y) {
        for (std::uint32_t x = 0; x < side; ++x) {
            const NativeAreaCell& in = area[y * side + x];
            RuntimeCell& out = runtime[y * 768u + x]; // native max stride

            out.height = in.height;
            out.terrain = in.terrain;
            out.object = in.static_object;
            out.object_word = in.static_object;
            out.accessibility = in.accessibility;

            if (in.claim == 0xFF) {
                out.claim = 0xFF;
                out.loader_flag = 0;
            } else if (party_map[in.claim] != 0xFF) {
                out.claim = party_map[in.claim];
                out.loader_flag = 0;
            } else {
                out.claim = 0xFF;
                out.loader_flag = 1;
            }

            if (out.claim != 0xFF) {
                out.accessibility = static_cast<std::uint8_t>(
                    out.accessibility | 0x40);
            }
            out.resource = in.ground_resource;

            out.dynamic_entity = 0;
            out.associated_link = 0;
            out.flags_a = 0;
            out.auxiliary = 0;

            // 0x4FD68D: water-level cells store compact runtime reef IDs.
            if (out.terrain <= 7
                && out.object >= 0x6F
                && out.object <= 0x72) {
                out.object = static_cast<std::uint8_t>(out.object - 0x62);
                out.object_word = out.object;
            }
        }
    }
}

// 0x4FF320. Argument names preserve the order used by the machine code.
std::uint32_t native_diagonal_separation(
    std::int32_t a, std::int32_t b,
    std::int32_t c, std::int32_t d) {
    if (a < c) {
        if (b < d) {
            return static_cast<std::uint32_t>(
                std::min(c - a, d - b));
        }
        return static_cast<std::uint32_t>((c - a) + (b - d));
    }
    if (b < d) {
        return static_cast<std::uint32_t>((a - c) + (d - b));
    }
    return static_cast<std::uint32_t>(
        std::min(a - c, b - d));
}

// 0x507F10. Requested mirror ID -> first active, unplaced slot.
int native_find_mirror(const NativeStartSlot* slots, int requested_id);

// 0x508420 -> 0x4D99E0.
// The table block is selected by pattern_kind + 57 * profile and has a 0x960
// byte stride from 0x6AA174. Its 32-bit offset tokens and sentinels are kept
// raw here; the interpreter branch structure is known, but naming every
// profile-specific pattern still requires a controlled data comparison.
bool native_footprint_gate(
    NativeWorld& world, int player_slot, int x, int y) {
    // CONFIRMED checks in 0x4D99E0:
    //   - roughly 15-cell interior margin;
    //   - key = 0x0F + 57 * slot.profile and block = 0x6AA174 + 0x960*key;
    //   - 0x80000000..0x80000003 control the token interpreter;
    //   - 0x80000004/0x80000005 occur in the raw block header and are not
    //     offset pairs in the normal stream;
    //   - terrain/claim/accessibility compatibility;
    //   - no occupied object/entity word at inspected cells.
    // The candidate ordering used by callers is the separate native hex bank.
    return native_4d99e0(world, x, y, 0x0F, player_slot, 2);
}

// 0x5081A0. The first gate is the footprint; the counters are a second,
// progressively relaxed quality filter for random candidates.
bool native_random_start_quality(
    NativeWorld& world,
    int context_value,
    int x,
    int y,
    std::uint32_t attempt) {
    if (!native_4d99e0(world, x, y, 0x0F, context_value, 2)) {
        return false;
    }

    std::uint32_t unclaimed = 0;
    std::uint32_t terrain_10 = 0;
    std::uint32_t objects_44_53 = 0;
    std::uint32_t object_weight_73_7e = 0;
    std::uint32_t resource_10 = 0;
    std::uint32_t resource_20 = 0;
    std::uint32_t resource_30 = 0;
    std::uint32_t resource_40 = 0;
    std::uint32_t resource_50 = 0;

    // The native code advances through offset indices 0..0x270A. Cell
    // contents are inspected only while the index is below 0xBB8.
    for (std::uint32_t i = 0; i < 0x270B; ++i) {
        auto [cx, cy] = world.start_offset(i, x, y);
        if (i < 0xBB8 && world.in_bounds(cx, cy)) {
            const RuntimeCell& cell = world.cell(cx, cy);

            if ((cell.terrain & 0xF0) == 0x10) {
                ++terrain_10;
            }
            if (cell.object >= 0x44 && cell.object <= 0x53) {
                ++objects_44_53;
            }
            if (cell.object >= 0x73 && cell.object <= 0x7E) {
                object_weight_73_7e += 0x7F - cell.object;
            }
            if (cell.claim == 0xFF) {
                ++unclaimed;
            }

            switch (cell.resource & 0xF0) {
            case 0x10: ++resource_10; break;
            case 0x20: ++resource_20; break;
            case 0x30: ++resource_30; break;
            case 0x40: ++resource_40; break;
            case 0x50: ++resource_50; break;
            default: break;
            }
        }
    }

    if (attempt < 30000) {
        return unclaimed >= 2900
            && terrain_10 >= 2000
            && objects_44_53 >= 20 && objects_44_53 <= 30
            && object_weight_73_7e >= 50
            && resource_10 >= 40 && resource_20 >= 20
            && resource_30 >= 10 && resource_40 >= 5
            && resource_50 >= 5;
    }
    if (attempt < 60000) {
        return unclaimed >= 2500
            && terrain_10 >= 1500
            && objects_44_53 >= 12
            && object_weight_73_7e >= 30
            && resource_10 >= 30 && resource_20 >= 15
            && resource_30 >= 5;
    }
    if (attempt < 100000) {
        return unclaimed >= 1500
            && terrain_10 >= 1000
            && objects_44_53 >= 5
            && object_weight_73_7e >= 15
            && resource_10 >= 20 && resource_20 >= 10;
    }
    return true;
}

// 0x50C9E0: entity allocation (field mapping confirmed in the audit).
std::uint16_t native_allocate_entity(
    NativeWorld& world,
    int x, int y, int entity_type, int owner);

// 0x50CB20: choose a suitable cell, allocate an entity and update selected
// player counters. The exact meaning of every argument is still PARTIAL.
void native_place_entity_batch(
    NativeWorld& world,
    int count_or_attempts,
    int type_or_mode,
    int owner,
    int dx,
    int dy);

// 0x506CF0: accepted start -> town core and profile-dependent initial batches.
void native_materialize_start_town(
    NativeWorld& world, int player, int x, int y, int profile) {
    // 1. Clear/mark the footprint using native terrain/accessibility helpers.
    // 2. Create the central type-5 entity.
    native_allocate_entity(world, x, y, 5, player);

    // This is the exact 0x506F68 branch. For 0x5046B0 the pair is
    // (value,type); other 0x412300-selected branches have their own literal
    // lists and must not be merged with this one. The 0x50CB20 calls are also
    // profile/edition-dependent and are kept as raw type/count data in the
    // audit rather than guessed game names.
    constexpr int observed_batches[][2] = {
        {8, 1}, {4, 1}, {8, 2}, {4, 2},
        {5, 0x0C}, {6, 0x0D}, {3, 0x0E},
        {2, 0x0F}, {1, 0x10},
    };
    for (const auto& batch : observed_batches) {
        // Argument order and profile-dependent variants are PARTIAL.
        native_place_start_batch(world, player, x, y,
                                  batch[0], batch[1], profile);
    }

    // Mark slot placed and store x/y in the caller's 0x148-byte record.
    world.mark_start_placed(player, x, y);
}

// Random coordinate formulas used by 0x5074B0.
int native_random_coord(std::uint16_t u, int side, int mode) {
    const int margin = (mode == 1 || mode == 2) ? 0x3F : 0x1F;
    const int offset = (mode == 1 || mode == 2) ? 0x20 : 0x10;
    return (static_cast<int>(u) * (side - margin) >> 16) + offset;
}

// 0x4FE5DC, conditional post-load resource normalization.
std::uint8_t native_normalize_resource(std::uint8_t r) {
    if ((r & 0xF0) == 0) {
        return r;
    }
    return static_cast<std::uint8_t>((r & 0xF0) + ((r >> 1) & 0x07));
}

// 0x4A6540/0x4A6600/0x4A66D0 use the same rolling XOR transform documented for
// EDM/MAP/SAV. It is shown here because this is the exact reversible operation
// applied to a decrypted payload; the surrounding record catalogue is below.
void native_decode_sav_payload(
    std::uint32_t full_type, std::uint8_t* payload, std::size_t size) {
    std::uint8_t key = static_cast<std::uint8_t>(full_type & 0xFF);
    for (std::size_t i = 0; i < size; ++i) {
        const std::uint8_t plain = static_cast<std::uint8_t>(payload[i] ^ key);
        payload[i] = plain;
        key = static_cast<std::uint8_t>((key << 1) ^ plain);
    }
}

struct NativeSavRecordObservation {
    std::uint32_t type;
    const char* observed_length;
    const char* observed_source;
};

// 0x509995 (GameDataSave::Save), restricted to records relevant to a future
// generator. Other records are intentionally not guessed from their sizes.
constexpr NativeSavRecordObservation kNativeSavGeneratorRecords[] = {
    {0x00000002, "variant 0: 0x2EF0; variant 1: 0x3E90",
     "world +0x32870/+0x32874 and +0x366F8/+0x366FC; payload copies to +0x2F990 and +0x32878"},
    {0x00000003, "side * (side * 24)",
     "0x4A66D0; runtime +0x67444; high word = part index"},
    {0x00000004, "0x33F8 + 0x740 * count",
     "structured table from +0xE114D8..; entry stride 0x740"},
    {0x00000006, "0x19FC",
     "configuration/player block; +0x1195FD4 and +0x11943DC"},
    {0x00000007, "0x4C + 0x40 * count",
     "entity table at +0x12A5E60; stride 0x40"},
    {0x00000008, "0x46 + 0x3A * count",
     "building table at +0x1499E64; stride 0x3A"},
    {0x00000009, "0x1A + 0x0E * count",
     "type-9 registry at +0x123885C; stride 0x0E"},
    {0x0000000A, "0x8D63", "bulk runtime state and metadata arrays"},
    {0x00000012, "0x7F", "119-byte metadata block at +0x15394B1"},
    {0x00000013, "0x28", "opaque global block at 0x7ACE64"},
};

// Persisting a SAV state is separate from producing random terrain. The table
// above can therefore be used later for an exporter without silently turning
// opaque runtime records into generation rules.
