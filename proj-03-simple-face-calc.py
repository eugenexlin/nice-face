import cv2, time, dlib
import math
import importlib
from nicefacelib.src.faceformulas.EyeTracker import EyeTracker
from nicefacelib.src.faceformulas.SimpleGeometry import SimpleGeometry
from nicefacelib.src.utils.ConvertDlib import *
from nicefacelib.src.utils.DataUtils import *

video=cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

try:

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    tick=0
    faceCalculator = SimpleGeometry()
    eyeTracker = EyeTracker()
    eyeTracker.paddingTopRatio = 0.15

    while True:
        tick=tick+1
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame = frame * 0
        faces = detector(gray)
        frame = gray
        if (len(faces) > 0):

            face = faces[0]
            landmarks = predictor(gray, face)
            coordinates = ConvertToSimpleMatrix(landmarks)

            faceCalculator.Next68Coordinates(coordinates)
            frame = eyeTracker.CalculatePupils(frame, coordinates)

            # for n in range(0, len(coordinates)):
            #     cv2.circle(frame, tuple(coordinates[n].astype(int)), radius=1, color=(0,255,0), thickness=-1)
            #     cv2.putText(frame, str(n), tuple(coordinates[n].astype(int) + 4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))
            
        cv2.putText(frame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))

        # show what the calculator has 
        
        # cv2.circle(frame, tuple(np.array(faceCalculator.Nose.current(), int)), radius=2, color=(0,0,255), thickness=-1)
        # cv2.circle(frame, tuple(np.array(faceCalculator.Head.current(), int)), radius=2, color=(0,0,255), thickness=-1)

        # cv2.putText(frame, str(faceCalculator.HeadRoll), (3,100), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadPitch), (3,120), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadYaw), (3,140), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        # cv2.putText(frame, str(faceCalculator.MouthOpen), (3,200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.Smile), (3,220), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        # render some interpreted values,.
        maxHeight = frame.shape[0]
        maxWidth = frame.shape[1]

        cv2.putText(frame, "size " + str(maxWidth) + "x" + str(maxHeight), (300,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        absx = (faceCalculator.Head.current()[0] - (maxWidth/2))/3
        absy = (faceCalculator.Head.current()[1] - (maxHeight/2))/3

        headPos = np.array([480,360])
        headPos = headPos + [absx, absy]
        neckPos = headPos + [0, 50]



        headOffset = [faceCalculator.HeadYaw * 20 , faceCalculator.HeadPitch * 24]
        headPos = headPos + headOffset
        headPos = pivotPoint(headPos, neckPos, -faceCalculator.HeadRoll)

        shoulderTop = pivotPoint(neckPos + [0, 36], neckPos, -faceCalculator.HeadRoll/2)
        shoulderLeft = pivotPoint(shoulderTop + [-60, 0], shoulderTop, -faceCalculator.HeadRoll/2) 
        shoulderRight = pivotPoint(shoulderTop + [60, 0], shoulderTop, -faceCalculator.HeadRoll/2) 
        sideLeft = pivotPoint(shoulderLeft + [0, 100], shoulderLeft, -faceCalculator.HeadRoll/2) 
        sideRight = pivotPoint(shoulderRight + [0, 100], shoulderRight, -faceCalculator.HeadRoll/2) 

        # eyes
        eyeOffset = np.array([swingCurve(faceCalculator.HeadYaw) * 25, swingCurve(faceCalculator.HeadPitch) * 36])
        eyePosLeft = pivotPoint(headPos + eyeOffset + [-28, -18], headPos, -faceCalculator.HeadRoll)
        eyePosRight = pivotPoint(headPos + eyeOffset + [28, -18], headPos, -faceCalculator.HeadRoll)

        # mouth
        minMouth = 0.03

        smile = faceCalculator.Smile + 0.2
        smile = max(smile, 0.0)
        smile = min(smile, 1.0)

        actualMouth = faceCalculator.MouthOpen - minMouth
        actualMouth = actualMouth*(max(smile+0.5, 1))
        actualMouth = max(actualMouth, 0)
        actualMouth = min(actualMouth, 1)
        mouthOffset = np.array([swingCurve(faceCalculator.HeadYaw) * 25, swingCurve(faceCalculator.HeadPitch) * 30 + 25])
        mouthPos = headPos + mouthOffset
        mouthTop = pivotPoint(mouthPos + [0, -8.0*actualMouth + 6.0*smile - 6.0*actualMouth], headPos, -faceCalculator.HeadRoll)
        mouthTopLeft = pivotPoint(mouthPos + [-15.0 + -9.0*max(smile-actualMouth/2,0.0), -4.0*actualMouth - 6.0*smile], headPos, -faceCalculator.HeadRoll)
        mouthTopRight = pivotPoint(mouthPos + [15.0 + 9.0*max(smile-actualMouth/2,0.0), -4.0*actualMouth - 6.0*smile], headPos, -faceCalculator.HeadRoll)
        mouthBottom = pivotPoint(mouthPos + [0, 24.0*actualMouth + 4.0*smile], headPos, -faceCalculator.HeadRoll)

        # cv2.putText(frame, str(actualMouth), (3,200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.Smile), (3,220), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(smile), (3,240), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.circle(frame, intTuple(neckPos), radius=1, color=(0,0,255), thickness=2)

        cv2.circle(frame, intTuple(headPos), radius=60, color=(255,255,255), thickness=2)

        # cv2.putText(frame, str(faceCalculator.EyeLeftOpen), (3,300), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.EyeRightOpen), (3,320), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        if faceCalculator.EyeLeftOpen < 0.3 and faceCalculator.EyeRightOpen < 0.3:
            eyeLines = np.array([eyePosLeft + pivotPoint([-12.0,6.0],[0.0,0.0], -faceCalculator.HeadRoll), eyePosLeft + pivotPoint([12.0,8.0],[0.0,0.0], -faceCalculator.HeadRoll)], np.int32)
            cv2.polylines(frame, [eyeLines], 0, color=(255,255,255), thickness=3)
            eyeLines = np.array([eyePosRight + pivotPoint([-12.0,8.0],[0.0,0.0], -faceCalculator.HeadRoll), eyePosRight + pivotPoint([12.0,6.0],[0.0,0.0], -faceCalculator.HeadRoll)], np.int32)
            cv2.polylines(frame, [eyeLines], 0, color=(255,255,255), thickness=3)
        else:
            cv2.circle(frame, intTuple(eyePosLeft), radius=16, color=(255,255,255), thickness=2)
            cv2.circle(frame, intTuple(eyePosRight), radius=16, color=(255,255,255), thickness=2)

        mouthLines = np.array([mouthTopLeft, mouthTop, mouthTopRight, mouthBottom], np.int32)
        cv2.polylines(frame, [mouthLines], 1, color=(255,255,255), thickness=2)
        shoulderLines = np.array([sideLeft, shoulderLeft, shoulderRight, sideRight], np.int32)
        cv2.polylines(frame, [shoulderLines], 1, color=(255,255,255), thickness=2)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(10)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
