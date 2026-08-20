from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class GenerationCacheKey:
    seed:int;side:int;players:int;mode:str;archetype:str;modifiers:tuple=();engine_revision:str='v1.5'

class SessionGenerationCache:
    def __init__(self,max_entries:int=8):self.max_entries=max(1,int(max_entries));self._items:OrderedDict[GenerationCacheKey,Any]=OrderedDict()
    def get(self,key):
        value=self._items.get(key)
        if value is not None:self._items.move_to_end(key)
        return value
    def put(self,key,value):
        self._items[key]=value;self._items.move_to_end(key)
        while len(self._items)>self.max_entries:self._items.popitem(last=False)
    def clear(self):self._items.clear()
    def entries(self):return list(reversed(self._items.items()))
    def __len__(self):return len(self._items)
