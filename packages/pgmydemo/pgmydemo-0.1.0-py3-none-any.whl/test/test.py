import cv2
import copy
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os

from package.laplacian import laplacian
from package.sobel import sobel
def cv_show(name, img):
    height, width = img.shape[:2]
    target_length = 500
    scale = target_length / max(width, height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    image = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def dist(pa, pb):
    pa = np.array(pa)
    pb = np.array(pb)
    distance = cv2.norm(pa, pb, cv2.NORM_L2)
    return distance


def cpcontours(image, contours, hierarchy):
    pixel_count_total = 0
    for i in range(len(contours)):
        if hierarchy[0][i][3] == -1:  # 父轮廓（没有父轮廓）
            mask = np.zeros_like(image)
            cv2.drawContours(mask, [contours[i]], -1, 255, thickness = cv2.FILLED)
            # 检查子轮廓
            child_idx = hierarchy[0][i][2]
            while child_idx!= -1:
                cv2.drawContours(mask, [contours[child_idx]], -1, 255, thickness = cv2.FILLED)
                child_idx = hierarchy[0][child_idx][0]
            pixel_count_total += cv2.countNonZero(mask)
    return pixel_count_total
def detect_scratches(image):
    gray_image = image
    height, width = image.shape[:2]
    shape = image.shape
    imagest = copy.deepcopy(image)
    imagest = cv2.cvtColor(imagest, cv2.COLOR_GRAY2BGR)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_image = clahe.apply(blurred_image)
    edges2 = cv2.Canny(enhanced_image, threshold1=90, threshold2=200)
    cv_show('edges2', edges2)
    x = int(width/2) ; y = int(height/2) ; r = int(height/2) ;rs = int(height / 2 * 0.45);rs1 = int(height / 2 * 0.39)
    contours, _ = cv2.findContours(edges2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours = list(contours)

    areas = [cv2.contourArea(contour) for contour in contours]
    max_index = np.argmax(areas)
    contours.pop(max_index)

    new_contours = []
    for contour in contours:
        if len(contour) <= 1000 and len(contour) > 5:
            new_contours.append(contour)

    for contour in new_contours:
        intermask = sobel(contour, image, x, y, r, rs1)
        if intermask is not None:
            intercontours, hierarchy = cv2.findContours(intermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for citem in intercontours:
                length = cv2.arcLength(citem, True)
                if length > 100 :
                    cv2.drawContours(imagest, [citem], 0, (0, 0, 255), 6)
                    print("A Scratch length " + str(length))
    for contour in new_contours:
        intermask = laplacian(contour,image, x, y, r, rs)
        if intermask is not None:
            intercontours, hierarchy = cv2.findContours(intermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for citem in intercontours:
                length = cv2.arcLength(citem, True)
                if length > 100 :
                    cv2.drawContours(imagest, [citem], 0, (0, 0, 255), 6)
                    print("B Scratch length " + str(length))
            for citem in intercontours:
                length = cv2.arcLength(citem, True)
                if length > 0 :
                    cv2.drawContours(imagest, [citem], 0, (0, 255, 0), 6)
                    print("B spot length " + str(length))
    cv_show('Detected Scratches', imagest)

def circleBig(image):
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circlesb = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=100, param1=30, param2=30, minRadius=360, maxRadius=380)
    if circlesb is not None:
        circlesb = np.round(circlesb[0, :]).astype("int")
        maskw = np.zeros_like(gray)
        maskb = np.full_like(gray, 255)
        for (x1, y1, r1) in circlesb:
            x = x1; y=y1; r=r1
            cv2.circle(gray, (x, y), r, 0, 6)
            cv2.circle(maskw, (x, y), r, 255, -1)
            cv2.circle(maskb, (x, y), r, 0, -1)
            extrub = cv2.bitwise_and(gray, gray, mask=maskw)
            top_left_x = max(0, x - r)
            top_left_y = max(0, y - r)
            bottom_right_x = min(width, x + r)
            bottom_right_y = min(height, y + r)
            areab = extrub[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
            break
        return areab
    return None

def deficore(image):
    height, width = image.shape[:2]
    gray = image
    circlesb = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=100, param1=30, param2=30, minRadius=140, maxRadius=180)
    if circlesb is not None:
        circlesb = np.round(circlesb[0, :]).astype("int")
        for (x1, y1, r1) in circlesb:
            x = x1; y=y1; r=r1
            cv2.circle(gray, (x, y), r, 0, 6)
        cv_show('c', gray)
        return False
    return True

def process_images_in_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)
        image = cv2.imread(image_path)
        circleb = circleBig(image)
        cv_show('circleb', circleb)
        if circleb is not None:
            #fiberbool = deficore(circleb)
            detect_scratches(circleb)

if __name__ == '__main__':
    input_directory = 'images'
    output_directory = 'imagesoutput/'
    process_images_in_directory(input_directory, output_directory)