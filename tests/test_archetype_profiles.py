from collections import OrderedDict
from copy import deepcopy

import numpy as np
import pytest

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.archetypes import (
    MACRO_BEACH,
    MACRO_GRASS,
    MACRO_MOUNTAIN,
    MACRO_SNOW,
    MACRO_WATER,
    classify_macro,
    analyze_macro_masses,
    analyze_startable_masses,
    archetype_contract_values,
    apply_native_relief_source,
    apply_native_noise_layers,
    build_noise_lab,
    continental_legacy_blocks_profile,
    continental_noise_calibration_profile,
    default_archetype_profile,
    duplicate_noise_layer,
    finite_domain_parameters,
    generate_archetype_indicative_preview,
    generate_archetype_noise_preview,
    generate_archetype_preview,
    generate_mask_component_previews,
    generate_noise_component_previews,
    has_active_mask_layers,
    iter_archetype_parameter_descriptors,
    macro_percentages,
    macro_rgb,
    noise_rgb,
    noise_delta_rgb,
    raw_height_rgb,
    remove_noise_layer,
    reorder_noise_layers,
    normalize_archetype_profile,
    NOISE_SOURCE_OPTIONS,
    NOISE_SOURCE_SETTING_APPLICABILITY,
    RELIEF_SOURCE_OPTIONS,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    MASK_LAYER_MANUAL_GRID_SIDE,
    project_preview_rgb,
    relief_thresholds,
    noise_source_setting_applies,
)
from s3mapgen.generation.archetypes.noise_sources import (
    NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD,
    NOISE_FREQUENCY_REFERENCE_SIDE,
    adapt_noise_settings_for_domain_size,
)
from s3mapgen.generation.archetypes import morphology as morphology_module
from s3mapgen.generation.custom import CustomGenerationConfig, build_custom_config
from s3mapgen.generation.generators.legacy.native_terrain import (
    generate_relief_preview_noise_fast,
    generate_primary_terrain,
    generate_relief_height,
    generate_relief_preview_height,
    generate_relief_preview_fields,
    generate_relief_preview_noise,
)
from s3mapgen.generation.generators.legacy import native_terrain as legacy_native
from s3mapgen.generation.generators.upgraded.native_terrain import (
    generate_primary_terrain as generate_upgraded_primary_terrain,
)
from s3mapgen.generation.archetypes.profiles import (
    CUSTOM_LEGACY_MOUNTAIN_THRESHOLD,
    CUSTOM_LEGACY_SNOW_THRESHOLD,
    thresholds_on_relief_source_change,
)


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def _calibrated_custom_legacy_profile():
    profile = default_archetype_profile("continental")
    profile["morphology"]["relief_source"] = RELIEF_SOURCE_CUSTOM_LEGACY
    profile["relief"]["mountain_threshold"] = CUSTOM_LEGACY_MOUNTAIN_THRESHOLD
    profile["relief"]["snow_threshold"] = CUSTOM_LEGACY_SNOW_THRESHOLD
    return profile


def test_continental_archetype_profile_records_native_macro_defaults():
    profile = default_archetype_profile("continental")

    assert profile["layout_engine"] == "native_relief_v1"
    assert profile["noise"]["family"] == "native_midpoint"
    assert profile["noise"]["display_range"] == {"minimum": -30, "maximum": 225}
    assert profile["coast"]["derived"] is True
    assert profile["mass"]["layout"] == "mainland"
    assert relief_thresholds(profile) == (0, 140, 190)
    assert profile["morphology"]["relief_source"] == "native_legacy"
    assert profile["morphology"]["size_adaptive_frequency"] is False
    assert profile["morphology"]["frame_margin_percent"] == 0
    assert RELIEF_SOURCE_OPTIONS == (
        "native_legacy",
        "legacy_blocks",
        "white",
        "value",
        "perlin",
        "simplex",
        "fbm",
        "hybrid_fbm",
        "heterogeneous_fbm",
        "billow",
        "turbulence",
        "ridged",
        "ridged_multifractal",
        "worley",
        "worley_f1",
        "worley_f2",
        "worley_f2_minus_f1",
        "domain_warp",
    )


def test_classic_and_continental_profiles_are_distinct_named_choices():
    classic = default_archetype_profile("continental")
    first = continental_legacy_blocks_profile()
    second = continental_legacy_blocks_profile()

    assert first == second
    assert classic["profile_name"] == "Classique"
    assert first["profile_name"] == "Continental"
    assert first["profile_preset_key"] == "continental_custom_r82"
    assert first["morphology"]["relief_source"] == "legacy_blocks"
    assert first["morphology"]["frame_margin_percent"] == 0
    assert first["relief"]["water_threshold"] == 0
    assert first["relief"]["mountain_threshold"] == 98
    assert first["relief"]["snow_threshold"] == 125
    assert first["morphology"]["noise_layer_count"] == 0
    assert first["morphology"]["mask_layer_count"] == 0
    assert classic["morphology"]["relief_source"] == "native_legacy"
    assert classic["morphology"]["noise_layer_count"] == 0
    assert continental_noise_calibration_profile()["morphology"]["relief_source"] == "fbm"


def test_adaptive_frequency_toggle_migrates_older_profiles_and_requires_a_bool():
    old_profile = normalize_archetype_profile(
        {"schema_version": 17, "morphology": {"relief_source": "fbm"}},
        archetype_key="continental",
    )

    assert old_profile["schema_version"] == 20
    assert old_profile["morphology"]["size_adaptive_frequency"] is False

    with pytest.raises(ValueError, match="size_adaptive_frequency"):
        normalize_archetype_profile(
            {"morphology": {"size_adaptive_frequency": "yes"}},
            archetype_key="continental",
        )


def test_adaptive_frequency_scales_domains_and_limits_unresolved_octaves():
    settings = {
        "frequency": 4.0,
        "octaves": 5,
        "lacunarity": 2.0,
        "gain": 0.5,
        "warp_frequency": 2.0,
        "warp_strength_percent": 80.0,
        "bias_percent": 3.0,
    }
    reference_side = 732
    small_side = 220
    small = adapt_noise_settings_for_domain_size(
        "domain_warp",
        settings,
        small_side,
        reference_domain_side=reference_side,
    )
    large = adapt_noise_settings_for_domain_size(
        "domain_warp",
        settings,
        reference_side * 2,
        reference_domain_side=reference_side,
    )

    assert small["frequency"] < settings["frequency"]
    assert small["warp_frequency"] < settings["warp_frequency"]
    assert small["octaves"] < settings["octaves"]
    assert small["frequency"] * settings["lacunarity"] ** (
        small["octaves"] - 1
    ) <= small_side / NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD
    assert large["frequency"] > settings["frequency"]
    assert large["octaves"] == settings["octaves"]
    assert small["bias_percent"] == settings["bias_percent"]
    assert settings["frequency"] == 4.0

    reference = adapt_noise_settings_for_domain_size(
        "fbm",
        {"frequency": 4.0, "octaves": 5},
        NOISE_FREQUENCY_REFERENCE_SIDE,
        reference_domain_side=NOISE_FREQUENCY_REFERENCE_SIDE,
    )
    assert reference == {"frequency": 4.0, "octaves": 5}


def test_progressive_octave_fade_is_deterministic_and_preserves_reference_domain():
    import s3mapgen.generation.archetypes.noise_sources as noise_module

    settings = {
        "frequency": 4.0,
        "octaves": 5,
        "lacunarity": 2.0,
        "gain": 0.5,
    }
    baseline = noise_module.generate_noise_source("fbm", 128, 20260920, settings)
    reference = noise_module.generate_noise_source(
        "fbm",
        128,
        20260920,
        settings,
        adaptive_domain=(732, 732),
    )
    small_first = noise_module.generate_noise_source(
        "fbm",
        128,
        20260920,
        settings,
        adaptive_domain=(244, 732),
    )
    small_second = noise_module.generate_noise_source(
        "fbm",
        128,
        20260920,
        settings,
        adaptive_domain=(244, 732),
    )
    weights = noise_module._adaptive_octave_fade_weights(
        (244, 732), 4.0, 5, 2.0
    )

    assert np.array_equal(baseline, reference)
    assert np.array_equal(small_first, small_second)
    assert not np.array_equal(baseline, small_first)
    assert weights is not None
    assert weights[:2] == (1.0, 1.0)
    assert 0.0 < weights[2] < 1.0
    assert weights[3:] == (0.0, 0.0)


def test_progressive_octave_fade_also_reaches_noise_based_source_masks(monkeypatch):
    profile = default_archetype_profile()
    morphology = profile["morphology"]
    morphology["size_adaptive_frequency"] = True
    morphology["relief_source"] = "perlin"
    morphology["relief_source_mask"].update(type="noise", source="fbm")
    captured = []

    def capture_noise(source, side, seed, settings, *, adaptive_domain=None):
        captured.append((source, adaptive_domain))
        return np.zeros((side, side), dtype=np.float32)

    monkeypatch.setattr(morphology_module, "generate_noise_source", capture_noise)
    side = 192
    margin, falloff = finite_domain_parameters(profile, side=side)
    morphology_module._configured_source_field(
        side,
        19,
        "perlin",
        morphology["relief_source_settings"],
        profile,
        morphology["relief_source_mask"],
        domain_parameters=(margin, falloff),
    )

    target_domain_side = side - 2 * margin
    reference_margin = finite_domain_parameters(
        profile,
        side=NOISE_FREQUENCY_REFERENCE_SIDE,
    )[0]
    expected_domain = (
        target_domain_side,
        NOISE_FREQUENCY_REFERENCE_SIDE - 2 * reference_margin,
    )
    assert captured == [("perlin", expected_domain), ("fbm", expected_domain)]


def test_continental_noise_calibration_profile_changes_only_the_composed_macro_field():
    native = default_archetype_profile("continental")
    custom = continental_noise_calibration_profile()
    native_preview = generate_archetype_preview(native, 256, 20260920)
    custom_preview = generate_archetype_preview(custom, 256, 20260920)

    assert not np.array_equal(native_preview.noise, custom_preview.noise)
    assert custom_preview.noise_lab is not None
    assert custom_preview.noise_lab.layers[0].source == "domain_warp"
    assert custom_preview.noise_lab.layers[1].source == "ridged"
    assert custom_preview.noise_lab.layers[0].enabled is True
    assert custom_preview.noise_lab.layers[1].enabled is True


def test_native_legacy_archetype_ignores_domain_margin_setting():
    default = default_archetype_profile("continental")
    changed = deepcopy(default)
    changed["morphology"]["frame_margin_percent"] = 25
    default_preview = generate_archetype_preview(
        default, 256, 20260920, relax_macro=False
    )
    changed_preview = generate_archetype_preview(
        changed, 256, 20260920, relax_macro=False
    )

    assert default["morphology"]["frame_margin_percent"] == 0
    assert np.array_equal(default_preview.noise, changed_preview.noise)
    assert np.array_equal(default_preview.macro, changed_preview.macro)


