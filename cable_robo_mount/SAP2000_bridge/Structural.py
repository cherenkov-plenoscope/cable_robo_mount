import numpy as np

class Structural(object):

    def __init__(self, config_dict):
        self.SAP_2000_directory = config_dict['system']['sap2000']['path']
        self.SAP_2000_working_directory = config_dict['system']['sap2000']['working_directory']

        self.reflector_yielding_point = config_dict['reflector']['material']['yielding_point']
        self.reflector_ultimate_point = config_dict['reflector']['material']['ultimate_point']
        self.reflector_material_e_modul = config_dict['reflector']['material']['e_modul']
        self.reflector_material_specific_weight = config_dict['reflector']['material']['specific_weight']
        self.reflector_bar_outer_diameter = config_dict['reflector']['bars']['outer_diameter']
        self.reflector_bar_thickness = config_dict['reflector']['bars']['thickness']
        self.reflector_security_distance_from_ground = config_dict["reflector"]["main"]["security_distance_from_ground"]

        self.tension_ring_yielding_point = config_dict['tension_ring']['material']['yielding_point']
        self.tension_ring_ultimate_point = config_dict['tension_ring']['material']['ultimate_point']
        self.tension_ring_material_e_modul = config_dict['tension_ring']['material']['e_modul']
        self.tension_ring_material_specific_weight = config_dict['tension_ring']['material']['specific_weight']
        self.tension_ring_bar_outer_diameter = config_dict['tension_ring']['bars']['outer_diameter']
        self.tension_ring_bar_thickness = config_dict['tension_ring']['bars']['thickness']

        self.cables_yielding_point = config_dict['cables']['material']['yielding_point']
        self.cables_ultimate_point = config_dict['cables']['material']['ultimate_point']
        self.cables_cs_area = config_dict['cables']['cross_section_area']
        self.cables_e_modul = config_dict['cables']['material']['e_modul']
        self.cables_material_specific_weight = config_dict['cables']['material']['specific_weight']

        self.facet_surface_weight = config_dict['reflector']['facet']['surface_weight']
        self.facet_actuator_weight = config_dict['reflector']['facet']['actuator_weight']
        self.facet_inner_hex_radius = config_dict['reflector']['facet']['inner_hex_radius']

        self._set_up_help_values()
        self._set_up_loading_scenarios(config_dict)

    def _set_up_help_values(self):
        #mainly help values for wind loading/shell load assignment
        self.facet_perimeter = 4*np.sqrt(3)*self.facet_inner_hex_radius
        self.facet_surface_area = 0.5*self.facet_inner_hex_radius*self.facet_perimeter
        self.total_facet_surface_weight = self.facet_surface_weight / 100 #in kN/m**2
        self.total_facet_weight = self.total_facet_surface_weight * self.facet_surface_area #in kN
        self.tripod_nodes_weight = self.total_facet_weight / 3 + self.facet_actuator_weight / 100 #in kN
        #help values for weight calculation
        self.bars_reflector_cs_area = np.pi/4*(self.reflector_bar_outer_diameter**2-(self.reflector_bar_outer_diameter-2*self.reflector_bar_thickness)**2)
        self.bars_tension_ring_cs_area = np.pi/4*(self.tension_ring_bar_outer_diameter**2-(self.tension_ring_bar_outer_diameter-2*self.tension_ring_bar_thickness)**2)

    def _set_up_loading_scenarios(self, config_dict):
        self.wind_direction= config_dict["load_scenario"]["wind"]["direction"]
        self.wind_speed = config_dict["load_scenario"]["wind"]["speed"]
        self.wind_terrain_factor = config_dict["load_scenario"]["wind"]["terrain_factor"]
        self.wind_orography_factor = config_dict["load_scenario"]["wind"]["orography_factor"]
        self.wind_K1_factor = config_dict["load_scenario"]["wind"]["K1"]
        self.wind_CsCd_factor = config_dict["load_scenario"]["wind"]["CsCd"]
        self.wind_density = config_dict["load_scenario"]["wind"]["wind_density"]
        self.cpei = config_dict["load_scenario"]["wind"]["cpei"]

        self.dead_load_scenario_security_factor = config_dict["load_scenario"]["security_factor"]["dead"]
        self.live_load_scenario_security_factor = config_dict["load_scenario"]["security_factor"]["live"]
        self.wind_load_scenario_security_factor = config_dict["load_scenario"]["security_factor"]["wind"]

    def __repr__(self):
        info = 'Structural and loading assumptions'
        info+= '(steel: S'+str(self.reflector_yielding_point/1000)+', facet_surface_weight: '+str(self.facet_surface_weight)+"kg/m2)"
        return info
