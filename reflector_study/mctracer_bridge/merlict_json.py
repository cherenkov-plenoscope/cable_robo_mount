import numpy as np
import json
from .. import mirror_alignment
from .. import camera
from ..HomTra import HomTra
from .. import optical_geometry

def list_f8(l):
    return [float(l[0]), float(l[1]), float(l[2])]


def hexagonal_imaging_mirror_facet(
    name,
    position,
    rotation,
    outer_radius,
    curvature_radius,
    reflection_vs_wavelength,
    color
):
    return {
        "type": "SphereCapWithHexagonalBound",
        "name": name,
        "pos": list_f8(position),
        "rot_axis": list_f8(rotation[0]),
        "rot_angle": float(rotation[1]),
        "outer_radius": float(outer_radius),
        "curvature_radius": float(curvature_radius),
        "surface": {
            "outer_color": color,
            "outer_reflection": reflection_vs_wavelength},
        "children": [],
    }


def cylinder(name, start_pos, end_pos, radius, color, refl='zero'):
    return {
        "type": "Cylinder",
        "name": name,
        "start_pos": list_f8(start_pos),
        "end_pos": list_f8(end_pos),
        "radius": float(radius),
        "surface": {
            "outer_color": color,
            "outer_reflection": refl},
        "children": []
    }


def disc(name, pos, rot, radius, color, refl):
    return {
        "type": "Disc",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "radius": float(radius),
        "surface": {
            "outer_color": color,
            "outer_reflection": refl},
        "children": []
    }


def sphere(name, pos, radius, color, refl):
    return {
        "type": "Sphere",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "radius": float(radius),
        "surface": {
            "outer_color": color,
            "outer_reflection": refl},
        "children": []
    }


def light_field_sensor_portal(
    name,
    pos,
    rot,
    lens_refraction_vs_wavelength,
    mirror_reflectivity_vs_wavelength
):
    return {
        "type": "LightFieldSensor",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "expected_imaging_system_focal_length": 106.5,
        "expected_imaging_system_aperture_radius": 35.5,
        "max_FoV_diameter_deg": 6.5,
        "hex_pixel_FoV_flat2flat_deg": 0.06667,
        "num_paxel_on_pixel_diagonal": 9,
        "housing_overhead": 1.1,
        "lens_refraction_vs_wavelength": lens_refraction_vs_wavelength,
        "bin_reflection_vs_wavelength": mirror_reflectivity_vs_wavelength,
        "children": []
    }


def cylinder_mount(name, pos, rot, hight, radius, color, refl):
    return {
        "type": "Frame",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "children": [
            disc(
                name=name+'_top',
                pos=[0, 0, hight],
                rot=[0, 0, 0],
                radius=radius,
                color=color,
                refl=refl),
            cylinder(
                name=name+'_body',
                start_pos=[0, 0, 0],
                end_pos=[0, 0, hight],
                radius=radius,
                color=color,
                refl=refl)]
    }


def plane(name, pos, rot, x_width, y_width, color, refl):
    return {
        "type": "Plane",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "x_width": float(x_width),
        "y_width": float(y_width),
        "surface": {
            "outer_color": color,
            "outer_reflection": refl},
        "children": [],
    }


