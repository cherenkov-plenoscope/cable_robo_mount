import reflector_study as rs
import numpy as np
"""
general imports
"""
geometry = rs.Geometry(rs.config.example)
#create reflector geometry
reflector = rs.factory.generate_reflector(geometry)
reflector_nodes = reflector["nodes"]
reflector_fixtures = np.array([x for x in reflector["fixtures"] if x != -1])
reflector_bars = reflector["bars"]
mirror_tripods = reflector["mirror_tripods"]

#create tension ring geometry

#find inner nodes of tension ring (not the same with fixtures, as in fixtures there are nodes in the middle layers)
tension_ring_inner_nodes = rs.tension_ring.tools_new.inner_tension_ring_nodes_indices(reflector_nodes, reflector_fixtures)
#categorize the inner nodes according to the angle from y axis
tension_ring_inner_nodes_categorized = rs.tension_ring.tools_new.radar_categorization(tension_ring_inner_nodes, reflector_nodes)
#create the bars related to the inner nodes (3 sets, the two diagonals and the straight ones)
bars_inner = rs.tension_ring.tools_new.bars_from_fixture(tension_ring_inner_nodes_categorized)

#create the new nodes of the tension ring (this is an array with coordinates)
tension_ring_new_nodes_coordinates= rs.tension_ring.tools_new.tension_ring_outter_nodes(geometry, tension_ring_inner_nodes_categorized, reflector_nodes)
#append them to the existing nodes array(from the reflector)
nodes = np.concatenate((reflector_nodes, tension_ring_new_nodes_coordinates), axis=0)
#find the node indices (simply the last tension_ring_new_nodes_coordinates.shape[0] nodes)
tension_ring_outter_nodes = np.arange(reflector_nodes.shape[0], nodes.shape[0])
#categorize the outter nodes according to the angle from y axis
tension_ring_outter_nodes_categorized = rs.tension_ring.tools_new.radar_categorization(tension_ring_outter_nodes, nodes)
#create the bars related to the outter nodes (3 sets, the two diagonals and the straight ones)
bars_outter = rs.tension_ring.tools_new.bars_from_fixture(tension_ring_outter_nodes_categorized)
#create the bars inbetween
bars_inbetween = rs.tension_ring.tools_new.bars_inbetween(tension_ring_inner_nodes_categorized, tension_ring_outter_nodes_categorized)

structural = rs.SAP2000_bridge.Structural(rs.config.example)
bridge = rs.SAP2000_bridge.Bridge(structural)
bridge._SapObject.Unhide()






reflector = rs.factory.generate_reflector(geometry)

nodes = reflector["nodes"]
fixtures = reflector["fixtures"]
bars = reflector["bars"]
mirror_tripods = reflector["mirror_tripods"]

"""
dish rotation
"""
homogenous_transformation = rs.HomTra()
homogenous_transformation.set_translation(geometry.translational_vector_xyz)
homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
nodes_rotated = rs.SAP2000_bridge.HomTra_bridge_tools.get_nodes_translated_position(nodes, homogenous_transformation)

"""
initialize SAP2000 and make assigns
"""
structural = rs.SAP2000_bridge.Structural(rs.config.example)
bridge = rs.SAP2000_bridge.Bridge(structural)
#bridge._SapObject.Hide()
#bridge._SapObject.Unhide()

path= "C:\\Users\\Spiros Daglas\\Desktop\\asdf\\test1\\spr"


bridge.save_model(path+".sdb")
rs.SAP2000_bridge.bridge_s2v.s2k(nodes, path)
rs.SAP2000_bridge.bridge_s2v.s2k_frames(bars, path)


bridge._SapModel.File.OpenFile(path+".$2k")


bridge.elastic_support_definition(fixtures)

bridge.load_scenario_dead()
bridge.load_scenario_facet_weight(mirror_tripods)
bridge.load_scenario_wind(mirror_tripods, nodes_rotated)

bridge.load_combination_3LP_definition(structural)

"""
run analysis and take Results
"""
bridge.run_analysis()

forces= bridge.get_forces_for_group_of_bars_for_selected_load_combination(load_combination_name= "dead+live+wind")
buckling = rs.SAP2000_bridge.BucklingControl.Knicknachweis(rs.config.example, forces)
log = buckling.log

nodes_deformed_rotated= bridge.get_total_absolute_deformations_for_load_combination(nodes= nodes_rotated, load_combination_name= "dead+live+wind", group_name= "ALL")

"""
bring dish to original position and prepare for mctracing simulation
"""
nodes_deformed = rs.SAP2000_bridge.HomTra_bridge_tools.get_nodes_zenith_position(nodes_deformed_rotated, homogenous_transformation)

reflector = rs.factory.generate_reflector(geometry)
reflector_deformed = reflector.copy()
reflector_deformed["nodes"]= nodes_deformed[:reflector["nodes"].copy().shape[0]]

"""
initialize ssh connection
"""
alignment = rs.mirror_alignment.ideal_alignment(reflector)

mctracer_server = rs.mctracer_bridge.RayTracingMachine(rs.config.example)
run_path = rs.config.example['system']['mctracer']['run_path_linux']
mctracer_propagate_path = rs.config.example['system']['mctracer']['ray_tracer_propagation_path_linux']
mctracer_server.execute('mkdir '+run_path)

"""
do what it takes for the ray tracing
"""
rs.mctracer_bridge.write_propagation_config_xml('config.xml')
rs.mctracer_bridge.write_star_light_xml(reflector=reflector_deformed, path='light.xml')
rs.mctracer_bridge.write_reflector_xml(reflector=reflector_deformed, alignment=alignment, path='scenery.xml')

mctracer_server.put('config.xml', run_path+'/'+'config.xml')
mctracer_server.put('light.xml', run_path+'/'+'light.xml')
mctracer_server.put('scenery.xml', run_path+'/'+'scenery.xml')

mctracer_server.execute(
    command=mctracer_propagate_path+
        ' -s '+run_path+'/'+'scenery.xml'+
        ' -c '+run_path+'/'+'config.xml'+
        ' -i '+run_path+'/'+'light.xml'+
        ' -o '+run_path+'/'+'out',
    out_path='mct_call')

mctracer_server.get(run_path+'/'+'out1_0', 'out1_0')
mctracer_server.get(run_path+'/'+'out1_1', 'out1_1')

mctracer_server.execute('rm -r '+run_path)

res = rs.mctracer_bridge.star_light_analysis.read_sensor_response('out1_0')
ground_res = rs.mctracer_bridge.star_light_analysis.read_sensor_response('out1_1')
image = rs.mctracer_bridge.star_light_analysis.make_image_from_sensor_response(reflector, res, rs.mctracer_bridge.star_light_analysis.config)
shadow_image = rs.mctracer_bridge.star_light_analysis.make_image_from_ground_response(reflector, ground_res, rs.mctracer_bridge.star_light_analysis.config)
rs.mctracer_bridge.star_light_analysis.plot_image(image)
rs.mctracer_bridge.star_light_analysis.plot_image(shadow_image)
#take back value of quality
