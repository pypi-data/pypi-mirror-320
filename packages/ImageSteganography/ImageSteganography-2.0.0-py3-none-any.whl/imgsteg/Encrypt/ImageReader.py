import sys
import os
import cv2 as cv
import numpy as np


class GetMatrix:
    """Reads the image and stores it's matrix"""
    def __init__(self, address):
        self.verify = None
        self.filename = None
        self.matrix = cv.imread(address)
        # self.matrix = cv.resize(self.image, (0, 0), fx = 0.5, fy = 0.5)

    def save(self, filename, matrix):
        """Saves the image with user entered filename and in code's parent folder"""
        self.filename = filename
        matrix = np.array(matrix, dtype=np.uint8)
        # Obtains the current parent directory path and saves image in parent folder
        self.filename = os.path.join(os.getcwd(), self.filename)
        cv.imwrite(self.filename, matrix)

        sys.stdout.write('Image saved successfully to address: \n')
        sys.stdout.write(self.filename + "\n")
