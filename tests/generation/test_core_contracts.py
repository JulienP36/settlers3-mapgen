import pytest

from s3mapgen.generation.core import (
    EDITOR_EXTENDED_SIDES,
    GenerationRequest,
    NATIVE_GAME_MAX_SIDE,
    NATIVE_GAME_MIN_SIDE,
    NATIVE_PLAYER_LIMITS,
    SeedStreams,
    native_size_warning_kind,
)
from s3mapgen.generation.generators.legacy.profile import load_profile


def test_native_size_limits_are_owned_by_generation_contract():
    assert NATIVE_PLAYER_LIMITS == {
        256: 4,
        320: 6,
        384: 8,
        448: 11,
        512: 15,
        576: 19,
        640: 20,
        704: 20,
        768: 20,
        832: 20,
        896: 20,
        960: 20,
        1024: 20,
    }
    for side, maximum in NATIVE_PLAYER_LIMITS.items():
        assert GenerationRequest(side=side, players=maximum, seed=42).side == side


def test_request_rejects_unsupported_size_and_player_count():
    with pytest.raises(ValueError, match="Taille non prise en charge"):
        GenerationRequest(side=192, players=2, seed=1)
    with pytest.raises(ValueError, match="Nombre de joueurs invalide"):
        GenerationRequest(side=384, players=9, seed=1)


def test_native_size_warning_categories_are_generation_contract_data():
    assert EDITOR_EXTENDED_SIDES == (832, 896, 960, 1024)
    assert NATIVE_GAME_MIN_SIDE == 384
    assert NATIVE_GAME_MAX_SIDE == 768
    assert native_size_warning_kind(256) == "small"
    assert native_size_warning_kind(320) == "small"
    assert native_size_warning_kind(384) is None
    assert native_size_warning_kind(768) is None
    for side in EDITOR_EXTENDED_SIDES:
        assert native_size_warning_kind(side) == "extended"


def test_extended_editor_sizes_have_total_legacy_profile_tables():
    profile = load_profile()
    for side in EDITOR_EXTENDED_SIDES:
        assert str(side) in profile["supported_sizes"]
        assert str(side) in profile["lakes"]["fraction_map_by_side"]
        assert str(side) in profile["lakes"]["component_target_by_side"]
        assert str(side) in profile["rivers"]["fraction_map_by_side"]
        assert str(side) in profile["rivers"]["system_target_by_side"]


def test_seed_streams_are_repeatable_and_stage_independent():
    first = SeedStreams(20260828)
    second = SeedStreams(20260828)
    assert first.value("macro") == second.value("macro")
    assert first.value("macro") != first.value("mountains")
    assert first.rng("macro").integers(0, 2**31) == second.rng("macro").integers(0, 2**31)
