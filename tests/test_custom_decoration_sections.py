"""Custom appearance rates for the native decoration families."""

import numpy as np

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import DECORATION_FAMILY_KEYS, build_custom_config


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def test_upgraded_decoration_rates_scale_one_native_family_without_changing_the_catalogue():
    generator = _generator()
    kwargs = dict(players=2, seed=20260904, archetype="continental", side=256)
    native = generator.generate(**kwargs, mode="upgraded")
    native_meta = native.state.metadata["upgraded_decorations"]
    baseline = native_meta["legacy_static"]["small_plants"]
    assert set(native_meta["rates"]) == set(DECORATION_FAMILY_KEYS)

    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["decorations"]["small_plants"] = 0
    result = generator.generate(
        **kwargs,
        mode="custom",
        custom_config=config.with_sections(sections),
    )
    meta = result.state.metadata["upgraded_decorations"]
    assert meta["rates"]["small_plants"] == 0.0
    assert meta["legacy_static_targets"]["small_plants"] == 0
    assert meta["legacy_static"]["small_plants"] == 0
    assert not np.any(np.isin(result.state.objects, (35, 36, 37)))
    assert baseline > 0
    assert all(value.passed for value in result.validations if value.hard)


def test_legacy_decoration_rate_replaces_only_the_selected_family():
    generator = _generator()
    kwargs = dict(players=2, seed=20260904, archetype="continental", side=256)
    config = build_custom_config("legacy")
    sections = config.semantic_sections()
    sections["decorations"]["small_plants"] = 0
    result = generator.generate(
        **kwargs,
        mode="custom",
        custom_config=config.with_sections(sections),
    )
    controls = result.state.metadata["custom_object_controls"]
    decorations = controls["decorations"]
    assert controls["replaced"] == ("decorations",)
    assert decorations["rates"]["small_plants"] == 0.0
    assert decorations["baseline_counts"]["small_plants"] > 0
    assert decorations["counts"]["small_plants"] == 0
    assert not np.any(np.isin(result.state.objects, (35, 36, 37)))
    assert decorations["counts"]["big_stones"] == decorations["baseline_counts"]["big_stones"]
    # Legacy's native reef default is zero; changing another decoration must
    # not accidentally turn reefs into a replaced family.
    assert decorations["rates"]["reefs"] == 0.0
    assert "reefs" not in decorations["cleared"]
    assert all(value.passed for value in result.validations if value.hard)


def test_legacy_custom_reef_rate_uses_the_upgraded_reference_instead_of_zero_baseline():
    generator = _generator()
    kwargs = dict(players=2, seed=20260904, archetype="continental", side=256)
    config = build_custom_config("legacy")
    sections = config.semantic_sections()
    sections["decorations"]["reefs"] = 100
    result = generator.generate(
        **kwargs,
        mode="custom",
        custom_config=config.with_sections(sections),
    )
    decorations = result.state.metadata["custom_object_controls"]["decorations"]
    assert decorations["rates"]["reefs"] == 100.0
    assert decorations["targets"]["reefs"] == 2
    assert decorations["counts"]["reefs"] == 2
    assert np.count_nonzero(np.isin(result.state.objects, (111, 112, 113, 114))) == 2
    assert all(value.passed for value in result.validations if value.hard)
