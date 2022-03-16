import numpy as np
from .space_frame_geometry import dish_space_frame_addresses_to_cartesian
from .tools.non_flat.tools import node_position
from .tools.non_flat.tools import node_in_range
from .tools.non_flat.tools import bar_in_range
from .tools.non_flat.tools import bar_start_and_end_position
from .tools.non_flat.tools import mirror_tripod_center
from .flatten import flatten
from .tension_ring.factory import generate_tension_ring
from .tension_ring.factory import generate_cables

def bar_is_part_of_reflector_dish(bar, nodes, geometry):
    if not bar_in_range(nodes, bar):
        return False
    start, end = bar_start_and_end_position(nodes, bar)
    r_start = np.hypot(start[0], start[1])
    r_end = np.hypot(end[0], end[1])
    radii = np.array([r_start, r_end])
    return radii.max() <= geometry.max_outer_radius + geometry.facet_outer_hex_radius


def point_in_hexagon(x, y, inner_radius, phi=0):
    ir = inner_radius
    THIRD = (2./3.) * np.pi
    U = np.array([
        np.cos(phi),
        np.sin(phi),
    ])
    V = np.array([
        np.cos(phi + THIRD),
        np.sin(phi + THIRD),
    ])
    W = np.array([
        np.cos(phi + 2 * THIRD),
        np.sin(phi + 2 * THIRD),
    ])

    projU = U[0] * x + U[1] * y
    projV = V[0] * x + V[1] * y
    projW = W[0] * x + W[1] * y
    return (
        projU < ir
        and
        projU > -ir
        and
        projV < ir
        and
        projV > -ir
        and
        projW < ir
        and
        projW > -ir
    )

def mirror_tripod_is_part_of_reflector_dish(mirror_tripod, nodes, geometry, outer_shape="hexagon"):
    A_in_range = node_in_range(nodes, mirror_tripod[0])
    B_in_range = node_in_range(nodes, mirror_tripod[1])
    C_in_range = node_in_range(nodes, mirror_tripod[2])

    if A_in_range and B_in_range and C_in_range:
        # outer shape of mirror
        # ---------------------
        center = mirror_tripod_center(nodes, mirror_tripod)
        if outer_shape == "round":
            radius = np.hypot(center[0], center[1])
            inside_outer_limit = radius + geometry.facet_outer_hex_radius <= geometry.max_outer_radius
            outside_inner_limit = radius - geometry.facet_outer_hex_radius > geometry.min_inner_radius
            return inside_outer_limit and outside_inner_limit
        elif outer_shape == "hexagon":
            inside_inner = point_in_hexagon(
                x=center[0],
                y=center[1],
                inner_radius=(
                    geometry.min_inner_radius
                    + geometry.facet_outer_hex_radius),
                phi=0
            )
            inside_outer = point_in_hexagon(
                x=center[0],
                y=center[1],
                inner_radius=(np.sqrt(3)/2) * (
                    geometry.max_outer_radius
                    - geometry.facet_outer_hex_radius),
                phi=0
            )
            return inside_outer and not inside_inner
        else:
            raise KeyError("Outer shape is not known: ", str(outer_shape))
    else:
        return False


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
                    scale=geometry.facet_spacing/2.0,
                    x_over_z_ratio=geometry.x_over_z_ratio)
    return nodes


def generate_empty_joints(geometry):
    joints = [[[]]]
    for i in range(geometry.lattice_range_i):
        joints.append([])
        for j in range(geometry.lattice_range_j):
            joints[i].append([])
            for k in range(geometry.lattice_range_k):
                joints[i][j].append([])
                joints[i][j][k] = []
    return joints


def generate_bars_and_joints(nodes, geometry):

    joints = generate_empty_joints(geometry)
    bars = []

    def bar_index(bars):
        return len(bars)-1

    def add_bar(iS, jS, kS, iE, jE, kE):
        bar = np.array([[iS, jS, kS],[iE, jE, kE]])
        if bar_is_part_of_reflector_dish(bar, nodes, geometry):
            bars.append(bar)
            joints[iS][jS][kS].append(bar_index(bars))
            joints[iE][jE][kE].append(bar_index(bars))

    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):

                add_bar(i, j, k, i,   j+1, k)
                add_bar(i, j, k, i+1, j,   k)

                if k+1 != geometry.lattice_range_k:
                    add_bar(i, j, k, i,   j,   k+1)
                    add_bar(i, j, k, i,   j+1, k+1)
                    add_bar(i, j, k, i+1, j,   k+1)
                    add_bar(i, j, k, i+1, j+1, k+1)

    return {'bars': np.array(bars), 'joints': joints}


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


def generate_connections_to_tension_ring(joints, geometry):
    fixtures = []
    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
                if len(joints[i][j][k]) <= 7:
                    fixtures.append(np.array([i,j,k]))
    return np.array(fixtures)


def generate_non_flat_reflector(geometry):
    nodes = generate_nodes(geometry)
    bars_and_joints = generate_bars_and_joints(nodes, geometry)
    bars = bars_and_joints['bars']
    joints = bars_and_joints['joints']
    mirror_tripods = generate_mirrir_tripods(nodes, geometry)
    fixtures = generate_connections_to_tension_ring(joints, geometry)
    return {
        'nodes': nodes,
        'joints': joints,
        'bars': bars,
        'mirror_tripods': mirror_tripods,
        'fixtures': fixtures,
        'geometry': geometry}


def generate_reflector(geometry):
    return flatten(generate_non_flat_reflector(geometry))

def generate_reflector_with_tension_ring_and_cables(geometry):
    reflector = generate_reflector(geometry)
    tension_ring = generate_tension_ring(geometry, reflector)
    cables_structure = generate_cables(geometry, tension_ring["nodes_reflector_tension_ring"], tension_ring["elastic_supports"])
    all_nodes = np.concatenate((reflector["nodes"], tension_ring["nodes_tension_ring_only_new"], cables_structure["nodes"]), axis= 0)
    return {
        'nodes': all_nodes,
        'bars_reflector': reflector["bars"],
        'bars_tension_ring': tension_ring["bars"],
        'mirror_tripods': reflector["mirror_tripods"],
        'elastic_supports': tension_ring["elastic_supports"],
        'cables': cables_structure["cables"],
        'cable_supports': cables_structure["cable_supports"],
        'geometry': geometry}
