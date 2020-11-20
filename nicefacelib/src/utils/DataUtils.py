import numpy as np
import math

def avgAllPts(*points):
    return np.array([sum(x)/len(x) for x in zip(*points)])
def avgPts(sourceArr, indexArr):
    arr = [sourceArr[item] for item in indexArr]
    return sum(arr)/len(arr)

def selectSubset(sourceArr, indexArr, type=float):
    return np.array([sourceArr[item] for item in indexArr], type)

# find max and min of both x and y of every point. e.g. find the min x y (no rotation) rectangle that contains all points
def getRekt(arr):
    if len(arr) <= 0:
        return np.array([[0,0],[1,1]])
    
    point = arr[0]
    minX = point[0]
    minY = point[1]
    maxX = point[0]
    maxY = point[1]
    for point in arr:
        minX = min(minX, point[0])
        minY= min(minY, point[1])
        maxX = max(maxX, point[0])
        maxY = max(maxY, point[1])

    maxX = max(maxX, minX+1)
    maxY = max(maxY, minY+1)
    
    return np.array([[minX,minY],[maxX,maxY]])

def getSubFrame(frame, rekt):
    return frame[rekt[0][1]: rekt[1][1], rekt[0][0]: rekt[1][0]]
def setSubFrame(frame, pt, data):
    frame[pt[1]: pt[1] + data.shape[0],  pt[0]: (pt[0] + data.shape[1])] = data

def intTuple(arr):
    return tuple(np.array(arr, int))

# ratio is how many times heavier the target value is to the source 
def ratioDecay(targetVal, destinationVal, ratio):
    return ((targetVal*ratio) + destinationVal)/(ratio + 1)

# some homebrw formula for curving a value between 0 and 1 so it moves faster near 0 and slower near 1
def swingCurve(val):
    if val == 0:
        return 0
    absval = math.fabs(val)
    pol = val/absval
    return pol * (math.sqrt(absval) + math.fabs(val)*2)/3

def pivotPoint(ptTarget, ptAnchor, rad):
    diff = np.array(ptAnchor) - np.array(ptTarget)
    norm =  np.linalg.norm(diff)
    roll = math.atan2(diff[1], diff[0]) - rad
        
    dx = norm * math.cos(roll)
    dy = norm * math.sin(roll)
    return np.array(ptAnchor) - [dx, dy]