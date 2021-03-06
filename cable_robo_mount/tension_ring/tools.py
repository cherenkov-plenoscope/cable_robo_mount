import numpy as np

def inner_tension_ring_nodes_indices(geometry, reflector_nodes, reflector_fixtures):
    l= np.zeros((reflector_fixtures.shape[0]))
    for i in range(reflector_fixtures.shape[0]):
        l[i] = reflector_nodes[reflector_fixtures[i]][2]
    z_upper= np.amax(l)
    z_lower= np.amin(l)
    tension_ring_inner_node_indices = []
    for i in range(reflector_fixtures.shape[0]):
        check = reflector_nodes[reflector_fixtures[i]][2]
        height_between_layers = geometry.x_over_z_ratio*geometry.facet_spacing/2
        if check > z_upper-height_between_layers/2 or check < z_lower+height_between_layers/2:
            tension_ring_inner_node_indices.append(reflector_fixtures[i])
    return np.array(tension_ring_inner_node_indices)

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

    list_angles_fixtures = list(zip(angle_from_y_clockwise, fixtures))

    sorted_= sorted(list_angles_fixtures, key=lambda x: x[0])
    fixtures_arranged = np.zeros(len(sorted_), dtype=int)
    for i in range(len(sorted_)):
        fixtures_arranged[i] = sorted_[i][1]
    return fixtures_arranged

def bars_from_fixture(fixtures):

    bars_diagonal_1 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)-1):
        bars_diagonal_1[i,0], bars_diagonal_1[i,1] = fixtures[i], fixtures[i+1]
    bars_diagonal_1[len(fixtures)-1, 0], bars_diagonal_1[len(fixtures)-1, 1] = fixtures[len(fixtures)-1], fixtures[0]

    bars_diagonal_2 = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(0, len(fixtures)-3, 2):
        bars_diagonal_2[i,0], bars_diagonal_2[i,1] = fixtures[i], fixtures[i+3]
    bars_diagonal_2[len(fixtures)-1, 0], bars_diagonal_2[len(fixtures)-1, 1] = fixtures[len(fixtures)-2], fixtures[1]
    mask = np.all(np.isnan(bars_diagonal_2), axis=1) | np.all(bars_diagonal_2 == 0, axis=1)
    bars_diagonal_2 = bars_diagonal_2[~mask]

    bars_straight = np.zeros((len(fixtures), 2), dtype=int)
    for i in range(len(fixtures)-2):
        bars_straight[i,0], bars_straight[i,1] = fixtures[i], fixtures[i+2]
    bars_straight[len(fixtures)-1, 0], bars_straight[len(fixtures)-1, 1] = fixtures[len(fixtures)-2], fixtures[0]
    bars_straight[len(fixtures)-2, 0], bars_straight[len(fixtures)-2, 1] = fixtures[len(fixtures)-1], fixtures[1]
    return np.concatenate((bars_diagonal_1, bars_diagonal_2, bars_straight), axis=0)

