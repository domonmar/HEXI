import cv2
import numpy as np
from helpers import nearest_odd


def find_circles(
        img,
        edge_detect_threshold,
        circle_threshold,
        radius,
        radius_tolerance,
        center_distance_mult,
        blur,
        threshold_area,
        threshold_subtraction):

    if len(img) == 0:
        return []

    preprocessed_img = img

    if blur > 0:
        preprocessed_img = cv2.medianBlur(preprocessed_img, nearest_odd(blur))

    if threshold_area > 0:
        preprocessed_img = cv2.adaptiveThreshold(
            preprocessed_img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            nearest_odd(threshold_area),
            threshold_subtraction)

    radius_tolerance_abs = radius * radius_tolerance / 100.0
    min_radius = max(1, round(radius - radius_tolerance_abs))
    max_radius = max(1, round(radius + radius_tolerance_abs))
    min_center_distance = min_radius * center_distance_mult

    circles = cv2.HoughCircles(
        preprocessed_img,
        cv2.HOUGH_GRADIENT,
        1,
        min_center_distance,
        param1=edge_detect_threshold,
        param2=circle_threshold,
        minRadius=min_radius,
        maxRadius=max_radius)

    if circles is None:
        return []

    return np.uint16(np.around(circles[0, :]))


class OpenCVHoughDetector:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "OpenCV-Hough"

    @staticmethod
    def get_parameter_list():
        return [
            ['Edge detect threshold', 0, 200, 120],
            ['Circle threshold', 1, 10, 4],
            ['Radius', 0, 100, 10],
            ['Radius tolerance %', 0, 100, 10],
            [r'Center distance (% of Radius)', 200, 800, 100],
            ['Blur', 0, 15, 3],
            ['Thresholding area', 0, 151, 0],
            ['Thresholding subtraction', 0, 100, 4],
        ]

    @staticmethod
    def evaluate(img, parameters):
        return find_circles(
            img,
            parameters['Edge detect threshold'],
            parameters['Circle threshold'],
            parameters['Radius'],
            parameters['Radius tolerance %'],
            parameters[r'Center distance (% of Radius)'] / 100.0,
            parameters['Blur'],
            parameters['Thresholding area'],
            parameters['Thresholding subtraction']
        )
