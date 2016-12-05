from ..factory import generate_non_flat_reflector
from .tools import *

def geometry_1(geometry):
    reflector_ijk = generate_non_flat_reflector(geometry)
    flat_nodes_upper, flat_nodes_lower, flat_joints_upper, flat_joints_lower = nodes_of_upper_and_lower_layer(reflector_ijk)
    def fixtures_arranged(nodes, joints):
        fixtures = fixtures_according_to_joints(nodes, joints)
        list_angles_fixtures = radar_categorization(fixtures, nodes)
        return arrange_fixtures_according_to_radar_categorization(list_angles_fixtures)
    #maybe later needed
    basic_dict= {
        'nodes_lower_layer': flat_nodes_lower,
        'joints_lower_layer': flat_joints_lower,
        'fixtures_lower_layer': fixtures_arranged(flat_nodes_lower, flat_joints_lower),
        'bars_lower_layer': bars_from_fixture(fixtures_arranged(flat_nodes_lower, flat_joints_lower)),
        'nodes_upper_layer': flat_nodes_upper,
        'joints_upper_layer': flat_joints_upper,
        'fixtures_upper_layer': fixtures_arranged(flat_nodes_upper, flat_joints_upper),
        'bars_upper_layer': bars_from_fixture(fixtures_arranged(flat_nodes_upper, flat_joints_upper))}

    first_bars_assignment= {
        'nodes_1': np.concatenate((flat_nodes_upper, flat_nodes_lower), axis=0),
        'fixtures_1': np.concatenate((fixtures_arranged(flat_nodes_upper, flat_joints_upper), [x+flat_nodes_upper.shape[0] for x in fixtures_arranged(flat_nodes_lower, flat_joints_lower)]), axis=0),
        'bars_1': np.concatenate((bars_from_fixture(fixtures_arranged(flat_nodes_upper, flat_joints_upper)), bars_from_fixture(fixtures_arranged(flat_nodes_lower, flat_joints_lower) + flat_nodes_upper.shape[0])))}

    new_fixtures, new_nodes= nodes_offseted(first_bars_assignment['fixtures_1'], first_bars_assignment['nodes_1'], 3)
    new_bars= bars_from_fixture(new_fixtures)
    return {
    'nodes': new_nodes,
    'fixtures': new_fixtures,
    'bars': new_bars}
