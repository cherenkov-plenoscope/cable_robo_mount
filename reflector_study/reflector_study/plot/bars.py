import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from ..tools import node_position


def bars(bars, nodes, mirror_tripods=None, fixtures=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x/m')
    ax.set_ylabel('y/m')
    ax.set_zlabel('z/m')

    for bar in bars:
        start = node_position(nodes, bar[0])
        end = node_position(nodes, bar[1])
        ax.plot([start[0], end[0]],
                [start[1], end[1]],
                [start[2], end[2]],'b')

    if mirror_tripods is not None:
        for mirror_tripod in mirror_tripods:
            n1 = node_position(nodes, mirror_tripod[0])
            n2 = node_position(nodes, mirror_tripod[1])
            n3 = node_position(nodes, mirror_tripod[2])
            ax.plot([n1[0], n2[0]],
                    [n1[1], n2[1]],
                    [n1[2], n2[2]],'r',linewidth=3.0) 
            ax.plot([n2[0], n3[0]],
                    [n2[1], n3[1]],
                    [n2[2], n3[2]],'r',linewidth=3.0) 
            ax.plot([n3[0], n1[0]],
                    [n3[1], n1[1]],
                    [n3[2], n1[2]],'r',linewidth=3.0)

    if fixtures is not None:
        for fixture in fixtures:   
            fix_pos = node_position(nodes, fixture)
            ax.scatter( [fix_pos[0]],
                        [fix_pos[1]],
                        [fix_pos[2]],
                        c='g',
                        marker='o') 
    plt.show()