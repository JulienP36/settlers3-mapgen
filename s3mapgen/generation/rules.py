from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ValidationResult:
    rule_id: str
    passed: bool
    message: str
    hard: bool = True

    def label(self):
        return ('PASS' if self.passed else 'FAIL') + f' {self.rule_id}: {self.message}'

PIPELINE_STAGES = (
    'archetype.macro_layout',
    'starts.maximin_early',
    'starts.reserve_zones',
    'hydrology.micro_water_cleanup',
    'hydrology.bathymetry',
    'hydrology.river_cleanup',
    'biomes.start_mini_swamps',
    'biomes.swamp_transitions',
    'snow.summit_rebuild',
    'resources.minerals_v7_nogap',
    'resources.fish_shore_only',
    'objects.decorations',
    'objects.adult_trees',
    'objects.smalltree84',
    'objects.building_stones',
    'accessibility.finalize',
    'validators.hard',
)
