import reflector_study as rs


def absolute_minimum_loop(config_new):
geometry = rs.Geometry(rs.config_new.example)
reflector = rs.factory.generate_reflector(geometry)
alignment = rs.mirror_alignment.ideal_alignment(reflector)
structural = rs.SAP2000_bridge.Structural(rs.config_new.example)
mctracer_server = rs.mctracer_bridge.RayTracingMachine(rs.config_new.example)

run_path = config_new.example['system']['ssh_connection']['run_path_linux']
mctracer_propagate_path = config_new.example['system']['ssh_connection']['mctracer_propagate_path']
mctracer_server.call('mkdir '+run_path)

bridge = rs.SAP2000_bridge.Bridge(structural)
bridge.nodes_definition(reflector)
bridge.frames_definition(reflector)
bridge.restraints_definition(reflector)
bridge.load_scenario_dead()
bridge.load_scenario_facet_weight(reflector)
bridge.load_combination_2LP_definition()
bridge.run_analysis()
reflector, reflector_deformed = bridge.get_deformed_reflector_for_all_nodes_for_selected_load_combination(reflector, "dead+live")

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
image = rs.mctracer_bridge.star_light_analysis.make_image_from_sensor_response(reflector, res, rs.mctracer_bridge.star_light_analysis.config)
rs.mctracer_bridge.star_light_analysis.plot_image(image)
