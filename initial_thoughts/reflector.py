import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def is_inside_anulus(xy ,outer_radius, inner_radius):
    distance_to_center = np.hypot(xy[:,0], xy[:,1])
    inside_outer_radius = distance_to_center <= outer_radius
    outside_inner_radius = distance_to_center >= inner_radius
    return np.logical_and(inside_outer_radius, outside_inner_radius)


def xy_hex_anulus(outer_radius, inner_radius, spacing):
    x = np.array([1.0, 0.0])
    y = np.array([0.0, 1.0])

    unit_hex_a = spacing*y
    unit_hex_b = spacing*(y*0.5+x*np.sqrt(3.0)/2.0)

    sample_radius = 2.0*np.floor(outer_radius/spacing);

    hexAs = np.arange(-sample_radius, sample_radius)
    hexBs = np.arange(-sample_radius, sample_radius)

    xy = []
    for a in hexAs:
        for b in hexBs:
            xy.append(unit_hex_a*a + unit_hex_b*b)
    xy = np.array(xy)

    in_anulus = is_inside_anulus(xy, outer_radius, inner_radius)

    return xy[in_anulus]


class Reflector(object):

    def __init__(self):

        # GEOMETRY
        self.focal_length = 75
        self.DaviesCotton_over_parabolic_mixing_factor = 0.0
        self.max_outer_aperture_radius = 25
        self.min_inner_aperture_radius = 5
        self.facet_inner_hex_radius = 1.2
        self.gap_between_facets = 0.02  

        # OPTICAL PROPERTIES
        self.reflectivity = 'aluminum_mirror_reflectivity'

        # SPACE TRASE
        self.number_of_spaceframe_layers = 5
        self.spaceframe_layer_spacing = 0.8
        self.distance_1st_layer_to_mirror_surface = 0.25

        # VISUAL APPERAENCE IN MCTRACER
        self.mirror_color = np.array([200,200,200])
        self.inner_mirror_color = np.array([40,40,40])

        self._post_init()
        self._init_mirror_facet_target_positions()
        self._make_mean_facet_distance_to_focal_point_match_focal_length()

        self._init_mirror_node_template()
        self._init_1st_layer_nodes()

    def _post_init(self):
        self.focal_point = np.array([0.0, 0.0, self.focal_length])
        self.facet_spacing = self.facet_inner_hex_radius*2.0 + self.gap_between_facets
        

    def _init_mirror_node_template(self):
        self._mirror2node_offset = np.array([0.5*self.facet_spacing, 0.0, 0.0])

    def _z_Davies_Cotton(self, radius):
        return self.focal_length - np.sqrt(self.focal_length**2 - radius**2) 

    def _z_Parabola(self, radius):
        return 1.0/(4.0*self.focal_length)*radius**2; 

    def _mirror_facet_target_position_z_for_radius(self, radius):
        zDC = self._z_Davies_Cotton(radius)
        zPa = self._z_Parabola(radius)
        DC_over_Pa = self.DaviesCotton_over_parabolic_mixing_factor
        return DC_over_Pa*zDC + (1.0 - DC_over_Pa)*zPa       

    def _init_mirror_facet_target_positions(self):
        xy = xy_hex_anulus(
            outer_radius=self.max_outer_aperture_radius,
            inner_radius=self.min_inner_aperture_radius,
            spacing=self.facet_spacing)

        radii = np.hypot(xy[:,0], xy[:,1])
        z = self._mirror_facet_target_position_z_for_radius(radii)

        self.mirror_facet_target_positions = np.vstack((xy[:,0],xy[:,1],z)).T

    def _make_mean_facet_distance_to_focal_point_match_focal_length(self):
        self._z_offset_makeing_mean_facet_dist_to_f_point_match_f = 0.0
        iteration_conter = 0
        deviation = 0.0

        while(True):
            iteration_conter +=1
            if iteration_conter > 1000:
                raise ToManyIterations

            deviation = self.focal_length - self._mean_distances_of_facets_from_focal_point()

            step = -deviation*0.5
            self._move_all_mirror_facets_in_z(step)

            self._z_offset_makeing_mean_facet_dist_to_f_point_match_f += step

            if np.abs(deviation) < self.focal_length*1e-9:
                break

    def _move_all_mirror_facets_in_z(self, z_movement):
        self.mirror_facet_target_positions[:,2]+=z_movement

    def _mean_distances_of_facets_from_focal_point(self):
        distances = np.linalg.norm(
            self.focal_point - self.mirror_facet_target_positions,
            axis=1)
        return np.mean(distances)

    def plot_mirror_facet_target_positions(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(
            self.mirror_facet_target_positions[:,0],
            self.mirror_facet_target_positions[:,1],
            self.mirror_facet_target_positions[:,2],
            'o')
        plt.show()

    def _init_1st_layer_nodes(self):
        xy_1st_node_layer = self._mirror2node_offset[0:1] + xy_hex_anulus(
            outer_radius=self.max_outer_aperture_radius + self.facet_spacing,
            inner_radius=self.min_inner_aperture_radius - self.facet_spacing,
            spacing=self.facet_spacing)

        radii = np.hypot(xy_1st_node_layer[:,0], xy_1st_node_layer[:,1])
        z = self._mirror_facet_target_position_z_for_radius(radii) + self._z_offset_makeing_mean_facet_dist_to_f_point_match_f - self.distance_1st_layer_to_mirror_surface

        self.node_1st_layer = np.vstack((xy_1st_node_layer[:,0],xy_1st_node_layer[:,1],z)).T

        self.mirrors = []
        for mirror_pos in self.mirror_facet_target_positions:
            xy_mirror_pos = mirror_pos[0:1]

            mirror_nodes = []
            for i, xy_node in enumerate(xy_1st_node_layer):
                if np.linalg.norm(xy_mirror_pos - xy_node) < 1.1*0.5*self.facet_spacing:
                    mirror_nodes.append(i)

            self.mirrors.append(mirror_nodes)

    def plot_1st_layer_nodes(self):
        xyz = []
        for mirror in self.mirrors:
            for node_idx in mirror:
                xyz.append(self.node_1st_layer[node_idx])
        xyz = np.array(xyz)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(
            xyz[:,0],
            xyz[:,1],
            xyz[:,2],
            'o')
        plt.show()