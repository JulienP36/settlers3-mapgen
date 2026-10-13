"""Team-to-island grouping for the team-islands archetype."""

from __future__ import annotations


def group_players_by_team(players: int, player_teams=()) -> list[list[int]]:
    """Return player-index groups in stable first-player order.

    Team zero means no team in MapGen, so every zero-valued player receives a
    separate island. Positive values identify an alliance and share one island.
    """

    count = int(players)
    teams = tuple(player_teams) if player_teams else (0,) * count
    if len(teams) != count or any(
        isinstance(team, bool) or not isinstance(team, int) or not 0 <= team <= 20
        for team in teams
    ):
        raise ValueError("Îles par équipe : une équipe valide est requise par joueur")

    groups: list[list[int]] = []
    alliances: dict[int, int] = {}
    for player, team in enumerate(teams):
        if team == 0:
            groups.append([player])
            continue
        group_index = alliances.get(team)
        if group_index is None:
            group_index = len(groups)
            alliances[team] = group_index
            groups.append([])
        groups[group_index].append(player)
    return groups


def player_island_labels(groups: list[list[int]], players: int) -> list[int]:
    """Map each player slot to its one-based team-island label."""

    labels = [0] * int(players)
    for island, members in enumerate(groups, 1):
        for player in members:
            labels[int(player)] = island
    if any(label == 0 for label in labels):
        raise ValueError("Îles par équipe : chaque joueur doit appartenir à une île")
    return labels


__all__ = ("group_players_by_team", "player_island_labels")
