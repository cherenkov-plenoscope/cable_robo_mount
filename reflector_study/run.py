import os
from . import pyswarm
from . import config
from .Geometry import Geometry
from .factory import generate_reflector_with_tension_ring_and_cables
from .SAP2000_bridge.Structural import Structural
from .SAP2000_bridge.HomTra_bridge_tools import get_nodes_moved_position, get_nodes_zenith_position
from .SAP2000_bridge.Bridge import Bridge
from .SAP2000_bridge import TextFilesBridge
from .HomTra import HomTra
from . import mctracer_bridge
from . import mirror_alignment
import numpy as np


def make_run_config(var_vector, template_config):
    run_config = template_config.copy()
    run_config['reflector']['bars']['outer_diameter'] = var_vector[0]
    run_config['tension_ring']['bars']['outer_diameter'] = var_vector[1]
    run_config['cables']['cross_section_area'] = var_vector[2]
    return run_config


def current_run_number(working_directory):
    paths_in_working_directory = os.listdir(working_directory)
    dirs_in_working_directory = []
    for path in paths_in_working_directory:
        path = os.path.join(working_directory, path)
        if os.path.isdir(path):
            dirs_in_working_directory.append(path)

    run_numbers_in_working_directory = []
    for run_dir in dirs_in_working_directory:
        run_dir_name = os.path.split(run_dir)[1]
        run_numbers_in_working_directory.append(int(run_dir_name))
    run_numbers_in_working_directory = np.array(run_numbers_in_working_directory)
    if run_numbers_in_working_directory.shape[0] == 0:
        return 0

    max_run_number = run_numbers_in_working_directory.max()
    return  max_run_number + 1


def run(var_vector, working_directory, template_config=config.example):

    run_number = current_run_number(working_directory)
    output_path = os.path.join(working_directory, str(run_number))
    os.mkdir(output_path)
    cfg = make_run_config(var_vector, template_config)
    cfg_path = os.path.join(output_path, 'config.json')
    config.write(cfg, cfg_path)

    # SET UP REFLECTOR GEOMETRY
    geometry = Geometry(cfg)
    dish = generate_reflector_with_tension_ring_and_cables(geometry)
    alignment = mirror_alignment.ideal_alignment(dish)
    nodes = dish["nodes"]
    bars_reflector = dish["bars_reflector"]
    bars_tension_ring = dish["bars_tension_ring"]
    cables = dish["cables"]
    elastic_supports = dish["elastic_supports"]
    cable_supports = dish["cable_supports"]
    mirror_tripods = dish["mirror_tripods"]
    fixtures = dish["elastic_supports"]

    # DISH ROTATION
    homogenous_transformation = HomTra()
    homogenous_transformation.set_translation(geometry.translational_vector_xyz)
    homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
    nodes_rotated = get_nodes_moved_position(dish["nodes"], dish["cable_supports"], homogenous_transformation)

    # RUN SAP
    structural = Structural(cfg)
    sap2k = Bridge(structural)
    #sap2k._SapObject.Hide()
    #sap2k._SapObject.Unhide()

    sap2k.save_model_in_working_directory()
    TextFilesBridge.JointsCreate(nodes_rotated, structural.SAP_2000_working_directory)
    TextFilesBridge.FramesCreate(bars_reflector, bars_tension_ring, structural)
    sap2k._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

    sap2k._cables_definition(cables)
    sap2k._restraints_definition(cable_supports)

    sap2k.load_scenario_dead()
    sap2k.load_scenario_facet_weight(mirror_tripods)
    sap2k.load_scenario_wind(mirror_tripods, nodes_rotated)

    sap2k.load_combination_3LP_definition(structural)

    """
    run analysis and take Results
    """
    sap2k._SapModel.Analyze.SetRunCaseFlag("DEAD", False, False)
    sap2k._SapModel.Analyze.SetRunCaseFlag("MODAL", False, False)

    sap2k.run_analysis()

    nodes_deformed_rotated= sap2k.get_total_absolute_deformations_for_load_combination(nodes= nodes_rotated, load_combination_name= "dead+live+wind", group_name= "ALL")
    nodes_deformed = get_nodes_zenith_position(nodes_deformed_rotated, cable_supports, homogenous_transformation)

    dish_deformed = dish.copy()
    dish_deformed['nodes'] = nodes_deformed

    mct = mctracer_bridge.RayTracingMachine(cfg)
    mct_run_path = cfg['system']['mctracer']['run_path_linux']
    mctracer_propagate_path = cfg['system']['mctracer']['ray_tracer_propagation_path_linux']
    mct.execute('rm -rf '+mct_run_path)
    mct.execute('mkdir '+mct_run_path)

    mct_cfg_path = os.path.join(output_path, 'mct_config.xml')
    mctracer_bridge.write_propagation_config_xml(mct_cfg_path)
    mct_light_path = os.path.join(output_path, 'light.xml')
    mctracer_bridge.write_star_light_xml(reflector=dish_deformed, path=mct_light_path)
    mct_scenery_path = os.path.join(output_path, 'scenery.xml')
    mctracer_bridge.write_reflector_xml(reflector=dish_deformed, alignment=alignment, path=mct_scenery_path)

    mct.put(mct_cfg_path, mct_run_path+'/'+'config.xml')
    mct.put(mct_light_path, mct_run_path+'/'+'light.xml')
    mct.put(mct_scenery_path, mct_run_path+'/'+'scenery.xml')
    mct.execute(
        command=mctracer_propagate_path+
            ' -s '+mct_run_path+'/'+'scenery.xml'+
            ' -c '+mct_run_path+'/'+'config.xml'+
            ' -i '+mct_run_path+'/'+'light.xml'+
            ' -o '+mct_run_path+'/'+'out'+
            ' -b',
        out_path='mct_call')

    mct_camera_response_path = os.path.join(output_path, 'camera_response.bin')
    mct.get(mct_run_path+'/'+'out1_0', mct_camera_response_path)

    mct_ground_response_path = os.path.join(output_path, 'ground_response.bin')
    mct.get(mct_run_path+'/'+'out1_1', mct_ground_response_path)

    camera_res = mctracer_bridge.star_light_analysis.read_binary_response(mct_camera_response_path)
    ground_res = mctracer_bridge.star_light_analysis.read_binary_response(mct_ground_response_path)
    stddev_of_psf = mctracer_bridge.star_light_analysis.stddev_of_point_spread_function(camera_res)
    image = mctracer_bridge.star_light_analysis.make_image_from_sensor_response(
        dish,
        camera_res,
        cfg['star_light_analysis'])
    ground_image = mctracer_bridge.star_light_analysis.make_image_from_ground_response(
        dish,
        ground_res,
        cfg['star_light_analysis'])

    mctracer_bridge.star_light_analysis.save_image(image, os.path.join(output_path, 'camera_image.png'))
    mctracer_bridge.star_light_analysis.save_image(ground_image, os.path.join(output_path, 'ground_image.png'))

    return stddev_of_psf

def PSO():
    lb = [0.0081, 0.0121, 0]
    ub = [0.05, 0.1, 0.000314]
    xopt, fopt, p, fp = pyswarm.pso(
        run, lb, ub, swarmsize = 5, maxiter = 10, debug = True, particle_output= True,
        kwargs={'working_directory': 'C:\\Users\\Spiros Daglas\\Desktop\\run_test'})
    return xopt, fopt, p, fp
