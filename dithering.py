import numpy as np
from PIL import Image
from numba import njit
from utils import matrices

def load_img_as_rgb(imagePath): 
    return Image.open(imagePath).convert('RGB')

@njit 
def _apply_floyd_steinberg(img, h, w, diffusion): 
    for y in range(h): 
        for x in range(w): 
            oldpixel = img[y, x]
            # Fast quantize 0 to 255
            newpixel = 255.0 if oldpixel > 127.5 else 0.0 
            img[y, x] = newpixel

            error = (oldpixel - newpixel) * diffusion 

            if x + 1 < w: 
                img[y, x+1] += error * 7 / 16
            if y + 1 < h: 
                if x > 0: 
                    img[y+1, x-1] += error * 3 / 16
                img[y+1, x] += error * 5 / 16
                if x + 1 < w: 
                    img[y+1, x+1] += error * 1 / 16

    return img 

def floyd_steinberg_dither(image, diffusion):
    img = np.array(image, dtype=np.float32) 
    h, w = img.shape 

    result = _apply_floyd_steinberg(img, h, w, diffusion) 
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def random_dither(image, intensity): 
    img = np.array(image, dtype=np.uint8)
    
    noise = np.random.uniform(0, 255, size=img.shape) * intensity

    dithered = np.where(img > noise, 255, 0).astype(np.uint8)

    return Image.fromarray(dithered)

 
def bayer_dither(image, idx, threshold_value=128): 
    img = np.array(image, dtype = np.float32) / 255.0
    h, w = img.shape

    m = matrices[idx]
    m_h, m_w = m.shape
    
    threshold_map = np.tile(m, (int(np.ceil(h/m_h)), int(np.ceil(w/m_w)))) 
    threshold_map = threshold_map[:h, :w]
    
    offset = (threshold_value / 255.0) - 0.5
    threshold_map = np.clip(threshold_map - offset, 0.0, 1.0) 

    dithered_array = (img>threshold_map).astype(np.uint8) * 255 
    
    return Image.fromarray(dithered_array, mode='L') 



