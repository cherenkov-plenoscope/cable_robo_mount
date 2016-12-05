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

def bars_tension(fixtures):
    bars = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)-1):
        bars[i,0], bars[i,1] = fixtures[i], fixtures[i+1]
    bars[len(fixtures)-1, 0], bars[len(fixtures)-1, 1] = fixtures[len(fixtures)-1], fixtures[0]
    return bars

def tan_fixtures(fixtures, nodes):
    tan_fix = np.zeros((len(fixtures)))
    for i in range(len(fixtures)):
        tangent_x = np.arctan(abs(nodes[fixtures[i]][0]) / abs(nodes[fixtures[i]][1]))
        tangent_y = np.arctan(abs(nodes[fixtures[i]][1]) / abs(nodes[fixtures[i]][0]))
        if (nodes[fixtures[i]][1]>=0) and (nodes[fixtures[i]][0]>0):
            tan_fix[i]= tangent_x
        elif (nodes[fixtures[i]][1]<=0) and (nodes[fixtures[i]][0]>0):
            tan_fix[i]= tangent_y + np.pi/2
        elif (nodes[fixtures[i]][1]<=0) and (nodes[fixtures[i]][0]<0):
            tan_fix[i]= tangent_x + np.pi
        elif (nodes[fixtures[i]][1]>=0) and (nodes[fixtures[i]][0]<0):
            tan_fix[i]= tangent_y + 3*np.pi/2
    return list(zip(tan_fix, fixtures))

def arrange_fixtures_according_to_tangent(tan_fixtures):
    asdf= sorted(tan_fixtures, key=lambda x: x[0])
    fixt = np.zeros(len(asdf), dtype=int)
    for i in range(len(asdf)):
        fixt[i] = asdf[i][1]
    return fixt
