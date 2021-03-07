import sys
import numpy as np
from nicefacelib.src.utils import MovingAverage

def test_MovingAverage_1():
    val = MovingAverage.MovingAverage(3)
    assert val.current() == 0
    val.push(3)
    assert val.current() == 3
    val.push(6)
    assert val.current() == 4
    val.push(6)
    assert val.current() == 5
    val.push(6)
    assert val.current() == 6
    val.push(-6)
    assert val.current() == 2
    val.push(-6)
    assert val.current() == -2
    val.push(-6)
    assert val.current() == -6

def test_MovingAverage_2():
    val = MovingAverage.MovingAverage(5)
    assert val.current() == 0
    val.push(5)
    assert val.current() == 5
    val.push(0)
    assert val.current() == 4
    val.push(0)
    assert val.current() == 3
    val.push(0)
    assert val.current() == 2
    val.push(0)
    assert val.current() == 1
    val.push(0)
    assert val.current() == 0

def test_MovingAverage_ForceVal():
    val = MovingAverage.MovingAverage(3)
    assert val.current() == 0
    val.push(3)
    assert val.current() == 3
    val.push(6)
    assert val.current() == 4
    val.forceVal(6)
    assert val.current() == 6
    val.push(-6)
    assert val.current() == 2
    val.push(-6)
    assert val.current() == -2
    val.push(-6)
    assert val.current() == -6

def test_MovingAverage_TestArr():
    val = MovingAverage.MovingAverage(3,2)
    val.forceVal([0,0])
    np.testing.assert_array_equal( val.current() , [0,0])
    val.push([3,6])
    np.testing.assert_array_equal( val.current() , [1,2])
    val.push([3,6])
    np.testing.assert_array_equal( val.current() , [2,4])
    val.push([3,6])
    np.testing.assert_array_equal( val.current() , [3,6])
    
def test_MovingAverage_TestTuple():
    val = MovingAverage.MovingAverage(3,2)
    val.forceVal((0,0))
    np.testing.assert_array_equal( val.current() , (0,0))
    val.push((3,6))
    np.testing.assert_array_equal( val.current() , (1,2))
    val.push((3,6))
    np.testing.assert_array_equal( val.current() , (2,4))
    val.push((3,6))
    np.testing.assert_array_equal( val.current() , (3,6))

def test_MovingAverage_TestFloat():
    val = MovingAverage.MovingAverage(5,2)
    val.forceVal([0.0,0.0])
    np.testing.assert_array_equal( val.current() , [0.0,0.0])
    val.push([1,2])
    np.testing.assert_array_equal( val.current() , [0.2,0.4])
    val.push([1,2])
    np.testing.assert_array_equal( val.current() , [0.4,0.8])
    val.push([1,2])
    np.testing.assert_array_equal( val.current() , [0.6,1.2])
def test_MovingAverage_TestArr2():
    val = MovingAverage.MovingAverage(3,2)
    val.push([3,6])
    np.testing.assert_array_equal( val.current() , [3,6])
    val.push([0,0])
    np.testing.assert_array_equal( val.current() , [2,4])
    val.push([0,0])
    np.testing.assert_array_equal( val.current() , [1,2])