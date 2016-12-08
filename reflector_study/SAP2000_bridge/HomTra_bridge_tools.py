import numpy as np

def get_nodes_translated_position(nodes, homogenous_transformation):
    nodes_rotated = np.zeros((nodes.shape[0],3))
    for i in range(nodes.shape[0]):
        nodes_rotated[i] = homogenous_transformation.transformed_position(nodes[i])
    return nodes_rotated

def get_nodes_zenith_position(nodes_rotated, homogenous_transformation):
    nodes = np.zeros((nodes_rotated.shape[0],3))
    for i in range(nodes_rotated.shape[0]):
        nodes[i] = homogenous_transformation.transformed_position_inverse(nodes_rotated[i])
    return nodes
