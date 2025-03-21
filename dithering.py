
from PyQt6.QtGui import * 
from PIL import Image
import numpy as np
from utils import *

def load_img_as_rgb(imagePath): 
    image = Image.open(imagePath).convert('RGB')
    return image

def random_dither(image, intensity): 
    img = np.array(image, dtype=np.uint8)
    noise = np.random.randint(0, 256, size=img.shape, dtype=np.uint8) * intensity

    dithered = np.where(img > noise, 255, 0).astype(np.uint8)

    return Image.fromarray(dithered)

 
def bayer_dither(image, idx, threshold_value): 
    img = np.array(image, dtype = np.float32) / 255.0

    h, w = img.shape
    matrix_size = matrices[idx].shape[0]

    threshold_map = np.tile(matrices[idx], (h // matrix_size + 1, w // matrix_size + 1))
    threshold_map = threshold_map[:h, :w]

    dithered_array = (img>threshold_map).astype(np.uint8) * threshold_value
        
    dithered_image = Image.fromarray(dithered_array, mode='L')
    
    return dithered_image


def floyd_steinberg_dither(image, mode, intensity): 
    img = np.array(image, dtype=np.float32) 

    if mode == "L": 
        h, w, = img.shape
    elif mode == "RGB":
        h, w, _ = img.shape 

    diffusion = [
        (1, 0, 7 / 16),
        (-1, 1, 3 / 16),
        (0, 1, 5 / 16),
        (1, 1, 1 / 16)
    ]

    for y in range(h): 
        for x in range(w): 
            oldpixel = img[y, x].copy()
            newpixel = np.round(oldpixel / 255) * 255
            img[y, x] = newpixel
            error = (oldpixel - newpixel) * intensity
            
            for dx, dy, factor in diffusion: 
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h: 
                    img[ny, nx] += error * factor
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))



    