def test_component_preview_cache_reuses_only_unchanged_fusion_sources(monkeypatch):
    import s3mapgen.generation.archetypes.morphology as morphology_module

    profile = continental_noise_calibration_profile()
    cache = OrderedDict()
    original = morphology_module.generate_noise_source
    calls = []

    def tracked(source, side, seed, settings, *, adaptive_domain=None):
        calls.append(source)
        return original(
            source,
            side,
            seed,
            settings,
            adaptive_domain=adaptive_domain,
        )

    monkeypatch.setattr(morphology_module, "generate_noise_source", tracked)
    _principal, first = generate_noise_component_previews(
        profile, 128, 20260920, include_principal=False,
        domain_side=768, component_cache=cache,
    )
    assert calls == ["domain_warp", "ridged"]
    profile["morphology"]["noise_layers"][0]["strength_percent"] = 80
    _principal, reused = generate_noise_component_previews(
        profile, 128, 20260920, include_principal=False,
        domain_side=768, component_cache=cache,
    )
    assert calls == ["domain_warp", "ridged"]
    assert all(np.array_equal(a, b) for a, b in zip(first, reused))

    # Returned arrays are detached; a consumer cannot poison the cache.
    reused[0][:] = 0
    _principal, restored = generate_noise_component_previews(
        profile, 128, 20260920, include_principal=False,
        domain_side=768, component_cache=cache,
    )
    assert np.array_equal(first[0], restored[0])

    profile["morphology"]["noise_layers"][1]["settings"]["frequency"] = 8.0
    _principal, changed = generate_noise_component_previews(
        profile, 128, 20260920, include_principal=False,
        domain_side=768, component_cache=cache,
    )
    assert calls == ["domain_warp", "ridged", "ridged"]
    assert not np.array_equal(first[1], changed[1])
    _principal, resized = generate_noise_component_previews(
        profile, 128, 20260920, include_principal=False,
        domain_side=384, component_cache=cache,
    )
    assert len(calls) == 5
    assert not np.array_equal(changed[0], resized[0])


def test_component_preview_cache_is_bounded_and_mask_edits_invalidate():
    profile = continental_noise_calibration_profile()
    profile["morphology"]["mask_layer_count"] = 1
    profile["morphology"]["mask_layers"][0].update(enabled=True, type="star")
    cache = OrderedDict()
    first = generate_mask_component_previews(
        profile, 128, 20260920, domain_side=768, component_cache=cache,
    )[0]
    profile["morphology"]["mask_layers"][0]["strength_percent"] = 65
    generate_mask_component_previews(
        profile, 128, 20260920, domain_side=768, component_cache=cache,
    )
    assert len(cache) == 1  # Strength changes the composition, not the raw mask.
    profile["morphology"]["mask_layers"][0]["settings"]["width_percent"] = 60
    changed = generate_mask_component_previews(
        profile, 128, 20260920, domain_side=768, component_cache=cache,
    )[0]
    assert not np.array_equal(first, changed)
    changed[:] = 0
    restored = generate_mask_component_previews(
        profile, 128, 20260920, domain_side=768, component_cache=cache,
    )[0]
    assert np.count_nonzero(restored) > 0

    for seed in range(60):
        generate_noise_component_previews(
            profile, 128, seed, include_principal=False,
            domain_side=768, component_cache=cache,
        )
    assert len(cache) <= 48


def test_adaptive_frequency_component_cache_tracks_reference_domain_settings(monkeypatch):
    import s3mapgen.generation.archetypes.morphology as morphology_module

    profile = continental_noise_calibration_profile()
    profile["morphology"].update(
        size_adaptive_frequency=True,
        frame_margin_percent=8,
    )
    cache = OrderedDict()
    original = morphology_module.generate_noise_source
    calls = []

    def tracked(source, side, seed, settings, *, adaptive_domain=None):
        calls.append(source)
        return original(
            source,
            side,
            seed,
            settings,
            adaptive_domain=adaptive_domain,
        )

    monkeypatch.setattr(morphology_module, "generate_noise_source", tracked)
    first_parameters = finite_domain_parameters(
        profile,
        side=128,
        reference_side=1024,
    )
    generate_noise_component_previews(
        profile,
        128,
        20260920,
        include_principal=False,
        domain_side=1024,
        component_cache=cache,
    )
    assert len(calls) == 2

    profile["morphology"]["frame_margin_percent"] = 9
    assert finite_domain_parameters(
        profile,
        side=128,
        reference_side=1024,
    ) == first_parameters
    generate_noise_component_previews(
        profile,
        128,
        20260920,
        include_principal=False,
        domain_side=1024,
        component_cache=cache,
    )
    assert len(calls) == 4


def test_noise_layer_stack_operations_are_persistent_and_bounded():
    profile = default_archetype_profile()
    layers = profile["morphology"]["noise_layers"]
    layers[0]["source"] = "perlin"
    layers[0]["family"] = "perlin"
    layers[1]["source"] = "ridged"
    layers[1]["family"] = "ridged"

    moved = reorder_noise_layers(layers, 2, 1, -1)
    assert [layer["source"] for layer in moved[:2]] == ["ridged", "perlin"]
    assert [layer["order"] for layer in moved] == list(range(6))
    assert [layer["source"] for layer in layers[:2]] == ["perlin", "ridged"]

    duplicated, count = duplicate_noise_layer(moved, 2, 0)
    assert count == 3
    assert [layer["source"] for layer in duplicated[:3]] == ["ridged", "ridged", "perlin"]
    assert [layer["order"] for layer in duplicated] == list(range(6))

    removed, count = remove_noise_layer(duplicated, count, 1)
    assert count == 2
    assert [layer["source"] for layer in removed[:2]] == ["ridged", "perlin"]
    assert [layer["order"] for layer in removed] == list(range(6))


def test_noise_layer_stack_duplicate_stops_at_the_six_slot_cap():
    profile = default_archetype_profile()
    layers = profile["morphology"]["noise_layers"]
    duplicated, count = duplicate_noise_layer(layers, 6, 0)

    assert count == 6
    assert duplicated == layers


def test_complete_relief_sources_ignore_native_coast_and_have_distinct_ranges():
    side = 128
    seed = 20260919
    all_water = np.zeros((side, side), dtype=np.uint8)
    all_high = np.full((side, side), 255, dtype=np.uint8)
    generated = {}

    for source_name in NOISE_SOURCE_OPTIONS:
        profile = default_archetype_profile()
        profile["morphology"]["relief_source"] = source_name
        source_from_water = apply_native_relief_source(all_water, profile, seed=seed)
        source_from_high = apply_native_relief_source(all_high, profile, seed=seed)
        generated[source_name] = source_from_water

        # The selected provider owns the entire field; it is not clipped to
        # whichever native coast happened to be present in the input.
        assert np.array_equal(source_from_water, source_from_high)
        assert source_from_water.dtype == np.uint8
        assert source_from_water.min() == 0
        assert source_from_water.max() >= 200
        assert np.count_nonzero(source_from_water < 31) > side * side // 20
        assert float(np.std(source_from_water)) > 10.0

    fingerprints = {values.tobytes() for values in generated.values()}
    assert len(fingerprints) == len(generated)


def test_retired_legacy_derived_profiles_migrate_to_block_generation():
    profile = default_archetype_profile("continental")
    profile["morphology"]["relief_source"] = "legacy_derived"

    normalized = normalize_archetype_profile(profile)

    assert normalized["morphology"]["relief_source"] == RELIEF_SOURCE_CUSTOM_LEGACY


