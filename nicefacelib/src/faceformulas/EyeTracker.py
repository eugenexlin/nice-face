import numpy as np
import cv2
import math
from nicefacelib.src.utils.DataUtils import *
from nicefacelib.src.utils.MovingAverage import MovingAverage

# Hi, this class was tested on pale asian guy with smol eye
class EyeTracker:

    # if you have downward eyelashes, you may notice the landmark detector making your top eye lid too low.
    # provide a number that is a multiplier to the eye width that is offset to the eye on the top 4 landmarks
    # along the perpendicular of the eye
    # give something like 0.1??
    paddingTopRatio = 0.0
    gaussianBlurFactor = 11

    # there fields control the eye levels for pupil detection
    # e.g. if you only set bottom = 50, all gray values under 50 will be black, and 50~255 will be linearly scaled from 0 to 255
    EyeGrayscaleLevelsDarkOffset = 20
    EyeGrayscaleLevelsLightOffset = 0
    EyeGrayscaleThreshold = 5

    # first we find the first dark spot. If your eyes are fair colored, you might just get the pupil directly.
    # if you have dark eyes, you enable this to zero in on the location and do another pass
    # where we up the brightness as high as possible to try to see if a pupil can be reasonably detected.
    IsFindPupilEnabled = 0

    debugDrawEye = 0

    IsAverageBothEyes = 1
    
    def __init__(self, smoothing=2):
        # raw data that should get smoothing
        self.Head = MovingAverage(smoothing, 2)

    def CreateMask(self, frame, coordinates):
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask.fill(255)
        points = np.array(coordinates, int)
        mask = cv2.fillConvexPoly(mask, points, 0)
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

        foundPupil = 0
        eyePosition = [0,0]

        offsetPoints = np.array([pt - rekt[0] for pt in points])
        if (workframe.shape[0] > 0 and workframe.shape[1] > 0):
            #we create mask of active area of pupil that will color in white, not black, because we will detect dark pupil
            mask = self.CreateMask(workframe, offsetPoints)
            

            # commenting because not sure i like this method of masking before gaussian blur
            # # get current max so we can set the area outside the eye to an average value
            # mediumValue = int(np.ndarray.mean(workframe))
            # mask = np.bitwise_and(mask, mediumValue) 
            # # apply mask to the workframe BEFORE gaussian blur and it will help dampen the darkness of eyelashes.
            # workframe = cv2.bitwise_or(workframe, mask)

            #cast to float for better blurry calculations
            workframe = workframe.astype(np.float)

            workframe = cv2.GaussianBlur(workframe, (self.gaussianBlurFactor,self.gaussianBlurFactor), 0)

            #do some calcs, but add some extreme boundaries
            minVal = min(workframe.min() + self.EyeGrayscaleLevelsDarkOffset, 240.0)
            maxVal =  max(workframe.max() - self.EyeGrayscaleLevelsLightOffset, minVal + 1.0)

            ratio = (255.0 / float(maxVal - minVal))
        
            # scale levels, but clip boundaries)
            workframe[:,:] = (workframe[:,:] - minVal) * ratio
            workframe = np.clip(workframe, 0, 255)

            #cast to int for support for throsholds/contours
            workframe = workframe.astype(np.uint8)
            
            # apply mask to the workframe BEFORE gaussian blur and it will help dampen the darkness of eyelashes.
            workframe = cv2.bitwise_or(workframe, mask)


            workframeAvg = np.average(workframe)

            # workframe = cv2.cvtColor(workframe, cv2.COLOR_BGR2GRAY)
            rows, cols = workframe.shape
            _, threshold = cv2.threshold(workframe, self.EyeGrayscaleThreshold, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
            maxArea = 0
            maxMassX = 0
            maxMassY = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                # to detect blinking eye,
                # we assume pupil will be a lot darker than eyelashes
                # but if eyes closed and pupils missing, then we will detect the line of the eye in its entirety or in parts.
                # if in parts, then if they are roughly similar area, we will merge the results.
                # if merged results have a widge of basically the whole eye, which the pupil can not possibly be, then we consider the eye closed.
                if area < maxArea/.3:
                    break

                # finding bounding rectangle is a nice approximate middle, but not perfect
                (x, y, w, h) = cv2.boundingRect(contour)
                # cv2.line(workframe, (x + int(w/2), 0), (x + int(w/2), rows), (0, 255, 0), 1)
                # cv2.line(workframe, (0, y + int(h/2)), (cols, y + int(h/2)), (0, 255, 0), 1)

                moment = cv2.moments(contour)

                if moment['m00'] > 0:
                    massX = int(moment['m10']/moment['m00'])
                    massY = int(moment['m01']/moment['m00'])
                    cv2.line(workframe, (massX, 0), (massX, rows), (255, 255, 0), 1)
                    cv2.line(workframe, (0, massY), (cols, massY), (255, 255, 0), 1)
                if area > maxArea:
                    maxArea = area
                    maxMassX = massX
                    maxMassY = massY
                        
               # one more issue is if your eye color is very similar to eyelash, you may detect like a ding off of the pupil detection.
               # in this case lets somehow normalize 


                cv2.drawContours(workframe, [contour], -1, (200, 200, 200), 1)

            cv2.line(workframe, (maxMassX, 0), (maxMassX, rows), (255, 255, 255), 1)
            cv2.line(workframe, (0, maxMassY), (cols, maxMassY), (255, 255, 255), 1)

        return np.array(eyePosition, int), workframe

    def CalculatePupils(self, frame, coordinates):
        leftPoints = selectSubset(coordinates, [36, 37, 38, 39, 40, 41], int)
        leftPupil, leftSubFrame = self.ProcessEye(frame, leftPoints)
        leftRekt = getRekt(leftPoints)

        rightPoints = selectSubset(coordinates, [42, 43, 44, 45, 46, 47], int)
        rightPupil, rightSubFrame = self.ProcessEye(frame, rightPoints)
        rightRekt = getRekt(rightPoints)

        # debug for displaying the data in case you wanted to see it visualized
        if self.debugDrawEye:
            setSubFrame(frame, [leftRekt[0][0],leftRekt[0][1]], leftSubFrame)
            setSubFrame(frame, [rightRekt[0][0],rightRekt[0][1]], rightSubFrame)

        return frame


