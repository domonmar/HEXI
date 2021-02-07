# from tkinter import *
from PIL import Image, ImageTk
import cv2


def convert_image_opencv_to_tk(opencv_image):
    # Rearrange the color channel
    b, g, r = cv2.split(opencv_image)
    img = cv2.merge((r, g, b))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(image=im)

    return img_tk


def convert_image_opencv_to_pil(opencv_image):
    b, g, r = cv2.split(opencv_image)
    img = cv2.merge((r, g, b))
    im_pil = Image.fromarray(img)
    return im_pil


def convert_image_pil_to_tk(pil_image):
    img_tk = ImageTk.PhotoImage(image=pil_image)
    return img_tk


def nearest_odd(number):
    return number + (number % 2) - 1


def set_entry_text(entry, text):
    entry.delete(0, "end")
    entry.insert(0, text)
