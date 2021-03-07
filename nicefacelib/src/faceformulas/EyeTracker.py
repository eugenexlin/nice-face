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

    # this flag is to test if the dark area of the eyes 
    # normally this is the iris, but if your eyes are closing, it might be the line across your whole eye.
    # if the longest distance of this dark part is compared to the total width of eye and is too long
    # we can consider the eye closed.
    # this ratio seems considerably large because we use min enclosing circle, which might overestimate
    DarkPartRatioMax = 0.8

    # first we find the first dark spot. If your eyes are fair colored, you might just get the pupil directly.
    # if you have dark eyes, you enable this to zero in on the location and do another pass
    # where we up the brightness as high as possible to try to see if a pupil can be reasonably detected.
    IsFindPupilEnabled = 0
    FindPupilMaxIteration = 50
    FindPupilIterationStep = 2
    FindPupilIterationSmoothing = 3
    FindPupilMinimumArea = 20 # area in pixels

    debugDrawEye = 0
    debugDrawFindPupil = 0

    # absolute iris or pupil position for the most recent fed frame
    EyeLeftAbsolute = [0,0]
    EyeRightAbsolute = [0,0]

    EyeLeftIsClosed = 0
    EyeRightIsClosed = 0

    # how open
    EyeLeftValue = 0
    EyeRightValue = 0

    EyeValue = 0

    EyeLeftPitch = 0.0
    EyeRightPitch = 0.0

    EyePitch = 0.0
    
    def __init__(self, smoothing=2):
        # raw data that should get smoothing
        pass

    def CreateEyeMask(self, frame, coordinates):
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask.fill(255)
        points = np.array(coordinates, int)
        mask = cv2.fillConvexPoly(mask, points, 0)
        return mask

    def CreateIrisCircleMask(self, frame, point, radius):
        mask = np.zeros(frame.shape[:2], dtype=np.float)
        mask.fill(255)

        # arbitrarily adding some 1.2 padding to radius to counter the gaussian blur
        mask = cv2.circle(mask, point, radius=int(radius*1.2), color=(0,0,0), thickness=-1)
        gaussianRadius = int(radius/2)*2 + 1
        mask = cv2.GaussianBlur(mask, (gaussianRadius,gaussianRadius), 0)
        mask = cv2.GaussianBlur(mask, (gaussianRadius,gaussianRadius), 0)
        mask = mask.astype(np.uint8)
        return mask

    # func() => (x,y) , workframe
    def ProcessEye(self, frame, points):
        eyeTop = avgPts(points, [1,2])
        eyeBottom = avgPts(points, [4,5])
        
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

        eyePosition = [0,0]
        isClosed = 1
        eyeWidth = np.linalg.norm(points[0] - points[5]) 
        eyeOpen = np.linalg.norm(eyeTop - eyeBottom) * 2 / eyeWidth
        eyeValue = eyeOpen

        offsetPoints = np.array([pt - rekt[0] for pt in points])
        if (workframe.shape[0] > 0 and workframe.shape[1] > 0):
            #we create mask of active area of pupil that will color in white, not black, because we will detect dark pupil
            mask = self.CreateEyeMask(workframe, offsetPoints)

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
            darkSize = 0
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
                    (x,y),radius = cv2.minEnclosingCircle(contour)
                    darkSize = radius * 2
                        
               # one more issue is if your eye color is very similar to eyelash, you may detect like a ding off of the pupil detection.
               # in this case lets somehow normalize 


                cv2.drawContours(workframe, [contour], -1, (200, 200, 200), 1)

            massRadius = math.sqrt(maxArea / math.pi)
            # cv2.circle(workframe, (maxMassX, maxMassY), radius=int(massRadius), color=(255,255,255), thickness=1)

            # extra routine that overrides the pupil stuff
            if self.IsFindPupilEnabled:

                pupilWorkframe = getSubFrame(frame, rekt)
                pupilmask = self.CreateIrisCircleMask(pupilWorkframe, (maxMassX, maxMassY), massRadius)
                pupilWorkframe = cv2.bitwise_or(pupilWorkframe, pupilmask) 
                pupilWorkframe = cv2.GaussianBlur(pupilWorkframe, (self.gaussianBlurFactor,self.gaussianBlurFactor), 0)

                pupil, pupilWorkframe = self.ScanThresholdForPupil(pupilWorkframe, [maxMassX, maxMassY])
                if (self.debugDrawFindPupil):
                    workframe = pupilWorkframe

                eyePosition = np.array(pupil,int)

                cv2.line(workframe, (int(pupil[0]), 0), (int(pupil[0]), rows), (255, 255, 255), 1)
                cv2.line(workframe, (0, int(pupil[1])), (cols, int(pupil[1])), (255, 255, 255), 1)
            else:

                eyePosition = np.array([maxMassX,maxMassY],int)

                cv2.line(workframe, (maxMassX, 0), (maxMassX, rows), (255, 255, 255), 1)
                cv2.line(workframe, (0, maxMassY), (cols, maxMassY), (255, 255, 255), 1)

            isClosed = darkSize/eyeWidth  > self.DarkPartRatioMax

        return np.array(eyePosition, int), eyeValue, isClosed, workframe

    def ScanThresholdForPupil(self, workframe, startingPoint):
        pupil = MovingAverage(self.FindPupilIterationSmoothing, 2)
        pupil.push(startingPoint)
        itr = self.FindPupilMaxIteration
        step = self.FindPupilIterationStep
        rows, cols = workframe.shape

        overflowWorkframe = workframe.astype(np.uint16)

        if itr > 255:
            itr = 255
            step = 1
        while itr > 0:
            itr = itr - 1

            overflowWorkframe[:,:] = overflowWorkframe[:,:] + step
            overflowWorkframe = np.clip(overflowWorkframe, 0, 255)
            workframe = overflowWorkframe.astype(np.uint8)
            _, threshold = cv2.threshold(workframe, self.EyeGrayscaleThreshold, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

            if len(contours) <= 0:
                break
            contour = contours[0]
            
            area = cv2.contourArea(contour)
            if area < self.FindPupilMinimumArea:
                break

            moment = cv2.moments(contour)

            if moment['m00'] > 0:
                massX = int(moment['m10']/moment['m00'])
                massY = int(moment['m01']/moment['m00'])
                pupil.push([massX, massY])

        return pupil.current(), workframe


    def CalculatePupils(self, frame, coordinates):
        rightWidth = np.linalg.norm(coordinates[42] - coordinates[45]) 

        leftPoints = selectSubset(coordinates, [36, 37, 38, 39, 40, 41], int)
        leftPupil, leftValue, leftIsClosed, leftSubFrame = self.ProcessEye(frame, leftPoints)
        leftRekt = getRekt(leftPoints)

        self.EyeLeftAbsolute = np.array([(leftRekt[0][0] + leftPupil[0]), (leftRekt[0][1] + leftPupil[1])], int)
        self.EyeLeftIsClosed = leftIsClosed
        self.EyeLeftValue = leftValue

        rightPoints = selectSubset(coordinates, [42, 43, 44, 45, 46, 47], int)
        rightPupil, rightValue,  rightIsClosed, rightSubFrame = self.ProcessEye(frame, rightPoints)
        rightRekt = getRekt(rightPoints)

        self.EyeRightAbsolute = np.array([(rightRekt[0][0] + rightPupil[0]), (rightRekt[0][1] + rightPupil[1])], int)
        self.EyeRightIsClosed = rightIsClosed
        self.EyeRightValue = rightValue

        self.EyeValue = (self.EyeLeftValue + self.EyeRightValue)/2

        # debug for displaying the data in case you wanted to see it visualized
        if self.debugDrawEye:
            setSubFrame(frame, [leftRekt[0][0],leftRekt[0][1]], leftSubFrame)
            setSubFrame(frame, [rightRekt[0][0],rightRekt[0][1]], rightSubFrame)

        return frame


