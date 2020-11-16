import cv2, time, dlib
import math
import importlib
from nicefacelib.src.faceformulas.SimpleGeometry import SimpleGeometry
from nicefacelib.src.utils.ConvertDlib import *

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
            
            for n in range(0, len(coordinates)):
                cv2.circle(frame, tuple(coordinates[n].astype(int)), radius=1, color=(0,255,0), thickness=-1)
                cv2.putText(frame, str(n), tuple(coordinates[n].astype(int) + 4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))
            
        cv2.putText(frame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))

        # show what the calculator has 
        
        cv2.circle(frame, tuple(np.array(faceCalculator.CenterNose.currVal(), int)), radius=2, color=(0,0,255), thickness=-1)
        cv2.circle(frame, tuple(np.array(faceCalculator.CenterHead.currVal(), int)), radius=2, color=(0,0,255), thickness=-1)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(20)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
