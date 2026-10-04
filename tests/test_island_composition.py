"""Preset parity and editable complete-source routing through real terrain."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.archetypes.island_source import generate_island_source
from s3mapgen.generation.archetypes.morphology import generate_noise_component_previews
from s3mapgen.generation.archetypes.previews import (
    generate_archetype_preview, generate_archetype_indicative_preview,
    generate_archetype_noise_preview,
)
from s3mapgen.generation.archetypes.profiles import (
    default_archetype_profile, normalize_archetype_profile, MASK_LAYER_MANUAL_GRID_SIDE,
)
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.constants import WATER_IDS


BASELINES = json.loads(Path("tests/fixtures/islands_r12_presets.json").read_text())["cases"]


def composed_profile(kind="fusion", origin="large_islands"):
    profile = default_archetype_profile(origin)
    morphology = profile["morphology"]
    morphology["relief_source"] = "large_islands"
    if kind in ("fusion", "both"):
        morphology["noise_layer_count"] = 1
        morphology["noise_layers"][0].update(
            enabled=True, source="perlin", operation="blend", strength_percent=20,
        )
    if kind in ("mask", "both"):
        morphology["mask_layer_count"] = 1
        morphology["mask_layers"][0].update(
            enabled=True, type="ellipse", operation="multiply", strength_percent=15,
        )
    if kind == "thresholds":
        profile["relief"].update(mountain_threshold=245, snow_threshold=255)
    if kind == "water":
        profile["relief"]["water_threshold"] = 5
    if kind == "negative_water":
        profile["relief"]["water_threshold"] = -5
    return normalize_archetype_profile(profile, archetype_key=origin)


@pytest.fixture(scope="module")
def baseline_fields():
    return generate_island_source(
        384, 4, 42, default_archetype_profile("large_islands"), native_relaxation=None,
    )


@pytest.mark.parametrize("operation", ["replace", "blend", "add", "subtract", "multiply", "min", "max"])
def test_full_island_source_accepts_all_shared_fusion_operations(operation, baseline_fields):
    profile = composed_profile()
    profile["morphology"]["noise_layers"][0]["operation"] = operation
    fields = generate_island_source(384, 4, 42, profile, native_relaxation=None)
    assert not np.array_equal(fields.noise, baseline_fields.noise)
    assert np.array_equal(fields.source_noise, baseline_fields.source_noise)
    assert fields.topology_labels is None  # edits may merge/split the original islands
    assert fields.noise_lab is not None


@pytest.mark.parametrize("enabled,strength", [(False, 40), (True, 0)])
def test_inactive_fusions_and_masks_are_exact_noops(enabled, strength, baseline_fields):
    profile = composed_profile("both")
    for name in ("noise_layers", "mask_layers"):
        profile["morphology"][name][0].update(enabled=enabled, strength_percent=strength)
    if strength == 0:
        profile["morphology"]["relief_source_mask"].update(type="edge", strength_percent=0)
    fields = generate_island_source(384, 4, 42, profile, native_relaxation=None)
    assert np.array_equal(fields.noise, baseline_fields.noise)
    assert np.array_equal(fields.height, baseline_fields.height)
    assert fields.topology_labels is not None


def test_source_mask_and_manual_global_mask_affect_the_complete_source(baseline_fields):
    source_mask = composed_profile("plain")
    source_mask["morphology"]["relief_source_mask"].update(type="edge", strength_percent=25)
    source = generate_island_source(384, 4, 42, source_mask, native_relaxation=None)
    assert not np.array_equal(source.source_noise, baseline_fields.source_noise)
    manual = composed_profile("mask")
    grid = np.zeros((MASK_LAYER_MANUAL_GRID_SIDE,) * 2, dtype=np.uint8)
    grid[12:52, 12:52] = 255
    manual["morphology"]["mask_layers"][0].update(
        type="manual", operation="subtract", strength_percent=20,
        provider_settings={"grid": grid.tolist()},
    )
    fields = generate_island_source(384, 4, 42, manual, native_relaxation=None)
    assert not np.array_equal(fields.noise, baseline_fields.noise)
    assert np.array_equal(fields.source_noise, baseline_fields.source_noise)


def test_thresholds_classify_without_rebuilding_the_island_source():
    base = generate_archetype_preview(composed_profile("plain"), 384, 42, players=4)
    for kind in ("thresholds", "water", "negative_water"):
        edited = generate_archetype_preview(composed_profile(kind), 384, 42, players=4)
        assert np.array_equal(edited.source_noise, base.source_noise), kind
        assert np.array_equal(edited.noise, base.noise), kind
        if kind != "negative_water":
            assert not np.array_equal(edited.macro, base.macro), kind
    high = generate_archetype_preview(composed_profile("thresholds"), 384, 42, players=4)
    assert not np.isin(high.macro, (3, 4)).any()


def test_source_selection_is_independent_of_the_profile_origin():
    for source in ("native_legacy", "legacy_blocks", "perlin", "large_islands"):
        continental, islands = (default_archetype_profile(key) for key in ("continental", "large_islands"))
        # Source equivalence requires the same classification thresholds;
        # named Large islands now has a higher default snow threshold.
        islands["relief"] = dict(continental["relief"])
        for profile in (continental, islands):
            profile["morphology"]["relief_source"] = source
            assert normalize_archetype_profile(profile, archetype_key=profile["archetype_key"])["morphology"]["relief_source"] == source
        first = generate_archetype_preview(continental, 384, 42, players=4)
        second = generate_archetype_preview(islands, 384, 42, players=4)
        assert np.array_equal(first.noise, second.noise), source
        assert np.array_equal(first.macro, second.macro), source


def test_fast_previews_and_source_thumbnail_use_real_islands():
    profile = composed_profile("both", origin="continental")
    noise = generate_archetype_noise_preview(profile, 384, 42, players=8)
    indicative, macro = generate_archetype_indicative_preview(profile, 384, 42, players=8)
    assert np.array_equal(noise, indicative)
    assert np.ptp(noise) > 100 and np.count_nonzero(macro) > noise.size // 4
    thumbnail, fusions = generate_noise_component_previews(
        profile, 64, 42, domain_side=384, players=8,
    )
    assert thumbnail.shape == (64, 64) and len(fusions) == 1
    assert np.ptp(thumbnail) > 100


@pytest.mark.parametrize("row", BASELINES, ids=lambda row: "-".join(map(str, row["case"])))
def test_inspectable_preset_matches_the_complete_map_and_keeps_classic_baseline(row):
    mode, archetype, side, players, seed = row["case"]
    config = build_custom_config(mode, archetype)
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        players, seed, mode="custom", archetype=archetype, side=side, custom_config=config,
    )
    if archetype == "continental":
        assert hashlib.sha256(result.state.area.tobytes()).hexdigest() == row["area_sha256"]
        assert [list(start) for start in result.state.starts] == row["starts"]
    else:
        # Compare the same named defaults, including the visible mini-swamp.
        # Explicitly disabling that bonus is now a real customization.
        preset = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
            players, seed, mode=mode, archetype=archetype, side=side,
        )
        assert np.array_equal(result.state.area, preset.state.area)
        assert result.state.starts == preset.state.starts
    assert all(value.passed for value in result.validations if value.hard)


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
@pytest.mark.parametrize("kind", ["both", "thresholds", "water", "negative_water"])
def test_real_generation_consumes_the_same_composed_height_as_preview(mode, kind, monkeypatch):
    from s3mapgen.generation.generators.legacy import native_terrain as legacy
    from s3mapgen.generation.generators.upgraded import native_terrain as upgraded
    engine = legacy if mode == "legacy" else upgraded
    profile = composed_profile(kind, origin="continental")
    preview = generate_archetype_preview(profile, 384, 42, players=4)
    captured = []
    classify = engine._classify_relief

    def capture(grid, archetype_profile, signed_noise=None):
        captured.append((grid.height.copy(), signed_noise.copy()))
        return classify(grid, archetype_profile, signed_noise)

    monkeypatch.setattr(engine, "_classify_relief", capture)
    config = build_custom_config(mode, "continental", start_packages=()).with_archetype_profile(profile)
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        4, 42, mode="custom", archetype="continental", side=384, custom_config=config,
    )
    assert len(captured) == 1
    assert np.array_equal(captured[0][0], np.clip(preview.noise, 0, 255).astype(np.uint8))
    assert np.array_equal(captured[0][1], preview.noise)
    assert result.state.metadata["archetype_relief_thresholds"] == list(preview.thresholds)
    assert "island_relief_source" in result.state.metadata
    assert all(value.passed for value in result.validations if value.hard), result.validations
    if kind == "thresholds":
        assert not any(value.rule_id == "ISLAND_MOUNTAINS" for value in result.validations)
    if kind == "water":
        assert np.isin(result.state.terrain, WATER_IDS).sum() > (preview.island_mask == 0).sum()


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_generator_can_disable_island_rivers_and_swamps(mode):
    config = build_custom_config(mode, "large_islands", start_packages=())
    sections = config.semantic_sections()
    sections["rivers"]["rate_percent"] = 0
    sections["terrains"]["swamp"]["enabled"] = False
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        4, 42, mode="custom", archetype="large_islands", side=384,
        custom_config=config.with_sections(sections),
    )
    assert not np.isin(result.state.terrain, (96, 97, 98, 99)).any()
    assert not np.isin(result.state.terrain, (21, 80, 81)).any()
    assert all(value.passed for value in result.validations if value.hard)


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_simple_noise_selected_from_island_origin_uses_generic_generation_and_mirror(mode):
    config = build_custom_config(mode, "large_islands", start_packages=())
    profile = config.archetype_profile
    profile["morphology"]["relief_source"] = "perlin"
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        4, 42, mode="custom", archetype="large_islands", side=384, mirror_mode=1,
        custom_config=config.with_archetype_profile(profile),
    )
    assert "island_relief_source" not in result.state.metadata
    assert "large_island_features" not in result.state.metadata
    assert all(value.passed for value in result.validations if value.hard)
