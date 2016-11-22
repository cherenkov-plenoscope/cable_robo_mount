import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from . import add2ax_flat

def overview(bars, nodes, mirror_tripods=None, fixtures=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x/m')
    ax.set_ylabel('y/m')
    ax.set_zlabel('z/m')

    add2ax_flat.add2ax_bars(ax, nodes, bars)

    if mirror_tripods is not None:
        add2ax_flat.add2ax_mirror_tripods(ax, nodes, mirror_tripods)

    if fixtures is not None:
        add2ax_flat.add2ax_fixtures(ax, nodes, fixtures)

    plt.show()
