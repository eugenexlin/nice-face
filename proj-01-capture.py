import cv2, time, dlib
import math

video=cv2.VideoCapture(0)

try:

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    tick=0

    while True:
        tick=tick+1

        check, frame = video.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)
        
        # for face in faces:
        #     x1 = face.left()
        #     x2 = face.right()
        #     y1 = face.top()
        #     y2 = face.bottom()
        #     # draw rect
        #     cv2.rectangle(frame, (x1,y1), (x2,y2), color=(255,0,0), thickness=1)

        #scale and show image for ease of seeing lel
        width = int(frame.shape[1] * 2)
        height = int(frame.shape[0] * 2)
        bigFrame = cv2.resize(frame, (width, height), interpolation = cv2.INTER_AREA)

        for face in faces:
            
            landmarks = predictor(gray, face)
            
            for n in range(0,68):
                x = landmarks.part(n).x * 2
                y = landmarks.part(n).y * 2
                cv2.circle(bigFrame, (x,y), radius=1, color=(0,255,0), thickness=-1)
                cv2.putText(bigFrame, str(n), (x+4,y+4), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(255,200,0))


        cv2.putText(bigFrame, "press esc to quit", (3,20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,200))
        cv2.imshow("Capture", bigFrame)

        key = cv2.waitKey(20)

        if key == ord('q'):
            break
        if key == 27: #esc
            break

finally:
    video.release()
