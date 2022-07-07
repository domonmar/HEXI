from math import pi
from numpy import average
from scipy import spatial
import matplotlib.pyplot as plt


class RadialDistributionFunction:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "Radial distribution function"

    @staticmethod
    def get_parameter_list():
        return [
            ['r min', 1, 100, 10],
            ['r max', 1, 100, 20],
            ['dr', 1, 10, 2]
        ]

    @staticmethod
    def evaluate(img, circles, parameters):
        r_min = parameters['r min']
        r_max = parameters['r max']
        delta_r = parameters['dr']

        result = []#list[tuple[int, float]]
        image_area = len(img[0]) * len(img)
        particle_density = len(circles) / image_area

        for r in range(r_min, r_max):
            points = list((circle[0], circle[1]) for circle in circles)
            tree = spatial.cKDTree(points)
            neighbors_within_r = tree.query_ball_point(points, r, return_length=True)
            neighbors_within_r_plus_dr = tree.query_ball_point(points, r + delta_r, return_length=True)
            neighbors_in_annulus = neighbors_within_r_plus_dr - neighbors_within_r
            average_neighbors_in_annulus = average(neighbors_in_annulus)
            result_corrected_for_annulus_area = average_neighbors_in_annulus / (2 * pi * r * delta_r)
            result_corrected_for_particle_density = result_corrected_for_annulus_area / particle_density
            result.append((r, result_corrected_for_particle_density))

        print(result, sep='\n')

        plt.plot(*zip(*result))
        plt.xlabel("r")
        plt.ylabel("g(r)")
        plt.show()

        return result
    
