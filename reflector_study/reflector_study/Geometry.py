import numpy as np

class Geometry(object):
    def __init__(self, config_dict):
        self.focal_length = config_dict['optics']['focal_length']
        self.max_outer_radius = config_dict['optics']['max_outer_radius']

        self._set_up_geometry()

    def _set_up_geometry(self):
        self.approximate_mirror_surface_area = np.pi*self.max_outer_radius**2.0

    def __repr__(self):
        info = 'Geometry'
        info+= '(focal length: '+str(self.focal_length)+'m)'
        return info