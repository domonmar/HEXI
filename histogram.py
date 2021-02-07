import numpy as np
import matplotlib.pyplot as plt


def show_histogram(data):
    plt.close()

    bins = np.arange(min(data), max(data) + 1.5) - 0.5

    n, bins, patches = plt.hist(data, bins=bins)

    plt.xlabel('Diameter (nm)')
    plt.ylabel('Count')
    plt.title(r'Histogram of circle diameters')
    plt.grid(True)

    plt.show(block=False)
