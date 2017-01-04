import os
from . import pyswarm
from . import config
from .Geometry import Geometry
from .factory import generate_reflector_with_tension_ring_and_cables
from .SAP2000_bridge.Structural import Structural
from .SAP2000_bridge.HomTra_bridge_tools import get_nodes_moved_position, get_nodes_zenith_position
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
    total_geometry = generate_reflector_with_tension_ring_and_cables(geometry)
    nodes = total_geometry["nodes"]
    bars_reflector = total_geometry["bars_reflector"]
    bars_tension_ring = total_geometry["bars_tension_ring"]
    cables = total_geometry["cables"]
    elastic_supports = total_geometry["elastic_supports"]
    cable_supports = total_geometry["cable_supports"]
    mirror_tripods = total_geometry["mirror_tripods"]
    fixtures = total_geometry["elastic_supports"]

    # DISH ROTATION
    homogenous_transformation = HomTra()
    homogenous_transformation.set_translation(geometry.translational_vector_xyz)
    homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
    nodes_rotated = get_nodes_moved_position(nodes, cable_supports, homogenous_transformation)

    # RUN SAP
    structural = Structural(var_vector, cfg)
    bridge = Bridge(structural)
    bridge._SapObject.Hide()
    #bridge._SapObject.Unhide()

    bridge.save_model_in_working_directory()
    TextFilesBridge.JointsCreate(nodes_rotated, structural.SAP_2000_working_directory)
    TextFilesBridge.FramesCreate(bars_reflector, bars_tension_ring, structural)
    bridge._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

    bridge._cables_definition(cables)
    bridge._restraints_definition(cable_supports)

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
    nodes_deformed = get_nodes_zenith_position(nodes_deformed_rotated, cable_supports, homogenous_transformation)

    value_to_minimize = abs(nodes_deformed[921][2] - nodes[921][2])

    return value_to_minimize

def PSO():
    lb = [0.0081, 0.0121, 0]
    ub = [0.1, 0.2, 5000]
    xopt, fopt, p, fp = pyswarm.pso(run, lb, ub, swarmsize = 5, maxiter = 20, debug = True, particle_output= True)
    return xopt, fopt, p, fp