def test_custom_legacy_anchors_have_one_coastal_ring_and_stationary_interior():
    from s3mapgen.generation.archetypes.legacy_blocks import seed_custom_legacy_anchors
    from s3mapgen.generation.generators.legacy.native_terrain import NativeRng16

    side = 384
    first = np.zeros((side, side), dtype=np.uint8)
    second = np.zeros_like(first)
    seed_custom_legacy_anchors(first, NativeRng16(20260918), variation_percent=100)
    seed_custom_legacy_anchors(second, NativeRng16(20260918), variation_percent=100)
    assert np.array_equal(first, second)

    anchors = np.zeros((side, side), dtype=bool)
    for col in range(32, side, 32):
        for row in range(32, side, 32):
            anchors[row, col] = True
            coastal = min(row, col, side - row, side - col) == 32
            assert 0 <= first[row, col] <= (150 if coastal else 255)
    assert np.count_nonzero(first[~anchors]) == 0

    # At zero variation every inland anchor has the same center, irrespective
    # of distance to the coast or map size. Only the native ocean ring differs.
    for side in (384, 768):
        flat = np.zeros((side, side), dtype=np.uint8)
        seed_custom_legacy_anchors(flat, NativeRng16(42), variation_percent=0)
        assert flat[32, 32] == flat[side - 32, side - 32] == 75
        assert flat[64, 64] == flat[side // 2, side // 2] == 135


def test_previous_custom_legacy_thresholds_migrate_to_the_real_altitude_range():
    old = {
        "schema_version": 19,
        "relief": {"water_threshold": 0, "mountain_threshold": 140, "snow_threshold": 190},
        "morphology": {"relief_source": RELIEF_SOURCE_CUSTOM_LEGACY},
    }
    migrated = normalize_archetype_profile(old, archetype_key="continental")
    assert migrated["schema_version"] == 20
    assert migrated["relief"]["mountain_threshold"] == CUSTOM_LEGACY_MOUNTAIN_THRESHOLD
    assert migrated["relief"]["snow_threshold"] == CUSTOM_LEGACY_SNOW_THRESHOLD
    assert normalize_archetype_profile(migrated, archetype_key="continental") == migrated


def test_custom_legacy_source_switch_exposes_calibrated_thresholds():
    custom = thresholds_on_relief_source_change(
        "native_legacy", RELIEF_SOURCE_CUSTOM_LEGACY, 140, 190,
    )
    assert custom == (
        CUSTOM_LEGACY_MOUNTAIN_THRESHOLD,
        CUSTOM_LEGACY_SNOW_THRESHOLD,
    )
    assert thresholds_on_relief_source_change(
        RELIEF_SOURCE_CUSTOM_LEGACY, "native_legacy", *custom,
    ) == (140, 190)
    assert thresholds_on_relief_source_change(
        "native_legacy", RELIEF_SOURCE_CUSTOM_LEGACY, 128, 180,
    ) == (128, 180)


def test_custom_refinement_uses_both_diagonals_without_changing_native():
    from s3mapgen.generation.generators.legacy.native_terrain import _refine_relief as legacy_refine
    from s3mapgen.generation.generators.upgraded.native_terrain import _refine_relief as upgraded_refine

    class Grid:
        side = 128

        def __init__(self):
            self.height = np.zeros((128, 128), dtype=np.uint8)
            self.height[32, 64] = self.height[64, 32] = 200

    class ConstantRng:
        def next(self):
            return 32768

    for refine in (legacy_refine, upgraded_refine):
        native = Grid()
        refine(native, ConstantRng(), start_scale=16, variation_percent=0)
        assert native.height[48, 48] == 0

        custom = Grid()
        refine(
            custom, ConstantRng(), start_scale=16, variation_percent=0,
            center_corner_blend_percent=75,
        )
        assert custom.height[48, 48] == 75


def test_largest_land_component_removes_only_disconnected_fragments():
    from s3mapgen.generation.archetypes.legacy_blocks import retain_largest_land_component
    from s3mapgen.map_data.hexgrid import component_labels

    height = np.zeros((12, 12), dtype=np.uint8)
    height[2:5, 2:5] = 80
    height[8, 8] = 120
    height[9:12, 10] = 120
    signed = height.astype(np.int16) - 30

    report = retain_largest_land_component(
        height,
        water_threshold=0,
        signed_noise=signed,
    )

    _, count = component_labels(height > 0)
    assert count == 1
    assert report == {"components_before": 3, "removed_cells": 4}
    assert np.all(height[2:5, 2:5] == 80)
    assert height[8, 8] == 0
    assert np.all(height[9:12, 10] == 0)
    assert signed[8, 8] == 0
    assert np.all(signed[9:12, 10] == 0)


def test_custom_legacy_emerges_as_a_single_landmass_with_central_water_and_relief():
    from s3mapgen.generation.archetypes.profiles import NATIVE_NOISE_MINIMUM
    from s3mapgen.map_data.hexgrid import component_labels

    for side in (384, 512, 768):
        for seed in (20260918, 123456789):
            profile = _calibrated_custom_legacy_profile()
            water_threshold, mountain_threshold, _snow_threshold = relief_thresholds(profile)
            signed = generate_relief_preview_noise_fast(
                side,
                seed,
                archetype_profile=profile,
                finalize=False,
            )
            raw = np.clip(
                signed.astype(np.int16) - int(NATIVE_NOISE_MINIMUM),
                0,
                255,
            )
            land = signed > water_threshold
            _, land_count = component_labels(land)
            assert land_count == 1
            assert 0.45 <= float(np.mean(land)) <= 0.90

            mountain_share = float(
                np.count_nonzero(raw[land] >= mountain_threshold - int(NATIVE_NOISE_MINIMUM))
            ) / max(1, int(land.sum()))
            assert mountain_share > 0.05

            water_labels, water_count = component_labels(~land)
            edge_labels = set(
                np.concatenate(
                    (
                        water_labels[0, :],
                        water_labels[-1, :],
                        water_labels[:, 0],
                        water_labels[:, -1],
                    )
                ).tolist()
            )
            inland_lakes = [
                label
                for label in range(1, water_count + 1)
                if label not in edge_labels
            ]
            assert inland_lakes
            lake_component_limit = {384: 32, 512: 48, 768: 100}[side]
            assert len(inland_lakes) <= lake_component_limit

            central_lakes = []
            for label in inland_lakes:
                rows, cols = np.where(water_labels == label)
                if rows.size < 32:
                    continue
                center_row = float(rows.mean())
                center_col = float(cols.mean())
                if (
                    side * 0.25 <= center_row <= side * 0.75
                    and side * 0.25 <= center_col <= side * 0.75
                ):
                    central_lakes.append(label)
            assert central_lakes


def test_custom_legacy_thresholds_change_land_mountain_and_snow_coverage():
    side = 384
    seed = 20260918
    base = _calibrated_custom_legacy_profile()
    noise = generate_relief_preview_noise_fast(
        side,
        seed,
        archetype_profile=base,
        finalize=False,
    )
    base_macro = classify_macro(noise, base)
    base_shares = macro_percentages(base_macro)

    wetter = deepcopy(base)
    wetter["relief"]["water_threshold"] = 20
    wet_shares = macro_percentages(classify_macro(noise, wetter))
    assert sum(wet_shares[1:]) < sum(base_shares[1:])

    higher_mountains = deepcopy(base)
    higher_mountains["relief"]["mountain_threshold"] = 110
    mountain_shares = macro_percentages(classify_macro(noise, higher_mountains))
    assert mountain_shares[3] + mountain_shares[4] < base_shares[3] + base_shares[4]

    higher_snow = deepcopy(base)
    higher_snow["relief"]["snow_threshold"] = 220
    snow_shares = macro_percentages(classify_macro(noise, higher_snow))
    assert snow_shares[4] < base_shares[4]


def test_custom_legacy_blocks_reach_previews_and_both_native_engines():
    side = 256
    seed = 20260918
    native_profile = default_archetype_profile("continental")
    custom_profile = _calibrated_custom_legacy_profile()

    principal, _components = generate_noise_component_previews(
        custom_profile,
        96,
        seed,
    )
    assert principal.shape == (96, 96)
    assert float(np.std(principal)) > 5.0

    native_preview = generate_archetype_noise_preview(
        native_profile,
        side,
        seed,
    )
    custom_preview = generate_archetype_noise_preview(
        custom_profile,
        side,
        seed,
    )
    assert not np.array_equal(native_preview, custom_preview)
    indicative_noise, indicative_macro = generate_archetype_indicative_preview(
        custom_profile,
        side,
        seed,
    )
    assert indicative_noise.shape == (side, side)
    assert float(np.std(indicative_noise)) > 5.0
    assert len(np.unique(indicative_macro)) >= 3

    custom_results = []
    for generate in (generate_primary_terrain, generate_upgraded_primary_terrain):
        native_result = generate(side, seed, archetype_profile=native_profile)
        result = generate(side, seed, archetype_profile=custom_profile)
        assert result.height.shape == (side, side)
        assert np.count_nonzero(native_result.height != result.height) > side * side // 4
        custom_results.append(result)
    assert np.array_equal(custom_results[0].height, custom_results[1].height)


def test_custom_legacy_full_engines_match_and_keep_one_landmass_at_classic_sizes():
    from s3mapgen.map_data.hexgrid import component_labels

    seed = 20260918
    profile = _calibrated_custom_legacy_profile()
    for side in (384, 512, 768):
        legacy = generate_primary_terrain(side, seed, archetype_profile=profile)
        upgraded = generate_upgraded_primary_terrain(
            side,
            seed,
            archetype_profile=profile,
        )
        assert np.array_equal(legacy.height, upgraded.height)
        river = (legacy.terrain >= 96) & (legacy.terrain <= 99)
        assert np.any(river)
        assert np.percentile(legacy.height[river], 90) < 85
        land = legacy.height > 0
        _, land_count = component_labels(land)
        assert land_count == 1


def test_noise_source_parameters_have_visible_independent_effects():
    raw = np.zeros((192, 192), dtype=np.uint8)
    base = default_archetype_profile()
    base["morphology"]["relief_source"] = "perlin"
    coarse = apply_native_relief_source(raw, base, seed=20260920)

    detailed = default_archetype_profile()
    detailed["morphology"]["relief_source"] = "perlin"
    detailed["morphology"]["relief_source_settings"].update(
        frequency=14.0,
        rotation_degrees=37,
        stretch_percent=220,
        bias_percent=15,
        contrast_percent=220,
        seed_offset=91,
    )
    changed = apply_native_relief_source(raw, detailed, seed=20260920)

    assert np.mean(np.abs(changed.astype(np.int16) - coarse.astype(np.int16))) > 35
    assert not np.array_equal(changed, coarse)


def test_extended_noise_providers_are_deterministic_and_distinct():
    import s3mapgen.generation.archetypes.noise_sources as noise_module

    settings = default_archetype_profile()["morphology"][
        "relief_source_settings"
    ]
    sources = (
        "hybrid_fbm",
        "heterogeneous_fbm",
        "turbulence",
        "ridged_multifractal",
        "worley_f1",
        "worley_f2",
        "worley_f2_minus_f1",
    )
    first = {
        source: noise_module.generate_noise_source(
            source,
            96,
            20260920,
            settings,
            adaptive_domain=(72, NOISE_FREQUENCY_REFERENCE_SIDE),
        )
        for source in sources
    }
    second = {
        source: noise_module.generate_noise_source(
            source,
            96,
            20260920,
            settings,
            adaptive_domain=(72, NOISE_FREQUENCY_REFERENCE_SIDE),
        )
        for source in sources
    }

    assert all(np.array_equal(first[source], second[source]) for source in sources)
    assert all(
        np.isfinite(first[source]).all()
        and float(first[source].min()) >= -1.0
        and float(first[source].max()) <= 1.0
        for source in sources
    )
    assert len({first[source].tobytes() for source in sources}) == len(sources)


def test_extended_noise_providers_can_drive_fusion_layers():
    raw = np.full((96, 96), 120, dtype=np.uint8)
    for source in (
        "hybrid_fbm",
        "heterogeneous_fbm",
        "turbulence",
        "ridged_multifractal",
        "worley_f1",
        "worley_f2",
        "worley_f2_minus_f1",
    ):
        profile = default_archetype_profile()
        profile["morphology"]["noise_layer_count"] = 1
        profile["morphology"]["noise_layers"][0].update(
            enabled=True,
            source=source,
            family=source,
            operation="blend",
            strength_percent=35,
        )
        composed = apply_native_noise_layers(raw, profile, seed=20260920)
        assert np.any(composed != raw), source


@pytest.mark.parametrize(
    ("setting", "value"),
    (
        ("inversion_percent", 100),
        ("absolute_percent", 100),
        ("gamma_percent", 250),
        ("terrace_steps", 5),
    ),
)
def test_common_noise_output_transforms_have_visible_effects(setting, value):
    raw = np.zeros((192, 192), dtype=np.uint8)
    base = default_archetype_profile()
    base["morphology"]["relief_source"] = "perlin"
    reference = apply_native_relief_source(raw, base, seed=20260920)

    transformed = default_archetype_profile()
    transformed["morphology"]["relief_source"] = "perlin"
    settings = transformed["morphology"]["relief_source_settings"]
    settings[setting] = value
    changed = apply_native_relief_source(raw, transformed, seed=20260920)

    assert not np.array_equal(changed, reference)
    assert np.mean(np.abs(changed.astype(np.int16) - reference.astype(np.int16))) > 4


@pytest.mark.parametrize(
    ("setting", "value"),
    (
        ("offset_x_percent", 35),
        ("offset_y_percent", -25),
        ("scale_x_percent", 220),
        ("scale_y_percent", 55),
        ("repeat_x", 3),
        ("repeat_y", 4),
        ("symmetry_x_percent", 100),
        ("symmetry_y_percent", 100),
    ),
)
def test_coordinate_transforms_have_visible_independent_effects(setting, value):
    raw = np.zeros((192, 192), dtype=np.uint8)
    base = default_archetype_profile()
    base["morphology"]["relief_source"] = "perlin"
    reference = apply_native_relief_source(raw, base, seed=20260920)

    transformed = default_archetype_profile()
    transformed["morphology"]["relief_source"] = "perlin"
    transformed["morphology"]["relief_source_settings"][setting] = value
    changed = apply_native_relief_source(raw, transformed, seed=20260920)

    assert not np.array_equal(changed, reference)
    assert np.mean(np.abs(changed.astype(np.int16) - reference.astype(np.int16))) > 10


def test_coordinate_transform_defaults_preserve_white_noise_hashing():
    import s3mapgen.generation.archetypes.noise_sources as noise_module

    profile = default_archetype_profile()
    settings = profile["morphology"]["relief_source_settings"]
    generated = noise_module.generate_noise_source("white", 64, 11, settings)
    rows, columns = np.indices((64, 64), dtype=np.int64)
    reference = noise_module._hash_unit(columns, rows, 11) * 2.0 - 1.0
    reference = np.clip((reference - 0.2) * 1.4, -1.0, 1.0).astype(np.float32)

    assert np.array_equal(generated, reference)


@pytest.mark.parametrize(
    "mask_type",
    ("height", "edge", "band_x", "band_y", "direction", "slope", "curvature", "noise"),
)
def test_finite_source_masks_have_visible_independent_effects(mask_type):
    raw = np.zeros((192, 192), dtype=np.uint8)
    base = default_archetype_profile()
    base["morphology"]["relief_source"] = "perlin"
    reference = apply_native_relief_source(raw, base, seed=20260920)

    masked = normalize_archetype_profile(
        {
            "morphology": {
                "relief_source": "perlin",
                "relief_source_mask": {
                    "type": mask_type,
                    "center_percent": 30,
                    "width_percent": 35,
                    "softness_percent": 20,
                    "angle_degrees": 37,
                    "source": "worley",
                    "seed_offset": 19,
                },
            }
        },
        archetype_key="continental",
    )
    changed = apply_native_relief_source(raw, masked, seed=20260920)

    assert not np.array_equal(changed, reference)
    assert np.mean(np.abs(changed.astype(np.int16) - reference.astype(np.int16))) > 2
    margin = round(raw.shape[0] * masked["morphology"]["frame_margin_percent"] / 100)
    outer = np.ones(raw.shape, dtype=bool)
    inner_end = raw.shape[0] - margin if margin else raw.shape[0]
    outer[margin:inner_end, margin:inner_end] = False
    assert np.array_equal(changed[outer], np.zeros(np.count_nonzero(outer), dtype=np.uint8))


def test_mask_defaults_are_neutral_for_source_and_fusion_paths():
    raw = np.zeros((128, 128), dtype=np.uint8)
    source_profile = default_archetype_profile()
    source_profile["morphology"]["relief_source"] = "perlin"
    explicit = normalize_archetype_profile(
        {
            "morphology": {
                "relief_source": "perlin",
                "relief_source_mask": {"type": "none"},
                "noise_layers": [
                    {
                        "enabled": True,
                        "source": "perlin",
                        "operation": "add",
                        "strength_percent": 70,
                        "mask_settings": {"type": "none"},
                    }
                ],
            }
        },
        archetype_key="continental",
    )
    assert np.array_equal(
        apply_native_relief_source(raw, source_profile, seed=77),
        apply_native_relief_source(raw, explicit, seed=77),
    )
    assert explicit["morphology"]["noise_layers"][0]["mask_settings"]["type"] == "none"


@pytest.mark.parametrize("shape_type", ("ellipse", "ring", "star", "dome"))
def test_mask_stack_modulates_the_complete_field_without_hard_clipping(shape_type):
    raw = np.tile(np.linspace(64, 192, 128, dtype=np.uint8), (128, 1))
    profile = default_archetype_profile()
    profile["morphology"]["mask_layer_count"] = 1
    layer = profile["morphology"]["mask_layers"][0]
    layer["enabled"] = True
    layer["type"] = shape_type
    layer["operation"] = "blend"
    layer["strength_percent"] = 45
    layer["settings"]["type"] = shape_type

    mask = generate_mask_component_previews(profile, 128, seed=20260922)[0]
    source = apply_native_relief_source(raw, profile, seed=20260922)
    composed = apply_native_noise_layers(source, profile, seed=20260922)

    assert has_active_mask_layers(profile)
    assert mask.min() == 0
    assert mask.max() >= 200
    assert np.array_equal(source, raw)
    assert np.any(composed != source)
    outside = mask == 0
    assert np.count_nonzero(composed[outside]) > 0
    assert np.ptp(composed[outside]) > 0


def test_retired_mask_names_load_as_their_simple_replacements():
    profile = default_archetype_profile()
    profile["morphology"]["shape_template"]["type"] = "volcano"
    profile["morphology"]["mask_layer_count"] = 1
    profile["morphology"]["mask_layers"][0]["type"] = "serpent"

    normalized = normalize_archetype_profile(profile)

    assert normalized["morphology"]["shape_template"]["type"] == "dome"
    assert normalized["morphology"]["mask_layers"][0]["type"] == "ellipse"


def test_mask_stack_is_applied_after_fusions_and_keeps_outside_variation():
    raw = np.tile(np.linspace(64, 192, 128, dtype=np.uint8), (128, 1))
    base = default_archetype_profile()
    base["morphology"]["mask_layer_count"] = 1
    base["morphology"]["mask_layers"][0].update(
        enabled=True,
        type="ellipse",
        operation="subtract",
        strength_percent=45,
    )
    base["morphology"]["mask_layers"][0]["settings"]["type"] = "ellipse"
    base["morphology"]["noise_layer_count"] = 1
    base["morphology"]["noise_layers"][0].update(
        enabled=True,
        source="ridged",
        operation="subtract",
        strength_percent=100,
    )

    report = build_noise_lab(raw, base, seed=20260922)
    outside = generate_mask_component_previews(base, 128, seed=20260922)[0] == 0

    assert report.active_layers
    assert np.count_nonzero(report.composed_height[outside]) > 0
    assert np.ptp(report.composed_height[outside]) > 0


def test_mask_profile_keeps_provider_specific_payload_out_of_common_settings():
    profile = normalize_archetype_profile(
        {
            "schema_version": 14,
            "morphology": {
                "mask_layer_count": 1,
                "mask_layers": [
                    {
                        "enabled": True,
                        "type": "star",
                        "settings": {
                            "width_percent": 70,
                            "height_percent": 80,
                            "offset_x_percent": 5,
                            "offset_y_percent": -5,
                            "rotation_degrees": 20,
                            "softness_percent": 12,
                            "points": 9,
                            "inner_radius_percent": 25,
                        },
                    }
                ],
            },
        },
        archetype_key="continental",
    )
    layer = profile["morphology"]["mask_layers"][0]

    assert set(layer["settings"]) == {
        "width_percent",
        "height_percent",
        "offset_x_percent",
        "offset_y_percent",
        "rotation_degrees",
        "softness_percent",
    }
    assert "points" not in layer["settings"]
    assert layer["provider_settings"]["points"] == 9
    assert layer["provider_settings"]["inner_radius_percent"] == 25


def test_manual_mask_grid_is_resampled_and_keeps_outside_variation():
    grid = np.zeros(
        (MASK_LAYER_MANUAL_GRID_SIDE, MASK_LAYER_MANUAL_GRID_SIDE),
        dtype=np.uint8,
    )
    grid[20:44, 12:52] = 255
    profile = normalize_archetype_profile(
        {
            "morphology": {
                "mask_layer_count": 1,
                "mask_layers": [
                    {
                        "enabled": True,
                        "type": "manual",
                        "operation": "add",
                        "strength_percent": 100,
                        "settings": {
                            "width_percent": 80,
                            "height_percent": 70,
                            "rotation_degrees": 15,
                        },
                        "provider_settings": {"grid": grid.tolist()},
                    }
                ],
            }
        },
        archetype_key="continental",
    )
    layer = profile["morphology"]["mask_layers"][0]
    preview = generate_mask_component_previews(profile, 128, seed=77)[0]
    raw = np.tile(np.linspace(64, 192, 128, dtype=np.uint8), (128, 1))
    source = apply_native_relief_source(raw, profile, seed=77)
    composed = apply_native_noise_layers(source, profile, seed=77)

    assert layer["type"] == "manual"
    assert len(layer["provider_settings"]["grid"]) == (
        MASK_LAYER_MANUAL_GRID_SIDE * MASK_LAYER_MANUAL_GRID_SIDE
    )
    assert preview.max() > 200
    assert np.any(composed != source)
    assert np.ptp(composed[preview == 0]) > 0


def test_fusion_mask_limits_an_operation_to_a_visible_band():
    raw = np.full((128, 128), 128, dtype=np.uint8)
    unmasked = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "source": "perlin",
                        "operation": "subtract",
                        "strength_percent": 100,
                    }
                ],
            }
        },
        archetype_key="continental",
    )
    masked = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "source": "perlin",
                        "operation": "subtract",
                        "strength_percent": 100,
                        "mask_settings": {
                            "type": "band_x",
                            "center_percent": 25,
                            "width_percent": 18,
                            "softness_percent": 0,
                        },
                    }
                ],
            }
        },
        archetype_key="continental",
    )
    full = apply_native_noise_layers(raw, unmasked, seed=20260920)
    limited = apply_native_noise_layers(raw, masked, seed=20260920)

    assert not np.array_equal(full, limited)
    assert np.count_nonzero(limited != raw) < np.count_nonzero(full != raw)
    assert np.any(limited[:, : raw.shape[1] // 3] != raw[:, : raw.shape[1] // 3])
    assert not np.any(
        limited[:, raw.shape[1] * 2 // 3 :] != raw[:, raw.shape[1] * 2 // 3 :]
    )


def test_common_noise_output_transform_controls_are_available_to_every_provider():
    for source in NOISE_SOURCE_OPTIONS:
        for setting in (
            "inversion_percent",
            "absolute_percent",
            "gamma_percent",
            "terrace_steps",
            "terrace_blend_percent",
        ):
            assert noise_source_setting_applies(source, setting)


def test_coordinate_transform_controls_are_available_to_every_provider():
    for source in NOISE_SOURCE_OPTIONS:
        for setting in (
            "offset_x_percent",
            "offset_y_percent",
            "scale_x_percent",
            "scale_y_percent",
            "repeat_x",
            "repeat_y",
            "symmetry_x_percent",
            "symmetry_y_percent",
        ):
            assert noise_source_setting_applies(source, setting)


def test_terrace_blend_controls_the_strength_of_the_remap():
    raw = np.zeros((192, 192), dtype=np.uint8)
    full = default_archetype_profile()
    full["morphology"]["relief_source"] = "perlin"
    full["morphology"]["relief_source_settings"].update(
        terrace_steps=5,
        terrace_blend_percent=100,
    )
    partial = default_archetype_profile()
    partial["morphology"]["relief_source"] = "perlin"
    partial["morphology"]["relief_source_settings"].update(
        terrace_steps=5,
        terrace_blend_percent=35,
    )

    full_values = apply_native_relief_source(raw, full, seed=20260920)
    partial_values = apply_native_relief_source(raw, partial, seed=20260920)

    assert not np.array_equal(full_values, partial_values)
    assert len(np.unique(full_values)) < len(np.unique(partial_values))


@pytest.mark.parametrize(
    ("setting", "value"),
    (
        ("remap_low_percent", 25),
        ("remap_high_percent", 75),
        ("threshold_low_percent", 30),
        ("threshold_high_percent", 50),
        ("clamp_low_percent", 20),
        ("clamp_high_percent", 60),
        ("curve_bias_percent", 70),
    ),
)
def test_advanced_noise_remap_controls_have_visible_effects(setting, value):
    raw = np.zeros((192, 192), dtype=np.uint8)
    base = default_archetype_profile()
    base["morphology"]["relief_source"] = "perlin"
    reference = apply_native_relief_source(raw, base, seed=20260920)

    transformed = default_archetype_profile()
    transformed["morphology"]["relief_source"] = "perlin"
    transformed["morphology"]["relief_source_settings"][setting] = value
    changed = apply_native_relief_source(raw, transformed, seed=20260920)

    assert not np.array_equal(changed, reference)
    assert np.mean(np.abs(changed.astype(np.int16) - reference.astype(np.int16))) > 4


def test_threshold_softness_changes_hard_plateaus_without_changing_the_source():
    raw = np.zeros((192, 192), dtype=np.uint8)
    hard = default_archetype_profile()
    hard["morphology"]["relief_source"] = "perlin"
    hard["morphology"]["relief_source_settings"].update(
        threshold_low_percent=30,
        threshold_high_percent=70,
        threshold_softness_percent=0,
    )
    soft = default_archetype_profile()
    soft["morphology"]["relief_source"] = "perlin"
    soft["morphology"]["relief_source_settings"].update(
        threshold_low_percent=30,
        threshold_high_percent=70,
        threshold_softness_percent=100,
    )

    hard_values = apply_native_relief_source(raw, hard, seed=20260920)
    soft_values = apply_native_relief_source(raw, soft, seed=20260920)

    assert not np.array_equal(hard_values, soft_values)
    assert np.mean(np.abs(hard_values.astype(np.int16) - soft_values.astype(np.int16))) > 4


def test_advanced_remap_defaults_migrate_older_profiles_as_identity_values():
    profile = normalize_archetype_profile(
        {
            "schema_version": 10,
            "morphology": {
                "relief_source": "perlin",
                "relief_source_settings": {"frequency": 6.0},
            },
        },
        archetype_key="continental",
    )
    settings = profile["morphology"]["relief_source_settings"]

    assert profile["schema_version"] == 20
    assert settings["frequency"] == 6.0
    assert settings["remap_low_percent"] == 0
    assert settings["remap_high_percent"] == 100
    assert settings["threshold_low_percent"] == 0
    assert settings["threshold_high_percent"] == 100
    assert settings["threshold_softness_percent"] == 0
    assert settings["clamp_low_percent"] == 0
    assert settings["clamp_high_percent"] == 100
    assert settings["curve_bias_percent"] == 0
    assert profile["morphology"]["relief_source_mask"]["type"] == "none"
    assert profile["morphology"]["relief_source_mask"]["strength_percent"] == 100


def test_noise_source_setting_applicability_matches_provider_contract():
    assert noise_source_setting_applies("white", "bias_percent")
    assert noise_source_setting_applies("white", "seed_offset")
    assert not noise_source_setting_applies("white", "frequency")
    assert not noise_source_setting_applies("perlin", "octaves")
    assert noise_source_setting_applies("fbm", "octaves")
    assert noise_source_setting_applies("hybrid_fbm", "octaves")
    assert noise_source_setting_applies("turbulence", "gain")
    assert not noise_source_setting_applies("worley_f2", "octaves")
    assert noise_source_setting_applies("domain_warp", "warp_strength_percent")
    assert not noise_source_setting_applies("native_legacy", "contrast_percent")
    for source in NOISE_SOURCE_OPTIONS:
        for setting in (
            "remap_low_percent",
            "remap_high_percent",
            "threshold_low_percent",
            "threshold_high_percent",
            "threshold_softness_percent",
            "clamp_low_percent",
            "clamp_high_percent",
            "curve_bias_percent",
        ):
            assert noise_source_setting_applies(source, setting)
    assert set(NOISE_SOURCE_SETTING_APPLICABILITY) == set(NOISE_SOURCE_OPTIONS)


@pytest.mark.parametrize(
    "operation",
    ("replace", "blend", "add", "subtract", "multiply", "min", "max"),
)
def test_every_fusion_operation_changes_the_complete_field(operation):
    raw = np.full((128, 128), 120, dtype=np.uint8)
    profile = default_archetype_profile()
    profile["morphology"]["noise_layer_count"] = 1
    layer = profile["morphology"]["noise_layers"][0]
    layer.update(
        enabled=True,
        source="worley",
        family="worley",
        operation=operation,
        strength_percent=65,
    )

    composed = apply_native_noise_layers(raw, profile, seed=20260920)

    assert composed.dtype == np.uint8
    assert np.any(composed != raw)


def test_complete_relief_sources_are_generated_inside_a_finite_rectangle():
    side = 256
    seed = 20260919
    raw = np.zeros((side, side), dtype=np.uint8)

    for source_name in NOISE_SOURCE_OPTIONS:
        profile = default_archetype_profile()
        profile["morphology"]["relief_source"] = source_name
        margin = round(side * profile["morphology"]["frame_margin_percent"] / 100)
        source = apply_native_relief_source(raw, profile, seed=seed)

        assert np.all(source[:margin, :] == 0)
        if margin:
            assert np.all(source[-margin:, :] == 0)
        assert np.all(source[:, :margin] == 0)
        if margin:
            assert np.all(source[:, -margin:] == 0)
        assert np.all(source[margin, :] < 31)
        assert np.all(source[:, margin] < 31)
        assert np.all(source[side - margin - 1, :] < 31)
        assert np.all(source[:, side - margin - 1] < 31)

        interior = source[margin + 20 : -margin - 20, margin + 20 : -margin - 20]
        assert float(np.std(interior)) > 10.0

        result = generate_primary_terrain(
            side,
            seed,
            archetype_profile=profile,
        )
        outside = np.ones((side, side), dtype=bool)
        outside[margin : side - margin, margin : side - margin] = False
        assert np.all(result.height[outside] == 0)
        assert np.all(result.height[margin, :] == 0)
        assert np.all(result.height[:, margin] == 0)
        assert np.all(result.height[side - margin - 1, :] == 0)
        assert np.all(result.height[:, side - margin - 1] == 0)


def test_complete_relief_source_is_reported_before_native_macro_pipeline():
    side = 128
    seed = 20260919
    raw = np.zeros((side, side), dtype=np.uint8)
    profile = default_archetype_profile()
    profile["morphology"]["relief_source"] = "warped_fbm"

    report = build_noise_lab(raw, profile, seed=seed)
    assert report.source_name == "domain_warp"
    assert report.source_active is True
    assert report.reference_land_mask is not None
    assert not np.any(report.reference_land_mask)
    assert np.array_equal(report.land_mask, report.source_height >= 31)
    assert np.array_equal(report.source_delta, report.source_height.astype(np.float32))
    assert np.all(report.layer_delta == 0.0)
    assert np.array_equal(report.total_delta, report.source_delta)
    assert report.source_land_percent > 0.0
    assert len(report.source_height_percentiles) == 3
    assert report.source_height_percentiles == tuple(
        sorted(report.source_height_percentiles)
    )
    assert np.array_equal(report.composed_height, report.source_height)

    preview = generate_archetype_preview(profile, side, seed)
    assert preview.noise_lab is not None
    assert preview.noise_lab.source_active is True
    assert preview.noise_lab.source_name == "domain_warp"
    assert np.count_nonzero(preview.macro != MACRO_WATER) > 0


def test_preview_source_raster_stays_before_fusion_layers():
    profile = default_archetype_profile()
    profile["morphology"]["relief_source"] = "domain_warp"
    profile["morphology"]["noise_layer_count"] = 1
    profile["morphology"]["noise_layers"][0]["enabled"] = True
    profile["morphology"]["noise_layers"][0]["strength_percent"] = 100

    preview = generate_archetype_preview(profile, 128, 20260919)

    assert preview.noise_lab is not None
    assert preview.source_noise is not None
    expected = preview.noise_lab.source_height.astype(np.int16) - 30
    expected[0, :] = -30
    expected[-1, :] = -30
    expected[:, 0] = -30
    expected[:, -1] = -30
    assert np.array_equal(preview.source_noise, expected)
    assert not np.array_equal(preview.source_noise, preview.noise)


def test_noise_layers_are_optional_bounded_and_normalized():
    profile = default_archetype_profile("continental")

    assert profile["morphology"]["noise_layer_count"] == 0
    assert len(profile["morphology"]["noise_layers"]) == 6
    assert all(not layer["enabled"] for layer in profile["morphology"]["noise_layers"])

    edited = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "ridged",
                        "scale_percent": 75,
                        "strength_percent": 60,
                    }
                ]
            }
        },
        archetype_key="continental",
    )
    first, second = edited["morphology"]["noise_layers"][:2]
    assert first["enabled"] is True
    assert first["source"] == first["family"] == "ridged"
    assert first["role"] == "full_field"
    assert first["mask"] == "finite_domain"
    assert first["stage"] == "source_composition"
    assert first["strength_percent"] == 60
    assert first["settings"]["frequency"] == 5.0
    assert second["enabled"] is False
    assert second["source"] == "ridged"
    assert second["settings"]["frequency"] == 8.0

    with pytest.raises(ValueError, match="maximum 6 couches"):
        normalize_archetype_profile(
            {"morphology": {"noise_layers": [{} for _ in range(7)]}},
            archetype_key="continental",
        )


