"""Detached opening settings shared by seed/variant experiments in one batch."""
from copy import deepcopy
from dataclasses import dataclass

from ...generation.custom.config import CustomGenerationConfig, build_custom_config
from ...generation.archetypes.profiles import default_archetype_profile, continental_landmass_profile


STANDARD_ARCHETYPES = ('classic', 'continental', 'large_islands', 'team_islands')


@dataclass(frozen=True)
class BatchContext:
    mode: str
    archetype_choice: str
    _payload: dict
    nations: tuple
    teams: tuple
    random_team_count: int

    def __post_init__(self):
        object.__setattr__(self, '_payload', deepcopy(self._payload))
        object.__setattr__(self, 'nations', tuple((list(self.nations) + [255]*20)[:20]))
        object.__setattr__(self, 'teams', tuple((list(self.teams) + [0]*20)[:20]))

    @property
    def modes(self):
        return ('legacy', 'upgraded') + (('custom',) if self.mode == 'custom' else ())

    @property
    def archetypes(self):
        return STANDARD_ARCHETYPES + (('edited',) if self.archetype_choice == 'edited' else ())

    def resolve(self, mode, choice):
        if mode not in self.modes or choice not in self.archetypes:
            raise ValueError('Selection unavailable in this batch context')
        saved = CustomGenerationConfig.from_dict(self._payload)
        if choice == 'edited':
            archetype, profile = saved.base_archetype, saved.archetype_profile
        else:
            archetype = choice if choice in ('large_islands', 'team_islands') else 'continental'
            profile = (continental_landmass_profile() if choice == 'continental'
                       else default_archetype_profile(archetype))
        if mode == 'custom':
            config = saved.with_archetype_profile(profile, base_archetype=archetype)
        else:
            config = build_custom_config(mode, archetype, archetype_profile=profile)
        return archetype, config
