import math
from scipy import spatial
from .classification_common import update_result_image

def point_distance_squared(point_1, point_2):
    return (float(point_2[0]) - float(point_1[0]))**2 + (float(point_2[1]) - float(point_1[1]))**2


# Returns the number of image "sides" the point is within distance of
def count_close_sides(point, image_size, distance):
    counter = 0
    if point[0] < distance:
        counter += 1
    if point[1] < distance:
        counter += 1
    if point[0] + distance > image_size[0]:
        counter += 1
    if point[1] + distance > image_size[1]:
        counter += 1
    return counter


def classify_by_neighbor_count(image_size, circle, neighbor_count, distance):
    # Six neighbors in hexagonal pattern + 1 for itself
    required_neighbors = 7

    # Reduce the number of required neighbors if the circle is close to the side of the image:
    close_sides_count = count_close_sides((circle[0], circle[1]), image_size, distance)
    required_neighbors = required_neighbors - close_sides_count * 3

    # Classify
    return 1 if neighbor_count >= required_neighbors else 0


def classify_circles_by_distance(img, circles, radius, loose_circle_threshold):
    image_size = (len(img[0]), len(img))
    classification = []

    distance = radius * 2 * loose_circle_threshold

    points = list((circle[0], circle[1]) for circle in circles)
    tree = spatial.cKDTree(points)
    neighbors_count = tree.query_ball_point(points, distance, return_length=True)

    for i in range(len(circles)):
        classification.append(classify_by_neighbor_count(image_size, circles[i], neighbors_count[i], distance))

    return classification


class DistanceClassifier:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "Distance"

    @staticmethod
    def get_parameter_list():
        return [
            ['Loose circle tolerance', 1, 100, 50],
            ['Radius', 0, 100, 10],
        ]

    @staticmethod
    def evaluate(img, circles, parameters):
        return classify_circles_by_distance(img, circles, parameters['Radius'], (parameters['Loose circle tolerance'] + 49.0) / 50.0)

    @staticmethod
    def update_result_image(img, active_image_area, circles, results : list[int], draw_parameters):
        update_result_image(img, active_image_area, circles, results, draw_parameters)
