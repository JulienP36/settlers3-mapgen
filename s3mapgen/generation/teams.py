"""Resolve user team choices without consuming the terrain's native PRNG."""
from __future__ import annotations

import hashlib
import random

RANDOM_TEAM = -1


def resolve_player_teams(players: int, seed: int, teams=(), random_team_count: int = 2) -> tuple[int, ...]:
    """Keep fixed alliances and independents; balance only the '?' players.

    The requested count includes fixed alliances, whose labels are preserved.
    More existing alliances raise the effective count; fewer eligible players
    lower it. Independent players never enter this draw. Empty input stays empty
    for compatibility with the existing default generation metadata.
    """
    teams = tuple(teams)
    if type(random_team_count) is not int or not 2 <= random_team_count <= 20:
        raise ValueError("Équipes aléatoires : nombre entier de 2 à 20 requis")
    if teams and (len(teams) != players or any(type(t) is not int or not -1 <= t <= 20 for t in teams)):
        raise ValueError("Équipes : une valeur entière de -1 à 20 par joueur requise")
    if RANDOM_TEAM not in teams:
        return teams
    fixed = sorted({t for t in teams if t > 0})
    possible_groups = len(fixed) + teams.count(RANDOM_TEAM)
    count = min(possible_groups, max(random_team_count, len(fixed)))
    labels = fixed + [t for t in range(1, 21) if t not in fixed][:count - len(fixed)]
    populations = {t: teams.count(t) for t in labels}
    # Separate seed domain: changing teams never advances native terrain RNG.
    material = f"mapgen-random-teams-v1:{int(seed)}:{teams}:{random_team_count}".encode("ascii")
    rng = random.Random(int.from_bytes(hashlib.sha256(material).digest(), "big"))
    slots = [i for i, t in enumerate(teams) if t == RANDOM_TEAM]
    rng.shuffle(slots)
    resolved = list(teams)
    for i in slots:
        minimum = min(populations.values())
        selected = rng.choice([t for t in labels if populations[t] == minimum])
        resolved[i] = selected
        populations[selected] += 1
    return tuple(resolved)
