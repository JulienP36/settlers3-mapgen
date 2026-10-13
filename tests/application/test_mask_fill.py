import numpy as np
from s3mapgen.application.custom.mask_library import MaskDrawing


def test_fill_respects_boundaries_diagonals_gray_and_history():
    grid=np.array([[12,12,90,12],[12,90,12,12],[90,12,12,90],[12,90,90,12]],dtype=np.uint8)
    drawing=MaskDrawing(grid)
    assert drawing.fill(0,0,150)
    expected=grid.copy();expected[0,:2]=150;expected[1,0]=150
    assert np.array_equal(drawing.grid,expected)
    assert len(drawing.undo_stack)==1
    drawing.undo();assert np.array_equal(drawing.grid,grid)
    drawing.redo();assert np.array_equal(drawing.grid,expected)
    assert not drawing.fill(0,0,150)
    assert not drawing.fill(-1,0,80)
    assert len(drawing.undo_stack)==1


def test_large_fill_and_rotation_direction_are_reversible():
    drawing=MaskDrawing(np.zeros((512,512),dtype=np.uint8))
    assert drawing.fill(511,511,127)
    assert np.all(drawing.grid==127)
    drawing.undo();assert not drawing.grid.any()
    grid=np.array([[0,1],[2,3]],dtype=np.uint8)
    drawing=MaskDrawing(grid)
    drawing.replace(np.rot90(drawing.grid));assert drawing.grid.tolist()==[[1,3],[0,2]]
    drawing.replace(np.rot90(drawing.grid,-1));assert np.array_equal(drawing.grid,grid)
    drawing.undo();assert drawing.grid.tolist()==[[1,3],[0,2]]
