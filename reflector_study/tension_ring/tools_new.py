import numpy as np

def tension_ring_outter_nodes(geometry, fixtures, nodes):
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
    return nodes_offseted
