"""Shared six-channel byte-array representation for generated and imported maps."""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

@dataclass
class MapState:
    side: int
    area: np.ndarray
    starts: list[tuple[int,int]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @classmethod
    def empty(cls, side:int):
        area=np.zeros((side,side,6),np.uint8)
        area[:,:,3]=255
        return cls(side,area)

    @property
    def height(self): return self.area[:,:,0]
    @property
    def terrain(self): return self.area[:,:,1]
    @property
    def objects(self): return self.area[:,:,2]
    @property
    def claim(self): return self.area[:,:,3]
    @property
    def accessibility(self): return self.area[:,:,4]
    @property
    def resources(self): return self.area[:,:,5]
