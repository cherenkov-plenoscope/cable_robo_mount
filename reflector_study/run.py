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
from .tools import tools
import time

def PSO():
    s = time.time()
    pso_specs = {
        'lower_bounds': [0.1054],# 0.0713, 0.000521, 0.006, 0.006, 1.36, 0.9, 0.6],  ###change here
        'upper_bounds': [0.10541],# 0.163, 0.001322, 0.01, 0.0105, 2.26, 1.5, 1.2], ###change here
        #'lower_bounds': [0.0413, 0.0813, 0.000821, 0.006, 0.006, 1.6, 1.2, 0.75],  ###change here
        #'upper_bounds': [0.0421, 0.0833, 0.0008322, 0.061, 0.006305, 1.61, 1.21, 0.76], ###change here
        'swarmsize': float(1),  ###change here
        'maxiter': float(0),  ###change here
        'working_directory': 'C:\\Users\\Spiros Daglas\\Desktop\\run\\test'}  ###change here

    pso_specs_path = os.path.join(pso_specs['working_directory'], 'pso_specs.json')
    config.write(pso_specs, pso_specs_path)

    xopt, fopt, p, fp = pyswarm.pso(
        run, lb=pso_specs['lower_bounds'], ub=pso_specs['upper_bounds'],
        swarmsize=int(pso_specs['swarmsize']), maxiter=int(pso_specs['maxiter']), debug = True,
        particle_output= True, kwargs={'working_directory': pso_specs['working_directory']})

    pso_results = {
        'xopt': xopt.tolist(),
        'fopt': float(fopt),
        'p': p.tolist(),
        'fp': fp.tolist()}

    results_path = os.path.join(pso_specs['working_directory'], 'results.json')
    config.write(pso_results, results_path)
    e = time.time()
    print(e-s)
    return xopt, fopt, p, fp

def make_run_config(var_vector, template_config):
    run_config = template_config.copy()
    run_config['reflector']['bars']['outer_diameter'] = var_vector[0]  ###change here
    """run_config['tension_ring']['bars']['outer_diameter'] = var_vector[1]  ###change here
    run_config['cables']['cross_section_area'] = var_vector[2]  ###change here
    run_config['reflector']['bars']['thickness'] = var_vector[3]  ###change here
    run_config['tension_ring']['bars']['thickness'] = var_vector[4]  ###change here
    run_config['reflector']['main']['x_over_z_ratio'] = var_vector[5]  ###change here
    run_config['tension_ring']['width'] = var_vector[6]  ###change here
    run_config['reflector']['facet']['inner_hex_radius'] = var_vector[7]  ###change here"""

    return {'run_config': run_config,
            'var_vector': var_vector}


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


def estimate_optical_performance(cfg, dish, alignment, output_path):
    mct = mctracer_bridge.RayTracingMachine(cfg)
    mct_run_path = cfg['system']['merlict']['run_path_linux']
    mctracer_propagate_path = cfg['system']['merlict']['ray_tracer_propagation_path_linux']
    mct.execute('rm -rf '+mct_run_path)
    mct.execute('mkdir '+mct_run_path)

    mct_cfg_path = os.path.join(output_path, 'mct_config.xml')
    mctracer_bridge.write_propagation_config_xml(mct_cfg_path)
    mct_light_path = os.path.join(output_path, 'light.xml')
    mctracer_bridge.write_star_light_xml(reflector=dish, path=mct_light_path)
    mct_scenery_path = os.path.join(output_path, 'scenery.xml')
    mctracer_bridge.write_reflector_xml(reflector=dish, alignment=alignment, path=mct_scenery_path)

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


def estimate_deformed_nodes(structural, dish, windBOOL):
    sap2k = Bridge(structural)
    sap2k._SapObject.Unhide()

    sap2k.save_model_in_working_directory()
    TextFilesBridge.JointsCreate(dish['nodes'], structural)
    TextFilesBridge.FramesCreate(dish['bars_reflector'], dish['bars_tension_ring'], structural)
    sap2k._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

    sap2k._cables_definition(dish['cables'])
    sap2k._restraints_definition(dish['cable_supports'])
    sap2k.load_scenario_dead()
    sap2k.load_scenario_facet_weight(dish['mirror_tripods'])
    sap2k.non_linearity()
    if windBOOL==True:
        sap2k.non_linearity_wind(dish['mirror_tripods'], dish['nodes'])

    #sap2k._restraints_definition(dish['elastic_supports'])
    #sap2k.load_scenario_dead()
    #sap2k.load_scenario_facet_weight(dish['mirror_tripods'])
    #sap2k.load_combination_2LP_definition(structural)

    sap2k._SapModel.Analyze.SetRunCaseFlag("DEAD", False, False)
    sap2k._SapModel.Analyze.SetRunCaseFlag("MODAL", False, False)

    sap2k.run_analysis()

    return sap2k.get_total_absolute_deformations_for_load_combination(
        nodes=dish['nodes'],
        load_combination_name=sap2k.load_combination_name,
        group_name="ALL")


