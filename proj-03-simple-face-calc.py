import cv2, time, dlib
import math
import importlib
from nicefacelib.src.faceformulas.SimpleGeometry import SimpleGeometry
from nicefacelib.src.utils.ConvertDlib import *
from nicefacelib.src.utils.DataUtils import *

video=cv2.VideoCapture(0)

try:

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    tick=0
    faceCalculator = SimpleGeometry()

    while True:
        tick=tick+1
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if (len(faces) > 0):

            face = faces[0]
            landmarks = predictor(gray, face)
            coordinates = ConvertToSimpleMatrix(landmarks)

            faceCalculator.Next68Coordinates(coordinates)

            # for n in range(0, len(coordinates)):
            #     cv2.circle(frame, tuple(coordinates[n].astype(int)), radius=1, color=(0,255,0), thickness=-1)
            #     cv2.putText(frame, str(n), tuple(coordinates[n].astype(int) + 4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))
            
        cv2.putText(frame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))

        # show what the calculator has 
        
        # cv2.circle(frame, tuple(np.array(faceCalculator.CenterNose.current(), int)), radius=2, color=(0,0,255), thickness=-1)
        # cv2.circle(frame, tuple(np.array(faceCalculator.CenterHead.current(), int)), radius=2, color=(0,0,255), thickness=-1)

        # cv2.putText(frame, str(faceCalculator.HeadRoll), (3,100), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadPitch), (3,120), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadYaw), (3,140), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        # render some interpreted values,.
        maxHeight = frame.shape[0]
        maxWidth = frame.shape[1]
        absx = (faceCalculator.CenterHead.current()[0] - (maxWidth/2))/5
        absy = (faceCalculator.CenterHead.current()[1] - (maxHeight/2))/5

        headPos = np.array([500,400])
        headPos = headPos + [absx, absy]
        neckPos = headPos + [0,-50]

        headOffset = [faceCalculator.HeadYaw * -10 , faceCalculator.HeadPitch * -20]
        headPos = headPos + headOffset
        headPos = pivotPoint(headPos, neckPos, -faceCalculator.HeadRoll)

        eyeOffset = np.array([swingCurve(faceCalculator.HeadYaw) * 25, swingCurve(faceCalculator.HeadPitch) * 25 - 15])
        eyePos = headPos + eyeOffset
        eyePosLeft = eyePos + pivotPoint([-28,0], [0,0], -faceCalculator.HeadRoll)
        eyePosRight = eyePos + pivotPoint([28,0], [0,0], -faceCalculator.HeadRoll)

        cv2.circle(frame, intTuple(headPos), radius=60, color=(255,255,255), thickness=2)
        cv2.circle(frame, intTuple(eyePosLeft), radius=16, color=(255,255,255), thickness=2)
        cv2.circle(frame, intTuple(eyePosRight), radius=16, color=(255,255,255), thickness=2)



        cv2.imshow("Capture", frame)

        key = cv2.waitKey(20)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
