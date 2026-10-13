"""Resolve visible island-source amplitude and classification thresholds."""

from math import pi, sqrt

from .profiles import (
    ISLAND_RELIEF_SOURCES,
    RELIEF_SOURCE_TEAM_ISLANDS, RELIEF_SOURCE_CONTINENTAL,
    normalize_archetype_profile,
)


def island_radius(side, players, island_player_counts=None):
    """Return the equivalent radius of the smallest generated island.

    Individual Islands gives every player one island.  Team Islands divides
    the same land budget by player count, so a team with ``n`` members gets
    ``n`` times the area of a solo island.  The smallest team controls the
    shared relief calibration; this keeps any singleton island from becoming
    too steep while allowing an all-in-one-team map to use its real large-island
    scale.
    """

    count = max(1, int(players))
    minimum_group = 1
    if island_player_counts is not None:
        sizes = tuple(int(value) for value in island_player_counts)
        if sizes:
            if any(value < 1 for value in sizes):
                raise ValueError("Chaque île doit correspondre à au moins un joueur")
            minimum_group = min(sizes)
    equivalent_islands = count / minimum_group
    return sqrt(.565 * int(side) ** 2 / equivalent_islands / pi)


def calibrated_thresholds(water, mountain, snow, amplitude, radius):
    correction = max(0., min(1., (100. - radius) / 40.))
    compensation = min(amplitude, 1. - amplitude)
    mountain = round(water + (mountain - water) * amplitude
                     + 30. * compensation * correction)
    snow = round(water + (snow - water) * amplitude
                 + 16. * compensation * correction)
    mountain = max(int(water) + 1, min(253, mountain))
    return mountain, max(mountain + 2, min(255, snow))


def resolve_island_profile(profile, side, players, *, player_teams=()):
    """Return an idempotent effective profile without changing saved controls.

    Continental sources are untouched. Automatic island amplitude only falls
    below 100% for an equivalent source radius below 100 cells.
    """
    if not profile or profile.get('morphology', {}).get('relief_source') not in ISLAND_RELIEF_SOURCES:
        return profile
    result = normalize_archetype_profile(profile, archetype_key=profile.get('archetype_key', 'large_islands'))
    morphology = result['morphology']
    island_player_counts = None
    if morphology["relief_source"] == RELIEF_SOURCE_TEAM_ISLANDS:
        from .island_teams import group_players_by_team

        groups = group_players_by_team(int(players), player_teams)
        island_player_counts = [len(group) for group in groups]
    radius = island_radius(side, 1, [1]) if morphology["relief_source"] == RELIEF_SOURCE_CONTINENTAL else island_radius(side, players, island_player_counts)
    if morphology['island_amplitude_auto']:
        t = max(0., min(1., (radius - 60.) / 40.))
        percent = round(50. + 50. * t * t * (3. - 2. * t))
    else:
        percent = morphology['island_amplitude_percent']
    morphology['island_amplitude_percent'] = percent
    morphology['island_amplitude_auto'] = False
    if morphology['island_thresholds_auto']:
        relief = result['relief']
        mountain, snow = calibrated_thresholds(
            relief['water_threshold'], max(140, relief['water_threshold'] + 1),
            max(200, relief['water_threshold'] + 3), percent / 100., radius,
        )
        relief.update(mountain_threshold=mountain, snow_threshold=snow)
    morphology['island_thresholds_auto'] = False
    return result
