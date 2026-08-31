import pytest

from s3mapgen.generation.core import GenerationRequest, NATIVE_PLAYER_LIMITS, SeedStreams


def test_native_size_limits_are_owned_by_generation_contract():
    assert NATIVE_PLAYER_LIMITS == {384: 8, 448: 11, 512: 15, 576: 19, 640: 20, 704: 20, 768: 20}
    for side, maximum in NATIVE_PLAYER_LIMITS.items():
        assert GenerationRequest(side=side, players=maximum, seed=42).side == side


def test_request_rejects_unsupported_size_and_player_count():
    with pytest.raises(ValueError, match="Taille non prise en charge"):
        GenerationRequest(side=320, players=2, seed=1)
    with pytest.raises(ValueError, match="Nombre de joueurs invalide"):
        GenerationRequest(side=384, players=9, seed=1)


def test_seed_streams_are_repeatable_and_stage_independent():
    first = SeedStreams(20260828)
    second = SeedStreams(20260828)
    assert first.value("macro") == second.value("macro")
    assert first.value("macro") != first.value("mountains")
    assert first.rng("macro").integers(0, 2**31) == second.rng("macro").integers(0, 2**31)
