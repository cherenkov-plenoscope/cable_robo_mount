import numpy as np
from ..factory import generate_nodes
from . import Rotation
from ..factory import generate_non_flat_reflector
from ..flatten import generate_flat_nodes

def from_zenith_to_new_position(
    xyz,
    rotational_matrix):

    xyz = np.matrix(xyz)
    xyz = np.transpose(xyz)
    xyz = rotational_matrix * xyz
    xyz = np.transpose(xyz)
    xyz = np.array(xyz)
    return xyz

def generate_nodes_final_position(geometry, rotation):
    nodes_final = generate_nodes(geometry).copy()

    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
                nodes_final[i,j,k] = from_zenith_to_new_position(
                    xyz= nodes_final[i,j,k],
                    rotational_matrix= rotation.rotational_matrix)
    nodes_final_flat = generate_flat_nodes(generate_non_flat_reflector(geometry))["nodes"]
    return nodes_final_flat
