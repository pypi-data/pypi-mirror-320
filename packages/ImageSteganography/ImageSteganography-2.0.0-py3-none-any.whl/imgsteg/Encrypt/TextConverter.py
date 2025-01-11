import sys


class Convert:
    """Functions = [convert_sum: to get self.passkey, convert_ascii: to obtain ascii of message in self.message]"""

    def __init__(self):
        self.message = None
        self.private_key = None
        self.pass_key = None

    def convert_sum(self, password: str):
        """Converts the password to its ascii value
        process: Converts the password to its ascii values then gets its binary representation then algebraically adds
        the obtained binary values and adds them again to get a 2 digit number saved as self.passkey"""
        # print(password, [ord(i) for i in password], [bin(ord(i))[2::] for i in password])
        self.pass_key = sum([int(bin(ord(i))[2::]) for i in password])
        self.pass_key = sum([int(i) for i in str(self.pass_key)])
        return self.pass_key

    def convert_ascii(self, text):
        """Returns a list of numbers where each number is ascii representation of the message character"""
        secret_message = [ord(i) for i in text]
        # Private Key is the minimum ascii value of the text given by user
        self.private_key = min(secret_message)
        # Deducts the minimum ascii value from all ascii values of characters of message
        self.message = [int(i - self.private_key) for i in secret_message]
##        print(secret_message, self.private_key, self.message)

        sys.stdout.write('Your private key is: ')
        sys.stdout.write(str(self.private_key ** 2) + "\n")
        return self.message
