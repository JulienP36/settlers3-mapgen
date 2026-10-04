"""Named-profile defaults and the single visible island-swamp generation path."""
import pytest
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig
from s3mapgen.generation.archetypes import continental_legacy_blocks_profile
from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator

@pytest.mark.parametrize('mode', ['legacy', 'upgraded'])
def test_named_defaults_and_explicit_choices(mode):
    classic = build_custom_config(mode)
    continental = build_custom_config(mode, archetype_profile=continental_legacy_blocks_profile())
    islands = build_custom_config(mode, 'large_islands')
    assert classic.semantic_sections()['rivers']['algorithm'] == 'native'
    assert continental.semantic_sections()['rivers']['algorithm'] == 'improved'
    assert islands.semantic_sections()['rivers']['algorithm'] == 'improved'
    assert islands.start_packages == ('start_mini_swamp',)
    assert classic.start_packages == continental.start_packages == ()
    off = islands.with_start_packages(())
    sections = off.semantic_sections()
    sections['rivers']['algorithm'] = 'native'
    off = off.with_sections(sections)
    restored = CustomGenerationConfig.from_dict(off.to_dict())
    assert restored.start_packages == ()
    assert restored.semantic_sections()['rivers']['algorithm'] == 'native'
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = islands
    assert not controller._custom_section_is_modified('start_bonus')
    controller._custom_config = off
    assert controller._custom_section_is_modified('start_bonus')

@pytest.mark.parametrize('mode', ['legacy', 'upgraded'])
@pytest.mark.parametrize('bonus', ['preset', 'custom', 'off'])
def test_island_bonus_uses_only_visible_configured_path(mode, bonus, monkeypatch):
    from s3mapgen.generation.generators.upgraded.content import UpgradedContent
    from s3mapgen.generation.archetypes import large_islands
    def forbidden(*args, **kwargs):
        pytest.fail('Hidden island mini-swamp path was called')
    monkeypatch.setattr(large_islands, 'ensure_island_swamp_spawns', forbidden, raising=False)
    monkeypatch.setattr(UpgradedContent, 'place_required_start_swamp', forbidden, raising=False)
    calls = []
    original = UpgradedContent._place_start_mini_swamps
    def observe(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        meta = args[0].metadata['upgraded_start_mini_swamps']
        if meta.get('enabled'):
            calls.append(dict(meta))
        return result
    monkeypatch.setattr(UpgradedContent, '_place_start_mini_swamps', observe)
    config = None
    if bonus != 'preset':
        config = build_custom_config(mode, 'large_islands')
        if bonus == 'off':
            config = config.with_start_packages(())
        else:
            sections = config.semantic_sections()
            sections['start_bonus']['mini_swamp'].update(shape='hexagon', radius=2)
            config = config.with_sections(sections)
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        4, 2026093004, mode=mode if config is None else 'custom',
        archetype='large_islands', side=384, custom_config=config,
    )
    assert all(v.passed for v in result.validations if v.hard), result.validations
    assert 'large_island_swamp_spawns' not in result.state.metadata
    if bonus == 'off':
        assert calls == []
        assert not any(v.rule_id == 'ISLAND_SWAMPS' for v in result.validations)
    else:
        assert len(calls) == 1
        assert calls[0]['starts_with_bonus'] == 4
        assert result.state.metadata['upgraded_start_mini_swamps'] == calls[0]
        if bonus == 'custom':
            assert calls[0]['radius'] == 2
            assert calls[0]['shape'] == 'hexagon'
