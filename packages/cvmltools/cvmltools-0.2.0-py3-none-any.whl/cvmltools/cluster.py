import cv2
import numpy as np

def c_t_m(contour, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
    return mask

def kmeansByShape(image, contour, maxk, mink):
    try:
        height, width = image.shape[:2]
        shape = image.shape
        x = int(width / 2)
        y = int(height / 2)
        mask1 = c_t_m(contour, shape)
        maskw = np.zeros_like(image)
        maskb = np.full_like(image, 255)
        cv2.circle(maskw, (x, y), maxk, 255, -1)
        cv2.circle(maskb, (x, y), mink, 0, -1)
        mask = cv2.bitwise_and(maskw, maskb)
        intermask = cv2.bitwise_and(mask1, mask)
        intercontours, hierarchy = cv2.findContours(intermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return intercontours, hierarchy
    except Exception:
        return -1

def gmmByShape(image, contour, k):
    try:
        height, width = image.shape[:2]
        shape = image.shape
        x = int(width / 2)
        y = int(height / 2)
        mask1 = c_t_m(contour, shape)
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (x, y), k, 255, thickness=cv2.FILLED)
        intermask = cv2.bitwise_and(mask1, mask)
        intercontours, hierarchy = cv2.findContours(intermask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return intercontours, hierarchy
    except Exception:
        return -1
def kmeansByPoint(image, maxk, mink):
    try:
        height, width = image.shape[:2]
        x = int(width / 2)
        y = int(height / 2)
        maskfi = np.zeros((height, width), dtype=np.uint8)
        maskfa = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(maskfi, (x, y), mink, 255, thickness=cv2.FILLED)
        ficore = cv2.bitwise_and(image, maskfi)
        cv2.circle(maskfa, (x, y), maxk, 255, thickness=cv2.FILLED)
        fiall = cv2.bitwise_and(image, maskfa)
        valuefi = np.sum(ficore)  # 7734001  10877053
        valuefa = np.sum(fiall)
        value = valuefi / (valuefi  + valuefa)
        return value
    except Exception:
        return -1