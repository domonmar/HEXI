from drawing_utilities import draw_circles_on_image
from drawing_utilities import draw_info_text_on_image
import math
#from collections.abc import Sequence

def calculate_coverage(circles, area):
        circle_count = len(circles)
        if circle_count > 0:
            
            circles_covered_area = sum(math.pi * circle[2] * circle[2] for circle in circles)
            return circles_covered_area / area
        else:
            return 0.0    

def get_info_text(circles, circle_classification, image_area):
    info_text = ""
    circle_count = len(circle_classification)
    if circle_count > 0:
        good_count = sum(circle_classification)
        loose_count = circle_count - good_count
        info_text = (f"{'Total:' :<6}{circle_count:>5} {'Ratio:' :<6}{(float(good_count) / circle_count):>5,.0%}" +
                     f"\n{'HEX:' :<6}{good_count:>5} {'Cvrg:':<6}{calculate_coverage(circles, image_area):>5,.1%}" +
                     f"\n{'N-HEX:' :<6}{loose_count :>5}")
    return info_text

def update_result_image(img, active_image_area : tuple[int, int, int, int], circles, results : list[int], draw_parameters):
    circle_classification = results
    result_image = img
    draw_circles_on_image(result_image, active_image_area, circles, draw_parameters['draw_perimeters'], circle_classification)
    if draw_parameters['draw_info_text']:
        x0, y0, x1, y1 = active_image_area
        image_area = (x1 - x0) * (y1 - y0)
        info_text = get_info_text(circles, circle_classification, image_area)
        draw_info_text_on_image(result_image, info_text)