import cv2, time, dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

video=cv2.VideoCapture(0)
tick=0

while True:
    tick=tick+1

    check, frame = video.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    for face in faces:
        x1 = face.left()
        x2 = face.right()
        y1 = face.top()
        y2 = face.bottom()

        # draw rect
        cv2.rectangle(frame, (x1,y1), (x2,y2), color=(255,0,0), thickness=1)

        landmarks = predictor(gray, face)
        
        for n in range(0,68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x,y), radius=2, color=(0,255,0), thickness=-1)


    cv2.imshow("Capture", frame)

    key = cv2.waitKey(20)

    if key == ord('q'):
        break

video.release()
