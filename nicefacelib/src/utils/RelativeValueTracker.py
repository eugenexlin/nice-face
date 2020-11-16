import numpy as np

class RelativeValueTracker:
    liveValue
    minValue
    maxValue
    
    def __init__(self, entryCount):
        self.entryCount = entryCount

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

    def current(self):
        if (self.index < 0):
            return 0
        sum=np.sum(self.entries)
        return sum/self.entryCount
