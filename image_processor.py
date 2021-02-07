import PIL
import PIL.ImageDraw
import PIL.ImageFont
import cv2
import math
import time

from process import process_image
from helpers import convert_image_opencv_to_pil
from classifiers.classification_brightness import BrightnessClassifier, BrightnessClassifierAdaptive
from classifiers.classification_distance import DistanceClassifier
from detectors.detector_opencv_hough import OpenCVHoughDetector


class ImageProcessor:
    def __init__(self, image_path):
        self.on_focus_callback = None

        # Display configuration options:
        self.draw_perimeters = True
        self.draw_info_text = True

        # Image processing results:
        self.circles = []
        self.circle_classification = []

        self.load_image(image_path)

        # Image processing options:
        image_size = self.get_image_size()
        self.active_crop_area = (0, 0, image_size[0], image_size[1])

    @staticmethod
    def get_available_classifiers():
        return [BrightnessClassifier, BrightnessClassifierAdaptive, DistanceClassifier]

    @staticmethod
    def get_available_detectors():
        return [OpenCVHoughDetector]

    def load_image(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def evaluate(self, detector, classifier, parameters):
        start_time = time.perf_counter()

        # Get cropped area:
        x0, y0, x1, y1 = self.active_crop_area
        cropped_img = self.grayscale_image[y0:y1, x0:x1]

        # Process cropped image:
        self.circles, self.circle_classification = process_image(
            cropped_img,
            detector,
            parameters,
            classifier,
            parameters)

        # Update result image:
        self.update_result_image()

        print('Evaluated in ' + str(time.perf_counter() - start_time) + ' seconds')

    def calculate_coverage(self):
        circle_count = len(self.circles)
        if circle_count > 0:
            x0, y0, x1, y1 = self.active_crop_area
            image_area = (x1 - x0) * (y1 - y0)
            circles_covered_area = sum(math.pi * circle[2] * circle[2] for circle in self.circles)
            return circles_covered_area / image_area
        else:
            return 0.0

    def get_info_text(self):
        info_text = ""

        if self.draw_info_text:
            circle_count = len(self.circles)
            if circle_count > 0:
                good_count = sum(self.circle_classification)
                loose_count = circle_count - good_count
                info_text = (f"{'Total:' :<6}{circle_count:>5} {'Ratio:' :<6}{(float(good_count) / circle_count):>5,.0%}" +
                             f"\n{'HEX:' :<6}{good_count:>5} {'Cvrg:':<6}{self.calculate_coverage():>5,.1%}" +
                             f"\n{'N-HEX:' :<6}{loose_count :>5}")
        return info_text

    def set_active_crop_area(self, active_crop_area):
        self.active_crop_area = active_crop_area
        self.circles = []
        self.circle_classification = []

    def autodetect_crop_area(self):
        # Calculate image derivative in vertical direction:
        dy_image = abs(cv2.Sobel(self.grayscale_image, cv2.CV_64F, 0, 1))

        # For each row, calculate sum of derivatives, this gives a
        # heuristic for the total change in brightness in vertical direction across row:
        dy_rows = list(sum(row) for row in dy_image)
        image_size = self.get_image_size()

        # Set the bottom border to the row where the total derivative first hits a very low
        # value (ignoring the first row where the derivative will be zero). We assume this is
        # where the uniformly colored information panel in the SEM image starts. :
        bottom_border = image_size[1]
        for rownum in range(1, len(dy_rows)):
            if dy_rows[rownum] < image_size[0]:
                bottom_border = rownum
                break

        self.active_crop_area = (0, 0, image_size[0], bottom_border)

    @staticmethod
    def rect_around(x, y, size, offset_x, offset_y):
        x1 = int(x) - int(size) + int(offset_x)
        y1 = int(y) - int(size) + int(offset_y)
        x2 = int(x) + int(size) + int(offset_x)
        y2 = int(y) + int(size) + int(offset_y)
        return [x1, y1, x2, y2]

    def update_result_image(self):
        self.result_image = convert_image_opencv_to_pil(self.image)

        if len(self.circles) > 0:
            # draw cirlces on image:
            draw = PIL.ImageDraw.Draw(self.result_image)

            offset_x, offset_y, dummy_1, dummy_2 = self.active_crop_area

            circle_class_colors = [(255, 0, 0), (0, 255, 0)]
            for index, circle in enumerate(self.circles):
                circle_type = self.circle_classification[index]
                color = circle_class_colors[circle_type]
                center_x = circle[0]
                center_y = circle[1]
                radius = circle[2]
                if self.draw_perimeters:
                    # draw the outer circle
                    draw.ellipse(self.rect_around(center_x, center_y, radius, offset_x,
                                                  offset_y), fill=None, outline=color, width=1)
                # draw the center of the circle
                center_point_size = 1
                draw.rectangle(self.rect_around(center_x, center_y, center_point_size,
                                                offset_x, offset_y), fill=color, outline=None, width=1)

        info_text = self.get_info_text()
        if info_text:
            # draw info text on image:
            draw = PIL.ImageDraw.Draw(self.result_image)

            font = PIL.ImageFont.truetype("cour.ttf", 20)
            text_size = draw.multiline_textsize(info_text, font=font)

            padding = 5

            pos_x = padding
            pos_y = self.result_image.height - text_size[1] - padding

            draw.rectangle([0, pos_y - padding, text_size[0] + padding + padding,
                            self.result_image.height], fill=(255, 255, 255), outline=None, width=1)
            draw.multiline_text((pos_x, pos_y), info_text, font=font, fill=(0, 0, 0))

    def get_image_size(self):
        return (len(self.image[0]), len(self.image))
