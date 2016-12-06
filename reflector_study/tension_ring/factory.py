from ..factory import generate_non_flat_reflector
from .tools import *

def fixtures_arranged(nodes, joints):
    #takes the outter nodes
    fixtures = fixtures_according_to_joints(nodes, joints)
    #takes a list of tuples with the angle and the fixture(node)
    list_angles_fixtures = radar_categorization(fixtures, nodes)
    #arranges the upper list according to the angle and exports only the second part.(the fixtures)
    return arrange_fixtures_according_to_radar_categorization(list_angles_fixtures)

def tension_ring_inner_nodes(flat_nodes_upper, flat_nodes_lower, flat_joints_upper, flat_joints_lower):
    outter_nodes_label_arranged_upper = fixtures_arranged(flat_nodes_upper, flat_joints_upper)
    outter_nodes_label_arranged_lower = fixtures_arranged(flat_nodes_lower, flat_joints_lower) + flat_nodes_upper.shape[0]
    return np.concatenate((outter_nodes_label_arranged_upper, outter_nodes_label_arranged_lower), axis= 0)

def generate_tension_ring(geometry):
    #reflector = generate_reflector(geometry)
    reflector_ijk = generate_non_flat_reflector(geometry)

    #it is not the reflector coordinate system/framework
    flat_nodes_upper, flat_nodes_lower, flat_joints_upper, flat_joints_lower = nodes_of_upper_and_lower_layer(reflector_ijk)
    tension_ring_nodes = np.concatenate((flat_nodes_upper, flat_nodes_lower), axis=0)

    new_fixtures, new_nodes= nodes_offseted(
                geometry= geometry,
                fixtures= tension_ring_inner_nodes(flat_nodes_upper, flat_nodes_lower, flat_joints_upper, flat_joints_lower),
                nodes= tension_ring_nodes)

    new_bars= bars_from_fixture(new_fixtures)
    final_bars = bars_inbetween(new_bars, new_fixtures)

    clean_nodes = nodisol_delete_and_renumbering(new_nodes, new_fixtures, final_bars)[0]
    clean_bars = nodisol_delete_and_renumbering(new_nodes, new_fixtures, final_bars)[1]
    return {
    'nodes': clean_nodes,
    #'fixtures': new_fixtures,
    'bars': clean_bars}
