import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def bars(bars, nodes, mirror_tripods=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for bar in bars:
        try:
            start_position = nodes[bar[0,0], bar[0,1], bar[0,2]]
            end_position = nodes[bar[1,0], bar[1,1], bar[1,2]]

            ax.plot(
                [start_position[0], end_position[0]],
                [start_position[1], end_position[1]],
                [start_position[2], end_position[2]],'b')
        except IndexError:
            pass

    """
    nodes_flat = []
    for i in range(nodes.shape[0]):
        for j in range(nodes.shape[1]):
            for k in range(nodes.shape[2]):
                nodes_flat.append(nodes[i,j,k,:])
    nodes_flat = np.array(nodes_flat)

    ax.scatter(
        nodes_flat[:,0],
        nodes_flat[:,1],
        nodes_flat[:,2],
        'or')
    """

    if mirror_tripods is not None:
        for mirror_tripod in mirror_tripods:
            try:
                mt = mirror_tripod
                n1 = nodes[mt[0,0], mt[0,1], mt[0,2]]
                n2 = nodes[mt[1,0], mt[1,1], mt[1,2]]
                n3 = nodes[mt[2,0], mt[2,1], mt[2,2]]
                ax.plot(
                    [n1[0], n2[0]],
                    [n1[1], n2[1]],
                    [n1[2], n2[2]],'r',linewidth=3.0) 
                ax.plot(
                    [n2[0], n3[0]],
                    [n2[1], n3[1]],
                    [n2[2], n3[2]],'r',linewidth=3.0) 
                ax.plot(
                    [n3[0], n1[0]],
                    [n3[1], n1[1]],
                    [n3[2], n1[2]],'r',linewidth=3.0)            
            except IndexError:
                pass
    plt.show()