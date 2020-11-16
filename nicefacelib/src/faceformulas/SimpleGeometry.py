import numpy as np
import math
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

    FRAME_SCALE_MULTIPLIER = 0.5

    def __init__(self, smoothing=2):
        # raw data that should get smoothing
        self.CenterHead = MovingAverage(smoothing, 2)
        self.CenterNose = MovingAverage(smoothing, 2)
        self.LeftHead = MovingAverage(smoothing, 2)
        self.RightHead = MovingAverage(smoothing, 2)
        self.BottomHead = MovingAverage(smoothing, 2)

        self.LeftEyeCorner = MovingAverage(smoothing, 2)
        self.RightEyeCorner = MovingAverage(smoothing, 2)


        # other data that is derived from smoothed data points
        # thus do not need any more smoothing
        self.HeadRoll = 0.0 # radians
        self.HeadPitch = 0.0 # arbitrary offset (not radians)
        self.HeadYaw = 0.0 # arbitrary offset (not radians)

        

    def Next68Coordinates(self, coordinates):
        # collect raw data points into moving average
        ptCenterHead = avgPts(coordinates, [0,1,2,14,15,16])
        self.CenterHead.push(ptCenterHead)
        ptCenterNose = avgPts(coordinates, [27,31,33,35])
        self.CenterNose.push(ptCenterNose)
        ptLeftHead = avgPts(coordinates, [0,1,2])
        self.LeftHead.push(ptLeftHead)
        ptRightHead = avgPts(coordinates, [14,15,16])
        self.RightHead.push(ptRightHead)
        ptBottomHead = avgPts(coordinates, [7,8,9])
        self.BottomHead.push(ptBottomHead)

        self.LeftEyeCorner.push(coordinates[36])
        self.RightEyeCorner.push(coordinates[45])

        # get the smoothed data point
        currentCenterHead = self.CenterHead.current()
        currentCenterNose = self.CenterNose.current()
        currentLeftHead = self.LeftHead.current()
        currentRightHead = self.RightHead.current()
        currentBottomHead = self.BottomHead.current()

        faceHeight = np.linalg.norm(currentCenterNose-currentBottomHead)
        faceWidth = np.linalg.norm(currentRightHead-currentLeftHead)
        frameScale = (faceHeight + faceWidth) / 2 * self.FRAME_SCALE_MULTIPLIER

        headRollDiff = self.RightEyeCorner.current() - self.LeftEyeCorner.current()
        if (headRollDiff[0] != 0):
            headRoll = math.atan2(headRollDiff[1], headRollDiff[0])
            self.HeadRoll = headRoll

        noseDiff = currentCenterNose - currentCenterHead
        noseNormal =  np.linalg.norm(noseDiff)
        if (noseDiff[0] != 0):
            noseRoll = math.atan2(noseDiff[1], noseDiff[0])
            # offset face tilt to find pitch and yaw
            trueNoseRoll = noseRoll - headRoll
            HeadPitch = noseNormal * math.sin(trueNoseRoll)
            HeadYaw = noseNormal * math.cos(trueNoseRoll)
            self.HeadPitch = HeadPitch / frameScale
            self.HeadYaw = HeadYaw / frameScale
