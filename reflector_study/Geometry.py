import numpy as np


class Geometry(object):
    def __init__(self, var_vector, config_dict):
        self.focal_length = config_dict['reflector']['optics']['focal_length']
        self.max_outer_radius = config_dict['reflector']['main']['max_outer_radius']
        self.min_inner_radius = config_dict['reflector']['main']['min_inner_radius']
        self.gap_between_facets = config_dict['reflector']['facet']['gap_in_between']
        self.facet_inner_hex_radius = config_dict['reflector']['facet']['inner_hex_radius']
        self.davies_cotton_over_parabola_ratio = config_dict['reflector']['optics']['davies_cotton_over_parabola_ratio']
        self.reflector_security_distance_from_ground = config_dict["reflector"]["main"]["security_distance_from_ground"]

        self.number_of_layers = config_dict['reflector']['main']['number_of_layers']
        self.x_over_z_ratio = config_dict['reflector']['main']['x_over_z_ratio']
        self.bar_outer_diameter = var_vector[0]

        self.tension_ring_width = config_dict['tension_ring']['width']
        self.tension_ring_support_position = config_dict['tension_ring']['support_position']

        self.tait_bryan_angle_Rx = np.deg2rad(config_dict["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][0])
        self.tait_bryan_angle_Ry = np.deg2rad(config_dict["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][1])
        self.tait_bryan_angle_Rz = np.deg2rad(config_dict["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][2])

        self._set_up_translational_vector_from_dish_orientation_2D()
        self._set_up_geometry()


    def _set_up_geometry(self):
        self.approximate_mirror_surface_area = np.pi*self.max_outer_radius**2.0
        self.facet_perimeter = 4*np.sqrt(3)*self.facet_inner_hex_radius
        self.facet_surface_area = 0.5*self.facet_inner_hex_radius*self.facet_perimeter
        self.facet_spacing = self.facet_inner_hex_radius*2.0 + self.gap_between_facets
        self.facet_outer_hex_radius = self.facet_inner_hex_radius*2.0/np.sqrt(3.0)

        self.facet_spacing_x = self.facet_spacing
        self.facet_spacing_y = self.facet_spacing*(np.sqrt(3.0))

        self.lattice_spacing_i = self.facet_spacing_x/2.0
        self.lattice_spacing_j = self.facet_spacing_y/2.0

        self.lattice_radius_i = 1+int(np.ceil(self.max_outer_radius/self.lattice_spacing_i))
        self.lattice_radius_j = 1+int(np.ceil(self.max_outer_radius/self.lattice_spacing_j))

        self.lattice_range_i = 2*self.lattice_radius_i+1
        self.lattice_range_j = 2*self.lattice_radius_j+1
        self.lattice_range_k = self.number_of_layers

    def _set_up_translational_vector_from_dish_orientation_2D(self):
        #create BC arrays for the creation of the line
        x = np.array([-self.max_outer_radius/25*23.6, 0, self.max_outer_radius/25*23.6])
        y = np.array([self.max_outer_radius/25*18.5, 0, self.max_outer_radius/25*18.5])
        #find the actual line equation(2nd order polynomial/parabolic trajectory)
        z = np.polyfit(x, y, 2)
        p = np.poly1d(z)
        self.translational_vector_xyz = [np.rad2deg(self.tait_bryan_angle_Ry)/45*x[2], 0, p(x[2])]

    def __repr__(self):
        info = 'Geometry'
        info+= '(focal length: '+str(self.focal_length)+'m)'
        return info
