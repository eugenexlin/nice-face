import cv2
import numpy as np

def DrawBar(frame, position, value, maxValue=1, color=(0,255,0), length=200, height=10):
    start = np.array([position[0], position[1]], int)
    x1 = int(position[0])
    x2 = x1 + int(length)
    y1 = int(position[1])
    y2 = y1 + int(height)

    #draw bar
    ratio = float(value) / float(maxValue)
    valueLength = int(ratio * float(length))
    cv2.rectangle(frame, (x1,y1), (x1 + valueLength,y2), color, -1)
    #if hit max, draw red line
    if value > maxValue:
        cv2.line(frame, (x2, y1-2), (x2, y2+2), (0,0,255), 3)
    #draw border
    cv2.rectangle(frame, (x1,y1), (x2,y2), (255,255,255), 1)

