import numpy as np
from .. import mirror_alignment
from .. import camera 
from ..HomTra import HomTra
from .. import optical_geometry 

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
    xml = '<function name="'+name+'">\n'
    xml+= '    <constant value="'+float2str(value)+'" lower_limit="200e-9" upper_limit="1200e-9"/>\n'
    xml+= '</function>\n'
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


def cylinder(name, start_pos, end_pos, radius, color, refl='zero'):
    xml = '<cylinder>\n'
    xml+= '    <set_frame name="'+name+'" pos="[0,0,0]" rot="[0,0,0]"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+refl+'" color="'+color+'"/>\n'
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


def cylinder_mount_xml(name, pos, rot, hight, radius, color, refl):
    xml = '<frame>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    xml+= '    '+disc(
        name=name+'_top', 
        pos=[0,0,hight], 
        rot=[0,0,0], 
        radius=radius, 
        color=color, 
        refl=refl)
    xml+= '    '+cylinder(
        name=name+'_body', 
        start_pos=[0,0,0], 
        end_pos=[0,0,hight], 
        radius=radius, 
        color=color,
        refl=refl)
    xml+= '</frame>\n'
    return xml


def plane_xml(name, pos, rot, x_width, y_width, color, refl):
    xml = '<plane>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+refl+'" color="'+color+'"/>\n'
    xml+= '    <set_plane x_width="'+float2str(x_width)+'" y_width="'+float2str(y_width)+'"/>\n'
    xml+= '</plane>\n'
    return xml    

def triangle_xml(name, pos, rot, Ax, Ay, Bx, By, Cx, Cy, color, refl):
    xml = '<triangle>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    xml+= '    <set_surface reflection_vs_wavelength="'+refl+'" color="'+color+'"/>\n'
    xml+= '    <set_triangle '
    xml+= 'Ax="'+float2str(Ax)+'" '
    xml+= 'Ay="'+float2str(Ay)+'" '
    xml+= 'Bx="'+float2str(Bx)+'" '
    xml+= 'By="'+float2str(By)+'" '
    xml+= 'Cx="'+float2str(Cx)+'" '
    xml+= 'Cy="'+float2str(Cy)+'" />\n'
    xml+= '</triangle>\n'
    return xml

def dish_support_concrete_pillar_xml(name, pos, rot, height, width, color, refl):
    xml = '<frame>\n'
    xml+= '    <set_frame name="'+name+'" pos="'+tuple3(pos)+'" rot="'+tuple3(rot)+'"/>\n'
    xml+= plane_xml(
        name=name+'_top', 
        pos=[0,0,height], 
        rot=[0,0,0], 
        x_width=width, 
        y_width=width, 
        color=color, 
        refl=refl)
    xml+= plane_xml(
        name=name+'_left_side', 
        pos=[0,width/2,height/2], 
        rot=[np.deg2rad(90),0,0], 
        x_width=width, 
        y_width=height, 
        color=color, 
        refl=refl)
    xml+= plane_xml(
        name=name+'_right_side', 
        pos=[0,-width/2,height/2], 
        rot=[-np.deg2rad(90),0,0], 
        x_width=width, 
        y_width=height, 
        color=color, 
        refl=refl)
    xml+= plane_xml(
        name=name+'_front_side', 
        pos=[width/2,0,height/2], 
        rot=[np.deg2rad(90),0,np.deg2rad(90)], 
        x_width=width, 
        y_width=height, 
        color=color, 
        refl=refl)
    xml+= plane_xml(
        name=name+'_rear_side', 
        pos=[-width/2,0,height/2], 
        rot=[-np.deg2rad(90),0,np.deg2rad(90)], 
        x_width=width, 
        y_width=height, 
        color=color, 
        refl=refl)
    xml+= '</frame>\n'
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


