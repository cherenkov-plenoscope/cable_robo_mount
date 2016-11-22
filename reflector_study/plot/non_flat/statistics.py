import numpy as np
import matplotlib.pyplot as plt
from ...non_flat_tools import bar_length


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
