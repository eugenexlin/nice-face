import numpy as np

def ConvertToSimpleMatrix(landmarks):
	coordinates = np.zeros((68, 2), float)
	for i in range(0, 68):
		coordinates[i] = [landmarks.part(i).x, landmarks.part(i).y]
	return coordinates