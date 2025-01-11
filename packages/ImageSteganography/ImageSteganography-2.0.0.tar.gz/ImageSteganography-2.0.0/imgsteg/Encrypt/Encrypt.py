import cv2

from .TextConverter import Convert
from .GetMatrix import ChangeMatrix
from .ImageReader import GetMatrix


class Encrypt:
    """Will import modules and do necessary calculations and return to you an image with your message encrypted"""

    def __init__(self, text, password, address):
        # data is an object of Convert class from TextConverter.py
        data = Convert()
        # Obtains list of normalised ascii values
        self.message = data.convert_ascii(text)
        self.pass_key = data.convert_sum(password)
        # returns matrix of your given image address
        self.image = GetMatrix(address)

        x = 0
        # traversing through image matrix to do manipulations
        for i in range(0, len(self.image.matrix), self.pass_key):   # Iterates through height with jump of self.passkey
            for j in range(0, len(self.image.matrix[i]), self.pass_key):    # same iterations for width
                if i == 0 and j == 0:
                    pass    # We pass this since we need to save self.passkey in the (0, 0) element of image
                else:
                    if x < len(self.message):
                        self.image.matrix[i][j] = ChangeMatrix(self.image.matrix[i][j], self.message[x]).matrix_row
                        x += 1
                    else:
                        break

        # Security purpose
        self.image.matrix[0][0][0] = self.pass_key
        self.image.matrix[0][0][1] = len(self.message)
        self.image.matrix[0][0][2] = 0
        if len(self.message) > 255:
            len_ = str(len(self.message))
            print(len_)
            self.image.matrix[0][0][1] = 255
            self.image.matrix[0][0][2] = len_ - 255

        print(f"Your entered password is: {password}")
        print(f"Your message: \n {text} \n")

        # save matrix as .png
        self.image.save(input('Enter the address/name of your encrypted image:\n'), self.image.matrix)

