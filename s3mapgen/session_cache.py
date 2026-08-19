from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationCacheKey:
    seed: int
    side: int
    players: int
    mode: str
    archetype: str
    modifiers: tuple[str, ...] = ()
    engine_revision: str = 'v1.5'


class SessionGenerationCache:
    """Small LRU cache that lives only for the lifetime of the GUI process."""

    def __init__(self, max_items: int = 8):
        self.max_items = max(1, int(max_items))
        self._items: OrderedDict[GenerationCacheKey, Any] = OrderedDict()

    def get(self, key: GenerationCacheKey):
        value = self._items.get(key)
        if value is None:
            return None
        self._items.move_to_end(key)
        return value

    def put(self, key: GenerationCacheKey, value: Any) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()

    def entries(self):
        return list(reversed(self._items.items()))

    def __len__(self) -> int:
        return len(self._items)
