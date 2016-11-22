import numpy as np
import matplotlib.pyplot as plt
from ..tools.tools import bar_length
from ..tools.tools import list_of_angles_between_neighbouring_bars


def histogram_bar_length(nodes, bars):
    bar_lengths = []
    for bar in bars:
        bar_lengths.append(bar_length(nodes, bar))
    bar_lengths = np.array(bar_lengths)

    plt.figure()
    plt.xlabel("length of bar /m")
    plt.ylabel("#/1")
    plt.title('Bar length distribution')
    number_of_bins = int(np.sqrt(bar_lengths.shape[0]))
    plt.hist(bar_lengths, bins=number_of_bins)
    plt.grid(True)
    plt.show()


def histogram_angles(joints, bars, nodes):
    angles = list_of_angles_between_neighbouring_bars(joints, bars, nodes)
    angles_array = np.array(angles.copy())

    plt.figure()
    plt.xlabel("angle /°")
    plt.ylabel("#/1")
    plt.title('Angle between bars distribution')
    number_of_bins = int(np.sqrt(angles_array.shape[0]))
    plt.hist(np.rad2deg(angles_array), bins=number_of_bins)
    plt.grid(True)
    plt.show()