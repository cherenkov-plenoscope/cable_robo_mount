import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

#plotting bars
def plot_bars_mirror_nodes_xyz(node_numbers_xyz, facet_supporting_nodes_xyz_x, facet_supporting_nodes_xyz_y, facet_supporting_nodes_xyz_z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    start_position = np.zeros((node_numbers_xyz.shape[0],3))
    end_position = np.zeros((node_numbers_xyz.shape[0],3))
    for i in range(node_numbers_xyz.shape[0]):
        try:
            start_position[i] = node_numbers_xyz[i,0]
            end_position[i] = node_numbers_xyz[i,1]

            ax.plot(
                [start_position[i,0], end_position[i,0]],
                [start_position[i,1], end_position[i,1]],
                [start_position[i,2], end_position[i,2]],'b')
            ax.set_title('Space frame for one facet')
            ax.set_xlabel('x Axis')
            ax.set_ylabel('y Axis')
            ax.set_zlabel('z Axis')

            ax.set_xlim(-7, 7)
            ax.set_ylim(-7, 7)
            ax.set_zlim(-3, 1)

            ax.view_init(elev=20, azim=45)              # elevation and angle
            ax.dist=12                                  # distance

            ax.scatter(facet_supporting_nodes_xyz_x, facet_supporting_nodes_xyz_y, facet_supporting_nodes_xyz_z, c = "red" , marker = "o")         #color = "red" etc marker is the symbol
        except IndexError:
            pass


    plt.show()
