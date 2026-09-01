from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationCacheKey:
    seed: int
    side: int
    players: int
    mode: str
    archetype: str
    modifiers: tuple = ()
    engine_revision: str = "v2.0-dev2-upgraded-only"


@dataclass(frozen=True)
class ImportedHistoryKey:
    """Stable identity for an imported source, independent from its path."""

    digest: str
    source_format: str


class SessionGenerationCache:
    """Session-only LRU cache with caller-defined protected outputs.

    The cache owns eviction order and metadata. The GUI owns protection roles
    (Viewer, comparison slots and manual locks) and exposes their current values
    through ``set_protected_provider``. Capacity is always a hard upper bound:
    when every existing value is protected, a newly inserted fallback value is
    rejected instead of creating a hidden overflow entry.
    """

    def __init__(self, max_entries: int = 8):
        self.max_entries = max(1, int(max_entries))
        self._items: OrderedDict[Any, Any] = OrderedDict()
        self._metadata: dict[Any, dict[str, Any]] = {}
        self._protected_provider: Callable[[], Iterable[Any]] | None = None

    def set_protected_provider(
        self,
        provider: Callable[[], Iterable[Any]] | None,
    ) -> None:
        self._protected_provider = provider

    def _protected_ids(self) -> set[int]:
        if self._protected_provider is None:
            return set()
        try:
            return {
                id(value)
                for value in self._protected_provider()
                if value is not None
            }
        except Exception:
            # Tk-owned providers may be queried while their window is closing.
            # Cache trimming must remain safe even if that UI state disappears.
            return set()

    def _trim(self, fallback_key: Any = None) -> None:
        while len(self._items) > self.max_entries:
            protected = self._protected_ids()
            victim = next(
                (
                    key
                    for key, value in self._items.items()
                    if id(value) not in protected
                ),
                None,
            )

            # A newly displayed result is protected by the Viewer role before
            # insertion. If every older entry is protected, reject that result
            # from history instead of silently growing beyond capacity.
            if victim is None and fallback_key in self._items:
                victim = fallback_key

            # Keep max_entries a hard invariant even if a non-UI caller bypasses
            # the rule that prevents resizing below the protected-map count.
            if victim is None:
                victim = next(iter(self._items), None)
            if victim is None:
                break

            self._items.pop(victim, None)
            self._metadata.pop(victim, None)

    def get(self, key: Any) -> Any:
        value = self._items.get(key)
        if value is not None:
            self._items.move_to_end(key)
        return value

    def peek(self, key: Any) -> Any:
        """Return a cached value without changing its LRU position."""

        return self._items.get(key)

    def put(self, key: Any, value: Any, metadata: dict | None = None) -> bool:
        """Insert a value and report whether it remains in the hard-cap cache."""

        is_new = key not in self._items
        self._items[key] = value
        self._items.move_to_end(key)
        if metadata is not None:
            self._metadata[key] = dict(metadata)
        self._trim(fallback_key=key if is_new else None)
        return key in self._items

    def metadata(self, key: Any) -> dict[str, Any]:
        return dict(self._metadata.get(key, {}))

    def set_metadata(self, key: Any, metadata: dict) -> None:
        if key in self._items:
            self._metadata[key] = dict(metadata)

    def remove(self, key: Any) -> Any:
        value = self._items.pop(key, None)
        self._metadata.pop(key, None)
        return value

    def resize(self, max_entries: int) -> None:
        self.max_entries = max(1, int(max_entries))
        self._trim()

    def clear(self) -> None:
        self._items.clear()
        self._metadata.clear()

    def entries(self) -> list[tuple[Any, Any]]:
        """Return newest-to-oldest entries without changing LRU recency."""

        return list(reversed(self._items.items()))

    def __len__(self) -> int:
        return len(self._items)


class SessionStatsCache:
    """Small session-only LRU for derived map statistics.

    Keys are state identities rather than generation parameters so the same
    cache also accelerates imported EDM/MAP/SAV files and A/B slot toggles.
    Keeping a strong state reference beside the id prevents accidental id reuse.
    """

    def __init__(self, max_entries: int = 12):
        self.max_entries = max(1, int(max_entries))
        self._items: OrderedDict[int, tuple[Any, Any]] = OrderedDict()

    def get(self, state: Any) -> Any:
        key = id(state)
        item = self._items.get(key)
        if item is None or item[0] is not state:
            return None
        self._items.move_to_end(key)
        return item[1]

    def put(self, state: Any, stats: Any) -> None:
        key = id(state)
        self._items[key] = (state, stats)
        self._items.move_to_end(key)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
