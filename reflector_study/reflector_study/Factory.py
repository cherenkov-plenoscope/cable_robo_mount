import numpy as np
from .space_frame_geometry import dish_space_frame_addresses_to_cartesian

def make_rectangular_reflector(geometry):
    node_radius_x_and_y = int(
        np.ceil(geometry.max_outer_radius/geometry.facet_spacing))
    
    i_radius = node_radius_x_and_y
    j_radius = node_radius_x_and_y
    k_radius = geometry.number_of_layers
    nodes = np.zeros(shape=(2*i_radius+1, 2*j_radius+1, k_radius, 3))
    bars = []
    mirror_tripods = []
    for i in range(2*i_radius+1):
        for j in range(2*j_radius+1):
            for k in range(k_radius):
                
                nodes[i,j,k] = dish_space_frame_addresses_to_cartesian(
                    i=i-i_radius,
                    j=j-j_radius,
                    k=-k,
                    focal_length=geometry.focal_length,
                    davies_cotton_over_parabola_ratio=geometry.davies_cotton_over_parabola_ratio,
                    scale=geometry.facet_spacing,
                    x_over_z_ratio=geometry.x_over_z_ratio)

                # Bars in between layers
                bars.append(np.array([[i, j, k],[i,  j,  k+1]]))
                bars.append(np.array([[i, j, k],[i,  j+1,k+1]]))
                bars.append(np.array([[i, j, k],[i+1,j,  k+1]]))
                bars.append(np.array([[i, j, k],[i+1,j+1,k+1]]))

                # Bars on layer
                bars.append(np.array([[i, j, k],[i,  j+1,k]]))
                bars.append(np.array([[i, j, k],[i+1,j,  k]]))

                # Nodes mirror tripod
                if k == 0: # only on top layer
                    if j-1>0: # no facets to overhanging the negative index edge
                        if np.mod(j,2) == 0: # Each 2nd in j
                            if np.mod(i+1,4) == 0: #Each 4th in i
                                    mirror_tripods.append(
                                        np.array([
                                            [i, j, k],
                                            [i+2,  j+1,k],
                                            [i+2,  j-1,k]]))
                            elif np.mod(i+1,2) == 0: #Each other 4th in i
                                    mirror_tripods.append(
                                        np.array([
                                            [i, j+1, k],
                                            [i+2,  j+1+1,k],
                                            [i+2,  j-1+1,k]]))
    bars = np.array(bars)
    mirror_tripods = np.array(mirror_tripods)
    return nodes, bars, mirror_tripods
