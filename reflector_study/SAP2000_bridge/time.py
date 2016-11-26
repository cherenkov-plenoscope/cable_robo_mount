Dish 50m

import time
start = time.time()
import reflector_study as rs
geometry = rs.Geometry(rs.config.example)
reflector = rs.factory.generate_reflector(geometry)
structural = rs.SAP2000_bridge.Structural(rs.SAP2000_bridge.config_loading.example)
bridge = rs.SAP2000_bridge.Bridge(structural)
bridge.nodes_definition(reflector)
bridge.frames_definition(reflector)
bridge.restraints_definition(reflector)
bridge.load_scenario_dead()
bridge.load_scenario_facet_weight(reflector)
bridge.run_analysis()
reflector, reflector_deformed= bridge.get_deformed_reflector_for_all_nodes_for_selected_load_pattern(reflector, "facets_live_load")
end = time.time()
print(end - start)
22.7 sec

start = time.time()
bridge.initialize_new_workspace()
bridge.material_definition()
bridge.cross_section_definition()
bridge.nodes_definition(reflector)
bridge.frames_definition(reflector)
bridge.restraints_definition(reflector)
bridge.load_scenario_dead()
bridge.load_scenario_facet_weight(reflector)
bridge.run_analysis()
reflector, reflector_deformed= bridge.get_deformed_reflector_for_all_nodes_for_selected_load_pattern(reflector, "dead_load")
end = time.time()
print(end - start)
12.3 sec
