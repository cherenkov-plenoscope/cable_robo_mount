import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def z_Parabola(radius, focal_length):
    return 1.0/(4.0*focal_length)*radius**2; 

def lattice(i,j,k,r=1):
    x = np.sqrt(3)/2*(i + 0.5*k)
    y = j + 0.5*k
    z = k
    return r*np.array([x,y,z])

outer_radius = 25
i_radius = 4
j_radius = 4
k_radius = 3
nodes = np.zeros(shape=(2*i_radius+1,2*j_radius+1,k_radius,3))
bars = []
mirror_tripods = []
for i in range(2*i_radius+1):
    for j in range(2*j_radius+1):
        for k in range(k_radius):
            xyz = lattice(i-i_radius,j-j_radius,-k)
            xyz[2]+= z_Parabola(np.hypot(xyz[0], xyz[1]), 25)
            nodes[i,j,k] = xyz

            # Bars in between layers
            bars.append(np.array([[i, j, k],[i,  j,  k+1]]))
            bars.append(np.array([[i, j, k],[i,  j+1,k+1]]))
            bars.append(np.array([[i, j, k],[i+1,j,  k+1]]))
            bars.append(np.array([[i, j, k],[i+1,j+1,k+1]]))

            # Bars on layer
            bars.append(np.array([[i, j, k],[i,  j+1,k]]))
            bars.append(np.array([[i, j, k],[i+1,j,  k]]))

            # Nodes mirror tripod
            if k == 0: # only on top layer
                if j-1>0: # no facets to overhanging the negative index edge
                    if np.mod(j,2) == 0: # Each 2nd in j
                        if np.mod(i+1,4) == 0: #Each 4th in i
                                mirror_tripods.append(
                                    np.array([
                                        [i, j, k],
                                        [i+2,  j+1,k],
                                        [i+2,  j-1,k]]))
                        elif np.mod(i+1,2) == 0: #Each other 4th in i
                                mirror_tripods.append(
                                    np.array([
                                        [i, j+1, k],
                                        [i+2,  j+1+1,k],
                                        [i+2,  j-1+1,k]]))
bars = np.array(bars)
mirror_tripods = np.array(mirror_tripods)

def plot_bars(bars, nodes, mirror_tripods=None):
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