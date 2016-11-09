import numpy as np
import matplotlib.pyplot as plt


def plot_histogram_of_bars(lengths):
    try:
        plt.hist(lengths)

        plt.xlabel("Bar length in meters")
        plt.ylabel("Number of bars")
        plt.title("Histogram of bar lengths")
        plt.axis([0, 4, 0, 200])
        plt.grid(True)

        plt.show()
    except IndexError:
        pass
