import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

#generate bars Sebastians way

def bars(supposed_i, supposed_j, supposed_k, lattice_grid):
    bars = []
    for i in range(-supposed_i+1, supposed_i-1):
        for j in range(-supposed_j+1, supposed_j-1):
            for k in range(-supposed_k, 1):
                #Bars in between layers
                bars.append(np.array([[i, j, k],[i,  j,  k+1]]))
                if k != 0:
                    bars.append(np.array([[i+1, j, k],[i,  j,k+1]]))
                    bars.append(np.array([[i, j+1, k],[i,j,  k+1]]))
                    bars.append(np.array([[i+1, j+1, k],[i,j,k+1]]))

                # Bars on layer
                bars.append(np.array([[i, j, k],[i,  j+1,k]]))
                bars.append(np.array([[i, j, k],[i+1,j,  k]]))
    bars = np.array(bars)
    return bars


#plotting bars
def plot_bars(bars, lattice_grid):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for bar in bars:
        try:
            start_position = lattice_grid[bar[0,0], bar[0,1], bar[0,2]]
            end_position = lattice_grid[bar[1,0], bar[1,1], bar[1,2]]

            ax.plot(
                [start_position[0], end_position[0]],
                [start_position[1], end_position[1]],
                [start_position[2], end_position[2]],'b')
            ax.set_title('Space frame for one facet')
            ax.set_xlabel('x Axis')
            ax.set_ylabel('y Axis')
            ax.set_zlabel('z Axis')

            ax.set_xlim(-7, 7)
            ax.set_ylim(-7, 7)
            ax.set_zlim(-3, 1)

            ax.view_init(elev=20, azim=45)              # elevation and angle
            ax.dist=12                                  # distance

        except IndexError:
            pass


    plt.show()
