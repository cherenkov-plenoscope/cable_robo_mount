import numpy as np
from .space_frame_geometry import dish_space_frame_addresses_to_cartesian
from .tools import node_position
from .tools import node_in_range
from .tools import bar_in_range
from .tools import bar_start_and_end_position
from .tools import mirror_tripod_center

def bar_is_part_of_reflector_dish(bar, nodes, geometry):
    if not bar_in_range(nodes, bar):
        return False
    start, end = bar_start_and_end_position(nodes, bar)
    r_start = np.hypot(start[0], start[1])
    r_end = np.hypot(end[0], end[1])
    radii = np.array([r_start, r_end])
    return radii.max() <= geometry.max_outer_radius + geometry.facet_outer_hex_radius


def mirror_tripod_is_part_of_reflector_dish(mirror_tripod, nodes, geometry):
    A_in_range = node_in_range(nodes, mirror_tripod[0])
    B_in_range = node_in_range(nodes, mirror_tripod[1])
    C_in_range = node_in_range(nodes, mirror_tripod[2])

    if A_in_range and B_in_range and C_in_range:
        center = mirror_tripod_center(nodes, mirror_tripod)
        radius = np.hypot(center[0], center[1])
        inside_outer_limit = radius + geometry.facet_outer_hex_radius <= geometry.max_outer_radius 
        outside_inner_limit = radius - geometry.facet_outer_hex_radius > geometry.min_inner_radius 
        return inside_outer_limit and outside_inner_limit
    else:
        return False


def node_is_connected_to_tension_ring(node, geometry):
    radius = np.hypot(node[0], node[1])
    is_inside_outer_limit = radius <= geometry.max_outer_radius
    is_most_outer_node = radius > geometry.max_outer_radius - geometry.facet_spacing
    return is_most_outer_node and is_inside_outer_limit


def generate_nodes(geometry):
    nodes = np.zeros(
        shape=(
            geometry.lattice_range_i, 
            geometry.lattice_range_j, 
            geometry.lattice_range_k, 
            3))

    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
                nodes[i,j,k] = dish_space_frame_addresses_to_cartesian(
                    i=i-geometry.lattice_radius_i,
                    j=j-geometry.lattice_radius_j,
                    k=-k,
                    focal_length=geometry.focal_length,
                    davies_cotton_over_parabola_ratio=geometry.davies_cotton_over_parabola_ratio,
                    scale=geometry.facet_spacing,
                    x_over_z_ratio=geometry.x_over_z_ratio)
    return nodes


def generate_bars(nodes, geometry):
    bars = []
    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):

                bar_o0 = np.array([[i, j, k],[i,  j+1,k]])
                if bar_is_part_of_reflector_dish(bar_o0, nodes, geometry):
                        bars.append(bar_o0)

                bar_o1 = np.array([[i, j, k],[i+1,j,  k]])
                if bar_is_part_of_reflector_dish(bar_o1, nodes, geometry):
                        bars.append(bar_o1)

                if k+1 != geometry.lattice_range_k:
                    bar_i0 = np.array([[i, j, k], [i,  j,  k+1]])
                    if bar_is_part_of_reflector_dish(bar_i0, nodes, geometry):
                        bars.append(bar_i0)

                    bar_i1 = np.array([[i, j, k], [i,  j+1,k+1]])
                    if bar_is_part_of_reflector_dish(bar_i1, nodes, geometry):
                        bars.append(bar_i1)

                    bar_i2 = np.array([[i, j, k], [i+1,j,  k+1]])
                    if bar_is_part_of_reflector_dish(bar_i2, nodes, geometry):
                        bars.append(bar_i2)

                    bar_i3 = np.array([[i, j, k], [i+1,j+1,k+1]])
                    if bar_is_part_of_reflector_dish(bar_i3, nodes, geometry):
                        bars.append(bar_i3)
    return np.array(bars)


def generate_mirrir_tripods(nodes, geometry):
    mirror_tripods = []
    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
 
                if k == 0: # only on top layer
                    if np.mod(i,2) == 0: # Each 2nd in i
                        if np.mod(j+1,2) == 0: #Each 2nd in j
                            mirror_tripod = np.array([
                                    [i,    j,   k],
                                    [i+1,  j+1, k],
                                    [i-1,  j+1, k]])
                            if mirror_tripod_is_part_of_reflector_dish(mirror_tripod, nodes, geometry):
                                mirror_tripods.append(mirror_tripod)
                        else: #Each other 2nd in j
                            mirror_tripod = np.array([
                                    [i+1,   j,   k],
                                    [i+1+1, j+1, k],
                                    [i-1+1, j+1, k]])
                            if mirror_tripod_is_part_of_reflector_dish(mirror_tripod, nodes, geometry):
                                mirror_tripods.append(mirror_tripod)
    return np.array(mirror_tripods)


def generate_connections_to_tension_ring(nodes, geometry):
    fixtures = []
    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
                if node_is_connected_to_tension_ring(nodes[i,j,k], geometry):
                    fixtures.append(np.array([i,j,k]))
    return np.array(fixtures)


def generate_all(geometry):
    nodes = generate_nodes(geometry)
    bars = generate_bars(nodes, geometry)
    mirror_tripods = generate_mirrir_tripods(nodes, geometry)
    fixtures = generate_connections_to_tension_ring(nodes, geometry)
    return nodes, bars, mirror_tripods, fixtures