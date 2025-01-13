import cv2
import numpy as np

def c_t_m(contour, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
    return mask

def laplacian1(contour, image, x, y, r, rs):
    height, width = image.shape[:2]
    shape = image.shape
    mask1 = c_t_m(contour, shape)
    maskw = np.zeros_like(image)
    maskb = np.full_like(image, 255)
    cv2.circle(maskw, (x, y), r - 20, 255, -1)
    cv2.circle(maskb, (x, y), rs, 0, -1)
    mask = cv2.bitwise_and(maskw, maskb)
    intermask = cv2.bitwise_and(mask1, mask)
    return intermask
