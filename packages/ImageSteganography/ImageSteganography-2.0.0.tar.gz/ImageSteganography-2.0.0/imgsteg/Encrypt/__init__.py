# Imports the encrypt image file and uses its Encrypt function for encryption
from .Encrypt import Encrypt
from tkinter import *
from tkinter import filedialog

# Bring the open image window in focus
root = Tk()
root.withdraw()
root.lift()
root.focus_force()

# Basic user instructions
print(f'''Thankyou for using our service .\n1.) We request you to not use any symbols as they are out of our range.
2.) If you get "Error Encrypting" then replace all symbols if used or replace white spaces with underscores ('_').\n''')

# Get details from users and start the operation
Encrypt((input("\nEnter your message:\n").strip()), (input('\nEnter your password:\n').strip()),
        (filedialog.askopenfile(title='Select Image for Encryption',
                                filetypes=[("Image files", "*.png *.jpg")]).name))
