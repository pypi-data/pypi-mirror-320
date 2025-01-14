import cv2
import copy
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os

#import gmmByShape
from cvmltools.cluster import gmmByShape
from cvmltools.cluster import kmeansByPoint

coordx = 5
coordy = 5

def putcontext(image, str, coord):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 0, 0)  # 蓝色，格式为(B, G, R)
    thickness = 2
    cv2.putText(image, str, coord, font, font_scale, color, thickness)
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



def detect_defect(image):
    global coordx,coordy
    gray_image = image
    height, width = image.shape[:2]
    shape = image.shape
    imagest = copy.deepcopy(image)
    imagest = cv2.cvtColor(imagest, cv2.COLOR_GRAY2BGR)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_image = clahe.apply(blurred_image)
    edges2 = cv2.Canny(enhanced_image, threshold1=90, threshold2=200)
    #cv_show('edges2', edges2)
    r = int(height/2) ;rs = int(height / 2 * 0.45);rs1 = int(height / 2 * 0.39)
    prob = kmeansByPoint(image, r-10, rs1)
    if prob < 0.15:
        str = "fibercore"
        print(str)
        coordy = coordy + 30
        putcontext(imagest, str, (coordx, coordy))

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
        contours, _ = gmmByShape(image, contour, r-20)
        for citem in contours:
            length = cv2.arcLength(citem, True)
            if length > 200 :
                cv2.drawContours(imagest, [citem], 0, (0, 0, 255), 6)
                str = "Scratch:{}".format(int(length))
                print(str)
                coordy = coordy + 30
                putcontext(imagest, str, (coordx, coordy))
    return imagest

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



def process_images_in_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)
        image = cv2.imread(image_path)
        circleb = circleBig(image)
        #cv_show('circleb', circleb)
        if circleb is not None:
            imgres = detect_defect(circleb)
        cv2.imwrite(os.path.join(output_dir, image_file), imgres)

if __name__ == '__main__':
    input_directory = 'images'
    output_directory = 'imagesoutput/'
    process_images_in_directory(input_directory, output_directory)