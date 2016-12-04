import numpy as np

def nodes_of_upper_and_lower_layer(reflector_ijk):

    joints_ijk = reflector_ijk['joints']
    geometry = reflector_ijk['geometry']
    flat_nodes_upper_layer = []
    flat_joints_upper_layer = []
    flat_nodes_lower_layer = []
    flat_joints_lower_layer = []

    flat_nodes_upper_layer_indices = - np.ones(
        shape=(
            geometry.lattice_range_i,
            geometry.lattice_range_j,
            geometry.lattice_range_k
            )
    )
    flat_nodes_lower_layer_indices = - np.ones(
        shape=(
            geometry.lattice_range_i,
            geometry.lattice_range_j,
            geometry.lattice_range_k
            )
    )

    node_count = 0
    for i, joint_jk in enumerate(joints_ijk):
        for j, joint_k in enumerate(joint_jk):
            for k, joint in enumerate(joint_k):
                if (k == 0) and (len(joint) > 0):
                    flat_nodes_upper_layer.append(reflector_ijk['nodes'][i,j,k])
                    flat_joints_upper_layer.append(joint)
                    flat_nodes_upper_layer_indices[i,j,k] = node_count
                    node_count += 1
                if (k == geometry.lattice_range_k-1) and (len(joint) > 0):
                    flat_nodes_lower_layer.append(reflector_ijk['nodes'][i,j,k])
                    flat_joints_lower_layer.append(joint)
                    flat_nodes_lower_layer_indices[i,j,k] = node_count
                    node_count += 1

    return np.array(flat_nodes_upper_layer), np.array(flat_nodes_lower_layer), flat_joints_upper_layer, flat_joints_lower_layer

def fixtures_according_to_joints(nodes, joints):
    fixtures = []
    for i in range(len(joints)):
        if len(joints[i]) <= 7:
            fixtures.append(i)
    return np.array(fixtures)
