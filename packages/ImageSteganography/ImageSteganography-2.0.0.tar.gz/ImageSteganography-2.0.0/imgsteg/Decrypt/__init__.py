# Importing libraries
from .Decrypt import Decrypt
from tkinter import *
from tkinter import filedialog

# Bring the open image window in focus
root = Tk()
root.withdraw()
root.lift()
root.focus_force()

# Basic user instructions and the process starts
Decrypt((filedialog.askopenfile(title='Select Image for Encryption',
                                filetypes=[("Image files", "*.png *.jpg")]).name),
        input('Enter your password:\n'), input('Enter your security key:\n'))

# Decrypt('Decrypt\\finally_done.png', '3020128', '1024')       # Dummy input for testing puspose
