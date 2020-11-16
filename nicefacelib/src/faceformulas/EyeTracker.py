import numpy as np
import cv2

def CreateMask(frame, features):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    mask = DrawEyeToMask(mask, [36, 37, 38, 39, 40, 41])
    mask = DrawEyeToMask(mask, [42, 43, 44, 45, 46, 47])
    return mask

def DrawEyeToMask(mask, features, coordinates):
    points = [features[i] for i in coordinates]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask


