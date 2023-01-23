import base64
import numpy as np
import cv2

def readb64(data):
    """Function that converts base64 to image in jpeg"""
    img_arr = np.frombuffer(base64.b64decode(data), np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return img