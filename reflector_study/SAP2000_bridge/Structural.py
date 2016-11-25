import numpy as np
from ..Geometry import Geometry
from .. import config

geometry =  Geometry(config.example)

class Structural(object):

    def __init__(self, config_loading_dict):
        self.SAP_2000_directory = config_loading_dict["SAP_2000_directory"]
        self.yielding_point = config_loading_dict['material']['yielding_point']
        self.ultimate_point = config_loading_dict['material']['ultimate_point']
        self.bar_outter_radius = config_loading_dict['bar_properties']['outter_radius']
        self.bar_thickness = config_loading_dict["bar_properties"]["thickness"]
        self.facet_surface_weight = config_loading_dict["mirror_facet_weight"]["surface_weight"]
        self.facet_actuator_weight = config_loading_dict["mirror_facet_weight"]["actuator_weight"]
        self.angle_from_zenith = config_loading_dict["angle_from_zenith"]
        self._set_up_loading()

    def _set_up_loading(self):
        self.total_facet_surface_weight = self.facet_surface_weight / 100 #in kN/m**2
        self.total_facet_weight = self.total_facet_surface_weight * geometry.facet_surface_area #in kN
        self.tripod_nodes_weight = self.total_facet_weight / 3 + self.facet_actuator_weight / 100 #in kN

    def __repr__(self):
        info = 'Structural and loading assumptions'
        info+= '(steel: S'+str(self.yielding_point/1000)+', facet_surface_weight: '+str(self.facet_surface_weight)+"kN/m2)"
        return info
