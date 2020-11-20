import numpy as np

class RelativeValueTracker:
    liveValue
    minValue
    maxValue
    
    def __init__(self, entryCount):
        self.entryCount = entryCount
