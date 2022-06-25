import cv2
import time

from process import process_image
from helpers import convert_image_opencv_to_pil
from processors.classifiers.classification_brightness import BrightnessClassifier, BrightnessClassifierAdaptive
from processors.classifiers.classification_distance import DistanceClassifier
from processors.none_processor import NoneProcessor
from detectors.detector_opencv_hough import OpenCVHoughDetector
from drawing_utilities import draw_circles_on_image

class ImageProcessor:
    def __init__(self, image_path):
        self.on_focus_callback = None

        # Display configuration options:
        self.draw_perimeters = True
        self.draw_info_text = True

        # Image processing results:
        self.circles = []
        self.processor_results = []

        self.load_image(image_path)

        # Image processing options:
        image_size = self.get_image_size()
        self.active_crop_area = (0, 0, image_size[0], image_size[1])

        # Algorithms:
        self.detector = None
        self.processor = None

    @staticmethod
    def get_available_processors():
        return [BrightnessClassifier, BrightnessClassifierAdaptive, DistanceClassifier, NoneProcessor]

    @staticmethod
    def get_available_detectors():
        return [OpenCVHoughDetector]

    def load_image(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def evaluate(self, detector, processor, parameters):
        start_time = time.perf_counter()

        self.detector = detector
        self.processor = processor

        # Get cropped area:
        x0, y0, x1, y1 = self.active_crop_area
        cropped_img = self.grayscale_image[y0:y1, x0:x1]

        # Process cropped image:
        self.circles, self.processor_results = process_image(
            cropped_img,
            self.detector,
            parameters,
            self.processor,
            parameters)

        # Update result image:
        self.update_result_image()

        print('Evaluated in ' + str(time.perf_counter() - start_time) + ' seconds')

    def set_active_crop_area(self, active_crop_area):
        self.active_crop_area = active_crop_area
        self.circles = []
        self.processor_results = []

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

    def update_result_image(self):
        self.result_image = convert_image_opencv_to_pil(self.image)
        
        if self.processor is not None and hasattr(self.processor, 'update_result_image') and callable(self.processor.update_result_image):
            draw_parameters = {
                'draw_perimeters' : self.draw_perimeters, 
                'draw_info_text' : self.draw_info_text
                }
            self.processor.update_result_image(self.result_image, self.active_crop_area, self.circles, self.processor_results, draw_parameters)
        else:
            draw_circles_on_image(self.result_image, self.active_crop_area, self.circles, self.draw_perimeters, None, [(50, 50, 255)])

    def get_image_size(self):
        return (len(self.image[0]), len(self.image))