def dish_support_concrete_pillar(
    name,
    pos,
    rot,
    height,
    width,
    color,
    refl
):
    return {
        "type": "Frame",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "children": [
            plane(
                name=name+'_top',
                pos=[0, 0, height],
                rot=[0, 0, 0],
                x_width=width,
                y_width=width,
                color=color,
                refl=refl),
            plane(
                name=name+'_left_side',
                pos=[0, width/2, height/2],
                rot=[np.deg2rad(90), 0, 0],
                x_width=width,
                y_width=height,
                color=color,
                refl=refl),
            plane(
                name=name+'_right_side',
                pos=[0, -width/2, height/2],
                rot=[-np.deg2rad(90), 0, 0],
                x_width=width,
                y_width=height,
                color=color,
                refl=refl),
            plane(
                name=name+'_front_side',
                pos=[width/2, 0, height/2],
                rot=[np.deg2rad(90), 0, np.deg2rad(90)],
                x_width=width,
                y_width=height,
                color=color,
                refl=refl),
            plane(
                name=name+'_rear_side',
                pos=[-width/2, 0, height/2],
                rot=[-np.deg2rad(90), 0, np.deg2rad(90)],
                x_width=width,
                y_width=height,
                color=color,
                refl=refl),
            make_ladder(
                name=name+'_ladder',
                pos=[width/4+0.05, 0, 0],
                rot=[0, 0, 0],
                hight=height),
        ]
    }


def bars_to_merlict(reflector):
    nodes = reflector['nodes']
    bars_reflector = reflector['bars_reflector']
    bars_tension_ring = reflector['bars_tension_ring']
    cables = reflector['cables']
    reflector_bar_radius = reflector['geometry'].bar_outer_diameter/2
    tension_ring_bar_radius = reflector['geometry'].bar_outer_diameter
    cables_radius = 0.02
    bars = []
    for i, bar in enumerate(bars_reflector):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        bars.append(
            cylinder(
                name='bar_'+str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=reflector_bar_radius,
                color='reflector_bar_color'))
    for i, bar in enumerate(bars_tension_ring):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        bars.append(
            cylinder(
                name='bar_'+str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=tension_ring_bar_radius,
                color='tension_ring_bar_color'))
    for i, bar in enumerate(cables):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        bars.append(
            cylinder(
                name='bar_'+str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=cables_radius,
                color='cable_color'))
    return bars


def facets_to_merlict(reflector, alignment):
    reflector2facets = mirror_alignment.reflector2facets(
        reflector=reflector,
        alignment=alignment)
    facets = []
    for i, reflector2facet in enumerate(reflector2facets):
        rot_axis, rot_angle = facet_rot_axis_and_angle(reflector2facet)
        facets.append(
            hexagonal_imaging_mirror_facet(
                name='facet_' + str(i),
                position=reflector2facet.translation(),
                rotation=[rot_axis, rot_angle],
                outer_radius=reflector['geometry'].facet_outer_hex_radius,
                curvature_radius=reflector['geometry'].focal_length*2.0,
                reflection_vs_wavelength='reflection_vs_wavelength',
                color='facet_color'))
    return facets


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
    imse = []
    imse.append(
        disc(
            name='sensor_screen',
            pos=sensor_pos,
            rot=rot,
            radius=sensor_radius,
            color='green',
            refl='zero',
            sensor_id=0))
    imse.append(
        disc(
            name='sensor_housing',
            pos=housing_pos,
            rot=rot,
            radius=housing_radius,
            color='grey',
            refl='zero'))
    return imse


def ground(reflector):
    return disc(
        name='ground',
        pos=np.array([0.0, 0.0, -0.1*reflector['geometry'].focal_length]),
        rot=np.array([0, 0, 0]),
        radius=reflector['geometry'].max_outer_radius*1.25,
        color='grass_green',
        refl='zero',
        sensor_id=1)


