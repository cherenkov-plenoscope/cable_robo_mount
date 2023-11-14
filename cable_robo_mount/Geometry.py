import numpy as np
from .HomTra import HomTra


class Geometry(object):
    def __init__(self, cfg):
        self.focal_length = cfg["reflector"]["optics"]["focal_length"]
        self.max_outer_radius = cfg["reflector"]["main"]["max_outer_radius"]
        self.min_inner_radius = cfg["reflector"]["main"]["min_inner_radius"]
        self.gap_between_facets = cfg["reflector"]["facet"]["gap_in_between"]
        self.facet_inner_hex_radius = cfg["reflector"]["facet"][
            "inner_hex_radius"
        ]
        self.davies_cotton_over_parabola_ratio = cfg["reflector"]["optics"][
            "davies_cotton_over_parabola_ratio"
        ]
        self.reflector_security_distance_from_ground = cfg["reflector"][
            "main"
        ]["security_distance_from_ground"]

        self.number_of_layers = cfg["reflector"]["main"]["number_of_layers"]
        self.x_over_z_ratio = cfg["reflector"]["main"]["x_over_z_ratio"]
        self.bar_outer_diameter = cfg["reflector"]["bars"]["outer_diameter"]

        self.tension_ring_width = cfg["tension_ring"]["width"]
        self.tension_ring_support_position = cfg["tension_ring"][
            "support_position"
        ]

        self.tait_bryan_angle_Rx = np.deg2rad(
            cfg["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][0]
        )
        self.tait_bryan_angle_Ry = np.deg2rad(
            cfg["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][1]
        )
        self.tait_bryan_angle_Rz = np.deg2rad(
            cfg["structure_spatial_position"]["rotational_vector_Rx_Ry_Rz"][2]
        )

        self._set_up_translational_vector_from_dish_orientation_2D()
        self._set_up_geometry()
        self._set_up_transformations(cfg)

    def _set_up_geometry(self):
        self.approximate_mirror_surface_area = (
            np.pi * self.max_outer_radius**2.0
        )
        self.facet_perimeter = 4 * np.sqrt(3) * self.facet_inner_hex_radius
        self.facet_surface_area = (
            0.5 * self.facet_inner_hex_radius * self.facet_perimeter
        )
        self.facet_spacing = (
            self.facet_inner_hex_radius * 2.0 + self.gap_between_facets
        )
        self.facet_outer_hex_radius = (
            self.facet_inner_hex_radius * 2.0 / np.sqrt(3.0)
        )

        self.facet_spacing_x = self.facet_spacing
        self.facet_spacing_y = self.facet_spacing * (np.sqrt(3.0))

        self.lattice_spacing_i = self.facet_spacing_x / 2.0
        self.lattice_spacing_j = self.facet_spacing_y / 2.0

        self.lattice_radius_i = 1 + int(
            np.ceil(self.max_outer_radius / self.lattice_spacing_i)
        )
        self.lattice_radius_j = 1 + int(
            np.ceil(self.max_outer_radius / self.lattice_spacing_j)
        )

        self.lattice_range_i = 2 * self.lattice_radius_i + 1
        self.lattice_range_j = 2 * self.lattice_radius_j + 1
        self.lattice_range_k = self.number_of_layers

    def _set_up_translational_vector_from_dish_orientation_2D(self):
        # create BC arrays for the creation of the line
        x_range = self.max_outer_radius / 25 * 23.6
        y_range = self.max_outer_radius / 25 * 18.5
        x = np.array([-x_range, 0, x_range])
        y = np.array([y_range, 0, y_range])
        # find the actual line equation(2nd order polynomial/parabolic trajectory)
        z = np.polyfit(x, y, 2)
        p = np.poly1d(z)
        max_rotation_angle = 45
        x_for_current_rotation = (
            np.rad2deg(self.tait_bryan_angle_Ry) / max_rotation_angle * x_range
        )
        self.translational_vector_xyz = [
            x_for_current_rotation,
            0,
            p(x_for_current_rotation),
        ]

    def _set_up_transformations(self, cfg):
        # Frame hirachy
        # -------------
        # root frame
        # |-> mount
        #     |-> dish
        #         |-> camera

        # root -> mount
        # -------------
        self.root2mount = HomTra()

        # mount -> dish
        # -------------
        self.mount2dish = HomTra()
        self.mount2dish.set_rotation_axis_and_angle(
            axis=dish_rotation_axis(np.deg2rad(cfg["pointing"]["azimuth"])),
            phi=np.deg2rad(cfg["pointing"]["zenith_distance"]),
        )
        self.mount2dish.set_translation(
            dish_translation_from_pointing(
                azimuth=np.deg2rad(cfg["pointing"]["azimuth"]),
                zenith_distance=np.deg2rad(cfg["pointing"]["zenith_distance"]),
                dish_radius=cfg["reflector"]["main"]["max_outer_radius"],
            )
            + np.array(
                [
                    0,
                    0,
                    cfg["reflector"]["main"]["security_distance_from_ground"],
                ]
            )
        )

        # dish -> camera
        # --------------
        self.dish2camera = HomTra()
        self.dish2camera.set_translation(
            np.array(
                [
                    0,
                    0,
                    cfg["camera"][
                        "sensor_distance_to_principal_aperture_plane"
                    ],
                ]
            )
            + np.array(cfg["camera"]["offset_position"])
        )
        self.dish2camera.set_rotation_tait_bryan_angles(
            Rx=cfg["camera"]["offset_rotation_tait_bryan"][0],
            Ry=cfg["camera"]["offset_rotation_tait_bryan"][1],
            Rz=cfg["camera"]["offset_rotation_tait_bryan"][2],
        )

        # root -> dish
        # ------------
        self.root2dish = self.root2mount.multiply(self.mount2dish)

        # root -> camera
        # ------------
        self.root2camera = self.root2dish.multiply(self.dish2camera)

    def __repr__(self):
        info = "Geometry"
        info += "(focal length: " + str(self.focal_length) + "m)"
        return info


def dish_rotation_axis(azimuth):
    az = azimuth
    return np.array([np.cos(az + np.pi / 2), np.sin(az + np.pi / 2), 0.0])


def dish_translation_axis(azimuth):
    az = azimuth
    return np.array([np.cos(az), np.sin(az), 0.0])


def dish_translation_from_pointing(azimuth, zenith_distance, dish_radius):
    RADIAL_RANGE = dish_radius / 25 * 23.6
    HIGHT_RANGE = dish_radius / 25 * 18.5
    MAX_ZENITH_DISTANCE = np.deg2rad(45)
    translation_axis_xy = dish_translation_axis(azimuth)
    radial_translation = zenith_distance / MAX_ZENITH_DISTANCE * RADIAL_RANGE
    return -radial_translation * translation_axis_xy + np.array(
        [
            0,
            0,
            HIGHT_RANGE
            * dish_hight_trajectory(radial_translation / RADIAL_RANGE),
        ]
    )


def dish_hight_trajectory(radial_displacement):
    return np.abs(np.sin(radial_displacement * np.pi / 2))
