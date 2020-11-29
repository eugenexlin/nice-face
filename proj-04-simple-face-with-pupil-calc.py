import cv2, time, dlib
import math
import importlib
from nicefacelib.src.faceformulas.EyeTracker import EyeTracker
from nicefacelib.src.faceformulas.SimpleGeometry import SimpleGeometry
from nicefacelib.src.utils.ConvertDlib import *
from nicefacelib.src.utils.DataUtils import *

video=cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
video.set(cv2.CAP_PROP_FPS, 60)

try:

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    tick=0
    faceCalculator = SimpleGeometry()
    eyeTracker = EyeTracker()
    eyeTracker.paddingTopRatio = 0.08
    eyeTracker.debugDrawEye = 1

    while True:
        tick=tick+1
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        frame = gray
        if (len(faces) > 0):

            face = faces[0]
            landmarks = predictor(gray, face)
            coordinates = ConvertToSimpleMatrix(landmarks)

            faceCalculator.Next68Coordinates(coordinates)
            frame = eyeTracker.CalculatePupils(frame, coordinates)
            
        cv2.putText(frame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))

        # show what the calculator has 
        
        # cv2.circle(frame, tuple(np.array(faceCalculator.Nose.current(), int)), radius=2, color=(0,0,255), thickness=-1)
        # cv2.circle(frame, tuple(np.array(faceCalculator.Head.current(), int)), radius=2, color=(0,0,255), thickness=-1)

        # cv2.putText(frame, str(faceCalculator.HeadRoll), (3,100), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadPitch), (3,120), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.HeadYaw), (3,140), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)

        # cv2.putText(frame, str(faceCalculator.MouthOpen), (3,200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)
        # cv2.putText(frame, str(faceCalculator.Smile), (3,220), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,255), thickness=1)


        cv2.imshow("Capture", frame)

        key = cv2.waitKey(5)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