def visual_scenery(reflector, number_of_dish_pillars=9):

    geometry = reflector['geometry']

    ideal_alignment = mirror_alignment.ideal_alignment(reflector)

    reflector['nodes'] = transform_nodes(reflector['nodes'], geometry.root2dish)

    xml = scenery_header()
    xml+= constant_function('zero', value=0.0)
    xml+= constant_function(name='reflection_vs_wavelength', value=0.9)
    xml+= color('desert_sand', [102,51,0])
    xml+= color(name='facet_color', rgb=np.array([75,75,75]))
    xml+= color(name='pale_blue_white', rgb=np.array([225,255,255]))
    xml+= color(name='red', rgb=np.array([225,0,0]))
    xml+= color(name='concrete_grey', rgb=np.array([128,128,128]))
    xml+= disc('ground', pos=[0,0,0], rot=[0,0,0], radius=10e3, color='desert_sand', refl='zero')

    # Reflector dish
    # --------------
    xml+= facets2mctracer(reflector=reflector, alignment=ideal_alignment)
    xml+= bars2xml(
        nodes=reflector['nodes'],
        bars=reflector['bars'],
        radius=geometry.bar_outer_diameter/2,
        color='pale_blue_white')

    # Reflector dish mount
    # --------------------
    dish_radius = geometry.max_outer_radius
    dish_pillar_circle_radius = 0.9*geometry.max_outer_radius*2
    dish_pillar_height = dish_pillar_circle_radius
    dish_pillar_width = 1/20*geometry.max_outer_radius*2
    dish_pillar_az_angles = np.linspace(0,2*np.pi,number_of_dish_pillars, endpoint=False)

    for phi in dish_pillar_az_angles:

        r = dish_pillar_width/2+dish_pillar_circle_radius
        dish_pillar_positions = [
            r*np.cos(phi),
            r*np.sin(phi),
            0.0]

        xml+= dish_support_concrete_pillar_xml(
            name='dish_pillar_', 
            pos=dish_pillar_positions, 
            rot=[0,0,-phi], 
            height=dish_pillar_height, 
            width=dish_pillar_width, 
            color='concrete_grey', 
            refl='zero')

    # Reflector dish cables
    # ---------------------
    cable_radius = 0.1
    cables_per_pillar = 2
    azimuth_cable_az_angles = np.linspace(
        0, 2*np.pi, 
        cables_per_pillar*number_of_dish_pillars, endpoint=False)
    azimuth_cable_az_angle_step = (2*np.pi)/(cables_per_pillar*number_of_dish_pillars)
    upper_dish_node_z = optical_geometry.z_hybrid(
        distance_to_z_axis=geometry.max_outer_radius, 
        focal_length=geometry.focal_length, 
        dc_over_pa=geometry.davies_cotton_over_parabola_ratio)

    for pillar in range(number_of_dish_pillars):
        phi = dish_pillar_az_angles[pillar]
        pillar_node = np.array([
            dish_pillar_circle_radius*np.cos(phi),
            dish_pillar_circle_radius*np.sin(phi),
            dish_pillar_height])

        lower_pillar_node = np.array([
            dish_pillar_circle_radius*np.cos(phi),
            dish_pillar_circle_radius*np.sin(phi),
            0.0])


        for cable in range(cables_per_pillar):
            theta = azimuth_cable_az_angles[pillar*cables_per_pillar+cable] 
            theta -= azimuth_cable_az_angle_step/2
            cable_dish_node = np.array([
                dish_radius*np.cos(theta),
                dish_radius*np.sin(theta),
                upper_dish_node_z])

            cable_dish_node = geometry.root2dish.transformed_position(cable_dish_node)
            nodes = np.array([pillar_node, cable_dish_node])
            bars = np.array([[0,1]])
            xml+= bars2xml(
                nodes=nodes, 
                bars=bars, 
                radius=cable_radius, 
                color='red', 
                prefix='dish_cable')

            nodes = np.array([lower_pillar_node, cable_dish_node])
            bars = np.array([[0,1]])
            xml+= bars2xml(
                nodes=nodes, 
                bars=bars, 
                radius=cable_radius, 
                color='red', 
                prefix='lower_dish_cable')            


    # Floor platform
    # --------------
    platfrom_hight = 0.05*geometry.reflector_security_distance_from_ground
    platform_radius = 1.25*geometry.max_outer_radius
    xml+= cylinder_mount_xml(
        name='dish_platform', 
        pos=[0,0,0], 
        rot=[0,0,0], 
        hight=platfrom_hight, 
        radius=platform_radius, 
        color='concrete_grey', 
        refl='zero')

    # Camera masts
    # ------------

    dish_d = geometry.max_outer_radius*2
    tower_base_width = dish_d*0.27722
    tower_hight = dish_d*2.277
    camera_tower = camera.factory.generate_camera_tower(
        hight=tower_hight, 
        top_width=dish_d*0.0594,
        base_width=tower_base_width, 
        bar_radius=(dish_d*0.0594)/33)

    tower_positions = [
        [2.37*dish_d,0.0,0.0],
        [0.0,2.37*dish_d,0.0],
        [-2.37*dish_d,0.0,0.0],
        [0.0,-2.37*dish_d,0.0],
    ]

    for tower_position in tower_positions:
        trafo = HomTra()
        trafo.set_translation(tower_position)
        xml+= bars2xml(
            nodes=transform_nodes(camera_tower['nodes'], trafo), 
            bars=camera_tower['bars'],
            radius=camera_tower['bar_radius'],
            color='pale_blue_white')

        base_positions = [
            [+tower_base_width/2,+tower_base_width/2,0],
            [+tower_base_width/2,-tower_base_width/2,0],
            [-tower_base_width/2,+tower_base_width/2,0],
            [-tower_base_width/2,-tower_base_width/2,0],
        ]

        for base_position in base_positions:
            absolute_base_position = np.array(base_position) + np.array(tower_position)
            xml += cylinder_mount_xml(
                name='tower_base', 
                pos=absolute_base_position, 
                rot=[0,0,0], 
                hight=tower_base_width/16, 
                radius=tower_base_width/6, 
                color='concrete_grey', 
                refl='zero')

    # Camera case
    # -----------
    f = geometry.focal_length
    lfs_radius = f*np.arctan(np.deg2rad(6.5/2.0))
    camera_structure = camera.factory.generate_camera_space_frame_quint(
        light_field_sensor_radius=lfs_radius)
    camera_nodes_in_root_frame = transform_nodes(
        nodes=camera_structure['nodes'], 
        trafo=geometry.root2camera)

    xml+= bars2xml(
        nodes=camera_nodes_in_root_frame, 
        bars=camera_structure['bars'],
        radius=camera_tower['bar_radius'],
        color='pale_blue_white')

    # Camera cables
    # -------------
    for i, tower_position in enumerate(tower_positions):

        upper_tower_cable_node = np.array(tower_position) + np.array([0,0,tower_hight])
        lower_tower_cable_node = np.array(tower_position) + np.array([0,0,tower_hight*0.45])

        upper_camera_cable_node = camera_nodes_in_root_frame[
            camera_structure['cable_supports']['upper'][i - 1]
        ]

        lower_camera_cable_node = camera_nodes_in_root_frame[
            camera_structure['cable_supports']['lower'][i - 1]
        ]

        nodes = np.array([upper_tower_cable_node, lower_camera_cable_node]) 
        bars = np.array([[0,1]])
        xml+= bars2xml(
            nodes=nodes, 
            bars=bars, 
            radius=cable_radius, 
            color='red', 
            prefix='camera_cable')

        nodes = np.array([lower_tower_cable_node, upper_camera_cable_node])
        bars = np.array([[0,1]])
        xml+= bars2xml(
            nodes=nodes, 
            bars=bars, 
            radius=cable_radius, 
            color='red', 
            prefix='camera_cable')

    xml+= scenery_end()
    return xml

def transform_nodes(nodes, trafo):
    nodes_t = np.zeros(shape=nodes.shape)
    for i, node in enumerate(nodes):
        nodes_t[i] = trafo.transformed_position(node)
    return nodes_t

def bars2xml(nodes, bars, radius=0.05, color='white', prefix='bar'):
    xml = ''
    for i, bar in enumerate(bars):
            start_pos = nodes[bar[0]]
            end_pos = nodes[bar[1]]
            xml += cylinder(
                name=prefix+'_'+str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=radius,
                color=color)
    return xml