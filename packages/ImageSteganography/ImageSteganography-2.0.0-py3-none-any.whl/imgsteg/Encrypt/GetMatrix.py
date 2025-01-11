class ChangeMatrix:

    def __init__(self, row, number):
        """row: a particular image pixel [r,g,b]
        number: a value from self.message (which is an ascii value) i.e., encrypted message
        Description: Iterates through the [r,g,b] set and replaces the last values of the element with self.message values
        rounds the number before replacing eg. [12, 222, 23] be row and 45 be message then output: [10, 224, 25]"""

        self.number = str(number)
        self.matrix_row = row
        # print(self.number, self.matrix_row)

        # Converts out self.number to 3-digit
        while len(self.number) != 3:
            self.number = "0" + self.number

        for i in range(1, len(self.matrix_row)+1):
            self.matrix_row[-i] = str(round(int(self.matrix_row[-i]), -1) + int(self.number[-i]))
        # print(self.matrix_row)