def test_dynamic_fusion_count_preserves_hidden_slots_and_skips_their_execution():
    profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 0,
                "noise_layers": [
                    {
                        "enabled": True,
                        "source": "white",
                        "operation": "replace",
                        "strength_percent": 100,
                    }
                ],
            }
        },
        archetype_key="continental",
    )
    raw = np.full((64, 64), 127, dtype=np.uint8)
    assert profile["morphology"]["noise_layers"][0]["enabled"] is True
    assert np.array_equal(apply_native_noise_layers(raw, profile, seed=17), raw)

    profile["morphology"]["noise_layer_count"] = 1
    restored = normalize_archetype_profile(profile, archetype_key="continental")
    assert restored["morphology"]["noise_layers"][0]["enabled"] is True
    assert not np.array_equal(apply_native_noise_layers(raw, restored, seed=17), raw)


def test_component_thumbnails_show_disabled_sources_without_running_macro_pipeline():
    profile = normalize_archetype_profile(
        {
            "morphology": {
                "relief_source": "perlin",
                "noise_layer_count": 3,
                "noise_layers": [
                    {"enabled": False, "source": "white"},
                    {"enabled": False, "source": "ridged"},
                    {"enabled": False, "source": "worley"},
                ],
            }
        },
        archetype_key="continental",
    )
    principal, layers = generate_noise_component_previews(profile, 80, 99)
    assert principal.shape == (80, 80)
    assert principal.dtype == np.uint8
    assert len(layers) == 3
    assert all(layer.shape == (80, 80) for layer in layers)
    assert all(np.ptp(layer) > 0 for layer in layers)


