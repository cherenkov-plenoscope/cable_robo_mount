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

def bars_from_fixture(fixtures):
    bars = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)-1):
        bars[i,0], bars[i,1] = fixtures[i], fixtures[i+1]
    bars[len(fixtures)-1, 0], bars[len(fixtures)-1, 1] = fixtures[len(fixtures)-1], fixtures[0]
    return bars

def radar_categorization(fixtures, nodes):
    angle_from_y_clockwise = np.zeros((len(fixtures)))
    for i in range(len(fixtures)):
        angle_x_top = np.arctan(abs(nodes[fixtures[i]][0]) / abs(nodes[fixtures[i]][1]))
        angle_y_top = np.arctan(abs(nodes[fixtures[i]][1]) / abs(nodes[fixtures[i]][0]))
        if (nodes[fixtures[i]][1]>=0) and (nodes[fixtures[i]][0]>0):
            angle_from_y_clockwise[i]= angle_x_top
        elif (nodes[fixtures[i]][1]<=0) and (nodes[fixtures[i]][0]>0):
            angle_from_y_clockwise[i]= angle_y_top + np.pi/2
        elif (nodes[fixtures[i]][1]<=0) and (nodes[fixtures[i]][0]<0):
            angle_from_y_clockwise[i]= angle_x_top + np.pi
        elif (nodes[fixtures[i]][1]>=0) and (nodes[fixtures[i]][0]<0):
            angle_from_y_clockwise[i]= angle_y_top + 3*np.pi/2
    return list(zip(angle_from_y_clockwise, fixtures))

def arrange_fixtures_according_to_radar_categorization(list_angles_fixtures):
    sorted_= sorted(list_angles_fixtures, key=lambda x: x[0])
    fixtures_arranged = np.zeros(len(sorted_), dtype=int)
    for i in range(len(sorted_)):
        fixtures_arranged[i] = sorted_[i][1]
    return fixtures_arranged