def run(var_vector, working_directory, template_config=config.example):

    run_number = current_run_number(working_directory)
    output_path = os.path.join(working_directory, str(run_number))
    os.mkdir(output_path)
    cfg = make_run_config(var_vector, template_config)["run_config"]
    cfg_path = os.path.join(output_path, 'config.json')
    config.write(cfg, cfg_path)
    variables_vector = make_run_config(var_vector, template_config)["var_vector"]
    variables_vector_path = os.path.join(output_path, 'variables_vector.json')
    config.write(variables_vector.tolist(), variables_vector_path)

    # SET UP REFLECTOR GEOMETRY
    geometry = Geometry(cfg)
    initial_dish = generate_reflector_with_tension_ring_and_cables(geometry)
    structural = Structural(cfg)

    zenith_dish = initial_dish.copy()
    zenith_dish['nodes'] = estimate_deformed_nodes(structural, initial_dish, False)

    alignment = mirror_alignment.ideal_alignment(zenith_dish)

    # DISH ROTATION
    homogenous_transformation = HomTra()
    homogenous_transformation.set_translation(geometry.translational_vector_xyz)
    homogenous_transformation.set_rotation_tait_bryan_angles(
        geometry.tait_bryan_angle_Rx,
        geometry.tait_bryan_angle_Ry,
        geometry.tait_bryan_angle_Rz)

    transformed_dish = initial_dish.copy()
    transformed_dish['nodes'] = get_nodes_moved_position(
        initial_dish["nodes"],
        initial_dish["cable_supports"],
        homogenous_transformation)

    deformed_transformed_dish = transformed_dish.copy()
    deformed_transformed_dish['nodes'] = estimate_deformed_nodes(
        structural,
        deformed_transformed_dish,
        True)

    deformed_dish = deformed_transformed_dish.copy()
    deformed_dish['nodes'] = get_nodes_zenith_position(
        deformed_transformed_dish['nodes'],
        deformed_transformed_dish["cable_supports"],
        homogenous_transformation)

    stddev_of_psf = estimate_optical_performance(
        cfg=cfg,
        dish=deformed_dish,
        alignment=alignment,
        output_path=output_path)

    reflector_weight=float(structural.reflector_material_specific_weight/10*structural.bars_reflector_cs_area*(tools.bars_length(initial_dish["nodes"], initial_dish["bars_reflector"]).sum()))
    tension_ring_weight=float(structural.tension_ring_material_specific_weight/10*structural.bars_tension_ring_cs_area*(tools.bars_length(initial_dish["nodes"], initial_dish["bars_tension_ring"]).sum()))
    max_final_deformation=np.linalg.norm(deformed_dish['nodes'] - initial_dish['nodes'], axis=1).max()

    fitness_function=stddev_of_psf/2+reflector_weight/250+tension_ring_weight/150+max_final_deformation/2  ###change here

    intermediate_results = {
        'fitness_function': fitness_function,
        'stddev_of_psf': float(stddev_of_psf),
        'reflector_bars_length': float(tools.bars_length(initial_dish["nodes"], initial_dish["bars_reflector"]).sum()),
        'tension_ring_bars_length': float(tools.bars_length(initial_dish["nodes"], initial_dish["bars_tension_ring"]).sum()),
        'reflector_weight': reflector_weight,
        'tension_ring_weight': tension_ring_weight,
        'max_intial_deformation': np.linalg.norm(zenith_dish['nodes'] - initial_dish['nodes'], axis=1).max(),
        'max_final_deformation': max_final_deformation,
        'max_in_plane_final_deformation': np.linalg.norm((deformed_dish['nodes'] - initial_dish['nodes'])[:, [0,1]], axis=1).max()
        }
    intermediate_results_path = os.path.join(output_path, 'intermediate_results.json')
    config.write(intermediate_results, intermediate_results_path)

    return fitness_function
