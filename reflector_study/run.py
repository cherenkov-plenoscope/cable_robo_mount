import os
from . import config
from .Geometry import Geometry
from .factory import generate_reflector_with_tension_ring
from .HomTra import HomTra

def run(cfg, output_path):

    os.mkdir(output_path)
    cfg_path = os.path.join(output_path, 'config.json')
    config.write(cfg, cfg_path)

    # SET UP REFLECTOR GEOMETRY
    geometry = Geometry(cfg)
    reflector = generate_reflector_with_tension_ring(geometry)
    nodes = reflector["nodes"]
    bars = reflector["bars"]
    cables = reflector["cables"]
    cable_supports = reflector["cable_supports"]
    mirror_tripods = reflector["mirror_tripods"]
    fixtures = reflector["elastic_supports"]

    # DISH ROTATION
    homogenous_transformation = HomTra()
    homogenous_transformation.set_translation(geometry.translational_vector_xyz)
    homogenous_transformation.set_rotation_tait_bryan_angles(geometry.tait_bryan_angle_Rx, geometry.tait_bryan_angle_Ry, geometry.tait_bryan_angle_Rz)
    nodes_rotated = rs.SAP2000_bridge.HomTra_bridge_tools.get_nodes_translated_position(nodes, homogenous_transformation)

    # RUN SAP
    structural = rs.SAP2000_bridge.Structural(rs.config.example)
    bridge = rs.SAP2000_bridge.Bridge(structural)
    #bridge._SapObject.Hide()
    bridge._SapObject.Unhide()

    bridge.save_model_in_working_directory()
    rs.SAP2000_bridge.TextFilesBridge.JointsCreate(nodes_rotated, structural.SAP_2000_working_directory)
    rs.SAP2000_bridge.TextFilesBridge.FramesCreate(bars, structural.SAP_2000_working_directory)
    bridge._SapModel.File.OpenFile(structural.SAP_2000_working_directory+".$2k")

    #bridge.elastic_support_definition(fixtures)
    ################for cables uncomment the following
    bridge._frames_definition(cables)
    bridge._set_tension_compression_limits_for_specific_frame_elements(cables)
    bridge._restraints_definition(cable_supports)
    ################

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

    #forces= bridge.get_forces_for_group_of_bars_for_selected_load_combination(load_combination_name= "dead+live+wind")
    #buckling = rs.SAP2000_bridge.BucklingControl.Knicknachweis(rs.config.example, forces)
    #log = buckling.log

    nodes_deformed_rotated= bridge.get_total_absolute_deformations_for_load_combination(nodes= nodes_rotated, load_combination_name= "dead+live+wind", group_name= "ALL")


    optical_quality = 1.0
    return {'optical_quality': optical_quality}
