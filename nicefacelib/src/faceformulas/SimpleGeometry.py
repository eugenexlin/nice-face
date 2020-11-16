from nicefacelib.src.utils.DataUtils import *
from nicefacelib.src.utils.MovingAverage import MovingAverage

# here is the simple formulas
# the idea is it doesnt have to be 100# exact with the face, it just needs to approximate the gestures
# and it should end up cute enough

# 1 and 15 are going to mark the middle of the left and right of the face,
# 27 31 35  will be averaged to find the center of the face in a way that partially ignores how deep the nose is.

# so we can use distance of left right and middle nose chin to estimate SCALE FACTOR
# so it can offset the differnce between when you are close or far away from the camera.


class SimpleGeometry:

    def __init__(self, smoothing=3):
        self.CenterHead = MovingAverage(smoothing, 2)
        self.CenterNose = MovingAverage(smoothing, 2)
        pass

    def Next68Coordinates(self, coordinates):
        ptCenterHead = avgPts(coordinates, [0,1,2,14,15,16])
        self.CenterHead.push(ptCenterHead)
        ptCenterNose = avgPts(coordinates, [27,31,35])
        self.CenterNose.push(ptCenterNose)
        pass