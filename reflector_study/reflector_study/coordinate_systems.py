import numpy as np
from .optical_geometry import z_hybrid

def hcp_lattice_to_cartesian(i, j, k, scale=1, offset_in_x_dir = 0.5, offset_in_y_dir = 0.5):
    """
    hexagonal closed packed lattice


    Comments
    Transforms the addressing coordinates to cartesian coordinates for a hexagonal closed packed lattice.
    The final coordinates are not the optimal for a hexagon, meaning that they are optimised for structural purposes.

    """
    x = i
    y = 3*j/np.sqrt(3)
    z = k

    return scale*np.array([x,y,z])

def hcp_parabolic_transformation(k, x_position, y_position, focal_length, dc_over_pa, scale):
    """
    """
    pos = np.zeros(3)
    pos[0] = x_position*scale
    pos[1] = y_position*scale
    distance_to_z_axis = np.hypot(pos[0], pos[1])
    pos[2] = k + z_hybrid(distance_to_z_axis, focal_length, dc_over_pa)
    return pos

def nodal_distance_in_polar_coordinates(i,j,k,lattice_grid):

    distance_r = np.hypot(lattice_grid[i][j][k][0], lattice_grid[i][j][k][1])

    return distance_r



"""
def hcp_axis_offset(i,j,k, scale, offset_in_x_dir, offset_in_y_dir):
    pos = hcp_lattice_to_cartesian(i, j, k ,scale)
    for n in range(i):
        for m in range(j):
            for l in range(0,k):
                pos[0] = l*pos[0]*offset_in_x_dir + pos[0]
                pos[1] = l*pos[1]*offset_in_y_dir + pos[1]
                return pos
"""
"""
def hcp_offset(i, j, k, scale=1, offset_in_x_dir = 0.5, offset_in_y_dir = 0.5):
    x = np.zeros(k)
    y = np.zeros(k)
    for l in range(1,k):
        x[l] = i+x[l-1]*offset_in_x_dir
        y[l] = 3*j/np.sqrt(3) + y[l-1]*offset_in_y_dir
        z = k
"""
