import numpy as np

class Geometry(object):
    def __init__(self, config_dict):
        self.focal_length = config_dict['optics']['focal_length']
        self.max_outer_radius = config_dict['optics']['max_outer_radius']
        self.min_inner_radius = config_dict['optics']['min_inner_radius']
        self.gap_between_facets = config_dict['optics']['gap_between_facets']
        self.facet_inner_hex_radius = config_dict['optics']['facet_inner_hex_radius']
        self._set_up_geometry()

    def _set_up_geometry(self):
        self.approximate_mirror_surface_area = np.pi*self.max_outer_radius**2.0
        self.facet_spacing = self.facet_inner_hex_radius*2.0 + self.gap_between_facets

    def __repr__(self):
        info = 'Geometry'
        info+= '(focal length: '+str(self.focal_length)+'m)'
        return info