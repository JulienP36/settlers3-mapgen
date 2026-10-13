import unittest
import numpy as np
from s3mapgen.generation.archetypes.large_islands import _spread_team_arrangement

class TeamSpacingRefinementTests(unittest.TestCase):
    def test_full_team_can_escape_a_close_pair_with_comparable_resources(self):
        points=np.array([[0,0],[50,0],[100,0],[200,0],[350,0]],dtype=np.int64)
        maximum=np.array([10,10,10,12,50]);total=maximum*2
        result=_spread_team_arrangement(points,maximum,total,[0,1,2],[0,1,2],[],100.)
        selected=points[result]
        self.assertNotIn(4,result) # Farther but poor resource access is excluded.
        distance=np.hypot(selected[:,None,0]-selected[None,:,0],selected[:,None,1]-selected[None,:,1])
        np.fill_diagonal(distance,np.inf)
        self.assertGreaterEqual(distance.min(),100.)

    def test_close_pair_remains_legal_when_no_better_arrangement_exists(self):
        points=np.array([[0,0],[50,0],[100,0]],dtype=np.int64)
        maximum=np.full(3,10);total=maximum*2
        self.assertEqual(_spread_team_arrangement(points,maximum,total,[0,1,2],[0,1,2],[],100.),[0,1,2])

if __name__=='__main__':unittest.main()
