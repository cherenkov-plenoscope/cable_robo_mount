import numpy as np


def get_nodes_moved_position(nodes, cable_supports, homogenous_transformation):
    nodes_rotated = np.zeros((nodes.shape[0], 3))
    for i in range(nodes.shape[0] - cable_supports.shape[0]):
        nodes_rotated[i] = homogenous_transformation.transformed_position(
            nodes[i]
        )
    for i in range(nodes.shape[0] - cable_supports.shape[0], nodes.shape[0]):
        nodes_rotated[i] = nodes[i]
    return nodes_rotated


def get_nodes_zenith_position(
    nodes_rotated, cable_supports, homogenous_transformation
):
    nodes = np.zeros((nodes_rotated.shape[0], 3))
    for i in range(nodes_rotated.shape[0] - cable_supports.shape[0]):
        nodes[i] = homogenous_transformation.transformed_position_inverse(
            nodes_rotated[i]
        )
    for i in range(
        nodes_rotated.shape[0] - cable_supports.shape[0],
        nodes_rotated.shape[0],
    ):
        nodes[i] = nodes_rotated[i]
    return nodes
