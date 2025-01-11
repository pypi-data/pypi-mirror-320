import cv2 as cv


class GetMatrix:
    """Obtains the given image path's matrix"""
    def __init__(self, address):
        self.matrix = cv.imread(address)
        