import sys
import numpy as np
from nicefacelib.src.utils.DataUtils import *

def test_AvgPoint_2Dim1():
    np.testing.assert_array_equal(avgAllPts([0,0],[0,2],[0,4]), [0,2])

def test_AvgPoint_2Dim2():
    np.testing.assert_array_equal( avgAllPts([3,0],[4,2],[5,4]), [4,2])

def test_AvgPoint_1Dim():
    np.testing.assert_array_equal( avgAllPts([9],[4],[5]) , [6])
    np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, avgAllPts([9],[4],[5]), [5])

def test_AvgPoint_3Dim():
    np.testing.assert_array_equal( avgAllPts([3,3,3],[6,6,6],[9,9,9],[12,12,12],[15,15,15]) , [9,9,9])
    np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, avgAllPts([3,3,3],[6,6,6],[9,9,9],[12,12,12],[15,15,15]), [9,1,1])

def test_AvgPoint_2DMatrix():
    data = [
        [1,1,1],
        [2,2,2],
        [3,3,3]
    ]
    np.testing.assert_array_equal( avgAllPts(*data), [2,2,2])
    np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, avgAllPts(*data), [2,1,2])

def test_AvgPoint_npNDArray():
    data = np.zeros((2, 2), float)
    data.fill(5)
    assert np.all(data==5)
    np.testing.assert_array_equal( avgAllPts(*data), [5,5])

def test_AvgPoint_IndexAddress():
    data = np.array(range(1, 50), float)
    data = data - 1
    assert data[0] == 0
    assert data[40] == 40
    assert avgPts(data, [12,14,34]) == 20