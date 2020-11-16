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

    geo = SimpleGeometry()

    while True:
        tick=tick+1

        check, frame = video.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)

        #scale and show image for ease of seeing lel
        width = int(frame.shape[1] * 2)
        height = int(frame.shape[0] * 2)
        bigFrame = cv2.resize(frame, (width, height), interpolation = cv2.INTER_AREA)

        if (len(faces) > 0):

            face = faces[0]
            landmarks = predictor(gray, face)
            coordinates = ConvertToSimpleMatrix(landmarks)
            coordinates = coordinates * 2
            
            for n in range(0, len(coordinates)):
                cv2.circle(bigFrame, tuple(coordinates[n].astype(int)), radius=1, color=(0,255,0), thickness=-1)
                cv2.putText(bigFrame, str(n), tuple(coordinates[n].astype(int) + 4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))

            # noseAvg = [(sum(x)/len(x),) for pts in zip(landmarks.part(27), landmarks.part(31),landmarks.part(35))]
            #     cv2.circle(bigFrame, (x,y), radius=1, color=(0,255,0), thickness=-1)
            #     cv2.putText(bigFrame, str(n), (x+4,y+4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))
            
        cv2.putText(bigFrame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))

        cv2.imshow("Capture", bigFrame)

        key = cv2.waitKey(20)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
