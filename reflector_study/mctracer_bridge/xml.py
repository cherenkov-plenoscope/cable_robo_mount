import numpy as np
from .. import mirror_alignment

def float2str(numeric_value):
    return "{:.9f}".format(numeric_value)


def tuple3(vec):
    return '['+float2str(vec[0])+','+float2str(vec[1])+','+float2str(vec[2])+']'


def scenery_header():
    xml = '<scenery author="Spiros Daglas. Sebastian Achim Mueller" comment="">\n'
    return xml

def scenery_end():
    xml = '</scenery>\n'
    return xml

def color(name, rgb):
    xml = '<color name="'+name+'" rgb="'+tuple3(rgb)+'"/>\n'
    return xml


def constant_function(name, value):
    xml = '<function name="'+name+'">'
    xml+= '    <constant value="'+float2str(value)+'" lower_limit="200e-9" upper_limit="1200e-9"/>'
    xml+= '</function>'
    return xml


def hexagonal_imaging_mirror_facet(
    name,
    position,
    rotation,
    outer_radius,
    curvature_radius,
    reflection_vs_wavelength,
    color):
    xml = '<sphere_cap_hexagonal>\n'
    xml+= '    <set_frame '
    xml+=           'name="'+name+'" '
    xml+=           'pos="'+tuple3(position)+'" '
    xml+=           'rot_axis="'+tuple3(rotation[0])+'" '
    xml+=           'rot_angle="'+float2str(rotation[1])+'"/>\n'
    xml+= '    <set_surface '
    xml+=           'reflection_vs_wavelength="'+reflection_vs_wavelength+'" '
    xml+=           'color="'+color+'"/>\n'
    xml+= '    <set_sphere_cap_hexagonal '
    xml+=           'curvature_radius="'+float2str(curvature_radius)+'" '
    xml+=           'outer_radius="'+float2str(outer_radius)+'"/>\n'
    xml+= '</sphere_cap_hexagonal>\n'
    return xml


def cylinder(name, start_pos, end_pos, radius, color):
    xml = '<cylinder>\n'
    xml+= '    <set_frame name="'+name+'" pos="[0,0,0]" rot="[0,0,0]"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="zero" color="'+color+'"/>\n'
    xml+= '    <set_cylinder radius="'+float2str(radius)+'" start_pos="'+tuple3(start_pos)+'" end_pos="'+tuple3(end_pos)+'"/>\n'
    xml+= '</cylinder>\n'
    return xml


def disc(name, pos, rot, radius, color, refl, sensor_id=None):
    xml = '<disc>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+refl+'" color="'+color+'"/>\n'
    xml+= '    <set_disc radius="'+float2str(radius)+'"/>\n'
    if sensor_id is not None:
        xml+= '    <set_sensitive id="'+str(sensor_id)+'"/>\n'
    xml+= '</disc>\n'
    return xml


def sphere(name, pos, radius, color, reflection_vs_wavelength):
    xml = '<sphere>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="[0,0,0]"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+reflection_vs_wavelength+'" color="'+color+'"/>\n'
    xml+= '    <set_sphere radius="'+float2str(radius)+'"/>\n'
    xml+= '</sphere>\n'
    return xml

def bars2mctracer(reflector):
    nodes = reflector['nodes']
    bars_reflector = reflector['bars_reflector']
    bars_tension_ring = reflector['bars_tension_ring']
    cables = reflector['cables']
    reflector_bar_radius = reflector['geometry'].bar_outer_diameter/2
    tension_ring_bar_radius = reflector['geometry'].bar_outer_diameter
    cables_radius = 0.02
    xml = ''
    for i, bar in enumerate(bars_reflector):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=reflector_bar_radius,
            color='reflector_bar_color')
    for i, bar in enumerate(bars_tension_ring):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=tension_ring_bar_radius,
            color='tension_ring_bar_color')
    for i, bar in enumerate(cables):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=cables_radius,
            color='cable_color')
    return xml


def facets2mctracer(reflector, alignment):
    reflector2facets = mirror_alignment.reflector2facets(
        reflector=reflector,
        alignment=alignment)

    xml = ''
    for i, reflector2facet in enumerate(reflector2facets):

        rot_axis, rot_angle = facet_rot_axis_and_angle(reflector2facet)

        xml+= hexagonal_imaging_mirror_facet(
            name='facet_'+str(i),
            position=reflector2facet.translation(),
            rotation=[rot_axis, rot_angle],
            outer_radius=reflector['geometry'].facet_outer_hex_radius,
            curvature_radius=reflector['geometry'].focal_length*2.0,
            reflection_vs_wavelength='reflection_vs_wavelength',
            color='facet_color'
        )
    return xml


def facet_rot_axis_and_angle(reflector2facet):
    unit_z = np.array([0.0, 0.0, 1.0])
    unit_z_in_Rframe = reflector2facet.transformed_orientation(unit_z)
    rot_axis = np.cross(unit_z, unit_z_in_Rframe)
    angle_to_unit_z = np.arccos(np.dot(unit_z, unit_z_in_Rframe))
    return rot_axis, angle_to_unit_z


