import numpy as np
from nicefacelib.src.utils.DataUtils import *

class MovingAverage:

    def __init__(self, entryCount, entryDimension = 1, dType=float):
        self.entryCount = entryCount
        self.entryDimension = entryDimension
        self.entries = np.zeros((entryCount, entryDimension), dType)
        self.index = -1
        self.lastIndex = 0

    def push(self, value):
        if (self.index < 0):
            for i in range(self.entryCount):
                self.entries[i] = value
            self.index = 0
        else:
            self.entries[self.index] = value
            self.lastIndex = self.index
            self.index = (self.index + 1) % len(self.entries)

    def forceVal(self, value):
        for i in range(self.entryCount):
            self.entries[i] = value
        self.index = 0

    #flatten single scalar is useless personally nice feature that says
    # if your dimension = 1, and you return [x]. return non matrix x instead
    def current(self, flattenSingleScalar=1):
        val = avgAllPts(*self.entries)
        if flattenSingleScalar:
            if len(val) == 1:
                return val[0]
        return np.array(val)
