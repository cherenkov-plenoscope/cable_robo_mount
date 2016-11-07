import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from . import generate_plot_bars as gpb

#generate mirror_tripods Sebastians way

def mirror_tripods(supposed_i, supposed_j, supposed_k, lattice_grid):
    mirror_tripods = []
    for i in range(-supposed_i+1, supposed_i-1,2):
        for j in range(-supposed_j+1, supposed_j-1,2):
            # mirror_tripods on layer
            mirror_tripods.append(np.array([[i, j, 0],[i+1,  j+1,0]]))
            mirror_tripods.append(np.array([[i+1, j+1, 0],[i+2,  j+2,0]]))
            mirror_tripods.append(np.array([[i+1, j+1, 0],[i+2,j,  0]]))
            mirror_tripods.append(np.array([[i+2, j, 0],[i+3, j-1,  0]]))
            mirror_tripods.append(np.array([[i, j, 0],[i+2,  j,0]]))
            mirror_tripods.append(np.array([[i-1, j-1, 0],[i+1,  j-1,0]]))

    mirror_tripods = np.array(mirror_tripods)
    return mirror_tripods

#plotting mirror_tripods
def plot_mirror_tripods(mirror_tripods, lattice_grid, bars):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for bar in mirror_tripods:
        try:
            start_position = lattice_grid[bar[0,0], bar[0,1], bar[0,2]]
            end_position = lattice_grid[bar[1,0], bar[1,1], bar[1,2]]

            ax.plot(
                [start_position[0], end_position[0]],
                [start_position[1], end_position[1]],
                [start_position[2], end_position[2]],
                'b', linewidth = 3)
            ax.set_title('Space frame for one facet')
            ax.set_xlabel('x Axis')
            ax.set_ylabel('y Axis')
            ax.set_zlabel('z Axis')

            ax.set_xlim(-4, 4)
            ax.set_ylim(-4, 4)
            ax.set_zlim(-3, 1)

            ax.view_init(elev=20, azim=45)              # elevation and angle
            ax.dist=12                                  # distance

        except IndexError:
            pass

    for bar in bars:
        try:
            start_position = lattice_grid[bar[0,0], bar[0,1], bar[0,2]]
            end_position = lattice_grid[bar[1,0], bar[1,1], bar[1,2]]

            ax.plot(
                [start_position[0], end_position[0]],
                [start_position[1], end_position[1]],
                [start_position[2], end_position[2]],
                'b', color = 'DarkMagenta')
            ax.set_title('Space frame for one facet')
            ax.set_xlabel('x Axis')
            ax.set_ylabel('y Axis')
            ax.set_zlabel('z Axis')

            ax.set_xlim(-4, 4)
            ax.set_ylim(-4, 4)
            ax.set_zlim(-3, 1)

            ax.view_init(elev=20, azim=45)              # elevation and angle
            ax.dist=12                                  # distance

        except IndexError:
            pass


    plt.show()
