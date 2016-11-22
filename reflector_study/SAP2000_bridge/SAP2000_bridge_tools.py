import numpy as np
from . import Rotation
from ..factory import generate_reflector

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
    nodes = generate_reflector(geometry)["nodes"]
    rotated_nodes = np.zeros((nodes.shape[0], 3))
    for i in range(nodes.shape[0]):
        rotated_nodes[i] = from_zenith_to_new_position(nodes[i], rotation.rotational_matrix)
    return rotated_nodes