def tension_ring_outter_nodes_and_elastic_supports(geometry, fixtures, nodes):
    angle_from_y_clockwise = np.zeros((len(fixtures)))
    nodes_offseted= np.zeros((fixtures.shape[0], 3))
    for i in range(len(fixtures)):
        X = nodes[fixtures[i]][0]
        Y = nodes[fixtures[i]][1]
        Z = nodes[fixtures[i]][2]
        X_abs = abs(X)
        Y_abs = abs(Y)
        hypot = np.hypot(X, Y)
        if (Y>0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot)
            nodes_offseted[i,0] = X + geometry.tension_ring_width * abs(np.sin(angle_from_y_clockwise[i]))
            nodes_offseted[i,1] = Y + geometry.tension_ring_width * abs(np.cos(angle_from_y_clockwise[i]))
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X>0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + np.pi/2
            nodes_offseted[i,0] = X + geometry.tension_ring_width * (abs(np.cos(angle_from_y_clockwise[i] - np.pi/2)))
            nodes_offseted[i,1] = Y - geometry.tension_ring_width * (abs(np.sin(angle_from_y_clockwise[i] - np.pi/2)))
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(Y_abs / hypot) + np.pi
            nodes_offseted[i,0] = X - geometry.tension_ring_width * (abs(np.sin(angle_from_y_clockwise[i] - np.pi)))
            nodes_offseted[i,1] = Y - geometry.tension_ring_width * (abs(np.cos(angle_from_y_clockwise[i] - np.pi)))
            nodes_offseted[i,2] = Z
        elif (Y>0) and (X<0):
            angle_from_y_clockwise[i]= np.arccos(X_abs / hypot) + 3*np.pi/2
            nodes_offseted[i,0] = X - geometry.tension_ring_width * (abs(np.cos(angle_from_y_clockwise[i] - 3*np.pi/2)))
            nodes_offseted[i,1] = Y + geometry.tension_ring_width * (abs(np.sin(angle_from_y_clockwise[i] - 3*np.pi/2)))
            nodes_offseted[i,2] = Z
        elif (Y==0) and (X>0):
            angle_from_y_clockwise[i]= np.pi/2
            nodes_offseted[i,0] = X + geometry.tension_ring_width
            nodes_offseted[i,1] = Y
            nodes_offseted[i,2] = Z
        elif (Y==0) and (X<0):
            angle_from_y_clockwise[i]= 3*np.pi/2
            nodes_offseted[i,0] = X - geometry.tension_ring_width
            nodes_offseted[i,1] = Y
            nodes_offseted[i,2] = Z
        elif (Y>0) and (X==0):
            angle_from_y_clockwise[i]= 0
            nodes_offseted[i,0] = X
            nodes_offseted[i,1] = Y + geometry.tension_ring_width
            nodes_offseted[i,2] = Z
        elif (Y<0) and (X==0):
            angle_from_y_clockwise[i]= np.pi
            nodes_offseted[i,0] = X
            nodes_offseted[i,1] = Y - geometry.tension_ring_width
            nodes_offseted[i,2] = Z

    elastic_supports = []
    closest_angles = []
    support_position = geometry.tension_ring_support_position*np.pi/180
    for i in range(int(2*np.pi//support_position)):
        closest_angles.append(min(angle_from_y_clockwise, key=lambda x:abs(x-(support_position*i))))
    for i in range(nodes_offseted.shape[0]):
        if angle_from_y_clockwise[i] in closest_angles:
            elastic_supports.append(i+nodes.shape[0])

    return nodes_offseted, np.array(elastic_supports)

def bars_inbetween(tension_ring_inner_nodes_categorized, tension_ring_outter_nodes_categorized):
    bars_straight = np.zeros((tension_ring_inner_nodes_categorized.shape[0], 2), dtype=int)
    for i in range(tension_ring_inner_nodes_categorized.shape[0]):
        bars_straight[i,0], bars_straight[i,1] = tension_ring_inner_nodes_categorized[i], tension_ring_outter_nodes_categorized[i]

    bars_diagonal_1 = np.zeros((tension_ring_inner_nodes_categorized.shape[0], 2), dtype=int)
    for i in range(0, tension_ring_inner_nodes_categorized.shape[0]-1, 2):
        bars_diagonal_1[i,0], bars_diagonal_1[i,1] = tension_ring_inner_nodes_categorized[i], tension_ring_outter_nodes_categorized[i+1]
    mask = np.all(np.isnan(bars_diagonal_1), axis=1) | np.all(bars_diagonal_1 == 0, axis=1)
    bars_diagonal_1 = bars_diagonal_1[~mask]

    bars_diagonal_2 = np.zeros((tension_ring_inner_nodes_categorized.shape[0], 2), dtype=int)
    for i in range(0, tension_ring_inner_nodes_categorized.shape[0]-1, 2):
        bars_diagonal_2[i,0], bars_diagonal_2[i,1] = tension_ring_inner_nodes_categorized[i+1], tension_ring_outter_nodes_categorized[i]
    mask = np.all(np.isnan(bars_diagonal_2), axis=1) | np.all(bars_diagonal_2 == 0, axis=1)
    bars_diagonal_2 = bars_diagonal_2[~mask]

    bars_diagonal_3 = np.zeros((tension_ring_inner_nodes_categorized.shape[0]+1, 2), dtype=int)
    for i in range(0, tension_ring_inner_nodes_categorized.shape[0]-2, 2):
        bars_diagonal_3[i,0], bars_diagonal_3[i,1] = tension_ring_inner_nodes_categorized[i], tension_ring_outter_nodes_categorized[i+2]
        bars_diagonal_3[i+1,0], bars_diagonal_3[i+1,1] = tension_ring_inner_nodes_categorized[i+1], tension_ring_outter_nodes_categorized[i+3]
    bars_diagonal_3[tension_ring_inner_nodes_categorized.shape[0]-1, 0] = tension_ring_inner_nodes_categorized[tension_ring_inner_nodes_categorized.shape[0]-2]
    bars_diagonal_3[tension_ring_inner_nodes_categorized.shape[0]-1, 1] = tension_ring_outter_nodes_categorized[0]
    bars_diagonal_3[tension_ring_inner_nodes_categorized.shape[0], 0] = tension_ring_inner_nodes_categorized[tension_ring_inner_nodes_categorized.shape[0]-1]
    bars_diagonal_3[tension_ring_inner_nodes_categorized.shape[0], 1] = tension_ring_outter_nodes_categorized[1]
    mask = np.all(np.isnan(bars_diagonal_3), axis=1) | np.all(bars_diagonal_3 == 0, axis=1)
    bars_diagonal_3 = bars_diagonal_3[~mask]

    bars_diagonal_4 = np.zeros((tension_ring_inner_nodes_categorized.shape[0]+1, 2), dtype=int)
    for i in range(0, tension_ring_inner_nodes_categorized.shape[0]-2, 2):
        bars_diagonal_4[i,0], bars_diagonal_4[i,1] = tension_ring_outter_nodes_categorized[i], tension_ring_inner_nodes_categorized[i+2]
        bars_diagonal_4[i+1,0], bars_diagonal_4[i+1,1] = tension_ring_outter_nodes_categorized[i+1], tension_ring_inner_nodes_categorized[i+3]
    bars_diagonal_4[tension_ring_inner_nodes_categorized.shape[0]-1, 0] = tension_ring_outter_nodes_categorized[tension_ring_inner_nodes_categorized.shape[0]-2]
    bars_diagonal_4[tension_ring_inner_nodes_categorized.shape[0]-1, 1] = tension_ring_inner_nodes_categorized[0]
    bars_diagonal_4[tension_ring_inner_nodes_categorized.shape[0], 0] = tension_ring_outter_nodes_categorized[tension_ring_inner_nodes_categorized.shape[0]-1]
    bars_diagonal_4[tension_ring_inner_nodes_categorized.shape[0], 1] = tension_ring_inner_nodes_categorized[1]
    mask = np.all(np.isnan(bars_diagonal_4), axis=1) | np.all(bars_diagonal_4 == 0, axis=1)
    bars_diagonal_4 = bars_diagonal_4[~mask]
    return np.concatenate((bars_diagonal_1, bars_diagonal_2, bars_diagonal_3, bars_diagonal_4, bars_straight), axis=0)

def cables(geometry, nodes_reflector_tension_ring, elastic_supports, cable_supports_indices):
    cables = []
    angle_from_y_clockwise = np.zeros(elastic_supports.shape[0])
    for i in range(elastic_supports.shape[0]):
        X = nodes_reflector_tension_ring[elastic_supports[i]][0]
        Y = nodes_reflector_tension_ring[elastic_supports[i]][1]
        Z = nodes_reflector_tension_ring[elastic_supports[i]][2]
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

    l= np.zeros((elastic_supports.shape[0]))
    for i in range(elastic_supports.shape[0]):
        l[i] = nodes_reflector_tension_ring[elastic_supports[i]][2]
    z_upper= np.amax(l)
    z_lower= np.amin(l)

    height_between_layers = geometry.x_over_z_ratio*geometry.facet_spacing/2

    for i in range(elastic_supports.shape[0]):
        if (angle_from_y_clockwise[i] <= np.pi/8) or (angle_from_y_clockwise[i] >= 15*np.pi/8):
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[2]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[10]])
        elif np.pi/8 <= angle_from_y_clockwise[i] <= 3*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[1]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[9]])
        elif 3*np.pi/8 <= angle_from_y_clockwise[i] <= 5*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[0]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[8]])
        elif 5*np.pi/8 <= angle_from_y_clockwise[i] <= 7*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[7]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[15]])
        elif 7*np.pi/8 <= angle_from_y_clockwise[i] <= 9*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[6]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[14]])
        elif 9*np.pi/8 <= angle_from_y_clockwise[i] <= 11*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[5]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[13]])
        elif 11*np.pi/8 <= angle_from_y_clockwise[i] <= 13*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[4]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[12]])
        elif 13*np.pi/8 <= angle_from_y_clockwise[i] <= 15*np.pi/8:
            if nodes_reflector_tension_ring[elastic_supports[i]][2] > z_upper - height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[3]])
            elif nodes_reflector_tension_ring[elastic_supports[i]][2] < z_lower + height_between_layers/2:
                cables.append([elastic_supports[i], cable_supports_indices[11]])
    return np.array(cables)

