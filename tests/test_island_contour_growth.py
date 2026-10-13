"""Behavioral checks for source growth, including the user's narrow-neck seed."""
import unittest
import numpy as np
from s3mapgen.generation.archetypes.large_islands import _growth_arrival_score, build_island_masks
from s3mapgen.map_data.hexgrid import component_labels, distance_from

class ContourGrowthTests(unittest.TestCase):
    def test_remote_low_potential_basin_is_admitted_progressively(self):
        yy,xx=np.indices((65,161))
        score=np.hypot(xx-25,yy-32).astype(np.float32)
        score[:,90:]-=150.
        safe=np.ones(score.shape,dtype=bool)
        arrival=_growth_arrival_score(safe,score,(32,25),60.)
        # Crossing the saddle must not admit all of the far depression together.
        self.assertLess(arrival[32,100],arrival[32,140])
        threshold=float((arrival[32,100]+arrival[32,140])*.5)
        self.assertTrue(arrival[32,100]<threshold)
        self.assertTrue(arrival[32,140]>threshold)
        self.assertEqual(arrival[32,25],0.)
        self.assertTrue(np.isfinite(arrival).all())

    def test_disconnected_territorial_fragment_has_finite_unreachable_rank(self):
        safe=np.zeros((20,30),dtype=bool);safe[1:15,1:10]=True;safe[1:15,20:28]=True
        score=np.zeros(safe.shape,dtype=np.float32)
        arrival=_growth_arrival_score(safe,score,(5,5),8.)
        self.assertTrue(np.isfinite(arrival).all())
        self.assertGreater(arrival[5,23],arrival[safe & (np.indices(safe.shape)[1]<10)].max())

    def test_reported_seed_keeps_proportions_without_a_large_beach_only_appendix(self):
        labels,*_=build_island_masks(768,2,984499091,island_player_counts=[3,9])
        self.assertEqual([int(np.count_nonzero(labels==i)) for i in [1,2]],[100477,301429])
        for i in [1,2]:
            mask=labels==i;self.assertEqual(component_labels(mask)[1],1)
            depth=distance_from(~mask)
            for inset in [1,2,3]:
                core,n=component_labels(mask & (depth>inset))
                sizes=np.sort(np.bincount(core.ravel())[1:])[::-1]
                # The original seed detaches a 5,497-cell appendix at inset 1.
                self.assertTrue(all(v < max(200,int(mask.sum()*.015)) for v in sizes[1:]))

if __name__=='__main__':unittest.main()
