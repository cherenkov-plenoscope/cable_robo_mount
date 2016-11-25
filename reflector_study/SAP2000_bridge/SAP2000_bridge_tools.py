import numpy as np

def from_zenith_to_new_position(
    xyz,
    rotational_matrix):

    xyz = np.matrix(xyz)
    xyz = np.transpose(xyz)
    xyz = rotational_matrix * xyz
    xyz = np.transpose(xyz)
    xyz = np.array(xyz)
    return xyz

def generate_reflector_roatated_position(reflector, rotation):
    rotated_nodes = np.zeros((reflector["nodes"].shape[0], 3))
    for i in range(reflector["nodes"].shape[0]):
        rotated_nodes[i] = from_zenith_to_new_position(reflector["nodes"][i], rotation.rotational_matrix)
    reflector_rotated = reflector.copy()
    reflector_rotated["nodes"] = rotated_nodes
    return reflector_rotated
