import numpy as np
import math

def avgAllPts(*points):
    return [sum(x)/len(x) for x in zip(*points)]
def avgPts(sourceArr, indexArr):
    arr = [sourceArr[item] for item in indexArr]
    return sum(arr)/len(arr)

def intTuple(arr):
    return tuple(np.array(arr, int))

# some homebrw formula for curving a value between 0 and 1 so it moves faster near 0 and slower near 1
def swingCurve(val):
    if val == 0:
        return 0
    absval = math.fabs(val)
    pol = val/absval
    return ((pol * math.sqrt(absval)) + val*2)/3

def pivotPoint(ptTarget, ptAnchor, rad):
    diff = np.array(ptTarget) - np.array(ptAnchor)
    norm =  np.linalg.norm(diff)
    roll = math.atan2(diff[1], diff[0]) - rad
        
    dx = norm * math.cos(roll)
    dy = norm * math.sin(roll)
    return np.array(ptAnchor) - [dx, dy]