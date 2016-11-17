import numpy as np


def node_position(nodes, ijk):
    return nodes[ijk[0], ijk[1], ijk[2]]


def node_in_range(nodes, ijk):
    i_valid = ijk[0] >= 0 and ijk[0] < nodes.shape[0]
    j_valid = ijk[1] >= 0 and ijk[1] < nodes.shape[1]
    k_valid = ijk[2] >= 0 and ijk[2] < nodes.shape[2]
    return i_valid and j_valid and k_valid


def bar_start_and_end_position(nodes, bar):
    start = node_position(nodes, bar[0])
    end = node_position(nodes, bar[1])
    return start, end


def bar_in_range(nodes, bar):
    start_is_in_range = node_in_range(nodes, bar[0])
    end_is_in_range = node_in_range(nodes, bar[1])
    return start_is_in_range and end_is_in_range


def bar_length(nodes, bar):
    start = node_position(nodes, bar[0])
    end = node_position(nodes, bar[1])
    return np.linalg.norm(end - start)


def mirror_tripod_center(nodes, mirror_tripod):
    A = node_position(nodes, mirror_tripod[0])
    B = node_position(nodes, mirror_tripod[1])
    C = node_position(nodes, mirror_tripod[2])
    return (A + B + C)/3.0


def mirror_tripod_surface_normal(nodes, mirror_tripod):
    A = node_position(nodes, mirror_tripod[0])
    B = node_position(nodes, mirror_tripod[1])
    C = node_position(nodes, mirror_tripod[2])
    AB = B - A
    AC = C - A
    return np.cross(AB, AC)


def mirror_tripod_x(nodes, mirror_tripod):
    A = node_position(nodes, mirror_tripod[0])
    B = node_position(nodes, mirror_tripod[1])
    AB = B - A
    return AB/np.linalg.norm(AB)


def mirror_tripod_z(nodes, mirror_tripod):
    surface_normal = mirror_tripod_surface_normal(nodes, mirror_tripod)
    return surface_normal/np.linalg.norm(surface_normal)


def mirror_tripod_y(nodes, mirror_tripod):
    z_axis = mirror_tripod_z(nodes, mirror_tripod)
    x_axis = mirror_tripod_x(nodes, mirror_tripod)
    return np.cross(x_axis, z_axis)