def cable_supports_indices(nodes_reflector_tension_ring):
    cable_supports_indices = np.arange(nodes_reflector_tension_ring.shape[0], nodes_reflector_tension_ring.shape[0]+16)
    return cable_supports_indices

def cable_supports_coordinates_definition(geometry):
    height_between_layers = geometry.x_over_z_ratio*geometry.facet_spacing/2
    cable_supports_coordinates = np.zeros((16, 3))

    for i in range(8):
        angle = np.pi/4
        cable_supports_coordinates[i][0] = (geometry.max_outer_radius*(1+18/25)+geometry.tension_ring_width)*np.cos(angle*i)
        cable_supports_coordinates[i][1] = (geometry.max_outer_radius*(1+18/25)+geometry.tension_ring_width)*np.sin(angle*i)
        cable_supports_coordinates[i][2] = geometry.max_outer_radius*40/25 + geometry.reflector_security_distance_from_ground + height_between_layers
    for i in range(8):
        angle = np.pi/4
        cable_supports_coordinates[i+8][0] = (geometry.max_outer_radius*(1+18/25)+geometry.tension_ring_width)*np.cos(angle*i)
        cable_supports_coordinates[i+8][1] = (geometry.max_outer_radius*(1+18/25)+geometry.tension_ring_width)*np.sin(angle*i)
        cable_supports_coordinates[i+8][2] = -(geometry.reflector_security_distance_from_ground + height_between_layers)
    return cable_supports_coordinates
