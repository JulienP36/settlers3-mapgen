import pytest

from s3mapgen.generation.core import (
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
    }
    for side, maximum in NATIVE_PLAYER_LIMITS.items():
        assert GenerationRequest(side=side, players=maximum, seed=42).side == side


def test_request_rejects_unsupported_size_and_player_count():
    with pytest.raises(ValueError, match="Taille non prise en charge"):
        GenerationRequest(side=192, players=2, seed=1)
    with pytest.raises(ValueError, match="Nombre de joueurs invalide"):
        GenerationRequest(side=384, players=9, seed=1)


def test_modifier_field_remains_reserved_and_rejects_nonempty_values():
    assert GenerationRequest(side=384, players=2, seed=1).modifiers == ()
    with pytest.raises(ValueError, match="modificateurs ne sont pas encore disponibles"):
        GenerationRequest(side=384, players=2, seed=1, modifiers=("reserved",))


def test_native_size_warning_categories_are_generation_contract_data():
    assert NATIVE_GAME_MIN_SIDE == 384
    assert NATIVE_GAME_MAX_SIDE == 768
    assert native_size_warning_kind(256) == "small"
    assert native_size_warning_kind(320) == "small"
    assert native_size_warning_kind(384) is None
    assert native_size_warning_kind(768) is None


@pytest.mark.parametrize('side',[832,896,960,1024])
@pytest.mark.parametrize('algorithm',['auto','classic','fair','islands'])
def test_generation_rejects_sizes_above_game_maximum(side,algorithm):
    with pytest.raises(ValueError,match="Taille non prise en charge"):
        GenerationRequest(side=side,players=4,seed=42,start_algorithm=algorithm,start_nations=(0,1,2,3))


def test_profile_sizes_match_generation_contract():
    assert set(map(int,load_profile()['supported_sizes']))==set(NATIVE_PLAYER_LIMITS)


def test_seed_streams_are_repeatable_and_stage_independent():
    first = SeedStreams(20260828)
    second = SeedStreams(20260828)
    assert first.value("macro") == second.value("macro")
    assert first.value("macro") != first.value("mountains")
    assert first.rng("macro").integers(0, 2**31) == second.rng("macro").integers(0, 2**31)
