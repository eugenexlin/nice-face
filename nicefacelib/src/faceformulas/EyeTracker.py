import numpy as np
import cv2
import math
from nicefacelib.src.utils.DataUtils import *
from nicefacelib.src.utils.MovingAverage import MovingAverage

class EyeTracker:

    # if you have downward eyelashes, you may notice the landmark detector making your top eye lid too low.
    # provide a number that is a multiplier to the eye width that is offset to the eye on the top 4 landmarks
    # along the perpendicular of the eye
    # give something like 0.1??
    paddingTopRatio = 0.0
    
    def __init__(self, smoothing=2, paddingTopRatio=0.0):
        # raw data that should get smoothing
        self.Head = MovingAverage(smoothing, 2)
        self.paddingTopRatio = paddingTopRatio

    def CreateMask(self, frame, coordinates):
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask = self.DrawEyeToMask(mask, coordinates)
        return mask

    def DrawEyeToMask(self, mask, points):
        points = np.array(points, dtype=np.int32)
        mask = cv2.fillConvexPoly(mask, points, 255)
        return mask

    # func() => (x,y) , workframe
    def ProcessEye(self, frame, points):
        # add extra points if paddign is on
        if self.paddingTopRatio > 0:
            horizDiff = points[3]-points[0]
            eyeNormal = math.atan2(horizDiff[1], horizDiff[0]) - (math.pi / 2)
            paddingScalar = np.linalg.norm(horizDiff) * self.paddingTopRatio
            paddingOffset = np.array([math.cos(eyeNormal) * paddingScalar, math.sin(eyeNormal) * paddingScalar], int)

            points[1] = points[1] + paddingOffset
            points[2] = points[2] + paddingOffset
            extraleft = points[0] + paddingOffset
            extraRight = points[3] + paddingOffset

            points = np.insert(points, 3, extraRight, axis=0)
            points = np.insert(points, 1, extraleft, axis=0)
            
        rekt = getRekt(points)
        workframe = getSubFrame(frame, rekt)

        offsetPoints = np.array([pt - rekt[0] for pt in points])
        if (workframe.shape[0] > 0 and workframe.shape[1] > 0):

            workframe = cv2.GaussianBlur(workframe, (min(workframe.shape[0],10),min(workframe.shape[1],10)), 0)
            mask = self.CreateMask(workframe, offsetPoints)
            workframe = cv2.bitwise_and(workframe, mask)

        # rows, cols = frame.shape
        # threshold, _ = cv2.threshold(workframe, 3, 255, cv2.THRESH_BINARY_INV)
        # contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        # for cnt in contours:
        #     (x, y, w, h) = cv2.boundingRect(cnt)
        #     #cv2.drawContours(roi, [cnt], -1, (0, 0, 255), 3)
        #     cv2.rectangle(workframe, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #     cv2.line(workframe, (x + int(w/2), 0), (x + int(w/2), rows), (0, 255, 0), 2)
        #     cv2.line(workframe, (0, y + int(h/2)), (workframe, y + int(h/2)), (0, 255, 0), 2)
        #     break

        return np.array([0,0], int), workframe

    def CalculatePupils(self, frame, coordinates):
        leftPoints = selectSubset(coordinates, [36, 37, 38, 39, 40, 41], int)
        leftPupil, leftSubFrame = self.ProcessEye(frame, leftPoints)
        leftRekt = getRekt(leftPoints)

        setSubFrame(frame, [leftRekt[0][0],leftRekt[0][1]], leftSubFrame)

        rightPoints = selectSubset(coordinates, [42, 43, 44, 45, 46, 47], int)
        rightPupil, rightSubFrame = self.ProcessEye(frame, rightPoints)
        rightRekt = getRekt(rightPoints)

        setSubFrame(frame, [rightRekt[0][0],rightRekt[0][1]], rightSubFrame)

        return frame


