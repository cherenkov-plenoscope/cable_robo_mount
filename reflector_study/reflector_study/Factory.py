import numpy as np
from .space_frame_geometry import dish_space_frame_addresses_to_cartesian

def position_of_node(nodes, ijk):
    return nodes[ijk[0], ijk[1], ijk[2]]

def in_range(nodes, ijk):
    i_valid = ijk[0] >= 0 and ijk[0] < nodes.shape[0]
    j_valid = ijk[1] >= 0 and ijk[1] < nodes.shape[1]
    k_valid = ijk[2] >= 0 and ijk[2] < nodes.shape[2]
    return i_valid and j_valid and k_valid

def make_rectangular_reflector(geometry):

    def is_valid(facet, nodes, geometry):
        if in_range(nodes, facet[0]) and in_range(nodes, facet[1]) and in_range(nodes, facet[2]):
            A = position_of_node(nodes, facet[0])
            B = position_of_node(nodes, facet[1])
            C = position_of_node(nodes, facet[2])

            center = (A + B + C)/3.0
            radius = np.hypot(center[0], center[1])
            inside_outer_limit = radius + geometry.facet_outer_hex_radius <= geometry.max_outer_radius 
            outside_inner_limit = radius - geometry.facet_outer_hex_radius > geometry.min_inner_radius 
            return inside_outer_limit and outside_inner_limit
        else:
            return False

    def is_ok(bar, nodes, geometry):

        if not in_range(nodes, bar[0]):
            return False
        if not in_range(nodes, bar[1]):
            return False

        c0 = position_of_node(nodes, bar[0])
        c1 = position_of_node(nodes, bar[1])
        r0 = np.hypot(c0[0], c0[1])
        r1 = np.hypot(c1[0], c1[1])
        radii = np.array([r0, r1])
        return radii.max() <= geometry.max_outer_radius + geometry.facet_outer_hex_radius

    def is_fixture(node, geometry):
        radius = np.hypot(node[0], node[1])
        is_inside_outer_limit = radius <= geometry.max_outer_radius
        is_most_outer_node = radius > geometry.max_outer_radius - geometry.facet_spacing
        return is_most_outer_node and is_inside_outer_limit

    i_radius = geometry.nodes_in_x
    j_radius = geometry.nodes_in_y
    k_radius = geometry.number_of_layers

    nodes = np.zeros(shape=(2*i_radius+1, 2*j_radius+1, k_radius, 3))

    for i in range(2*i_radius+1):
        for j in range(2*j_radius+1):
            for k in range(k_radius):
                nodes[i,j,k] = dish_space_frame_addresses_to_cartesian(
                    i=i-i_radius,
                    j=j-j_radius,
                    k=-k,
                    focal_length=geometry.focal_length,
                    davies_cotton_over_parabola_ratio=geometry.davies_cotton_over_parabola_ratio,
                    scale=geometry.facet_spacing,
                    x_over_z_ratio=geometry.x_over_z_ratio)

    bars = []
    for i in range(2*i_radius+1):
        for j in range(2*j_radius+1):
            for k in range(k_radius):

                bar_o0 = np.array([[i, j, k],[i,  j+1,k]])
                if is_ok(bar_o0, nodes, geometry):
                        bars.append(bar_o0)

                bar_o1 = np.array([[i, j, k],[i+1,j,  k]])
                if is_ok(bar_o1, nodes, geometry):
                        bars.append(bar_o1)

                if k+1 != k_radius:
                    bar_i0 = np.array([[i, j, k], [i,  j,  k+1]])
                    if is_ok(bar_i0, nodes, geometry):
                        bars.append(bar_i0)

                    bar_i1 = np.array([[i, j, k], [i,  j+1,k+1]])
                    if is_ok(bar_i1, nodes, geometry):
                        bars.append(bar_i1)

                    bar_i2 = np.array([[i, j, k], [i+1,j,  k+1]])
                    if is_ok(bar_i2, nodes, geometry):
                        bars.append(bar_i2)

                    bar_i3 = np.array([[i, j, k], [i+1,j+1,k+1]])
                    if is_ok(bar_i3, nodes, geometry):
                        bars.append(bar_i3)


    mirror_tripods = []
    for i in range(2*i_radius+1):
        for j in range(2*j_radius+1):
            for k in range(k_radius):
 
                if k == 0: # only on top layer
                    if np.mod(i,2) == 0: # Each 2nd in i
                        if np.mod(j+1,2) == 0: #Each 2nd in j
                            facet = np.array([
                                    [i,    j,   k],
                                    [i+1,  j+1, k],
                                    [i-1,  j+1, k]])
                            if is_valid(facet, nodes, geometry):
                                mirror_tripods.append(facet)
                        else: #Each other 2nd in j
                            facet = np.array([
                                    [i+1,   j,   k],
                                    [i+1+1, j+1, k],
                                    [i-1+1, j+1, k]])
                            if is_valid(facet, nodes, geometry):
                                mirror_tripods.append(facet)

    fixtures = []
    for i in range(2*i_radius+1):
        for j in range(2*j_radius+1):
            for k in range(k_radius):
                if is_fixture(nodes[i,j,k], geometry):
                    fixtures.append(np.array([i,j,k]))

                  
    bars = np.array(bars)
    mirror_tripods = np.array(mirror_tripods)
    fixtures = np.array(fixtures)
    return nodes, bars, mirror_tripods, fixtures
