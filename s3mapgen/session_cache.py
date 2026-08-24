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
    modifiers: tuple = ()
    engine_revision: str = 'v1.5'

@dataclass(frozen=True)
class ImportedHistoryKey:
    """Stable identity for an imported source, independent from its path."""
    digest: str
    source_format: str

class SessionGenerationCache:
    def __init__(self, max_entries: int = 8):
        self.max_entries = max(1, int(max_entries))
        self._items: OrderedDict[Any, Any] = OrderedDict()
        self._metadata: dict[Any, dict[str, Any]] = {}
        self._protected_provider = None
    def set_protected_provider(self,provider): self._protected_provider=provider
    def _protected_ids(self):
        if self._protected_provider is None:return set()
        try:return {id(value) for value in self._protected_provider() if value is not None}
        except Exception:return set()
    def _trim(self):
        while len(self._items)>self.max_entries:
            protected=self._protected_ids();victim=next((key for key,value in self._items.items() if id(value) not in protected),None)
            if victim is None:break
            self._items.pop(victim,None);self._metadata.pop(victim,None)
    def get(self, key):
        value = self._items.get(key)
        if value is not None:
            self._items.move_to_end(key)
        return value
    def peek(self,key): return self._items.get(key)
    def put(self, key, value, metadata=None):
        self._items[key] = value; self._items.move_to_end(key)
        if metadata is not None:
            self._metadata[key] = dict(metadata)
        self._trim()
    def metadata(self,key): return dict(self._metadata.get(key,{}))
    def set_metadata(self,key,metadata):
        if key in self._items:self._metadata[key]=dict(metadata)
    def remove(self,key):
        value=self._items.pop(key,None);self._metadata.pop(key,None);return value
    def resize(self,max_entries):
        self.max_entries=max(1,int(max_entries));self._trim()
    def clear(self): self._items.clear();self._metadata.clear()
    def entries(self): return list(reversed(self._items.items()))
    def __len__(self): return len(self._items)


class SessionStatsCache:
    """Small session-only LRU for derived map statistics.

    Keys are state identities rather than generation parameters so the same cache
    also accelerates imported EDM/MAP/SAV files and A/B slot toggles.  Keeping a
    strong state reference beside the id prevents accidental id reuse.
    """
    def __init__(self, max_entries: int = 12):
        self.max_entries = max(1, int(max_entries))
        self._items: OrderedDict[int, tuple[Any, Any]] = OrderedDict()

    def get(self, state):
        key = id(state)
        item = self._items.get(key)
        if item is None or item[0] is not state:
            return None
        self._items.move_to_end(key)
        return item[1]

    def put(self, state, stats):
        key = id(state)
        self._items[key] = (state, stats)
        self._items.move_to_end(key)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    def clear(self):
        self._items.clear()

    def __len__(self):
        return len(self._items)