def benchmark_scenery(reflector, alignment):
    sc = {}
    sc['functions'] = [
        {
            "name": "zero",
            "argument_versus_value": [
                [200e-9, 0.0],
                [1200e-9, 0.0]]},
        {
            "name": "reflection_vs_wavelength",
            "argument_versus_value": [
                [200e-9, 0.9],
                [1200e-9, 0.9]]}
    ]
    sc['colors'] = [
        {"name": 'facet_color', 'rgb': [75, 75, 75]},
        {"name": 'reflector_bar_color', 'rgb': [255, 91, 49]},
        {"name": 'tension_ring_bar_color', 'rgb': [178, 34, 34]},
        {"name": 'cable_color', 'rgb': [255, 255, 255]},
        {"name": 'green', 'rgb': [25, 255, 57]},
        {"name": 'grey', 'rgb': [64, 64, 64]},
        {"name": 'grass_green', 'rgb':[22, 91, 49]},]
    sc['children'] = [
        ground(reflector=reflector),
        image_sensor(
            focal_length=reflector['geometry'].focal_length,
            PAP_offset=alignment['principal_aperture_plane_offset'],
            field_of_view=np.deg2rad(6.5)),
        bars_to_merlict(reflector=reflector),
    ]
    tmp_facets = facets_to_merlict(reflector=reflector, alignment=alignment)
    for tmp_facet in tmp_facets:
        sc['children'].append(tmp_facet)

    return sc


def star_light(radius, pos, number_of_photons):
    return {
        "parallel_disc": {
            "disc_radius": float(radius),
            "num_photons": float(number_of_photons)},
        "pos": list_f8(pos),
        "rot": [0, 1.5705, 0]}


def write_json(scenery, path):
    with open(path, 'wt') as fout:
        fout.write(json.dumps(scenery, indent=4))


def write_reflector(reflector, alignment, path):
    """
    Writes the benchmark scenery into an merlict json file

    Parameter
    ---------
    reflector       The reflector dictionary

    alignment       The alignment dictionary

    path            Path to the output merlict json file
    """
    write_json(
        benchmark_scenery(reflector, alignment),
        path)


def write_star_light(reflector, path, number_of_photons=1e6):
    """
    Writes a steering input json for the merlict to simulate parallel
    star light

    Parameter
    ---------
    reflector           The reflector dictionary

    path                Path of the output json file

    number_of_photons   The total number of photons to be emitted
    """
    write_json(
        star_light(
            radius=1.1*reflector['geometry'].max_outer_radius,
            pos=np.array([0.0, 0.0, 10.0*reflector['geometry'].focal_length]),
            number_of_photons=number_of_photons),
        path)


def write_propagation_config(path, mutlithread=True):
    """
    Writes the merlict propagation config json.

    Parameter
    ---------
    path                Path of the output json file

    mutlithread         propagate in parallel if True
    """
    write_json(
        {
          "max_num_interactions_per_photon": 1337,
          "use_multithread_when_possible": mutlithread},
        path)


def write_camera_tower(
    tower_nodes_and_bars,
    name,
    pos,
    rot,
    color='white'
):
    children = []
    for i, bar in enumerate(tower_nodes_and_bars['bars']):
        start_pos = tower_nodes_and_bars['nodes'][bar[0]]
        end_pos = tower_nodes_and_bars['nodes'][bar[1]]
        children.append(
            cylinder(
                name='bar_' + str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=tower_nodes_and_bars['bar_radius'],
                color=color))
    return {
        "type": "Frame",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "children": children
    }


def make_ladder(name, pos, rot, hight, color='pale_blue_white'):
    pos = np.array(pos)
    rot = np.array(rot)
    STEP_WIDTH = 0.35
    STEP_PITCH = 0.28
    STEP_RADIUS = 0.016
    PILLAR_RADIUS = 2*STEP_RADIUS
    children = []
    children.append(
        cylinder(
            name='left_pillar',
            start_pos=pos + np.array([0, STEP_WIDTH/2, 0]),
            end_pos=pos + np.array([0, STEP_WIDTH/2, hight]),
            radius=PILLAR_RADIUS,
            color=color))
    children.append(
        cylinder(
        name='right_pillar',
        start_pos=pos + np.array([0, -STEP_WIDTH/2, 0]),
        end_pos=pos + np.array([0, -STEP_WIDTH/2, hight]),
        radius=PILLAR_RADIUS,
        color=color))
    number_of_sprosses = int(np.floor(hight/STEP_PITCH))
    for i in range(number_of_sprosses):
        j = i + 1
        step_hight = j*STEP_PITCH
        start_pos = pos + np.array([0, STEP_WIDTH/2, step_hight])
        end_pos = pos + np.array([0, -STEP_WIDTH/2, step_hight])
        children.append(
            cylinder(
                name='step_'+str(i),
                start_pos=start_pos,
                end_pos=end_pos,
                radius=STEP_RADIUS,
                color=color))
    return {
        "type": "Frame",
        "name": name,
        "pos": list_f8(pos),
        "rot": list_f8(rot),
        "children": children
    }


