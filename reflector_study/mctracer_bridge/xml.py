import numpy as np

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
    xml+= '    <constant value="'+str(value)+'" lower_limit="200e-9" upper_limit="1200e-9"/>'
    xml+= '</function>'
    return xml


def hexagonal_imaging_mirror_facet(
    name,
    position,
    rotation,
    outer_radius,
    curvature_radius,
    reflection_vs_wavelength):
    xml = '<sphere_cap_hexagonal>\n'
    xml+= '    <set_frame '
    xml+=           'name="'+name+'" '
    xml+=           'pos="'+tuple3(position)+'" '
    xml+=           'rot="'+tuple3(rotation)+'">\n'
    xml+= '    <set_surface '
    xml+=           'reflection_vs_wavelength="'+reflection_vs_wavelength+'" '
    xml+=           'color="[75,75,75]"/>\n'
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


def sphere(name, pos, radius, color, reflection_vs_wavelength):
    xml = '<sphere>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="[0,0,0]"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+reflection_vs_wavelength+'" color="'+color+'"/>\n'
    xml+= '    <set_sphere radius="'+float2str(radius)+'"/>\n'
    xml+= '</sphere>\n'
    return xml


def bars2mctracer(nodes, bars, bar_radius, bar_color):
    xml = ''
    for i, bar in enumerate(bars):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        xml += cylinder(
            name='bar_'+str(i),
            start_pos=start_pos,
            end_pos=end_pos,
            radius=bar_radius,
            color=bar_color)
    return xml


def facets2mctracer(HomTras_reflector2facet, reflector):
    xml = ''
    for i, HomTra_reflector2facet in enumerate(HomTras_reflector2facet):

        xml+= hexagonal_imaging_mirror_facet(
            name='facet_'+str(i),
            position=HomTra_reflector2facet.translation(),
            rotation=np.array([0,0,0]),
            outer_radius=reflector['geometry'].facet_outer_hex_radius,
            curvature_radius=reflector['geometry'].focal_length*2.0,
            reflection_vs_wavelength='reflection_vs_wavelength'
        )
    return xml