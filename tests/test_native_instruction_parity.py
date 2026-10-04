"""Native instruction-replay fixtures, replacing hashes of the erroneous port."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from s3mapgen.generation.generators.legacy import native_terrain as legacy
from s3mapgen.generation.generators.upgraded import native_terrain as upgraded


FIXTURES = Path(__file__).parent / "fixtures/native_terrain_r9"
CASES = json.loads((FIXTURES / "provenance.json").read_text())["fixtures"]


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
@pytest.mark.parametrize(
    "case", CASES,
    ids=lambda c: f"{c['side']}-{c['seed']}-{c['mode']}-{c['stage']}",
)
def test_native_relief_and_rivers_match_independent_instruction_replay(engine, case):
    path = FIXTURES / case["fixture"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == case["fixture_sha256"]
    with np.load(path) as reference:
        native = reference["fields"]
        native_rng = reference["rng"]

    side, seed, mode = case["side"], case["seed"], case["mode"]
    grid = engine.NativeTerrainGrid.empty(side)
    rng = engine.NativeRng16(seed)
    engine._initialize_cells(grid)
    engine._seed_coarse_relief(grid, rng)
    engine._refine_relief(grid, rng)
    engine._normalize_relief(grid)
    if mode == 0:
        for _ in range(side * side // 16):
            row = 1 + math.trunc((rng.next() * side - 2) / 65536)
            col = 1 + ((rng.next() * (side - 3)) >> 16)
            if engine._interior(grid, row, col):
                engine._sculpt_candidate(grid, row, col)
        engine._consume_sculpture_markers(grid)
    engine._relax_relief(grid, bool(mode))
    if case["stage"] != "relaxation":
        engine._classify_relief(grid)
        engine._clear_pre_river_fields(grid)
        engine._generate_rivers(grid, rng)
    if case["stage"] == "structural":
        engine._apply_structural_transitions(grid)

    assert np.array_equal(np.stack([grid.height, grid.marker, grid.terrain], axis=-1), native)
    assert np.array_equal([rng.a, rng.b, rng.c], native_rng)
