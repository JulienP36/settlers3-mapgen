"""Civilization policy for optional MapGen departure bonuses."""


def start_player_slots(state):
    slots = state.metadata.get("start_slot_indices")
    if slots is not None and len(slots) == len(state.starts):
        return list(slots)
    disabled = set(state.metadata.get("classic_disabled_slots", ()))
    count = int(state.metadata.get("players", len(state.starts)))
    active = [i for i in range(count) if i not in disabled]
    return active[:len(state.starts)]


def swamp_bonus_players(state):
    """Chinese (2) and free choice (255), indexed by retained starts."""
    nations = state.metadata.get("player_nations", ())
    return [int(nations[slot] if slot < len(nations) else 255) in (2, 255)
            for slot in start_player_slots(state)]
