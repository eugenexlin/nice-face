
def avgAllPts(*points):
    return [sum(x)/len(x) for x in zip(*points)]
def avgPts(sourceArr, indexArr):
    arr = [sourceArr[item] for item in indexArr]
    return sum(arr)/len(arr)