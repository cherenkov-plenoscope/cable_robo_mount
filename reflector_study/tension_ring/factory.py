import numpy as np
from . import tools

def generate_tension_ring(geometry, reflector):
    reflector_fixtures = np.array([x for x in reflector["fixtures"] if x != -1])
    #find inner nodes of tension ring (not the same with fixtures, as in fixtures there are nodes in the middle layers)
    tension_ring_inner_nodes_indices = tools.inner_tension_ring_nodes_indices(reflector["nodes"], reflector_fixtures)
    #categorize the inner nodes according to the angle from y axis
    tension_ring_inner_nodes_categorized = tools.radar_categorization(tension_ring_inner_nodes_indices, reflector["nodes"])
    #create an array with the coordinates of the inner nodes of tension ring (just in case someone wants to create the tension ring alone)
    inner_tension_ring_nodes = np.array([reflector["nodes"][indice] for indice in tension_ring_inner_nodes_categorized])
    #create the bars related to the inner nodes (3 sets, the two diagonals and the straight ones)
    bars_inner = tools.bars_from_fixture(tension_ring_inner_nodes_categorized)
    #create the new nodes of the tension ring (this is an array with coordinates)
    tension_ring_new_nodes_coordinates= tools.tension_ring_outter_nodes(geometry, tension_ring_inner_nodes_categorized, reflector["nodes"])
    #append them to the existing nodes array(from the reflector)
    nodes = np.concatenate((reflector["nodes"], tension_ring_new_nodes_coordinates), axis=0)
    #find the node indices (simply the last tension_ring_new_nodes_coordinates.shape[0] nodes)
    tension_ring_outter_nodes = np.arange(reflector["nodes"].shape[0], nodes.shape[0])
    #categorize the outter nodes according to the angle from y axis
    tension_ring_outter_nodes_categorized = tools.radar_categorization(tension_ring_outter_nodes, nodes)
    #create the bars related to the outter nodes (3 sets, the two diagonals and the straight ones)
    bars_outter = tools.bars_from_fixture(tension_ring_outter_nodes_categorized)
    #create the bars inbetween
    bars_inbetween = tools.bars_inbetween(tension_ring_inner_nodes_categorized, tension_ring_outter_nodes_categorized)
    #bring all bars together
    bars = np.concatenate((bars_inner, bars_outter, bars_inbetween), axis= 0)
    #put the total nodes of the tension ring together
    tension_ring_nodes_coordinates = np.concatenate((inner_tension_ring_nodes, tension_ring_new_nodes_coordinates), axis= 0)

    return {
    'nodes_all': tension_ring_nodes_coordinates,
    'nodes_only_new': tension_ring_new_nodes_coordinates,
    'bars': bars
    }
