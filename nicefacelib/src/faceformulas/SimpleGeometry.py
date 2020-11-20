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
        self.Head = MovingAverage(smoothing, 2)
        self.Nose = MovingAverage(smoothing, 2)
        self.NoseTip = MovingAverage(smoothing, 2)

        self.HeadLeft = MovingAverage(smoothing, 2)
        self.HeadRight = MovingAverage(smoothing, 2)
        self.HeadBottom = MovingAverage(smoothing, 2)

        self.EyeLeft = MovingAverage(smoothing, 2)
        self.EyeRight = MovingAverage(smoothing, 2)

        self.MouthTop = MovingAverage(smoothing, 2)
        self.MouthBottom = MovingAverage(smoothing, 2)
        self.MouthLeft = MovingAverage(smoothing, 2)
        self.MouthRight = MovingAverage(smoothing, 2)


        # other data that is derived from smoothed data points
        # thus do not need any more smoothing
        self.HeadRoll = 0.0 # radians
        self.HeadPitch = 0.0 # arbitrary offset (not radians)
        self.HeadYaw = 0.0 # arbitrary offset (not radians)

        self.MouthOpen = 0.0

        self.EyeLeftScale = 0.0
        self.EyeLeftMin = 0.0 #need to decay over time to prevent glitches from ruining the data
        self.EyeLeftMax = 0.0
        self.EyeLeftOpen = 0.0 #linear scaling of how eye value compare to min and max
        self.EyeRightScale = 0.0
        self.EyeRightMin = 0.0
        self.EyeRightMax = 0.0
        self.EyeRightOpen = 0.0

        #track smile based on how close corners of mouth are to eyes i guess
        self.Smile = 0.0

    def Next68Coordinates(self, coordinates):
        # collect raw data points into moving average
        self.Head.push(avgPts(coordinates, [0,1,2,14,15,16]))
        self.Nose.push(avgPts(coordinates, [27,31,33,35]))
        self.NoseTip.push(avgPts(coordinates, [30]))
        self.HeadLeft.push(avgPts(coordinates, [0,1,2]))
        self.HeadRight.push(avgPts(coordinates, [14,15,16]))
        self.HeadBottom.push(avgPts(coordinates, [7,8,9]))

        self.EyeLeft.push(avgPts(coordinates, [37,38,40,41]))
        self.EyeRight.push(avgPts(coordinates, [43,44,46,47]))

        self.MouthTop.push(avgPts(coordinates, [61,62,63]))
        self.MouthBottom.push(avgPts(coordinates, [65,66,67]))
        self.MouthLeft.push(coordinates[48])
        self.MouthRight.push(coordinates[54])

        # get the smoothed data point
        currentHead = self.Head.current()
        currentNose = self.Nose.current()
        currentNoseTip = self.NoseTip.current()
        currentHeadLeft = self.HeadLeft.current()
        currentHeadRight = self.HeadRight.current()
        currentHeadBottom = self.HeadBottom.current()

        currentEyeLeft = self.EyeLeft.current()
        currentEyeRight = self.EyeRight.current()

        currentMouthTop = self.MouthTop.current()
        currentMouthBottom = self.MouthBottom.current()
        currentMouthLeft = self.MouthLeft.current()
        currentMouthRight = self.MouthRight.current()

        faceHeight = np.linalg.norm(currentNose-currentHeadBottom)
        faceWidth = np.linalg.norm(currentHeadRight-currentHeadLeft)
        frameScale = (faceHeight + faceWidth) / 2 * self.FRAME_SCALE_MULTIPLIER

        headRollDiff = self.EyeRight.current() - self.EyeLeft.current()
        if (headRollDiff[0] != 0):
            headRoll = math.atan2(headRollDiff[1], headRollDiff[0])
            self.HeadRoll = headRoll

        noseDiff = currentNoseTip - currentHead
        noseNormal =  np.linalg.norm(noseDiff)
        noseRoll = math.atan2(noseDiff[1], noseDiff[0])
        # offset face tilt to find pitch and yaw
        trueNoseRoll = noseRoll - headRoll
        HeadPitch = noseNormal * math.sin(trueNoseRoll)
        HeadYaw = noseNormal * math.cos(trueNoseRoll)
        self.HeadPitch = HeadPitch / frameScale
        self.HeadYaw = HeadYaw / frameScale

        # track mouth openness
        mouthVerticalNormal =  np.linalg.norm(currentMouthBottom-currentMouthTop)
        self.MouthOpen = (mouthVerticalNormal * 2) / frameScale

        eyeMid = avgAllPts(currentEyeLeft, currentEyeRight) 
        mouthMid = avgAllPts(currentMouthTop, currentMouthBottom) 

        distanceMouthMid = np.linalg.norm(eyeMid - mouthMid)
        distanceMouthLeft = np.linalg.norm(currentEyeLeft - currentMouthLeft)
        distanceMouthRight = np.linalg.norm(currentEyeRight - currentMouthRight)
        distanceMouthEdge = (distanceMouthLeft + distanceMouthRight) / 2
        self.Smile = (distanceMouthEdge - distanceMouthMid) * -5 / frameScale

        # track eyeopenness
        eyeLeftTop = avgPts(coordinates, [37,38])
        eyeLeftBottom = avgPts(coordinates, [40,41])
        eyeRightTop = avgPts(coordinates, [43,44])
        eyeRightBottom = avgPts(coordinates, [46,47])

        eyeLeftWidth = np.linalg.norm(coordinates[36] - coordinates[39]) 
        eyeRightWidth = np.linalg.norm(coordinates[42] - coordinates[45]) 
        
        eyeLeftDist = np.linalg.norm(eyeLeftTop - eyeLeftBottom) / eyeLeftWidth
        eyeRightDist = np.linalg.norm(eyeRightTop - eyeRightBottom) / eyeRightWidth

        #decay to autocorreect video glitches messing up max and min
        self.EyeLeftMin = ratioDecay(self.EyeLeftMin,eyeLeftDist, 500)
        self.EyeLeftMax = ratioDecay(self.EyeLeftMax,eyeLeftDist, 500)
        self.EyeRightMin = ratioDecay(self.EyeRightMin,eyeRightDist, 500)
        self.EyeRightMax = ratioDecay(self.EyeRightMax,eyeRightDist, 500)

        self.EyeLeftMin = min(self.EyeLeftMin, eyeLeftDist)
        self.EyeLeftMax = max(self.EyeLeftMax, eyeLeftDist)
        self.EyeRightMin = min(self.EyeRightMin, eyeRightDist)
        self.EyeRightMax = max(self.EyeRightMax, eyeRightDist)
        
        #add magic negligible amount to avoid divide by zero
        eyeLeftHowClosed = max((eyeLeftDist - self.EyeLeftMin), 0.01)
        eyeLeftHowOpened = max((self.EyeLeftMax - eyeLeftDist), 0.01)
        self.EyeLeftOpen = eyeLeftHowClosed / (eyeLeftHowClosed + eyeLeftHowOpened)
        eyeRightHowClosed = max((eyeRightDist - self.EyeRightMin), 0.01)
        eyeRightHowOpened = max((self.EyeRightMax - eyeRightDist), 0.01)
        self.EyeRightOpen = eyeRightHowClosed / (eyeRightHowClosed + eyeRightHowOpened)

