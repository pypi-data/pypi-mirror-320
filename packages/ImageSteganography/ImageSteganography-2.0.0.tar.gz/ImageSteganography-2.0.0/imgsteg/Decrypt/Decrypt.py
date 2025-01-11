from .GetMatrix import GetMatrix
from .TextConverter import Convert
import sys


class Decrypt:
    """Will import modules and do necessary calculations and return to you the hidden text"""

    def __init__(self, address, password, shared_key):
        self.matrix = GetMatrix(address)  # Obtain image address

        # Converts password and private key into usable format
        data = Convert()
        self.pass_key = data.convert_pw(password)

        # Check if password is correct
        if self.pass_key != int(self.matrix.matrix[0][0][0]):
            sys.stdout.write('Incorrect Password !\n')
            sys.exit()
        else:
            sys.stdout.write('Passwords match...\n\n')
        self.shared_key = data.convert_text_helper(shared_key)

        # extract list of characters and add pass key to decrypt the text
        self.extracted_text = []
        self.length = int(self.matrix.matrix[0][0][1])  # Get length of message
        if self.length == 255:
            self.length += int(self.matrix.matrix[0][0][2])

        x = 0
        # Starts iteration to get ascii of hidden message
        for i in range(0, len(self.matrix.matrix), self.pass_key):
            for m in range(0, len(self.matrix.matrix[i]), self.pass_key):
                if i == 0 and m == 0:
                    pass  # Since this has our CRC details
                elif x < self.length:
                    # Until length of list is less than message length
                    for k in range(len(self.matrix.matrix[i][m])):
                        self.extracted_text.append(str(self.matrix.matrix[i][m][k])[-1])
                        if len(str(self.matrix.matrix[i][m][-1])) > 1:
                            if int(str(self.matrix.matrix[i][m][k])[-k]) == 0:
                                continue
                    self.extracted_text.append(',')  # Decimeter between ascii of 2 characters
                    x += 1
                else:
                    break

        # Convert encoded message to text
        self.message = data.secret_message(self.extracted_text, self.shared_key)
        sys.stdout.write("Your message is:\n")
        sys.stdout.write(self.message)
        sys.stdout.write(""
                         "\n")
