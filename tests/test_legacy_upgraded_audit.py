import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from s3mapgen.app_paths import LEGACY_PROFILE, UPGRADED_PROFILE


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def test_audited_profiles_are_explicitly_separate():
    legacy = load(LEGACY_PROFILE)
    upgraded = load(UPGRADED_PROFILE)
    assert legacy['profile_kind'] == 'legacy'
    assert upgraded['profile_kind'] == 'upgraded'


def test_hydrology_split_is_locked():
    legacy = load(LEGACY_PROFILE)
    upgraded = load(UPGRADED_PROFILE)
    assert legacy['water']['cleanup_micro_water'] is False
    assert legacy['water']['forbid_inland_components_leq'] == 0
    assert legacy['river']['apply_practical_trim'] is False
    assert upgraded['water']['cleanup_micro_water'] is True
    assert upgraded['water']['forbid_inland_components_leq'] == 4
    assert upgraded['river']['apply_practical_trim'] is True
    assert upgraded['river']['p99_scale_slope'] == 0.0245
    assert upgraded['river']['p99_scale_intercept'] == 34.7


def test_tree_pool_and_upgraded_bonus_are_locked():
    legacy = load(LEGACY_PROFILE)
    upgraded = load(UPGRADED_PROFILE)
    native_pool = [68,69,70,71,72,73,74,75,76,77,80,81]
    assert legacy['trees']['adult_ids'] == native_pool
    assert upgraded['trees']['adult_ids'] == native_pool
    assert legacy['trees']['small_tree_target'] == 0
    assert upgraded['trees']['small_tree_target'] > 0
    assert upgraded['trees']['adult_global_target'] > legacy['trees']['adult_global_target']
    assert legacy['trees']['palm_target'] > 0
    assert upgraded['trees']['palm_target'] > 0


def test_stone_and_decoration_split_is_locked():
    legacy = load(LEGACY_PROFILE)
    upgraded = load(UPGRADED_PROFILE)
    assert legacy['building_stones']['global_stock_target'] == 10892
    assert upgraded['building_stones']['global_stock_target'] == 14160
    assert legacy['building_stones']['start_bonus_units'] == []
    assert upgraded['building_stones']['start_bonus_units']
    assert legacy['decor']['reef_target'] == 0
    assert upgraded['decor']['reef_target'] > 0
    assert legacy['decor']['decorative_stone_target'] == 886
    assert upgraded['decor']['decorative_stone_target'] == 89
    assert legacy['decor']['swamp_target'] == upgraded['decor']['swamp_target']
    assert legacy['decor']['desert_target'] == upgraded['decor']['desert_target']


def test_upgraded_mineral_baseline_is_not_legacy_baseline():
    legacy = load(LEGACY_PROFILE)
    upgraded = load(UPGRADED_PROFILE)
    assert upgraded['minerals']['rocky_accessible_occupancy_target'] == 0.90
    assert legacy['minerals']['rocky_accessible_occupancy_target'] != upgraded['minerals']['rocky_accessible_occupancy_target']
    shares = upgraded['minerals']['shares']
    assert abs(sum(shares.values()) - 1.0) < 1e-4
    assert shares == {
        '16': 0.50186,
        '32': 0.21564,
        '48': 0.14417,
        '64': 0.05446,
        '80': 0.08388,
    }