def image_sensor(focal_length, PAP_offset, field_of_view):
    sensor_pos = np.array([0, 0, focal_length+PAP_offset])
    sensor_radius = np.tan(field_of_view/2.0)*focal_length

    housing_pos = sensor_pos + np.array([0, 0, 0.001])
    housing_radius = sensor_radius*1.1

    rot = np.array([0., 0., 0.])
    xml = ''
    xml+= disc(
        name='sensor_screen',
        pos=sensor_pos,
        rot=rot,
        radius=sensor_radius,
        color='green',
        refl='zero',
        sensor_id=0)
    xml+= disc(
        name='sensor_housing',
        pos=housing_pos,
        rot=rot,
        radius=housing_radius,
        color='grey',
        refl='zero')
    return xml


def ground(reflector):
    return disc(
        name='ground',
        pos=np.array([0.0, 0.0, -0.1*reflector['geometry'].focal_length]),
        rot=np.array([0,0,0]),
        radius=reflector['geometry'].max_outer_radius*1.25,
        color='grass_green',
        refl='zero',
        sensor_id=1)


def benchmark_scenery(reflector, alignment):
    xml = ''
    xml+= scenery_header()
    xml+= constant_function(name='reflection_vs_wavelength', value=0.9)
    xml+= constant_function(name='zero', value=0.0)
    xml+= color(name='facet_color', rgb=np.array([75,75,75]))
    xml+= color(name='reflector_bar_color', rgb=np.array([255,91,49]))
    xml+= color(name='tension_ring_bar_color', rgb=np.array([178,34,34]))
    xml+= color(name='cable_color', rgb=np.array([255,255,255]))
    xml+= color(name='green', rgb=np.array([25,255,57]))
    xml+= color(name='grey', rgb=np.array([64,64,64]))
    xml+= color(name='grass_green', rgb=np.array([22,91,49]))
    xml+= facets2mctracer(reflector=reflector, alignment=alignment)
    xml+= bars2mctracer(reflector=reflector)
    xml+= image_sensor(
        focal_length=reflector['geometry'].focal_length,
        PAP_offset=alignment['principal_aperture_plane_offset'],
        field_of_view=np.deg2rad(6.5))
    xml+= ground(reflector=reflector)
    xml+= scenery_end()
    return xml


def star_light(radius, pos, number_of_photons):
    xml = ''
    xml+= '<lightsource>\n'
    xml+= '    <parallel_disc\n'
    xml+= '        disc_radius_in_m="'+float2str(radius)+'"\n'
    xml+= '        number_of_photons="'+float2str(number_of_photons)+'"\n'
    xml+= '        pos="'+tuple3(pos)+'"\n'
    xml+= '        rot_in_deg="[0.0, 180.0, 0.0]"\n'
    xml+= '    />\n'
    xml+= '</lightsource>\n'
    return xml


def write_xml(xml, path):
    f = open(path, 'w')
    f.write(xml)
    f.close()


def write_reflector_xml(reflector, alignment, path):
    """
    Writes the benchmark scenery into an mctracer xml file

    Parameter
    ---------
    reflector       The reflector dictionary

    alignment       The alignment dictionary

    path            Path to the output mctracer xml file
    """
    write_xml(
        benchmark_scenery(reflector, alignment),
        path)


def write_star_light_xml(reflector, path, number_of_photons=1e6):
    """
    Writes a steering input xml for the mctracer to simulate parallel star light

    Parameter
    ---------
    reflector           The reflector dictionary

    path                Path of the output xml file

    number_of_photons   The total number of photons to be emitted
    """
    write_xml(
        star_light(
            radius=1.1*reflector['geometry'].max_outer_radius,
            pos=np.array([0.0, 0.0, 10.0*reflector['geometry'].focal_length]),
            number_of_photons=number_of_photons),
        path)


def write_propagation_config_xml(path, mutlithread=True):
    """
    Writes the mctracer propagation config xml.

    Parameter
    ---------
    path                Path of the output xml file

    mutlithread         propagate in parallel if True
    """
    parallel = 'False'
    if mutlithread:
        parallel='True'

    xml = '<settings\n'
    xml+= '    max_number_of_interactions_per_photon="42"\n'
    xml+= '    use_multithread_when_possible="'+parallel+'"\n'
    xml+= '/>\n'
    write_xml(xml, path)


def write_camera_tower_xml(tower_nodes_and_bars, name, pos, rot, color='white'):
    xml = '<frame>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    
    for i, bar in enumerate(tower_nodes_and_bars['bars']):
        start_pos = tower_nodes_and_bars['nodes'][bar[0]]
        end_pos = tower_nodes_and_bars['nodes'][bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=tower_nodes_and_bars['bar_radius'],
            color=color)

    xml+= '</frame>\n'
    return xml