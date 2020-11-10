import numpy as np

class MovingAverage:

    entryCount = 3
    entries = []
    index = -1
    lastIndex = 0

    def __init__(self, entryCount):
        self.entryCount = entryCount
        self.entries = []
        self.index = -1
        self.lastIndex = 0

    def push(self, value):
        if (self.index < 0):
            #first time, fill the array
            entries = []
            for i in range(self.entryCount):
                self.entries.append(value)
            self.index = 0
        else:
            self.entries[self.index] = value
            self.lastIndex = self.index
            self.index = (self.index + 1) % len(self.entries)

    def forceVal(self, value):
        for i in range(self.entryCount):
            self.entries[i] = (value)

    def currVal(self):
        if (self.index < 0):
            return 0
        sum=np.sum(self.entries)
        return sum/self.entryCount