def test_native_component_thumbnail_is_not_a_black_placeholder():
    profile = normalize_archetype_profile(
        {"morphology": {"relief_source": "native_legacy"}},
        archetype_key="continental",
    )

    principal, _layers = generate_noise_component_previews(profile, 80, 99)

    assert principal.shape == (80, 80)
    assert principal.dtype == np.uint8
    assert np.ptp(principal) > 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("operation", "xor", "Opération de bruit inconnue"),
        ("source", "unknown", "Source de bruit inconnue"),
        ("order", 100, "ordre de la couche de bruit"),
    ),
)
def test_noise_layer_semantics_reject_unimplemented_roles_and_operations(field, value, message):
    with pytest.raises(ValueError, match=message):
        normalize_archetype_profile(
            {
                "morphology": {
                    "noise_layers": [
                        {
                            "enabled": True,
                            "family": "smooth",
                            field: value,
                        }
                    ]
                }
            },
            archetype_key="continental",
        )


def test_noise_fusions_operate_on_the_complete_finite_field():
    native_noise, _native_height = generate_relief_preview_fields(
        256,
        20260918,
        finalize=False,
    )
    raw = np.clip(native_noise - (-30), 0, 255).astype(np.uint8)
    add_profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "smooth",
                        "operation": "add",
                        "scale_percent": 80,
                        "strength_percent": 80,
                    }
                ]
            }
        },
        archetype_key="continental",
    )
    subtract_profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "smooth",
                        "operation": "subtract",
                        "scale_percent": 80,
                        "strength_percent": 80,
                    }
                ]
            }
        },
        archetype_key="continental",
    )

    added = apply_native_noise_layers(raw, add_profile, seed=20260918)
    lowered = apply_native_noise_layers(raw, subtract_profile, seed=20260918)

    margin = round(raw.shape[0] * add_profile["morphology"]["frame_margin_percent"] / 100)
    outer = np.ones(raw.shape, dtype=bool)
    inner_end = raw.shape[0] - margin if margin else raw.shape[0]
    outer[margin:inner_end, margin:inner_end] = False
    assert np.array_equal(added[outer], raw[outer])
    assert np.array_equal(lowered[outer], raw[outer])
    assert np.any((added > raw) & (raw < 31))
    assert np.any(lowered < raw)
    assert not np.array_equal(added, lowered)


