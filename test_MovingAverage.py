import sys
from nicefacelib.src.utils import MovingAverage

def test_MovingAverage_1():
    val = MovingAverage.MovingAverage(3)
    assert val.currVal() == 0
    val.push(3)
    assert val.currVal() == 3
    val.push(6)
    assert val.currVal() == 4
    val.push(6)
    assert val.currVal() == 5
    val.push(6)
    assert val.currVal() == 6
    val.push(-6)
    assert val.currVal() == 2
    val.push(-6)
    assert val.currVal() == -2
    val.push(-6)
    assert val.currVal() == -6

def test_MovingAverage_2():
    val = MovingAverage.MovingAverage(5)
    assert val.currVal() == 0
    val.push(5)
    assert val.currVal() == 5
    val.push(0)
    assert val.currVal() == 4
    val.push(0)
    assert val.currVal() == 3
    val.push(0)
    assert val.currVal() == 2
    val.push(0)
    assert val.currVal() == 1
    val.push(0)
    assert val.currVal() == 0

def test_MovingAverage_ForceVal():
    val = MovingAverage.MovingAverage(3)
    assert val.currVal() == 0
    val.push(3)
    assert val.currVal() == 3
    val.push(6)
    assert val.currVal() == 4
    val.forceVal(6)
    assert val.currVal() == 6
    val.push(-6)
    assert val.currVal() == 2
    val.push(-6)
    assert val.currVal() == -2
    val.push(-6)
    assert val.currVal() == -6