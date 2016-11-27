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
    xml+=           'rot="'+tuple3(rotation)+'"/>\n'
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
        xml+= '    <sensitive id="'+str(sensor_id)+'"/>\n'
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
    bars = reflector['bars']
    bar_radius = reflector['geometry'].bar_outer_radius
    xml = ''
    for i, bar in enumerate(bars):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=bar_radius,
            color='bar_color')
    return xml


def facets2mctracer(reflector, alignment):
    HomTras_reflector2facet = mirror_alignment.reflector2facets(
        reflector, 
        alignment)

    xml = ''
    for i, HomTra_reflector2facet in enumerate(HomTras_reflector2facet):

        xml+= hexagonal_imaging_mirror_facet(
            name='facet_'+str(i),
            position=HomTra_reflector2facet.translation(),
            rotation=np.array([0,0,0]),
            outer_radius=reflector['geometry'].facet_outer_hex_radius,
            curvature_radius=reflector['geometry'].focal_length*2.0,
            reflection_vs_wavelength='reflection_vs_wavelength',
            color='facet_color'
        )
    return xml


def facet_rot_axis_and_angle(HomTra_reflector2facet):
    unit_z = np.array([0.0, 0.0, 1.0])
    unit_z_in_Rframe = HomTra_reflector2facet.transformed_orientation(unit_z)
    rot_axis = np.cross(unit_z, unit_z_in_Rframe)
    angle_to_unit_z = np.arccos(np.dot(unit_z, unit_z_in_Rframe))
    return rot_axis, angle_to_unit_z


def image_sensor(focal_length, field_of_view):
    sensor_pos = np.array([0, 0, focal_length])
    sensor_radius = np.tan(field_of_view/2.0)*focal_length

    housing_pos = sensor_pos + np.array([0, 0, 0.001])
    housing_radius = sensor_radius*1.1

    rot = np.array([0., 0., 0.])
    xml = ''
    xml+= disc(name='sensor_screen', pos=sensor_pos, rot=rot, radius=sensor_radius, color='green', refl='zero', sensor_id=0)
    xml+= disc(name='sensor_housing', pos=housing_pos, rot=rot, radius=housing_radius, color='grey', refl='zero')
    return xml


def benchmark_scenery(reflector, alignment):
    xml = ''
    xml+= scenery_header()
    xml+= constant_function(name='reflection_vs_wavelength', value=0.9)
    xml+= constant_function(name='zero', value=0.0)
    xml+= color(name='facet_color', rgb=np.array([75,75,75]))
    xml+= color(name='bar_color', rgb=np.array([255,91,49]))
    xml+= color(name='green', rgb=np.array([25,255,57]))
    xml+= color(name='grey', rgb=np.array([64,64,64]))
    xml+= facets2mctracer(reflector=reflector, alignment=alignment)
    xml+= bars2mctracer(reflector=reflector)
    xml+= image_sensor(focal_length=reflector['geometry'].focal_length, field_of_view=np.deg2rad(6.5))
    xml+= scenery_end()
    return xml


def write_xml(xml, path):
    f = open(path, 'w')
    f.write(xml)
    f.close()


def reflector2scenery(reflector, alignment, path):
    write_xml(
        benchmark_scenery(reflector, alignment),
        path)