def test_legacy_noise_layer_keys_migrate_to_the_semantic_contract():
    profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 2,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "smooth",
                        "operation": "subtract",
                    }
                ]
            }
        },
        archetype_key="continental",
    )
    layer = profile["morphology"]["noise_layers"][0]
    assert layer["source"] == "fbm"
    assert layer["family"] == "fbm"
    assert layer["role"] == "full_field"
    assert layer["mask"] == "finite_domain"
    assert layer["stage"] == "source_composition"
    assert layer["operation"] == "subtract"
    assert layer["order"] == 0


def test_noise_lab_reports_source_domain_operation_order_and_contribution():
    native_noise, _native_height = generate_relief_preview_fields(
        256,
        20260918,
        finalize=False,
    )
    raw = np.clip(native_noise + 30, 0, 255).astype(np.uint8)
    profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 2,
                "noise_layers": [
                    {
                        "enabled": True,
                        "source": "ridged",
                        "operation": "subtract",
                        "order": 10,
                        "scale_percent": 90,
                        "strength_percent": 60,
                    },
                    {
                        "enabled": True,
                        "source": "smooth",
                        "operation": "add",
                        "order": 1,
                        "scale_percent": 70,
                        "strength_percent": 40,
                    },
                ]
            }
        },
        archetype_key="continental",
    )
    report = build_noise_lab(raw, profile, seed=20260918)
    assert len(report.layers) == 2
    assert [layer.source for layer in report.layers] == ["fbm", "ridged"]
    assert [layer.order for layer in report.layers] == [1, 10]
    assert all(layer.role == "full_field" for layer in report.layers)
    assert all(layer.mask == "finite_domain" for layer in report.layers)
    assert all(layer.stage == "source_composition" for layer in report.layers)
    assert report.active_layers[0].operation == "add"
    assert np.any(np.abs(report.total_delta) > 1e-6)
    assert np.any(np.abs(report.layer_delta) > 1e-6)
    assert np.array_equal(report.total_delta, report.source_delta + report.layer_delta)
    assert np.array_equal(
        report.composed_height,
        apply_native_noise_layers(raw, profile, seed=20260918),
    )


def test_noise_lab_is_exposed_by_active_archetype_preview_and_delta_rgb_is_signed():
    profile = normalize_archetype_profile(
        {"morphology": {"noise_layer_count": 1, "noise_layers": [{"enabled": True, "strength_percent": 70}]}},
        archetype_key="continental",
    )
    preview = generate_archetype_preview(profile, 256, 20260918)
    assert preview.noise_lab is not None
    assert len(preview.noise_lab.active_layers) == 1
    diagnostic = noise_delta_rgb(preview.noise_lab.layer_delta)
    assert diagnostic.shape == (256, 256, 3)
    assert diagnostic.dtype == np.uint8
    assert np.any(diagnostic[:, :, 0] != diagnostic[:, :, 2])


def test_relief_source_does_not_pollute_raw_layer_contribution():
    raw = np.zeros((128, 128), dtype=np.uint8)
    profile = default_archetype_profile()
    profile["morphology"]["relief_source"] = "warped_fbm"

    report = build_noise_lab(raw, profile, seed=20260919)

    assert np.any(np.abs(report.source_delta) > 1e-6)
    assert np.all(report.layer_delta == 0.0)
    assert np.array_equal(report.total_delta, report.source_delta)


def test_continental_contract_is_explicit_and_morphology_is_editable():
    profile = default_archetype_profile("continental")
    contract = archetype_contract_values(profile)

    assert contract == {
        "layout_engine": "native_relief_v1",
        "noise_family": "native_midpoint",
        "noise_editable": False,
        "noise_minimum": -30,
        "noise_maximum": 225,
        "coast_derived": True,
        "coast_rule": "water_to_shore_to_land",
        "mass_layout": "mainland",
        "micro_islands": False,
    }
    assert tuple(descriptor.key for descriptor in iter_archetype_parameter_descriptors(profile)) == (
        "morphology.shape_scale_percent",
        "morphology.relief_contrast_percent",
        "morphology.native_coarse_variation_percent",
        "morphology.native_refinement_percent",
        "morphology.native_large_scale_refinement_percent",
        "morphology.native_fine_scale_refinement_percent",
        "morphology.native_sculpture_attempts_percent",
        "morphology.native_relaxation_strength_percent",
        "morphology.frame_margin_percent",
        "morphology.edge_falloff_percent",
        "relief.water_threshold",
        "relief.mountain_threshold",
        "relief.snow_threshold",
    )


def test_archetype_shape_scale_is_limited_to_native_size():
    descriptor = {
        item.key: item
        for item in iter_archetype_parameter_descriptors(
            default_archetype_profile("continental")
        )
    }["morphology.shape_scale_percent"]

    assert descriptor.maximum == 100
    with pytest.raises(ValueError, match="shape_scale_percent"):
        normalize_archetype_profile(
            {"morphology": {"shape_scale_percent": 101}},
            archetype_key="continental",
        )


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("layout_engine",), "perlin"),
        (("noise", "family"), "simplex"),
        (("noise", "display_range", "minimum"), -12),
        (("coast", "derived"), False),
        (("mass", "micro_islands"), True),
    ),
)
def test_continental_locked_contract_cannot_drift_into_an_ignored_parameter(path, value):
    with pytest.raises(ValueError, match="contrat macro Continental natif est verrouillé"):
        normalize_archetype_profile(
            {path[0]: {path[1]: value} if len(path) > 1 else value},
            archetype_key="continental",
        )


def test_archetype_profile_thresholds_are_ordered_and_round_trip():
    config = build_custom_config("upgraded")
    restored = CustomGenerationConfig.from_dict(config.to_dict())
    changed = config.with_archetype_value(("relief", "snow_threshold"), 205)

    assert restored.to_dict() == config.to_dict()
    assert changed.archetype_profile["relief"]["snow_threshold"] == 205
    assert changed.digest != config.digest
    assert changed.runtime_profile()["_custom_runtime"]["archetype_profile"] == changed.archetype_profile

    with pytest.raises(ValueError, match="eau < montagne < neige"):
        normalize_archetype_profile(
            {"relief": {"water_threshold": 150, "mountain_threshold": 140}},
            archetype_key="continental",
        )


@pytest.mark.parametrize("mode", ("legacy", "upgraded"))
def test_unchanged_custom_archetype_matches_the_base_map(mode):
    generator = _generator()
    kwargs = {"players": 2, "seed": 20260918, "archetype": "continental", "side": 256}
    native = generator.generate(**kwargs, mode=mode)
    custom = generator.generate(
        **kwargs,
        mode="custom",
        custom_config=build_custom_config(mode),
    )

    for field in ("height", "terrain", "objects", "resources", "accessibility", "claim"):
        assert np.array_equal(getattr(native.state, field), getattr(custom.state, field))
    assert native.state.starts == custom.state.starts
    assert custom.state.metadata["archetype_relief_thresholds"] == [0, 140, 190]


@pytest.mark.parametrize("mode", ("legacy", "upgraded"))
def test_custom_archetype_runs_under_the_selected_generator_mode(mode):
    generator = _generator()
    base = generator.generate(
        2, 20260920, mode=mode, archetype="continental", side=256
    )
    profile = default_archetype_profile()
    profile["morphology"]["relief_source"] = "domain_warp"
    config = build_custom_config(mode).with_archetype_profile(profile)

    edited = generator.generate(
        2,
        20260920,
        mode=mode,
        archetype="continental",
        side=256,
        custom_config=config,
    )

    assert generator.current_mode == mode
    assert not np.array_equal(base.state.height, edited.state.height)


@pytest.mark.parametrize(
    "generate_native",
    (generate_primary_terrain, generate_upgraded_primary_terrain),
)
@pytest.mark.parametrize("side", (256, 512))
@pytest.mark.parametrize("mirror_mode", (0, 3))
def test_explicit_base_archetype_contract_matches_implicit_native_defaults(
    generate_native,
    side,
    mirror_mode,
):
    profile = default_archetype_profile("continental")
    implicit = generate_native(side, 20260918, mirror_mode)
    explicit = generate_native(
        side,
        20260918,
        mirror_mode,
        archetype_profile=profile,
    )

    for field in ("height", "terrain", "variant", "marker"):
        assert np.array_equal(getattr(implicit, field), getattr(explicit, field))
    assert explicit.metadata["archetype_relief_thresholds"] == [0, 140, 190]


def test_custom_archetype_threshold_changes_only_the_custom_macro_result():
    config = build_custom_config("upgraded")
    changed = config.with_archetype_value(("relief", "mountain_threshold"), 100)
    generator = _generator()

    base = generator.generate(
        2,
        20260918,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config,
    )
    edited = generator.generate(
        2,
        20260918,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=changed,
    )

    assert np.array_equal(base.state.height, edited.state.height)
    assert not np.array_equal(base.state.terrain, edited.state.terrain)
    assert edited.state.metadata["archetype_relief_thresholds"] == [0, 100, 190]


