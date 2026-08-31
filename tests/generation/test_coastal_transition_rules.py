from __future__ import annotations

from s3mapgen.generation.generators.legacy.profile import load_profile
from s3mapgen.generation.generators.legacy.validators import validate
from s3mapgen.map_data.constants import GRASS, WATER_IDS
from s3mapgen.map_data.model import MapState


def test_validator_rejects_direct_water_to_grass_transition():
    state = MapState.empty(32)
    state.metadata.update(runtime_native_inputs=0, players=0)
    state.accessibility[:] = 1
    state.terrain[:] = GRASS
    state.terrain[15, 15] = WATER_IDS[0]

    by_rule = {result.rule_id: result for result in validate(state, load_profile())}

    assert by_rule["WATER_SHORE_TRANSITIONS"].passed is False
    assert by_rule["NO_WATER_GRASS_DIRECT"].passed is False
