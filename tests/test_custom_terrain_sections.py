import numpy as np

from s3mapgen.application.paths import BASE
from s3mapgen.generation.custom import (
    TERRAIN_FAMILY_KEYS,
    apply_custom_terrain_rates,
    build_custom_config,
    effective_decoration_rates,
    effective_terrain_rates,
    normalize_sections,
)
from s3mapgen.generation.custom.terrain import TERRAIN_FAMILY_SPECS
from s3mapgen.generation.custom.terrain import terrain_transition_violations


def _mixed_surface_fixture(side=48):
    terrain = np.full((side, side), 16, dtype=np.uint8)
    terrain[3:11, 3:11] = 64
    terrain[14:22, 3:11] = 80
    terrain[25:33, 3:11] = 144
    terrain[3:11, 15:23] = 24
    terrain[14:22, 15:23] = 18
    terrain[25:33, 15:23] = 34
    # Add the transition IDs to each family so the public rate covers the
    # complete visual family rather than only its solid centre.
    terrain[3, 4:10] = 20
    terrain[4, 4:10] = 65
    terrain[14, 4:10] = 21
    terrain[15, 4:10] = 81
    terrain[25, 4:10] = 23
    terrain[26, 4:10] = 145
    return terrain


def test_custom_terrain_rate_at_100_is_a_strict_noop():
    terrain = _mixed_surface_fixture()
    original = terrain.copy()
    sections = build_custom_config("legacy").semantic_sections()

    metadata = apply_custom_terrain_rates(terrain, sections, seed=20260904)

    assert np.array_equal(terrain, original)
    assert metadata["changed"] is False
    assert set(metadata["rates"]) == set(TERRAIN_FAMILY_KEYS)


def test_custom_terrain_rate_zero_removes_the_whole_family():
    terrain = _mixed_surface_fixture()
    sections = build_custom_config("legacy").semantic_sections()
    for key in TERRAIN_FAMILY_KEYS:
        sections["terrains"][key].update(enabled=False, rate_percent=0)

    apply_custom_terrain_rates(terrain, sections, seed=20260904)

    for key in TERRAIN_FAMILY_KEYS:
        ids = tuple(TERRAIN_FAMILY_SPECS[key]["ids"])
        assert not np.any(np.isin(terrain, ids)), key


def test_enabled_terrain_rate_zero_is_promoted_to_one_percent():
    sections = build_custom_config("upgraded").semantic_sections()
    sections["terrains"]["swamp"]["rate_percent"] = 0

    normalized = normalize_sections(
        sections,
        fallback=build_custom_config("upgraded").semantic_sections(),
    )

    assert normalized["terrains"]["swamp"] == {"enabled": True, "rate_percent": 1.0}
    assert effective_terrain_rates(normalized)["swamp"] == 1.0


def test_upgraded_custom_can_activate_the_zero_native_mud_slot():
    from s3mapgen.generation.generators.upgraded.native_terrain import generate_primary_terrain

    native = generate_primary_terrain(256, 20260905)
    assert not np.isin(native.terrain, (23, 144, 145)).any()

    sections = build_custom_config("upgraded").semantic_sections()
    assert sections["terrains"]["mud"] == {"enabled": False, "rate_percent": 0.0}
    custom_default = generate_primary_terrain(256, 20260905, surface_rates=sections)
    assert not np.isin(custom_default.terrain, (23, 144, 145)).any()

    sections["terrains"]["mud"] = {"enabled": True, "rate_percent": 100.0}
    custom_enabled = generate_primary_terrain(256, 20260905, surface_rates=sections)
    assert np.isin(custom_enabled.terrain, (23, 144, 145)).any()


def test_high_terrain_rates_add_legal_zones_without_shortfall():
    from s3mapgen.generation.generators.upgraded.native_terrain import generate_primary_terrain

    sections = build_custom_config("upgraded").semantic_sections()
    for key in TERRAIN_FAMILY_KEYS:
        sections["terrains"][key] = {"enabled": True, "rate_percent": 500.0}

    result = generate_primary_terrain(256, 2026081901, surface_rates=sections)
    metadata = result.metadata["custom_terrain"]

    assert terrain_transition_violations(result.terrain)["total"] == 0
    assert metadata["transition_violations"]["total"] == 0
    for key in TERRAIN_FAMILY_KEYS:
        family = metadata["families"][key]
        # Native complete zones are reserved before painting.  A saturated
        # map may legitimately miss part of the nominal budget, but it must
        # never lose its calibrated 100% family or create a chopped zone.
        assert family["after_cells"] >= family["before_cells"], key
        assert family["zones_after"] >= family["zones_before"], key


def test_high_rate_native_recipe_density_is_monotonic_per_family():
    from s3mapgen.generation.generators.upgraded.native_terrain import generate_primary_terrain

    counts = {}
    for key in TERRAIN_FAMILY_KEYS:
        counts[key] = {}
        for rate in (200.0, 500.0):
            sections = build_custom_config("upgraded").semantic_sections()
            sections["terrains"][key] = {"enabled": True, "rate_percent": rate}
            result = generate_primary_terrain(256, 2026081901, surface_rates=sections)
            assert result.metadata["custom_terrain"]["transition_violations"]["total"] == 0
            counts[key][rate] = result.metadata["custom_terrain"]["families"][key]["after_cells"]

        assert counts[key][500.0] >= counts[key][200.0], key


def test_native_profile_is_byte_identical_when_custom_defaults_are_untouched():
    from s3mapgen.generation.generators.legacy.native_terrain import generate_primary_terrain as legacy_terrain
    from s3mapgen.generation.generators.upgraded.native_terrain import generate_primary_terrain as upgraded_terrain

    for mode, generate in (("legacy", legacy_terrain), ("upgraded", upgraded_terrain)):
        sections = build_custom_config(mode).semantic_sections()
        native = generate(256, 20260904).terrain
        custom = generate(256, 20260904, surface_rates=sections).terrain
        assert np.array_equal(custom, native), mode


def test_custom_terrain_transition_validator_accepts_high_rate_maps():
    from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from s3mapgen.generation import MapGenerator

    sections = build_custom_config("upgraded").semantic_sections()
    for key in TERRAIN_FAMILY_KEYS:
        sections["terrains"][key] = {"enabled": True, "rate_percent": 500.0}
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        4,
        2026081901,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=build_custom_config("upgraded").with_sections(sections),
    )

    assert all(value.passed for value in result.validations if value.hard)
    assert any(value.rule_id == "CUSTOM_TERRAIN_TRANSITIONS" for value in result.validations)


def test_disabled_terrain_zeroes_only_dependent_decoration_rates():
    sections = build_custom_config("upgraded").semantic_sections()
    sections["terrains"]["desert"]["enabled"] = False
    sections["terrains"]["desert"]["rate_percent"] = 100
    sections["terrains"]["swamp"]["enabled"] = False

    rates = effective_terrain_rates(sections)
    decorations = effective_decoration_rates(sections)

    assert rates["desert"] == 0.0
    assert rates["swamp"] == 0.0
    assert decorations["cacti"] == 0.0
    assert decorations["dead_trees"] == 0.0
    assert decorations["skeletons"] == 0.0
    assert decorations["reeds"] == 0.0
    assert decorations["bushes"] == 100.0


def test_mineral_sprite_assets_are_exactly_16_pixels():
    from PIL import Image

    for key in ("coal", "iron", "gold", "gems", "sulfur"):
        with Image.open(BASE / "data" / "mineral_icons" / f"{key}.png") as image:
            assert image.size == (16, 16)
            assert image.mode in {"RGBA", "LA"}
