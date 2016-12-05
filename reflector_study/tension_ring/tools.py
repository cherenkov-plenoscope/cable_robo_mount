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
    bars[len(fixtures)//4-1, 0], bars[len(fixtures)//4-1, 1] = fixtures[len(fixtures)//4-1], fixtures[0]
    bars[len(fixtures)//2-1, 0], bars[len(fixtures)//2-1, 1] = fixtures[len(fixtures)//2-1], fixtures[len(fixtures)//4]
    bars[3*len(fixtures)//4-1, 0], bars[3*len(fixtures)//4-1, 1] = fixtures[3*len(fixtures)//4-1], fixtures[len(fixtures)//2]
    bars[len(fixtures)-1, 0], bars[len(fixtures)-1, 1] = fixtures[3*len(fixtures)//4], fixtures[len(fixtures)-1]
    return bars

def radar_categorization(fixtures, nodes):
    angle_from_y_clockwise = np.zeros((len(fixtures)))
    for i in range(len(fixtures)):
        X = nodes[fixtures[i]][0]
        Y = nodes[fixtures[i]][1]
        X_abs = abs(X)
        Y_abs = abs(Y)
        hypot = np.hypot(X, Y)
        if (Y>0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot)
        elif (Y<0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + np.pi/2
        elif (Y<0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot) + np.pi
        elif (Y>0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + 3*np.pi/2
        elif (Y==0) and (X>0):
            angle_from_y_clockwise[i]= np.pi/2
        elif (Y==0) and (X<0):
            angle_from_y_clockwise[i]= 3*np.pi/2
        elif (Y>0) and (X==0):
            angle_from_y_clockwise[i]= 0
        elif (Y<0) and (X==0):
            angle_from_y_clockwise[i]= np.pi
    return list(zip(angle_from_y_clockwise, fixtures))

def arrange_fixtures_according_to_radar_categorization(list_angles_fixtures):
    sorted_= sorted(list_angles_fixtures, key=lambda x: x[0])
    fixtures_arranged = np.zeros(len(sorted_), dtype=int)
    for i in range(len(sorted_)):
        fixtures_arranged[i] = sorted_[i][1]
    return fixtures_arranged

def nodes_offseted(geometry, fixtures, nodes, ring_width):
    angle_from_y_clockwise = np.zeros((len(fixtures)))
    nodes_offseted= np.zeros((fixtures.shape[0], geometry.tension_ring_width))
    fixtures_offseted= np.arange(max(fixtures)+1, max(fixtures) + len(fixtures)+1, dtype=int)
    for i in range(len(fixtures)):
        X = nodes[fixtures[i]][0]
        Y = nodes[fixtures[i]][1]
        Z = nodes[fixtures[i]][2]
        X_abs = abs(X)
        Y_abs = abs(Y)
        hypot = np.hypot(X, Y)
        if (Y>0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot)
            nodes_offseted[i,0] = X + ring_width * abs(np.sin(angle_from_y_clockwise[i]))
            nodes_offseted[i,1] = Y + ring_width * abs(np.cos(angle_from_y_clockwise[i]))
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + np.pi/2
            nodes_offseted[i,0] = X + ring_width * (abs(np.cos(angle_from_y_clockwise[i] - np.pi/2)))
            nodes_offseted[i,1] = Y - ring_width * (abs(np.sin(angle_from_y_clockwise[i] - np.pi/2)))
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot) + np.pi
            nodes_offseted[i,0] = X - ring_width * (abs(np.sin(angle_from_y_clockwise[i] - np.pi)))
            nodes_offseted[i,1] = Y - ring_width * (abs(np.cos(angle_from_y_clockwise[i] - np.pi)))
            nodes_offseted[i,2] = Z
        elif (Y>0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + 3*np.pi/2
            nodes_offseted[i,0] = X - ring_width * (abs(np.cos(angle_from_y_clockwise[i] - 3*np.pi/2)))
            nodes_offseted[i,1] = Y + ring_width * (abs(np.sin(angle_from_y_clockwise[i] - 3*np.pi/2)))
            nodes_offseted[i,2] = Z
        elif (Y==0) and (X>0):
            angle_from_y_clockwise[i]= np.pi/2
            nodes_offseted[i,0] = X + ring_width
            nodes_offseted[i,1] = Y
            nodes_offseted[i,2] = Z
        elif (Y==0) and (X<0):
            angle_from_y_clockwise[i]= 3*np.pi/2
            nodes_offseted[i,0] = X - ring_width
            nodes_offseted[i,1] = Y
            nodes_offseted[i,2] = Z
        elif (Y>0) and (X==0):
            angle_from_y_clockwise[i]= 0
            nodes_offseted[i,0] = X
            nodes_offseted[i,1] = Y + ring_width
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X==0):
            angle_from_y_clockwise[i]= np.pi
            nodes_offseted[i,0] = X
            nodes_offseted[i,1] = Y - ring_width
            nodes_offseted[i,2] = Z
    return np.concatenate((fixtures, fixtures_offseted), axis=0), np.concatenate((nodes, nodes_offseted), axis=0)

def bars_inbetween(bars, fixtures):
    bars1 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4-1):
        bars1[i,0], bars1[i,1] = fixtures[i], fixtures[i+len(fixtures)//4]
    bars1[len(fixtures)//4,0], bars1[len(fixtures)//4,1] = fixtures[len(fixtures)//4-1], fixtures[len(fixtures)//2-1]
    for i in range(len(fixtures)//2, 3*len(fixtures)//4-1):
        bars1[i,0], bars1[i,1] = fixtures[i], fixtures[i+len(fixtures)//4]
    bars1[len(fixtures)-1,0], bars1[len(fixtures)-1,1] = fixtures[3*len(fixtures)//4-1], fixtures[len(fixtures)-1]

    bars2 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4):
        bars2[i,0], bars2[i,1] = fixtures[i], fixtures[i+len(fixtures)//4-1]
    bars2[len(fixtures)//4,0], bars2[len(fixtures)//4,1] = fixtures[0], fixtures[len(fixtures)//2-1]
    for i in range(len(fixtures)//2, 3*len(fixtures)//4):
        bars2[i,0], bars2[i,1] = fixtures[i], fixtures[i+len(fixtures)//4-1]
    bars2[len(fixtures)-1,0], bars2[len(fixtures)-1,1] = fixtures[len(fixtures)//2], fixtures[len(fixtures)-1]

    bars3 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4-1):
        bars3[i,0], bars3[i,1] = fixtures[i], fixtures[i+len(fixtures)//4+1]
    bars3[len(fixtures)//4,0], bars3[len(fixtures)//4,1] = fixtures[len(fixtures)//4-1], fixtures[len(fixtures)//4]
    for i in range(len(fixtures)//2, 3*len(fixtures)//4-1):
        bars3[i,0], bars3[i,1] = fixtures[i], fixtures[i+len(fixtures)//4+1]
    bars3[len(fixtures)-1,0], bars3[len(fixtures)-1,1] = fixtures[3*len(fixtures)//4-1], fixtures[3*len(fixtures)//4]

    bars4 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4-1):
        bars4[i,0], bars4[i,1] = fixtures[i], fixtures[i+len(fixtures)//2]
    bars4[len(fixtures)//4-1,0], bars4[len(fixtures)//4-1,1] = fixtures[len(fixtures)//4-1], fixtures[3*len(fixtures)//4-1]
    for i in range(len(fixtures)//4, len(fixtures)//2-1):
        bars4[i,0], bars4[i,1] = fixtures[i], fixtures[i+len(fixtures)//2]
    bars4[len(fixtures)-1,0], bars4[len(fixtures)-1,1] = fixtures[len(fixtures)//2-1], fixtures[len(fixtures)-1]

    bars5 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4-1):
        bars5[i,0], bars5[i,1] = fixtures[i], fixtures[i+len(fixtures)//2+1]
    bars5[len(fixtures)//4-1,0], bars5[len(fixtures)//4-1,1] = fixtures[len(fixtures)//4-1], fixtures[len(fixtures)//2]
    for i in range(len(fixtures)//4, len(fixtures)//2-1):
        bars5[i,0], bars5[i,1] = fixtures[i], fixtures[i+len(fixtures)//2+1]
    bars5[len(fixtures)-1,0], bars5[len(fixtures)-1,1] = fixtures[len(fixtures)//2-1], fixtures[3*len(fixtures)//4]

    bars6 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(1, len(fixtures)//4):
        bars6[i,0], bars6[i,1] = fixtures[i], fixtures[i+len(fixtures)//2-1]
    bars6[0,0], bars6[0,1] = fixtures[0], fixtures[3*len(fixtures)//4-1]
    for i in range(len(fixtures)//4+1, len(fixtures)//2):
        bars6[i,0], bars6[i,1] = fixtures[i], fixtures[i+len(fixtures)//2-1]
    bars6[len(fixtures)//4,0], bars6[len(fixtures)//4,1] = fixtures[len(fixtures)//4], fixtures[len(fixtures)-1]

    bars7 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)//4-1):
        bars7[i,0], bars7[i,1] = fixtures[i], fixtures[i+3*len(fixtures)//4]
    bars7[len(fixtures)//4-1,0], bars7[len(fixtures)//4-1,1] = fixtures[len(fixtures)//4-1], fixtures[len(fixtures)-1]
    for i in range(len(fixtures)//4, len(fixtures)//2-1):
        bars7[i,0], bars7[i,1] = fixtures[i], fixtures[i+len(fixtures)//4]
    bars7[len(fixtures)-1,0], bars7[len(fixtures)-1,1] = fixtures[3*len(fixtures)//4-1], fixtures[len(fixtures)//2-1]

    return np.concatenate((bars, bars1, bars2, bars3, bars4, bars5, bars6, bars7), axis=0)
