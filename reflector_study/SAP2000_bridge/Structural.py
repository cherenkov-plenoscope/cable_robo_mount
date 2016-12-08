import numpy as np

class Structural(object):

    def __init__(self, config_dict):
        self.SAP_2000_directory = config_dict['system']['sap2000']['path']
        self.yielding_point = config_dict['reflector']['material']['yielding_point']
        self.ultimate_point = config_dict['reflector']['material']['ultimate_point']
        self.bar_outter_radius = config_dict['reflector']['bars']['outer_diameter']
        self.bar_thickness = config_dict['reflector']['bars']['thickness']
        self.facet_surface_weight = config_dict['reflector']['facet']['surface_weight']
        self.facet_actuator_weight = config_dict['reflector']['facet']['actuator_weight']
        self.facet_inner_hex_radius = config_dict['reflector']['facet']['inner_hex_radius']
        self._set_up_loading()
        self._set_up_loading_scenarios(config_dict)

    def _set_up_loading(self):
        self.facet_perimeter = 4*np.sqrt(3)*self.facet_inner_hex_radius
        self.facet_surface_area = 0.5*self.facet_inner_hex_radius*self.facet_perimeter
        self.total_facet_surface_weight = self.facet_surface_weight / 100 #in kN/m**2
        self.total_facet_weight = self.total_facet_surface_weight * self.facet_surface_area #in kN
        self.tripod_nodes_weight = self.total_facet_weight / 3 + self.facet_actuator_weight / 100 #in kN

    def _set_up_loading_scenarios(self, config_dict):
        self.wind_direction= config_dict["load_scenario"]["wind"]["direction"]
        self.wind_speed = config_dict["load_scenario"]["wind"]["speed"]
        self.wind_terrain_factor = config_dict["load_scenario"]["wind"]["terrain_factor"]
        self.wind_orography_factor = config_dict["load_scenario"]["wind"]["orography_factor"]
        self.wind_K1_factor = config_dict["load_scenario"]["wind"]["K1"]
        self.wind_CsCd_factor = config_dict["load_scenario"]["wind"]["CsCd"]
        self.wind_density = config_dict["load_scenario"]["wind"]["wind_density"]
        self.wind_security_distance_from_ground = config_dict["load_scenario"]["wind"]["security_distance_from_ground"]

    def __repr__(self):
        info = 'Structural and loading assumptions'
        info+= '(steel: S'+str(self.yielding_point/1000)+', facet_surface_weight: '+str(self.facet_surface_weight)+"kg/m2)"
        return info
