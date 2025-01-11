import sys


class Convert:
    """Converts the password to its ascii value
    process: Converts the password to its ascii values then gets its binary representation then algebraically adds
    the obtained binary values and adds them again to get a 2 digit number saved as self.passkey"""

    def __init__(self):
        self.message = None
        self.list = None
        self.key = None
        self.pass_key = None

    def convert_pw(self, password):
        """Does necessary operations on password to get number of skips, so we can find the elements having our text
        process: Get the password from user, convert it to ascii and obtain its binary value then sum the digits"""
        self.pass_key = sum([int(bin(ord(i))[2::]) for i in password])
        self.pass_key = sum([int(i) for i in str(self.pass_key)])
        return int(self.pass_key)

    @staticmethod
    def convert_text_helper(pass_key):
        """Gets the jumping factor"""
        return int(pass_key)**0.5

    def secret_message(self, lst, key):
        """We add the shared key to the extracted text to obtain the original ascii and convert to text"""
        self.list = lst
        self.key = int(key)
        self.message = ''.join(self.list)
        temp = self.message.strip().split(',')
        temp = [chr(int(i) + self.key) for i in temp if i.isdigit()]
        return ''.join(temp)
