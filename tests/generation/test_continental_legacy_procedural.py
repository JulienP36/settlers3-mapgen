from __future__ import annotations

import numpy as np
import pytest

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.core import GenerationRequest
from s3mapgen.generation.generators.legacy import generate


@pytest.fixture(scope="module")
def generated_384():
    return generate(GenerationRequest(side=384, players=4, seed=2026082901))


def test_procedural_legacy_is_deterministic_and_has_no_native_runtime_input(generated_384):
    state, validations = generated_384
    other, other_validations = generate(GenerationRequest(side=384, players=4, seed=2026082901))
    assert np.array_equal(state.area, other.area)
    assert state.starts == other.starts
    assert all(result.passed for result in validations if result.hard)
    assert all(result.passed for result in other_validations if result.hard)
    assert state.metadata["generator"] == "continental_legacy_v2"
    assert state.metadata["runtime_native_inputs"] == 0
    assert "native_template_index" not in state.metadata


def test_procedural_legacy_supports_the_native_smallest_size(generated_384):
    state, _ = generated_384
    assert state.side == 384
    assert len(state.starts) == 4
    assert state.metadata["lake_components"] > 0
    assert state.metadata["river_cells"] > 0
    assert state.metadata["coastal_bands_enabled"] is True
    assert state.metadata["coastal_bands_thinned_cells"] > 0
    assert state.metadata["coastal_bands_thickened_cells"] > 0
    assert state.metadata["coastal_bands_deepened_cells"] > 0
    assert state.metadata["coastal_bands_shore_break_cells"] == 0
    assert state.metadata["coastal_bands_transition_violations"] == 0


def test_terrain_masks_and_hydrology_keep_their_hard_invariants(generated_384):
    state, validations = generated_384
    by_rule = {result.rule_id: result for result in validations}
    for rule in (
        "MOUNTAIN_TRANSITIONS",
        "DESERT_TRANSITIONS",
        "SWAMP_TRANSITIONS",
        "SNOW_TRANSITIONS",
        "NO_TERRAIN_FAMILY_HOLES",
        "SHORE_REAL_RIMS",
        "WATER_SHORE_TRANSITIONS",
        "NO_WATER_GRASS_DIRECT",
        "START_FOOTPRINT_GRASS",
    ):
        assert by_rule[rule].passed, by_rule[rule].message
    assert state.metadata["macro_mainland_components"] == 1
    assert state.metadata["macro_satellite_components"] <= 7
    assert state.metadata["river_systems"] <= 48


def test_app_generator_progress_contract_is_three_arguments():
    events = []
    generator = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, UPGRADED_REFERENCE,
        progress_callback=lambda stage, detail, index: events.append((stage, detail, index)),
    )
    output = generator.generate(4, 2026082902, mode="legacy", archetype="continental", side=384)
    assert all(result.passed for result in output.validations if result.hard)
    assert events[0][0] == "continental_v2.begin"
    assert events[-1][0] == "continental_v2.complete"
    assert [event[2] for event in events] == list(range(1, len(events) + 1))
    assert [event[0] for event in events] == [
        "continental_v2.begin",
        "continental_v2.macro",
        "continental_v2.starts",
        "continental_v2.mountains",
        "continental_v2.relief",
        "continental_v2.snow",
        "continental_v2.lakes",
        "continental_v2.coastal_bands",
        "continental_v2.rivers",
        "continental_v2.swamps",
        "continental_v2.surface",
        "continental_v2.trees",
        "continental_v2.stones",
        "continental_v2.decorations",
        "continental_v2.minerals",
        "continental_v2.fish",
        "continental_v2.accessibility",
        "continental_v2.validate",
        "continental_v2.complete",
    ]


def test_app_generator_accepts_a_per_call_progress_route():
    default_events = []
    worker_events = []
    generator = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, UPGRADED_REFERENCE,
        progress_callback=lambda stage, detail, index: default_events.append(index),
    )
    output = generator.generate(
        4,
        2026082903,
        mode="legacy",
        archetype="continental",
        side=384,
        progress_callback=lambda stage, detail, index: worker_events.append(index),
    )
    assert all(result.passed for result in output.validations if result.hard)
    assert worker_events == list(range(1, len(worker_events) + 1))
    assert default_events == []
