

class INE_Detection:
    def __init__(self, boundingBox, score, class_id, label, orientation=None, quality=None):
        self.boundingBox = boundingBox
        self.score = score
        self.class_id = class_id
        self.label = label

        self.orientation = orientation
        self.quality = quality

    def setOrientation(self, orientation):
        self.orientation = orientation

    def setQuality(self, quality):
        self.quality = quality