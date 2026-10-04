import numpy as np
import pytest

from s3mapgen.generation.archetypes import (
    CONTINENTAL_CALIBRATION_PROFILE_NAME,
    CONTINENTAL_CALIBRATION_RELIEF_CONTRAST_PERCENT,
    CONTINENTAL_CALIBRATION_SHAPE_SCALE_PERCENT,
    MASK_LAYER_MANUAL_GRID_SIDE,
    QUALIFICATION_REPRESENTATIVE_SIZES,
    RELIEF_SOURCE_OPTIONS,
    continental_calibration_profile,
    continental_calibration_report,
    continental_custom_report,
    continental_noise_calibration_profile,
    default_archetype_profile,
    manual_mask_fixture_grid,
    manual_mask_profile,
    manual_mask_report,
    qualification_player_cases,
    qualification_report,
    qualify_preview,
    qualify_providers,
    target_matrix,
)


def test_target_matrix_covers_the_first_three_archetype_families():
    matrix = target_matrix()

    assert matrix["matrix_version"] == 1
    assert matrix["sizes"] == [384, 448, 512, 576, 640, 704, 768]
    assert matrix["representative_sizes"] == list(QUALIFICATION_REPRESENTATIVE_SIZES)
    assert matrix["mirror_modes"] == [0, 3]
    assert set(matrix["player_cases"]) == {str(side) for side in matrix["sizes"]}
    assert [row["key"] for row in matrix["archetypes"]] == [
        "continental",
        "large_islands",
        "small_islands",
    ]
    assert matrix["archetypes"][0]["implemented"] is True
    assert [row["implemented"] for row in matrix["archetypes"]] == [True, True, False]


def test_qualification_player_cases_include_small_and_maximum_populations():
    assert qualification_player_cases(384) == (2, 4, 8)
    assert qualification_player_cases(512) == (2, 4, 15)
    assert qualification_player_cases(768) == (2, 4, 20)


def test_native_preview_has_a_macro_qualification_without_raw_provider_metrics():
    result = qualify_preview(
        default_archetype_profile("continental"),
        384,
        20260920,
    )

    assert result.status == "PASS"
    assert result.metrics.source == "native_legacy"
    assert result.metrics.raw_source_land_percent is None
    assert result.metrics.edge_water_percent == 100.0
    assert all(check.passed for check in result.checks)


def test_continental_calibration_profile_is_provisional_and_keeps_native_contract():
    base = default_archetype_profile("continental")
    calibrated = continental_calibration_profile()

    assert calibrated["profile_name"] == CONTINENTAL_CALIBRATION_PROFILE_NAME
    assert (
        calibrated["morphology"]["shape_scale_percent"]
        == CONTINENTAL_CALIBRATION_SHAPE_SCALE_PERCENT
    )
    assert (
        calibrated["morphology"]["relief_contrast_percent"]
        == CONTINENTAL_CALIBRATION_RELIEF_CONTRAST_PERCENT
    )
    assert base["morphology"]["shape_scale_percent"] == 100
    assert base["morphology"]["relief_contrast_percent"] == 100
    assert calibrated["mass"] == base["mass"]
    assert calibrated["coast"] == base["coast"]


def test_continental_calibration_report_gates_macro_and_player_starts():
    report = continental_calibration_report(
        sizes=(384,),
        seeds=(20260920,),
        mirror_modes=(0,),
        players=(2, 4),
    )

    assert report["summary"] == {
        "macro_rows": 1,
        "macro_passed": 1,
        "macro_failed": 0,
        "start_rows": 2,
        "start_passed": 2,
        "start_failed": 0,
        "gates_passed": 3,
        "gates_total": 3,
        "status": "PASS",
    }
    assert all(gate["passed"] for gate in report["gates"])
    assert all(row["status"] == "PASS" for row in report["start_results"])
    assert report["diagnostics"]["startable_mass_is_soft"] is True
    assert report["macro_results"][0]["case"] == {
        "side": 384,
        "seed": 20260920,
        "mirror_mode": 0,
    }


def test_continental_custom_report_qualifies_noise_composition_and_starts():
    report = continental_custom_report(
        sizes=(384,),
        seeds=(20260920,),
        mirror_modes=(0,),
        players=(2, 4),
    )

    assert report["profile"]["profile_name"] == continental_noise_calibration_profile()["profile_name"]
    assert report["profile"]["morphology"]["relief_source"] == "fbm"
    assert report["profile"]["morphology"]["noise_layer_count"] == 2
    assert report["summary"] == {
        "macro_rows": 1,
        "macro_passed": 1,
        "macro_failed": 0,
        "start_rows": 2,
        "start_passed": 2,
        "start_failed": 0,
        "gates_passed": 3,
        "gates_total": 3,
        "status": "PASS",
    }


def test_independent_providers_are_measured_separately_and_deterministically():
    first = qualify_providers(
        sizes=(384,),
        seed=20260920,
        sources=RELIEF_SOURCE_OPTIONS[1:],
    )
    second = qualify_providers(
        sizes=(384,),
        seed=20260920,
        sources=RELIEF_SOURCE_OPTIONS[1:],
    )

    assert [result.metrics.source for result in first] == list(RELIEF_SOURCE_OPTIONS[1:])
    assert [result.to_dict() for result in first] == [result.to_dict() for result in second]
    assert all(result.metrics.raw_source_land_percent is not None for result in first)
    assert all(result.metrics.edge_water_percent == 100.0 for result in first)
    # Qualification targets are diagnostics, not presets that every source
    # must imitate.  R29 deliberately includes white/cellular/ridged fields
    # whose standalone distributions differ strongly from Continental.
    assert len({result.metrics.macro_class_percentages for result in first}) >= 7


def test_qualification_report_exposes_deferred_gameplay_gates():
    report = qualification_report(
        sizes=(384,),
        sources=("fractal_fbm",),
    )

    assert report["summary"] == {"rows": 1, "passed": 1, "failed": 0}
    assert report["matrix"]["provider_gate_scope"] == "macro_preview"
    assert "starts" in report["matrix"]["deferred_gates"]
    assert report["results"][0]["status"] == "PASS"


def test_unimplemented_target_cannot_be_qualified_as_if_it_existed():
    with pytest.raises(NotImplementedError, match="Petites îles"):
        qualify_preview(
            default_archetype_profile("continental"),
            384,
            20260920,
            target_key="small_islands",
        )


def test_manual_mask_fixture_is_asymmetric_and_portable():
    grid = manual_mask_fixture_grid()

    assert grid.shape == (MASK_LAYER_MANUAL_GRID_SIDE, MASK_LAYER_MANUAL_GRID_SIDE)
    assert grid.dtype == np.uint8
    assert int(grid.min()) == 0
    assert int(grid.max()) == 255
    assert not np.array_equal(grid, np.flipud(grid))
    assert not np.array_equal(grid, np.fliplr(grid))


def test_manual_mask_report_qualifies_sizes_seeds_and_mirrors():
    report = manual_mask_report(
        manual_mask_profile(manual_mask_fixture_grid()),
        sizes=(128, 256),
        seeds=(20260920, 20260921),
        mirror_modes=(0, 3),
    )

    assert report["summary"] == {
        "rows": 8,
        "passed": 8,
        "failed": 0,
        "gates_passed": 4,
        "gates_total": 4,
        "status": "PASS",
    }
    assert all(gate["passed"] for gate in report["gates"])
    assert max(row["outside_noise_range"] for row in report["cases"]) > 0
    assert all(row["preview_changed_percent"] > 0 for row in report["cases"])