def visual_scenery(reflector, number_of_dish_pillars=9):
    geometry = reflector['geometry']
    ideal_alignment = mirror_alignment.ideal_alignment(reflector)
    reflector['nodes'] = transform_nodes(
        reflector['nodes'],
        geometry.root2dish)

    sc = {}
    sc['functions'] = [
        {
            "name": "zero",
            "argument_versus_value": [
                [200e-9, 0.0],
                [1200e-9, 0.0]]},
        {
            "name": "reflection_vs_wavelength",
            "argument_versus_value": [
                [200e-9, 1.],
                [1200e-9, 1.]]},
        {
            "name": "refraction_vs_wavelength",
            "argument_versus_value": [
                [200e-9, 1.45],
                [1200e-9, 1.45]]}
    ]
    sc['colors'] = [
        {"name": 'facet_color', 'rgb': [75, 75, 75]},
        {"name": 'pale_blue_white', 'rgb': [225, 255, 255]},
        {"name": 'desert_sand', 'rgb': [204, 102, 0]},
        {"name": 'concrete_grey', 'rgb': [128, 128, 128]},
        {"name": 'cable_color', 'rgb': [140, 128, 128]},
    ]
    sc['children'] = []

    sc['children'].append(
        disc(
            name='ground',
            pos=[0, 0, 0],
            rot=[0, 0, 0],
            radius=10e3,
            color='desert_sand',
            refl='zero'))

    # Reflector dish
    # --------------
    tmp_facets = facets_to_merlict(
        reflector=reflector,
        alignment=ideal_alignment)
    for tmp_facet in tmp_facets:
        sc['children'].append(tmp_facet)

    tmp_bars = bars_to_merlict_2(
        nodes=reflector['nodes'],
        bars=reflector['bars'],
        radius=geometry.bar_outer_diameter/2,
        color='pale_blue_white')
    for tmp_bar in tmp_bars:
        sc['children'].append(tmp_bar)

    # Reflector dish mount
    # --------------------
    dish_radius = geometry.max_outer_radius
    dish_pillar_circle_radius = 0.9*geometry.max_outer_radius*2
    dish_pillar_height = dish_pillar_circle_radius
    dish_pillar_width = 1/20*geometry.max_outer_radius*2
    dish_pillar_az_angles = np.linspace(
        0,
        2*np.pi,
        number_of_dish_pillars,
        endpoint=False)

    for phi in dish_pillar_az_angles:
        r = dish_pillar_width/2+dish_pillar_circle_radius
        dish_pillar_positions = [
            r*np.cos(phi),
            r*np.sin(phi),
            0.0]

        sc['children'].append(
            dish_support_concrete_pillar(
                name='dish_pillar_',
                pos=dish_pillar_positions,
                rot=[0, 0, -phi],
                height=dish_pillar_height,
                width=dish_pillar_width,
                color='concrete_grey',
                refl='zero'))

    # Reflector dish cables
    # ---------------------
    cable_radius = 0.05
    cables_per_pillar = 2
    azimuth_cable_az_angles = np.linspace(
        0,
        2*np.pi,
        cables_per_pillar*number_of_dish_pillars,
        endpoint=False)
    azimuth_cable_az_angle_step = (2*np.pi)/(
        cables_per_pillar*number_of_dish_pillars)
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

            cable_dish_node = geometry.root2dish.transformed_position(
                cable_dish_node)
            nodes = np.array([pillar_node, cable_dish_node])
            bars = np.array([[0, 1]])

            tmp_dish_cables = bars_to_merlict_2(
                nodes=nodes,
                bars=bars,
                radius=cable_radius,
                color='cable_color',
                prefix='dish_cable')
            for tmp_dish_cable in tmp_dish_cables:
                sc['children'].append(tmp_dish_cable)

            nodes = np.array([lower_pillar_node, cable_dish_node])
            bars = np.array([[0, 1]])
            tmp_dish_cables = bars_to_merlict_2(
                nodes=nodes,
                bars=bars,
                radius=cable_radius,
                color='cable_color',
                prefix='lower_dish_cable')
            for tmp_dish_cable in tmp_dish_cables:
                sc['children'].append(tmp_dish_cable)

    # Floor platform
    # --------------
    platfrom_hight = 0.05*geometry.reflector_security_distance_from_ground
    platform_radius = 1.25*geometry.max_outer_radius
    sc['children'].append(
        cylinder_mount(
            name='dish_platform',
            pos=[0, 0, 0],
            rot=[0, 0, 0],
            hight=platfrom_hight,
            radius=platform_radius,
            color='concrete_grey',
            refl='zero'))

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
        [2.37*dish_d, 0.0, 0.0],
        [0.0, 2.37*dish_d, 0.0],
        [-2.37*dish_d, 0.0, 0.0],
        [0.0, -2.37*dish_d, 0.0],
    ]

    for tower_position in tower_positions:
        trafo = HomTra()
        trafo.set_translation(tower_position)
        tmp_tower_bars = bars_to_merlict_2(
            nodes=transform_nodes(camera_tower['nodes'], trafo),
            bars=camera_tower['bars'],
            radius=camera_tower['bar_radius'],
            color='pale_blue_white')
        for tmp_tower_bar in tmp_tower_bars:
            sc['children'].append(tmp_tower_bar)

        base_positions = [
            [+tower_base_width/2, +tower_base_width/2, 0],
            [+tower_base_width/2, -tower_base_width/2, 0],
            [-tower_base_width/2, +tower_base_width/2, 0],
            [-tower_base_width/2, -tower_base_width/2, 0],
        ]

        for base_position in base_positions:
            absolute_base_position = (
                np.array(base_position) +
                np.array(tower_position))
            sc['children'].append(
                cylinder_mount(
                    name='tower_base',
                    pos=absolute_base_position,
                    rot=[0, 0, 0],
                    hight=tower_base_width/16,
                    radius=tower_base_width/6,
                    color='concrete_grey',
                    refl='zero'))

    # Camera case
    # -----------
    f = geometry.focal_length
    lfs_radius = f*np.arctan(np.deg2rad(6.5/2.0))
    camera_structure = camera.factory.generate_camera_space_frame_quint(
        light_field_sensor_radius=lfs_radius*1.1)
    camera_nodes_in_root_frame = transform_nodes(
        nodes=camera_structure['nodes'],
        trafo=geometry.root2camera)

    tmp_case_bars = bars_to_merlict_2(
        nodes=camera_nodes_in_root_frame,
        bars=camera_structure['bars'],
        radius=camera_tower['bar_radius'],
        color='pale_blue_white')
    for tmp_case_bar in tmp_case_bars:
        sc['children'].append(tmp_case_bar)

    z_root2camera = geometry.root2camera.transformed_orientation([0, 0, 1])
    pointing_az = np.arctan2(z_root2camera[1], z_root2camera[0])
    pointing_zd = np.arccos(z_root2camera[2])
    print(
        'pointing_az',
        np.rad2deg(pointing_az),
        'pointing_zd',
        np.rad2deg(pointing_zd))
    sc['children'].append(
        light_field_sensor_portal(
            name='sensor',
            pos=geometry.root2camera.transformed_position([0, 0, 0]),
            rot=np.array([0, pointing_zd, np.deg2rad(180) - pointing_az]),
            lens_refraction_vs_wavelength='refraction_vs_wavelength',
            mirror_reflectivity_vs_wavelength='reflection_vs_wavelength',))

    # Camera cables
    # -------------
    for i, tower_position in enumerate(tower_positions):

        upper_tower_cable_node = (
            np.array(tower_position) +
            np.array([0, 0, tower_hight]))
        lower_tower_cable_node = (
            np.array(tower_position) +
            np.array([0, 0, tower_hight*0.45]))

        upper_camera_cable_node = camera_nodes_in_root_frame[
            camera_structure['cable_supports']['upper'][i - 1]
        ]

        lower_camera_cable_node = camera_nodes_in_root_frame[
            camera_structure['cable_supports']['lower'][i - 1]
        ]

        nodes = np.array([upper_tower_cable_node, lower_camera_cable_node])
        bars = np.array([[0, 1]])

        tmp_camera_cables = bars_to_merlict_2(
            nodes=nodes,
            bars=bars,
            radius=cable_radius,
            color='cable_color',
            prefix='camera_cable')
        for tmp_camera_cable in tmp_camera_cables:
            sc['children'].append(tmp_camera_cable)

        nodes = np.array([lower_tower_cable_node, upper_camera_cable_node])
        bars = np.array([[0, 1]])

        tmp_camera_cables = bars_to_merlict_2(
            nodes=nodes,
            bars=bars,
            radius=cable_radius,
            color='cable_color',
            prefix='camera_cable')
        for tmp_camera_cable in tmp_camera_cables:
            sc['children'].append(tmp_camera_cable)

        # static cables
        upper_tower_cable_anchor = 2*np.array(tower_position)
        lower_tower_cable_anchor = 1.4*np.array(tower_position)

        nodes = np.array([upper_tower_cable_anchor, upper_tower_cable_node])
        bars = np.array([[0, 1]])
        tmp_camera_cables = bars_to_merlict_2(
            nodes=nodes,
            bars=bars,
            radius=cable_radius,
            color='cable_color',
            prefix='camera_cable')
        for tmp_camera_cable in tmp_camera_cables:
            sc['children'].append(tmp_camera_cable)

        sc['children'].append(
            cylinder_mount(
                name='upper_tower_cable_anchor',
                pos=upper_tower_cable_anchor,
                rot=[0, 0, 0],
                hight=tower_base_width/16,
                radius=tower_base_width/6,
                color='concrete_grey',
                refl='zero'))

        nodes = np.array([lower_tower_cable_anchor, lower_tower_cable_node])
        bars = np.array([[0, 1]])

        tmp_bars = bars_to_merlict_2(
            nodes=nodes,
            bars=bars,
            radius=cable_radius,
            color='cable_color',
            prefix='camera_cable')

        for tmp_bar in tmp_bars:
            sc['children'].append(tmp_bar)

        sc['children'].append(
            cylinder_mount(
                name='lower_tower_cable_anchor',
                pos=lower_tower_cable_anchor,
                rot=[0, 0, 0],
                hight=tower_base_width/16,
                radius=tower_base_width/6,
                color='concrete_grey',
                refl='zero'))

    return sc


def transform_nodes(nodes, trafo):
    nodes_t = np.zeros(shape=nodes.shape)
    for i, node in enumerate(nodes):
        nodes_t[i] = trafo.transformed_position(node)
    return nodes_t


def bars_to_merlict_2(nodes, bars, radius=0.05, color='white', prefix='bar'):
    bar_dicts = []
    for i, bar in enumerate(bars):
            start_pos = nodes[bar[0]]
            end_pos = nodes[bar[1]]
            bar_dicts.append(
                cylinder(
                    name=prefix + '_' + str(i),
                    start_pos=start_pos,
                    end_pos=end_pos,
                    radius=radius,
                    color=color))
    return bar_dicts
