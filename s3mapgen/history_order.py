from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Hashable, TypeVar


HistoryKey = TypeVar("HistoryKey", bound=Hashable)
HistoryValue = TypeVar("HistoryValue")


def reconcile_visual_order(
    lru_entries: Sequence[tuple[HistoryKey, HistoryValue]],
    previous_order: Iterable[HistoryKey],
) -> tuple[list[HistoryKey], list[tuple[HistoryKey, HistoryValue]]]:
    """Merge live LRU entries into the stable user-visible history order.

    New cache keys appear first, surviving manually ordered keys retain their
    relative order, and evicted keys disappear. The input cache order is never
    mutated or touched, so this operation cannot alter real LRU recency.
    """

    live = dict(lru_entries)
    kept = [key for key in previous_order if key in live]
    kept_set = set(kept)
    added = [key for key, _ in lru_entries if key not in kept_set]
    order = added + kept
    return order, [(key, live[key]) for key in order]


def move_visual_key(
    order: Sequence[HistoryKey],
    key: HistoryKey,
    step: int,
) -> tuple[list[HistoryKey], bool]:
    """Move one visible key by a clamped step and report whether it moved."""

    updated = list(order)
    if key not in updated:
        return updated, False

    old_index = updated.index(key)
    new_index = max(0, min(len(updated) - 1, old_index + int(step)))
    if new_index == old_index:
        return updated, False

    updated[old_index], updated[new_index] = (
        updated[new_index],
        updated[old_index],
    )
    return updated, True


def cached_protected_outputs(
    cache_entries: Iterable[tuple[Any, HistoryValue]],
    candidates: Iterable[HistoryValue | None],
) -> list[HistoryValue]:
    """Return unique candidate outputs that are still resident in the cache.

    Identity is intentional: two output instances may compare equal while still
    representing distinct maps held by Viewer, A/B or manual-lock roles.
    """

    cached_by_id = {id(value): value for _, value in cache_entries}
    protected: list[HistoryValue] = []
    seen: set[int] = set()
    for value in candidates:
        if value is None:
            continue
        identity = id(value)
        if identity in cached_by_id and identity not in seen:
            protected.append(cached_by_id[identity])
            seen.add(identity)
    return protected
