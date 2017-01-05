import reflector_study as rs
import numpy as np
import subprocess

geometry = rs.Geometry([0.04,0], rs.config.example)
reflector = rs.factory.generate_reflector(geometry)
alignment = rs.mirror_alignment.ideal_alignment(reflector)

stddev_of_node_position_noise = 0.0001
number_of_nodes = reflector['nodes'].shape[0]
x_noise = np.random.normal(loc=0.0, scale=stddev_of_node_position_noise, size=number_of_nodes)
y_noise = np.random.normal(loc=0.0, scale=stddev_of_node_position_noise, size=number_of_nodes)
z_noise = np.random.normal(loc=0.0, scale=stddev_of_node_position_noise, size=number_of_nodes)

deformed_reflector = reflector.copy()
deformed_reflector['nodes'][:,0] += x_noise
deformed_reflector['nodes'][:,1] += y_noise
deformed_reflector['nodes'][:,2] += z_noise

rs.mctracer_bridge.write_propagation_config_xml('config.xml')
rs.mctracer_bridge.write_star_light_xml(reflector=reflector, path='light.xml')
rs.mctracer_bridge.write_reflector_xml(reflector=deformed_reflector, alignment=alignment, path='scenery.xml')

subprocess.call(
    args=[ '/home/sebastian/raytracing/build/mctPropagate',
        '-s', 'scenery.xml',
        '-c', 'config.xml',
        '-i', 'light.xml',
        '-o', 'out',
        '-b'])

res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_0')
ground_res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_1')
stddev = rs.mctracer_bridge.star_light_analysis.stddev_of_point_spread_function(res)

image = rs.mctracer_bridge.star_light_analysis.make_image_from_sensor_response(reflector, res, rs.mctracer_bridge.star_light_analysis.config)
shadow_image = rs.mctracer_bridge.star_light_analysis.make_image_from_ground_response(reflector, ground_res, rs.mctracer_bridge.star_light_analysis.config)

rs.mctracer_bridge.star_light_analysis.plot_image(image)
rs.mctracer_bridge.star_light_analysis.plot_image(shadow_image)