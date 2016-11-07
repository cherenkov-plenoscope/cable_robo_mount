import numpy as np
import matplotlib.pyplot as plt

def lengths_of_bars(bars, node_numbers_xyz):

    lengths = []
    for i in range(bars.shape[0]):
        try:
            start, end = node_numbers_xyz[i,0], node_numbers_xyz[i,1]
            lengths.append(np.linalg.norm(np.absolute(end - start)))
        except IndexError:
            pass
    return np.array(lengths)

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
