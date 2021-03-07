import cv2, time, dlib
import math
import importlib
from nicefacelib.src.faceformulas.EyeTracker import EyeTracker
from nicefacelib.src.faceformulas.SimpleGeometry import SimpleGeometry
from nicefacelib.src.utils.ConvertDlib import *
from nicefacelib.src.utils.DataUtils import *

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

faceCalculator = SimpleGeometry()
eyeTracker = EyeTracker()
eyeTracker.debugDrawEye = 1
eyeTracker.IsFindPupilEnabled = 1

files = ["testfaces\\face1.png", "testfaces\\face2.png"]

for path in files:
    frame = cv2.imread(path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    frame = gray
    if (len(faces) > 0):

        face = faces[0]
        landmarks = predictor(gray, face)
        coordinates = ConvertToSimpleMatrix(landmarks)

        faceCalculator.Next68Coordinates(coordinates)
        frame = eyeTracker.CalculatePupils(frame, coordinates)
        
    recolor = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    cv2.putText(recolor, "press any key to destroy all windows", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0,0,255))
    cv2.imshow(path, recolor)

cv2.waitKey()

cv2.destroyAllWindows()