@pytest.mark.parametrize("mode", (0, 3))
def test_archetype_preview_uses_shared_fast_relief_preview(mode):
    profile = default_archetype_profile("continental")
    preview = generate_archetype_preview(profile, 256, 20260918, mode)
    preview_noise = generate_relief_preview_noise(256, 20260918, mode)
    preview_height = generate_relief_preview_height(256, 20260918, mode)
    direct_height = generate_relief_height(256, 20260918, mode)
    native_result = generate_primary_terrain(
        256,
        20260918,
        mode,
        archetype_profile=profile,
    )

    assert np.array_equal(preview.noise, preview_noise)
    assert preview.noise.dtype == np.int16
    assert int(preview.noise.min()) == -30
    assert np.all(preview_height >= 0)
    assert np.array_equal(direct_height, native_result.height)
    assert np.array_equal(preview.macro, classify_macro(preview_height, profile))
    assert not np.array_equal(preview.noise, direct_height)


def test_archetype_preview_is_deterministic_and_uses_five_macro_classes():
    profile = default_archetype_profile("continental")
    first = generate_archetype_preview(profile, 256, 20260918)
    second = generate_archetype_preview(profile, 256, 20260918)

    assert np.array_equal(first.noise, second.noise)
    assert np.array_equal(first.macro, second.macro)
    assert set(np.unique(first.macro)).issubset(
        {MACRO_WATER, MACRO_BEACH, MACRO_GRASS, MACRO_MOUNTAIN, MACRO_SNOW}
    )
    assert first.thresholds == (0, 140, 190)
    assert first.mass is not None
    assert first.mass.mass_count >= 1


def test_macro_mass_report_uses_hex_connected_land_components():
    macro = np.zeros((5, 5), dtype=np.uint8)
    macro[1:4, 1:4] = MACRO_GRASS
    macro[0, 4] = MACRO_GRASS

    report = analyze_macro_masses(macro)

    assert report.land_cells == 10
    assert report.water_cells == 15
    assert report.mass_count == 2
    assert report.largest_mass_cells == 9
    assert report.largest_mass_share_percent == pytest.approx(90.0)


def test_startable_mass_report_is_diagnostic_and_keeps_start_components():
    terrain = np.zeros((6, 6), dtype=np.uint8)
    terrain[1:5, 1:5] = 16
    terrain[0, 5] = 16

    report = analyze_startable_masses(terrain, [(2, 2), (0, 5)], candidate_centers_considered=12)

    assert report["grass_mass_count"] == 2
    assert report["starts_in_largest_grass_mass"] == 1
    assert report["all_starts_in_largest_grass_mass"] is False
    assert report["candidate_centers_considered"] == 12


def test_large_archetype_preview_uses_exact_native_resolution():
    profile = default_archetype_profile("continental")
    small = generate_archetype_preview(profile, 256, 20260918)
    large = generate_archetype_preview(profile, 512, 20260918)

    assert large.noise.shape == (512, 512)
    assert not np.array_equal(large.noise[::2, ::2], small.noise)
    assert large.macro.shape == (512, 512)
    assert set(np.unique(large.macro)).issubset(
        {MACRO_WATER, MACRO_BEACH, MACRO_GRASS, MACRO_MOUNTAIN, MACRO_SNOW}
    )


def test_archetype_preview_threshold_edit_keeps_noise_and_changes_macro():
    base_profile = default_archetype_profile("continental")
    edited_profile = normalize_archetype_profile(
        {"relief": {"mountain_threshold": 100}},
        archetype_key="continental",
    )
    base = generate_archetype_preview(base_profile, 256, 20260918)
    edited = generate_archetype_preview(edited_profile, 256, 20260918)

    assert np.array_equal(base.noise, edited.noise)
    assert not np.array_equal(base.macro, edited.macro)
    assert edited.thresholds == (0, 100, 190)


def test_archetype_preview_morphology_edit_changes_the_shared_noise_field():
    base_profile = default_archetype_profile("continental")
    edited_profile = normalize_archetype_profile(
        {"morphology": {"shape_scale_percent": 75}},
        archetype_key="continental",
    )

    base = generate_archetype_preview(base_profile, 256, 20260918)
    edited = generate_archetype_preview(edited_profile, 256, 20260918)

    assert not np.array_equal(base.noise, edited.noise)
    assert not np.array_equal(base.macro, edited.macro)


def test_noise_layers_are_deterministic_and_shared_by_preview_paths():
    layered_profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 2,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "smooth",
                        "scale_percent": 80,
                        "strength_percent": 70,
                    },
                    {
                        "enabled": True,
                        "family": "ridged",
                        "scale_percent": 140,
                        "strength_percent": 45,
                    },
                ]
            }
        },
        archetype_key="continental",
    )
    base = generate_archetype_preview(
        default_archetype_profile("continental"),
        256,
        20260918,
        3,
    )
    first = generate_archetype_preview(layered_profile, 256, 20260918, 3)
    second = generate_archetype_preview(layered_profile, 256, 20260918, 3)
    fast_noise = generate_archetype_noise_preview(layered_profile, 256, 20260918, 3)
    fields_noise, fields_height = generate_relief_preview_fields(
        256,
        20260918,
        3,
        archetype_profile=layered_profile,
    )

    assert np.array_equal(first.noise, second.noise)
    assert np.array_equal(first.macro, second.macro)
    assert np.array_equal(first.noise, fast_noise)
    assert np.array_equal(first.noise, fields_noise)
    assert np.array_equal(first.macro, classify_macro(fields_noise, layered_profile, final_height=fields_height))
    assert not np.array_equal(first.noise, base.noise)


def test_archetype_preview_morphology_cache_reuses_native_fields():
    cache = OrderedDict()
    base_profile = default_archetype_profile("continental")
    edited_profile = normalize_archetype_profile(
        {"morphology": {"relief_contrast_percent": 150}},
        archetype_key="continental",
    )

    base = generate_archetype_preview(
        base_profile,
        256,
        20260918,
        noise_cache=cache,
    )
    edited = generate_archetype_preview(
        edited_profile,
        256,
        20260918,
        noise_cache=cache,
    )

    assert base.noise_reused is False
    assert edited.noise_reused is True
    assert not np.array_equal(base.noise, edited.noise)
    assert len(cache) == 1


@pytest.mark.parametrize("mode", (0, 3))
def test_fast_archetype_noise_matches_the_completed_noise_preview(mode):
    profile = normalize_archetype_profile(
        {"morphology": {"shape_scale_percent": 75, "relief_contrast_percent": 125}},
        archetype_key="continental",
    )

    fast = generate_archetype_noise_preview(profile, 256, 20260918, mode)
    complete = generate_archetype_preview(profile, 256, 20260918, mode)

    assert np.array_equal(fast, complete.noise)


def test_indicative_archetype_preview_classifies_the_fast_field():
    profile = default_archetype_profile("continental")

    noise, macro = generate_archetype_indicative_preview(
        profile,
        256,
        20260918,
        noise_cache=OrderedDict(),
    )

    assert noise.shape == (256, 256)
    assert macro.shape == (256, 256)
    assert np.array_equal(macro, classify_macro(noise, profile))
    assert set(np.unique(macro)).issubset(
        {MACRO_WATER, MACRO_BEACH, MACRO_GRASS, MACRO_MOUNTAIN, MACRO_SNOW}
    )


