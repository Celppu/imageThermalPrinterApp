from escpos.printer import Serial
from PIL import Image as PILImage
from tkinter import *
import cv2
from PIL import ImageTk
from PIL import ImageEnhance
import numpy as np

import halftone as ht

def image_resize(image, width = 500):
    # resize the image to width of 500 and proportional height
    wpercent = (width / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    img_resized = image.resize((width, hsize))
    return img_resized



def adjust_image(brightness=1.0, contrast=1.0):
    # resize the image to width of 500 and proportional height
    global img; resize_button2; halftone_button2
    img2 = img
    #img2 = image_resize(img, width= width_scale.get())
    #resize img to half size the scale size, enhace and then resize back to original size to get 2x2 blocky look
    wwidth = width_scale.get()

    #resize to half size
    if resize_button2.get() == 1:
        print("resize")
        img2 = image_resize(img, width=wwidth//2)
    else:
        img2 = image_resize(img, width=wwidth)

    enhancer = ImageEnhance.Brightness(img2)
    img_enhanced = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Contrast(img_enhanced)
    img_enhanced = enhancer.enhance(contrast)

    #if halftone
    if halftone_button2.get() == 1:
        print("halftone")
        img_enhanced = ht.halftone(img_enhanced, ht.euclid_dot(spacing=halftone_spacing.get(), angle=30))
    else:
        # Convert to 1-bit black and white image
        img_enhanced = img_enhanced.convert('1')

    # resize back to original size
    img_enhanced = image_resize(img_enhanced, width=wwidth)

    # Convert to PhotoImage to display in tkinter
    photo = ImageTk.PhotoImage(image=img_enhanced)
    label.config(image=photo)
    label.image = photo  # keep a reference to avoid garbage collection

# Function to adjust image based on scale values
def adjust_image_from_scales(val):
    brightness = brightness_scale.get()
    contrast = contrast_scale.get()
    adjust_image(brightness=float(brightness), contrast=float(contrast))

def print_image():
    # get slider values
    brightness = brightness_scale.get()
    contrast = contrast_scale.get()

    # Initialize the printer
    p = Serial(devfile="COM19", baudrate=9600, bytesize=8, timeout=1, dsrdtr=True)

    # resize the image to width of 500 and proportional height
    #width = 500
    #img_resized = image_resize(img, width=width_scale.get())

    #enhancer = ImageEnhance.Brightness(img_resized)
    #img_enhanced = enhancer.enhance(brightness)
    #enhancer = ImageEnhance.Contrast(img_enhanced)
    #img_enhanced = enhancer.enhance(contrast)

    global img; resize_button2
    wwidth = width_scale.get()

        #resize to half size
    if resize_button2.get() == 1:
        print("resize")
        img2 = image_resize(img, width=wwidth//2)
    else:
        img2 = image_resize(img, width=wwidth)

    enhancer = ImageEnhance.Brightness(img2)
    img_enhanced = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Contrast(img_enhanced)
    img_enhanced = enhancer.enhance(contrast)

    
    if halftone_button2.get() == 1:
        print("halftone")
        img_enhanced = ht.halftone(img_enhanced, ht.euclid_dot(spacing= halftone_spacing.get(), angle=30))
    else:
        # Convert to 1-bit black and white image
        img_enhanced = img_enhanced.convert('1')

    # resize back to original size
    img_enhanced = image_resize(img_enhanced, width=wwidth)

    # Print the image
    p.image(img_enhanced, impl="bitImageColumn")#, high_density_vertical = False, high_density_horizontal = False)

    # Print image configuration if needed
    if print_config_button2.get() == 1:
        print("Print config")
        
        p.text("Brightness: " + str(brightness) + "\n")
        p.text("Contrast: " + str(contrast) + "\n")
        p.text("Width: " + str(wwidth) + "\n")
        if halftone_button2.get() == 1:
            p.text("Halftone: " + str(halftone_button2.get()) + "\n")
            p.text("Halftone spacing: " + str(halftone_spacing.get()) + "\n")
        else:
            p.text("1/0\n")
        p.text("Resize: " + str(resize_button2.get()) + "\n")

    # Cut the paper
    p.cut()

root = Tk()

# Load your image
img = PILImage.open('unnamed.jpg').convert('L')

wantedwidth = 500

# Image label
photo = ImageTk.PhotoImage(image=img)
label = Label(root, image=photo)
label.pack()

# Brightness scale
brightness_scale = Scale(root, from_=0, to=2, resolution=0.1, length=400,
                         label="Brightness", orient=HORIZONTAL,
                         command=adjust_image_from_scales)
brightness_scale.set(1.0)
brightness_scale.pack()

# Contrast scale
contrast_scale = Scale(root, from_=0, to=2, resolution=0.1, length=400,
                       label="Contrast", orient=HORIZONTAL,
                       command=adjust_image_from_scales)
contrast_scale.set(1.0)
contrast_scale.pack()

# width scale
width_scale = Scale(root, from_=1, to=600, resolution=1, length=400,
                          label="Width", orient=HORIZONTAL,
                            command=adjust_image_from_scales)
width_scale.set(wantedwidth)
width_scale.pack()

# toggle button to enable/disable resize down and back for 2x2 blocky look
def on_checkbutton_change(*args):
    if resize_button2.get() == 1:
        print("Resize is enabled")
    else:
        print("Resize is disabled")
    adjust_image()

resize_button2 = IntVar()
resize_button2.trace("w", on_checkbutton_change)
resize_button = Checkbutton(root, text="2x2 blocky", variable=resize_button2)
resize_button.pack()

# toggle button to enable/disable half tone
def on_checkbutton_change2(*args):
    if halftone_button2.get() == 1:
        print("Halftone is enabled")
    else:
        print("Halftone is disabled")
    adjust_image()

halftone_button2 = IntVar()
halftone_button2.trace("w", on_checkbutton_change2)
halftone_button = Checkbutton(root, text="Halftone", variable=halftone_button2)
halftone_button.pack()

#slider for halftone spacing
halftone_spacing = Scale(root, from_=1, to=20, resolution=1, length=400, label="Halftone Spacing", orient=HORIZONTAL, command=adjust_image_from_scales)
halftone_spacing.set(8)
halftone_spacing.pack()

#toggle button to enable to print image configuration after the image on the reciept
def on_checkbutton_change3(*args):
    if print_config_button2.get() == 1:
        print("Print config is enabled")
    else:
        print("Print config is disabled")
    adjust_image()

print_config_button2 = IntVar() #variable for the button
print_config_button2.trace("w", on_checkbutton_change3) #trace the button
print_config_button = Checkbutton(root, text="Print Config", variable=print_config_button2) #create the button
print_config_button.pack() #pack the button


# Print button
print_button = Button(root, text="Print", command=print_image)
print_button.pack()

root.mainloop()
