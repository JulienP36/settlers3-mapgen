import unittest
import numpy as np
from s3mapgen.generation.river_policy import ImprovedRiverPolicy
from s3mapgen.generation.generators.legacy import native_terrain as legacy
from s3mapgen.generation.generators.upgraded import native_terrain as upgraded

class RiverTieBreakingTests(unittest.TestCase):
    def test_seeded_ranking_is_repeatable_and_independent_of_candidate_order(self):
        terrain=np.full((64,64),16,dtype=np.uint8)
        winners=[]
        for seed in range(256):
            p=ImprovedRiverPolicy(terrain,seed=seed)
            a=p.choose_tied_direction([1,2,3,4,5,6],32,32,phase=7)
            self.assertEqual(a,p.choose_tied_direction([6,4,2,5,3,1],32,32,phase=7))
            self.assertEqual(p.choose_tied_direction([4],32,32),4)
            winners.append(a)
        self.assertEqual(set(winners),{1,2,3,4,5,6})

    def test_native_ties_and_strictly_better_heights_are_preserved_in_both_engines(self):
        for engine in [legacy,upgraded]:
            with self.subTest(engine=engine.__name__):
                grid=engine.NativeTerrainGrid.empty(64);grid.terrain[:]=16;grid.height[:]=5;grid.marker[:]=0
                rng=engine.NativeRng16(71);before=(rng.a,rng.b,rng.c)
                policy=ImprovedRiverPolicy(grid.terrain,seed=71)
                self.assertEqual(engine._choose_first_river_step(grid,32,32,False),1)
                for seed in range(10):
                    policy.tie_seed=seed
                    dr,dc=engine.HEX6[4];grid.height[32+dr,32+dc]=15
                    self.assertEqual(engine._choose_first_river_step(grid,32,32,False,tie_policy=policy),5)
                    grid.height[32+dr,32+dc]=5
                self.assertEqual((rng.a,rng.b,rng.c),before)
                allowed=np.zeros((64,64),dtype=bool);dr,dc=engine.HEX6[5];allowed[32+dr,32+dc]=True
                self.assertEqual(engine._choose_first_river_step(grid,32,32,False,allowed_mask=allowed,tie_policy=policy),6)

if __name__=='__main__':unittest.main()
