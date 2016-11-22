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

def generate_nodes_final_position(geometry):
    nodes_final = ft.generate_nodes(geometry).copy()

    for i in range(geometry.lattice_range_i):
        for j in range(geometry.lattice_range_j):
            for k in range(geometry.lattice_range_k):
                nodes_final[i,j,k] = from_zenith_to_new_position(
                    xyz= nodes_final[i,j,k],
                    rotational_matrix= geometry.rotational_matrix)
    return nodes_final
