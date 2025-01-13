import cv2
import numpy as np

def c_t_m(contour, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
    return mask

def sobel1(contour, image, x, y, r, rs):
    height, width = image.shape[:2]
    shape = image.shape
    mask1 = c_t_m(contour, shape)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (x, y), rs, 255, thickness=cv2.FILLED)
    intermask = cv2.bitwise_and(mask1, mask)
    return intermask