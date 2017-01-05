import reflector_study as rs
import subprocess

geometry = rs.Geometry([0.04,0], rs.config.example)
reflector = rs.factory.generate_reflector(geometry)
alignment = rs.mirror_alignment.ideal_alignment(reflector)

rs.mctracer_bridge.write_propagation_config_xml('config.xml')
rs.mctracer_bridge.write_star_light_xml(reflector=reflector, path='light.xml')
rs.mctracer_bridge.write_reflector_xml(reflector=reflector, alignment=alignment, path='scenery.xml')

subprocess.call(
    args=[ '/home/sebastian/raytracing/build/mctPropagate',
        '-s', 'scenery.xml',
        '-c', 'config.xml',
        '-i', 'light.xml',
        '-o', 'out',
        '-b'])

res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_0')
ground_res = rs.mctracer_bridge.star_light_analysis.read_binary_response('out1_1')


image = rs.mctracer_bridge.star_light_analysis.make_image_from_sensor_response(reflector, res, rs.mctracer_bridge.star_light_analysis.config)
shadow_image = rs.mctracer_bridge.star_light_analysis.make_image_from_ground_response(reflector, ground_res, rs.mctracer_bridge.star_light_analysis.config)

rs.mctracer_bridge.star_light_analysis.plot_image(image)
rs.mctracer_bridge.star_light_analysis.plot_image(shadow_image)