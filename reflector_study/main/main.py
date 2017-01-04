import reflector_study as rs

"""
general imports
"""
geometry = rs.Geometry([0.04,0], rs.config.example)
total_geometry = rs.factory.generate_reflector_with_tension_ring_and_cables(geometry)
nodes = total_geometry["nodes"]
bars_reflector = total_geometry["bars_reflector"]
bars_tension_ring = total_geometry["bars_tension_ring"]
cables = total_geometry["cables"]
elastic_supports = total_geometry["elastic_supports"]
cable_supports = total_geometry["cable_supports"]
mirror_tripods = total_geometry["mirror_tripods"]
fixtures = total_geometry["elastic_supports"]

"""
dish rotation
"""
homogenous_transformation = rs.HomTra()
homogenous_transformation.set_translation(geometry.translational_vector_xyz)
homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
nodes_rotated = rs.SAP2000_bridge.HomTra_bridge_tools.get_nodes_moved_position(nodes, cable_supports, homogenous_transformation)

"""
initialize SAP2000 and make assigns
"""
structural = rs.SAP2000_bridge.Structural([0.04, 0], rs.config.example)
bridge = rs.SAP2000_bridge.Bridge(structural)
bridge._SapObject.Hide()
#bridge._SapObject.Unhide()

bridge.save_model_in_working_directory()
rs.SAP2000_bridge.TextFilesBridge.JointsCreate(nodes_rotated, structural.SAP_2000_working_directory)
rs.SAP2000_bridge.TextFilesBridge.FramesCreate(bars_reflector, bars_tension_ring, structural)
bridge._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

#bridge.elastic_support_definition(fixtures)
################for cables uncomment the following
bridge._cables_definition(cables)
#bridge._set_tension_compression_limits_for_specific_frame_elements(cables)
bridge._restraints_definition(cable_supports)
################

bridge.load_scenario_dead()
bridge.load_scenario_facet_weight(mirror_tripods)
bridge.load_scenario_wind(mirror_tripods, nodes_rotated)

bridge.load_combination_3LP_definition(structural)

"""
run analysis and take Results
"""
bridge._SapModel.Analyze.SetRunCaseFlag("DEAD", False, False)
bridge._SapModel.Analyze.SetRunCaseFlag("MODAL", False, False)

bridge.run_analysis()

#forces= bridge.get_forces_for_group_of_bars_for_selected_load_combination(load_combination_name= "dead+live+wind")
#buckling = rs.SAP2000_bridge.BucklingControl.Knicknachweis(rs.config.example, forces)
#log = buckling.log

nodes_deformed_rotated= bridge.get_total_absolute_deformations_for_load_combination(nodes= nodes_rotated, load_combination_name= "dead+live+wind", group_name= "ALL")

"""
bring dish to original position and prepare for mctracing simulation
"""
nodes_deformed = rs.SAP2000_bridge.HomTra_bridge_tools.get_nodes_zenith_position(nodes_deformed_rotated, cable_supports, homogenous_transformation)

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
        ' -o '+run_path+'/'+'out'+
        ' -b',
    out_path='mct_call')

mctracer_server.get(run_path+'/'+'out1_0', 'out1_0')
mctracer_server.get(run_path+'/'+'out1_1', 'out1_1')

mctracer_server.execute('rm -r '+run_path)

res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_0')
ground_res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_1')
image = rs.mctracer_bridge.star_light_analysis.make_image_from_sensor_response(reflector, res, rs.mctracer_bridge.star_light_analysis.config)
shadow_image = rs.mctracer_bridge.star_light_analysis.make_image_from_ground_response(reflector, ground_res, rs.mctracer_bridge.star_light_analysis.config)
end = time.time()
rs.mctracer_bridge.star_light_analysis.plot_image(image)
rs.mctracer_bridge.star_light_analysis.plot_image(shadow_image)
#take back value of quality
