import numpy as np

class Geometry(object):
    def __init__(self, config_dict):
        self.focal_length = config_dict['optics']['focal_length']
        self.max_outer_radius = config_dict['optics']['max_outer_radius']
        self.min_inner_radius = config_dict['optics']['min_inner_radius']
        self.gap_between_facets = config_dict['optics']['gap_between_facets']
        self.facet_inner_hex_radius = config_dict['optics']['facet_inner_hex_radius']
        self.davies_cotton_over_parabola_ratio = config_dict['optics']['davies_cotton_over_parabola_ratio']

        self.number_of_layers = config_dict['space_frame']['number_of_layers']
        self.x_over_z_ratio = config_dict['space_frame']['x_over_z_ratio']
        self._set_up_geometry()

    def _set_up_geometry(self):
        self.approximate_mirror_surface_area = np.pi*self.max_outer_radius**2.0
        self.facet_spacing = self.facet_inner_hex_radius*2.0 + self.gap_between_facets
        self.facet_outer_hex_radius = self.facet_inner_hex_radius*2.0/np.sqrt(3.0)

        self.facet_spacing_x = self.facet_spacing
        self.facet_spacing_y = self.facet_spacing*(np.sqrt(3.0))

        self.nodes_in_x = 1+int(np.ceil(self.max_outer_radius/self.facet_spacing_x))
        self.nodes_in_y = 1+int(np.ceil(self.max_outer_radius/self.facet_spacing_y))

    def __repr__(self):
        info = 'Geometry'
        info+= '(focal length: '+str(self.focal_length)+'m)'
        return info