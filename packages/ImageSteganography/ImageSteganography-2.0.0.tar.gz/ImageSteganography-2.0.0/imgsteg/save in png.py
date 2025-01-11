import cv2
import numpy as np
from PIL import Image

def save_image_with_proper_png_header(image, output_filename):
    header = b"\x89PNG\r\n\x1a\n"
    with open(output_filename, "wb") as f:
        f.write(header)
    cv2.imwrite(f, image)

# Example usage:

image = cv2.imread(r"C:\Users\Justin\Desktop\Ayush_project\imgsteg\image.jpg")
save_image_with_proper_png_header(image, "output.png")
