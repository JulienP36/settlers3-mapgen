import unittest
import numpy as np
from s3mapgen.generation.archetypes.profiles import continental_legacy_blocks_profile, normalize_archetype_profile, RELIEF_SOURCE_OPTIONS
from s3mapgen.generation.archetypes.island_source import generate_island_source
from s3mapgen.generation.custom import build_custom_config

class ContinentalLandmassTests(unittest.TestCase):
    def test_source_is_independent_of_players_and_teams(self):
        profile=continental_legacy_blocks_profile()
        a=generate_island_source(384,2,2026101205,profile,native_relaxation=None,player_teams=(0,0))
        b=generate_island_source(384,12,2026101205,profile,native_relaxation=None,player_teams=(1,)*12)
        self.assertTrue(np.array_equal(a.height,b.height))
        self.assertTrue(np.array_equal(a.source_labels,b.source_labels))
        self.assertIsNone(a.topology_labels)
        self.assertFalse(a.report['preset_features_required'])
        self.assertEqual(a.report['inland_lake_counts_by_island'],[1])

    def test_old_default_source_migrates_once_and_new_preset_has_no_swamp_bonus(self):
        profile=continental_legacy_blocks_profile()
        old=dict(profile);old['morphology']=dict(profile['morphology'],relief_source='legacy_blocks')
        old['relief']=dict(profile['relief'],mountain_threshold=98,snow_threshold=125)
        migrated=normalize_archetype_profile(old)
        self.assertEqual(migrated['morphology']['relief_source'],'continental_landmass')
        self.assertEqual(migrated['relief']['mountain_threshold'],140)
        self.assertEqual(migrated,normalize_archetype_profile(migrated))
        self.assertNotIn('legacy_blocks',RELIEF_SOURCE_OPTIONS)
        self.assertNotIn('start_mini_swamp',build_custom_config('upgraded','continental',archetype_profile=profile).start_packages)

if __name__=='__main__':unittest.main()
