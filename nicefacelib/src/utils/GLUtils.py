
def getIndicesForSquareMeshDegenerateTriangles(countX, countY):
	indices = []
	for y in range(countY - 1):
		currentRowIndex = y*countX
		nextRowIndex = currentRowIndex + countX
		for x in range(countX):
			indices.append(currentRowIndex + x)
			indices.append(nextRowIndex + x)
		# if it is not the last row, add in degenerate triangles
		if y < countY - 1:
			indices.append(nextRowIndex + countX - 1)
			indices.append(nextRowIndex)
	return indices

