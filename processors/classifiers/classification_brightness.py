from matplotlib.pyplot import draw
import numpy as np
import cv2
from .classification_common import update_result_image

def circle_avg_brightness(circle, img):
    sum_brightness = 0
    counter = 0

    cx = int(circle[0])
    cy = int(circle[1])
    cr = int(circle[2])

    if cx - cr < 0 or cx + cr >= len(img[0]) or cy - cr < 0 or cy + cr >= len(img):
        return 0

    for x in range(cx - cr, cx + cr):
        for y in range(cy - cr, cy + cr):
            sum_brightness += img[y, x]
            counter += 1

    return int(sum_brightness / counter)


def classify_circle(circle, brightness_threshold):
    """ Classify circle according to circle area brightness

        Returns 1 if circle is "good", 0 if "loose" """

    brightness = circle[3]
    return 1 if brightness < brightness_threshold else 0


def calculate_circle_brightnesses(circles, img):
    def f(c): return circle_avg_brightness(c, img)
    brightnesses = np.array(list(map(f, circles)))
    return np.c_[circles, brightnesses]


def calculate_median_brightness(circles):
    if len(circles) == 0:
        return 0
    return np.median(circles[:, 3])


def classify_circles_by_brightness(img, circles, loose_circle_threshold):
    circles = calculate_circle_brightnesses(circles, img)
    median_brightness = calculate_median_brightness(circles)
    classification_threshold = median_brightness * loose_circle_threshold
    classification = list(map(lambda circle: classify_circle(circle, classification_threshold), circles))
    return classification


def classify_circles_by_brightness_adaptive(img, circles, loose_circle_threshold, averaging_area):
    circles = calculate_circle_brightnesses(circles, img)

    img_averages = cv2.blur(img, (averaging_area, averaging_area))

    classification = []

    for circle in circles:
        circle_x = int(circle[0])
        circle_y = int(circle[1])
        circle_x = max(0, min(circle_x, len(img[0])-1))
        circle_y = max(0, min(circle_y, len(img)-1))

        classification.append(classify_circle(circle, img_averages[circle_y, circle_x] * loose_circle_threshold))

    return classification


class BrightnessClassifier:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "Brightness"

    @staticmethod
    def get_parameter_list():
        return [
            ['Loose circle tolerance', 1, 100, 55],
        ]

    @staticmethod
    def evaluate(img, circles, parameters):
        return classify_circles_by_brightness(img, circles, parameters['Loose circle tolerance'] / 50.0)

    @staticmethod
    def update_result_image(img, active_image_area, circles, results : list[int], draw_parameters):
        update_result_image(img, active_image_area, circles, results, draw_parameters)


class BrightnessClassifierAdaptive:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "Brightness-Adaptive"

    @staticmethod
    def get_parameter_list():
        return [
            ['Loose circle tolerance', 1, 100, 55],
            ['Averaging area', 5, 500, 100]
        ]

    @staticmethod
    def evaluate(img, circles, parameters):
        return classify_circles_by_brightness_adaptive(img, circles, parameters['Loose circle tolerance'] / 50.0, parameters['Averaging area'])

    @staticmethod
    def update_result_image(img, active_image_area, circles, results : list[int], draw_parameters):
        update_result_image(img, active_image_area, circles, results, draw_parameters)
        
