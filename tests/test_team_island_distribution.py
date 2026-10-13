"""R57: usable interior water and resource access without teammate packing."""
import itertools
import unittest
import numpy as np
from s3mapgen.generation.archetypes.large_islands import _island_lakes, place_island_starts
from s3mapgen.generation.start_safety import validate_start_safety
from s3mapgen.map_data.hexgrid import component_labels, distance_from
from s3mapgen.map_data.model import MapState

class TeamIslandDistributionTests(unittest.TestCase):
    def test_small_interior_basins_are_separate_and_use_less_water(self):
        yy, xx = np.indices((500, 500))
        island = (xx - 250)**2 + (yy - 250)**2 <= 220**2
        depth = distance_from(~island)
        signal = np.zeros(island.sum(), dtype=np.float32)
        def flat(x, y, wavelength, seed):
            return np.zeros(np.asarray(x).shape, dtype=np.float32)
        lakes, count, cells = _island_lakes(island, depth, signal, 2026101015, flat)
        old, old_count, old_cells = _island_lakes(island, depth, signal, 2026101015, flat, distributed=False)
        self.assertGreater(count, old_count)
        self.assertLess(cells / count, old_cells / old_count)
        self.assertEqual(component_labels(lakes)[1], count)
        self.assertTrue(np.all(island[lakes]))
        self.assertGreaterEqual(depth[lakes].min(), .35 * depth[island].max())
        self.assertEqual(component_labels(island & ~lakes)[1], 1)

    def test_teammates_spread_along_resource_fronts_without_changing_terrain(self):
        for player_count in (3, 4):
            with self.subTest(players=player_count):
                state = MapState.empty(256)
                labels = np.zeros((256,256),dtype=np.int16)
                labels[16:240,16:240] = 1
                state.terrain[labels>0] = 16
                state.terrain[40:216,75:79] = 17
                state.terrain[40:216,131:135] = 96
                state.metadata.update(players=player_count,large_island_topology={
                    'team_islands':True,'requested_islands':1,
                    'player_island_labels':[1]*player_count,'preset_features_required':False,
                },large_island_features=[{'island':1}])
                original=state.area.copy()
                place_island_starts(state,player_count,np.random.default_rng(7),labels,14)
                self.assertEqual(len(state.starts),player_count)
                self.assertTrue(np.array_equal(state.area,original))
                nearest=min(np.hypot(a[0]-b[0],a[1]-b[1]) for a,b in itertools.combinations(state.starts,2))
                self.assertGreaterEqual(nearest,65. if player_count == 3 else 50.)
                self.assertTrue(all(v.passed for v in validate_start_safety(state)))
                report=state.metadata['island_start_search']
                for row in report['selected_by_player']:
                    self.assertLessEqual(max(row['mountain_distance_hex'],row['river_distance_hex']),38)
                if player_count == 4:
                    self.assertEqual(report['resource_guard_islands'], [1])

if __name__=='__main__':
    unittest.main()
