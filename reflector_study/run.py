import os
from . import pyswarm
from . import config
from .Geometry import Geometry
from .SAP2000_bridge.Structural import Structural
from .SAP2000_bridge.HomTra_bridge_tools import get_nodes_translated_position, get_nodes_zenith_position
from .SAP2000_bridge.Bridge import Bridge
from .SAP2000_bridge import TextFilesBridge
from .factory import generate_reflector
from .HomTra import HomTra

def run(var_vector, cfg=config.example):

    #os.mkdir(output_path)
    #cfg_path = os.path.join(output_path, 'config.json')
    #config.write(cfg, cfg_path)

    # SET UP REFLECTOR GEOMETRY
    geometry = Geometry(var_vector, cfg)
    reflector = generate_reflector(geometry)
    nodes = reflector["nodes"]
    bars = reflector["bars"]
    mirror_tripods = reflector["mirror_tripods"]
    fixtures = reflector["fixtures"]

    # DISH ROTATION
    homogenous_transformation = HomTra()
    homogenous_transformation.set_translation(geometry.translational_vector_xyz)
    homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
    nodes_rotated = get_nodes_translated_position(nodes, homogenous_transformation)

    # RUN SAP
    structural = Structural(var_vector, cfg)
    bridge = Bridge(structural)
    #bridge._SapObject.Hide()
    #bridge._SapObject.Unhide()

    bridge.save_model_in_working_directory()
    TextFilesBridge.JointsCreate(nodes_rotated, structural.SAP_2000_working_directory)
    TextFilesBridge.FramesCreate(bars, structural.SAP_2000_working_directory)
    bridge._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

    bridge._restraints_definition(fixtures)

    bridge.load_scenario_dead()
    bridge.load_scenario_facet_weight(mirror_tripods)
    bridge.load_scenario_wind(mirror_tripods, nodes_rotated)

    bridge.load_combination_3LP_definition(structural)

    """
    run analysis and take Results
    """
    bridge._SapModel.Analyze.SetRunCaseFlag("DEAD", False, False)
    bridge._SapModel.Analyze.SetRunCaseFlag("MODAL", False, False)

    bridge.run_analysis()

    nodes_deformed_rotated= bridge.get_total_absolute_deformations_for_load_combination(nodes= nodes_rotated, load_combination_name= "dead+live+wind", group_name= "ALL")
    nodes_deformed = get_nodes_zenith_position(nodes_deformed_rotated, homogenous_transformation)

    value_to_minimize = abs(nodes_deformed[921][2] - nodes[921][2])

    return value_to_minimize

def PSO():
    lb = [0.08, 0]
    ub = [0.4, 45]
    xopt, fopt = pyswarm.pso(run, lb, ub, swarmsize = 5, maxiter = 10, debug = True)
    return xopt, fopt