def test_fast_noise_preview_stops_before_relief_relaxation(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("la relaxation ne doit pas être appelée par la preview rapide")

    monkeypatch.setattr(legacy_native, "_relax_relief", fail_if_called)
    noise = generate_relief_preview_noise_fast(256, 20260918)

    assert noise.shape == (256, 256)
    assert noise.dtype == np.int16
    assert int(noise.min()) == -30
    assert np.all(noise[0, :] == -30)
    assert np.all(noise[-1, :] == -30)


def test_exact_macro_preview_can_skip_relief_relaxation(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("le lissage doit être désactivable dans la macro")

    monkeypatch.setattr(legacy_native, "_relax_relief", fail_if_called)
    preview = generate_archetype_preview(
        default_archetype_profile("continental"),
        256,
        20260918,
        relax_macro=False,
    )

    assert preview.macro_relaxed is False
    assert preview.noise.shape == (256, 256)
    assert preview.macro.shape == (256, 256)


def test_exact_macro_relaxation_switch_can_change_classification():
    profile = default_archetype_profile("continental")
    relaxed = generate_archetype_preview(
        profile,
        256,
        42,
        relax_macro=True,
    )
    raw = generate_archetype_preview(
        profile,
        256,
        42,
        relax_macro=False,
    )

    assert relaxed.macro_relaxed is True
    assert raw.macro_relaxed is False
    assert not np.array_equal(relaxed.macro, raw.macro)
    assert np.array_equal(relaxed.noise, raw.noise)


@pytest.mark.parametrize("generate_native", (generate_primary_terrain, generate_upgraded_primary_terrain))
def test_archetype_morphology_reaches_both_native_generators(generate_native):
    base_profile = default_archetype_profile("continental")
    edited_profile = normalize_archetype_profile(
        {"morphology": {"relief_contrast_percent": 160}},
        archetype_key="continental",
    )

    base = generate_native(256, 20260918, archetype_profile=base_profile)
    edited = generate_native(256, 20260918, archetype_profile=edited_profile)

    assert not np.array_equal(base.height, edited.height)
    assert edited.metadata["archetype_relief_thresholds"] == [0, 140, 190]


@pytest.mark.parametrize("generate_native", (generate_primary_terrain, generate_upgraded_primary_terrain))
def test_noise_layers_reach_both_native_generators(generate_native):
    base_profile = default_archetype_profile("continental")
    layered_profile = normalize_archetype_profile(
        {
            "morphology": {
                "noise_layer_count": 1,
                "noise_layers": [
                    {
                        "enabled": True,
                        "family": "smooth",
                        "scale_percent": 90,
                        "strength_percent": 80,
                    }
                ]
            }
        },
        archetype_key="continental",
    )

    base = generate_native(256, 20260918, archetype_profile=base_profile)
    layered = generate_native(256, 20260918, archetype_profile=layered_profile)

    assert not np.array_equal(base.height, layered.height)
    assert layered.metadata["archetype_relief_thresholds"] == [0, 140, 190]


def test_archetype_preview_and_profile_aware_relief_fields_are_identical():
    profile = normalize_archetype_profile(
        {"morphology": {"shape_scale_percent": 75, "relief_contrast_percent": 125}},
        archetype_key="continental",
    )
    preview = generate_archetype_preview(profile, 256, 20260918, 3)
    noise, height = generate_relief_preview_fields(
        256,
        20260918,
        3,
        archetype_profile=profile,
    )

    assert np.array_equal(preview.noise, noise)
    assert np.array_equal(preview.macro, classify_macro(height, profile))


def test_archetype_thresholds_allow_native_negative_floor_and_guard_snow_gap():
    profile = normalize_archetype_profile(
        {
            "relief": {
                "water_threshold": -30,
                "mountain_threshold": 20,
                "snow_threshold": 22,
            }
        },
        archetype_key="continental",
    )

    assert relief_thresholds(profile) == (-30, 20, 22)

    with pytest.raises(ValueError, match="au moins 2"):
        normalize_archetype_profile(
            {
                "relief": {
                    "water_threshold": -30,
                    "mountain_threshold": 20,
                    "snow_threshold": 21,
                }
            },
            archetype_key="continental",
        )


def test_archetype_threshold_spinbox_bounds_follow_the_other_thresholds():
    profile = normalize_archetype_profile(
        {
            "relief": {
                "water_threshold": -10,
                "mountain_threshold": 100,
                "snow_threshold": 190,
            }
        },
        archetype_key="continental",
    )
    descriptors = {
        descriptor.key: descriptor
        for descriptor in iter_archetype_parameter_descriptors(profile)
    }

    assert descriptors["relief.water_threshold"].minimum == -30
    assert descriptors["relief.water_threshold"].maximum == 99
    assert descriptors["relief.mountain_threshold"].minimum == -9
    assert descriptors["relief.mountain_threshold"].maximum == 188
    assert descriptors["relief.snow_threshold"].minimum == 102


def test_archetype_preview_cache_reuses_noise_across_threshold_edits():
    cache = OrderedDict()
    base_profile = default_archetype_profile("continental")
    edited_profile = normalize_archetype_profile(
        {"relief": {"mountain_threshold": 100}},
        archetype_key="continental",
    )

    first = generate_archetype_preview(
        base_profile,
        256,
        20260918,
        noise_cache=cache,
    )
    second = generate_archetype_preview(
        edited_profile,
        256,
        20260918,
        noise_cache=cache,
    )

    assert first.noise_reused is False
    assert second.noise_reused is True
    assert np.array_equal(first.noise, second.noise)
    assert not np.array_equal(first.macro, second.macro)
    assert len(cache) == 1


def test_archetype_preview_reports_progressive_noise_snapshots():
    profile = default_archetype_profile("continental")
    progress = []

    preview = generate_archetype_preview(
        profile,
        256,
        20260918,
        progress=lambda fraction, noise: progress.append((fraction, noise.shape)),
    )

    fractions = [fraction for fraction, _shape in progress]
    assert len(progress) >= 3
    assert fractions == sorted(fractions)
    assert fractions[-1] == 1.0
    assert all(shape == preview.noise.shape for _fraction, shape in progress)


def test_macro_preview_classifies_thresholds_and_derives_beach():
    noise = np.full((7, 7), 255, dtype=np.uint8)
    noise[0] = (0, 10, 139, 140, 189, 190, 255)

    macro = classify_macro(noise)

    assert macro[0].tolist() == [
        MACRO_WATER,
        MACRO_BEACH,
        MACRO_GRASS,
        MACRO_MOUNTAIN,
        MACRO_MOUNTAIN,
        MACRO_SNOW,
        MACRO_SNOW,
    ]
    assert noise_rgb(noise).shape == (7, 7, 3)
    raw = np.array([[0, 31], [128, 255]], dtype=np.uint8)
    raw_rgb = raw_height_rgb(raw)
    assert raw_rgb.shape == (2, 2, 3)
    assert np.array_equal(raw_rgb[:, :, 0], raw)
    assert np.array_equal(raw_rgb[:, :, 1], raw)
    assert np.array_equal(raw_rgb[:, :, 2], raw)
    assert macro_rgb(macro).shape == (7, 7, 3)


def test_preview_projection_keeps_square_and_expands_parallelogram():
    rgb = np.arange(4 * 4 * 3, dtype=np.uint8).reshape((4, 4, 3))

    square = project_preview_rgb(rgb, "square")
    parallelogram = project_preview_rgb(rgb, "parallelogram")

    assert np.array_equal(square, rgb)
    assert parallelogram.shape == (8, 11, 3)
    assert np.all(parallelogram[0, 3:5] == rgb[0, 0])
    assert np.all(parallelogram[-1, 0:2] == rgb[-1, 0])


def test_macro_percentages_report_all_five_classes():
    macro = np.tile(
        np.array(
            [MACRO_WATER, MACRO_BEACH, MACRO_GRASS, MACRO_MOUNTAIN, MACRO_SNOW],
            dtype=np.uint8,
        ),
        (5, 1),
    )

    assert macro_percentages(macro) == (20.0, 20.0, 20.0, 20.0, 20.0)


def test_custom_effective_margin_is_the_new_zero_baseline():
    profile = continental_legacy_blocks_profile()
    assert profile["morphology"]["frame_margin_percent"] == 0
    assert profile["morphology"]["relief_source"] == "legacy_blocks"


def test_legacy_midpoint_refinement_parameter_is_editable_in_both_engines():
    from s3mapgen.generation.generators.legacy.native_terrain import (
        generate_primary_terrain as generate_legacy,
    )
    from s3mapgen.generation.generators.upgraded.native_terrain import (
        generate_primary_terrain as generate_upgraded,
    )

    for generate in (generate_legacy, generate_upgraded):
        native = generate(256, 20260918)
        baseline = generate(
            256, 20260918, archetype_profile=default_archetype_profile("continental")
        )
        assert np.array_equal(native.height, baseline.height)
        edited_profile = default_archetype_profile("continental")
        edited_profile["morphology"]["native_refinement_percent"] = 50
        edited = generate(256, 20260918, archetype_profile=edited_profile)
        assert not np.array_equal(native.height, edited.height)
        coarse_profile = default_archetype_profile("continental")
        coarse_profile["morphology"]["native_coarse_variation_percent"] = 50
        coarse = generate(256, 20260918, archetype_profile=coarse_profile)
        assert not np.array_equal(native.height, coarse.height)
        for band in ("native_large_scale_refinement_percent", "native_fine_scale_refinement_percent"):
            band_profile = default_archetype_profile("continental")
            band_profile["morphology"][band] = 50
            band_result = generate(256, 20260918, archetype_profile=band_profile)
            assert not np.array_equal(native.height, band_result.height)
        sculpture_profile = default_archetype_profile("continental")
        sculpture_profile["morphology"]["native_sculpture_attempts_percent"] = 50
        sculpture_baseline = generate(256, 297650040)
        sculpture = generate(256, 297650040, archetype_profile=sculpture_profile)
        assert not np.array_equal(sculpture_baseline.height, sculpture.height)
        relax_baseline = generate(256, 297650040)
        relax_profile = default_archetype_profile("continental")
        relax_profile["morphology"]["native_relaxation_strength_percent"] = 50
        relaxed = generate(256, 297650040, archetype_profile=relax_profile)
        assert not np.array_equal(relax_baseline.height, relaxed.height)


def test_midpoint_parameter_does_not_disable_complete_noise_map_sources():
    from s3mapgen.generation.generators.legacy.native_terrain import (
        generate_primary_terrain as generate_legacy,
    )
    from s3mapgen.generation.generators.upgraded.native_terrain import (
        generate_primary_terrain as generate_upgraded,
    )

    for generate in (generate_legacy, generate_upgraded):
        low = continental_noise_calibration_profile()
        high = deepcopy(low)
        low["morphology"]["native_refinement_percent"] = 0
        high["morphology"]["native_refinement_percent"] = 300
        low["morphology"]["native_coarse_variation_percent"] = 0
        high["morphology"]["native_coarse_variation_percent"] = 200
        low["morphology"]["native_large_scale_refinement_percent"] = 0
        high["morphology"]["native_large_scale_refinement_percent"] = 200
        low["morphology"]["native_fine_scale_refinement_percent"] = 0
        high["morphology"]["native_fine_scale_refinement_percent"] = 200
        low["morphology"]["native_sculpture_attempts_percent"] = 0
        high["morphology"]["native_sculpture_attempts_percent"] = 200
        low["morphology"]["native_relaxation_strength_percent"] = 0
        high["morphology"]["native_relaxation_strength_percent"] = 100
        first = generate(256, 20260920, archetype_profile=low)
        second = generate(256, 20260920, archetype_profile=high)
        for field in ("height", "terrain", "variant", "marker"):
            assert np.array_equal(getattr(first, field), getattr(second, field))


def test_native_refinement_parameter_refreshes_live_previews_and_cache():
    baseline_profile = default_archetype_profile("continental")
    changed_profile = deepcopy(baseline_profile)
    changed_profile["morphology"]["native_refinement_percent"] = 50
    changed_profile["morphology"]["native_coarse_variation_percent"] = 50
    cache = OrderedDict()

    baseline = generate_archetype_preview(
        baseline_profile, 256, 20260918, noise_cache=cache
    )
    changed = generate_archetype_preview(
        changed_profile, 256, 20260918, noise_cache=cache
    )
    assert not np.array_equal(baseline.noise, changed.noise)
    assert not np.array_equal(baseline.macro, changed.macro)
    assert changed.noise_reused is False

    restored = generate_archetype_preview(
        baseline_profile, 256, 20260918, noise_cache=cache
    )
    assert restored.noise_reused is True
    assert np.array_equal(restored.noise, baseline.noise)

    coarse_only = deepcopy(baseline_profile)
    coarse_only["morphology"]["native_coarse_variation_percent"] = 50
    coarse_preview = generate_archetype_preview(coarse_only, 256, 20260918)
    assert not np.array_equal(coarse_preview.noise, baseline.noise)

    sculpture_baseline_profile = deepcopy(baseline_profile)
    sculpture_only = deepcopy(baseline_profile)
    sculpture_only["morphology"]["native_sculpture_attempts_percent"] = 50
    from s3mapgen.generation.generators.legacy.native_terrain import (
        generate_relief_preview_fields,
    )
    _base_noise, base_sculpted_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=sculpture_baseline_profile
    )
    _edited_noise, edited_sculpted_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=sculpture_only
    )
    assert not np.array_equal(edited_sculpted_height, base_sculpted_height)
    relaxed_profile = deepcopy(baseline_profile)
    relaxed_profile["morphology"]["native_relaxation_strength_percent"] = 50
    _noise_base, full_relax_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=baseline_profile
    )
    _noise_relaxed, partial_relax_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=relaxed_profile
    )
    assert not np.array_equal(partial_relax_height, full_relax_height)
    no_relax_profile = deepcopy(baseline_profile)
    no_relax_profile["morphology"]["native_relaxation_strength_percent"] = 0
    _noise_zero, zero_strength_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=no_relax_profile
    )
    _noise_skip, pre_relax_height = generate_relief_preview_fields(
        256, 297650040, archetype_profile=no_relax_profile, relax_relief=False
    )
    assert np.array_equal(zero_strength_height, pre_relax_height)

    fast_baseline = generate_archetype_noise_preview(
        baseline_profile, 192, 20260918, noise_cache=cache
    )
    fast_changed = generate_archetype_noise_preview(
        changed_profile, 192, 20260918, noise_cache=cache
    )
    assert not np.array_equal(fast_baseline, fast_changed)

    indicative_baseline = generate_archetype_indicative_preview(
        baseline_profile, 192, 20260918
    )
    indicative_changed = generate_archetype_indicative_preview(
        changed_profile, 192, 20260918
    )
    assert not np.array_equal(indicative_baseline[0], indicative_changed[0])

    source_baseline, _ = generate_noise_component_previews(
        baseline_profile, 128, 20260918
    )
    source_changed, _ = generate_noise_component_previews(
        changed_profile, 128, 20260918
    )
    assert not np.array_equal(source_baseline, source_changed)
