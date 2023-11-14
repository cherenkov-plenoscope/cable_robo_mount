import cable_robo_mount as rs
import numpy as np


def test_principal_aperture_plane_offset_z_for_Davies_Cotton():
    config = rs.config.example
    config["reflector"]["optics"]["davies_cotton_over_parabola_ratio"] = 1.0
    reflector = rs.factory.generate_reflector(rs.Geometry(config))
    focal_length = reflector["geometry"].focal_length
    nodes = reflector["nodes"]
    tripods = reflector["mirror_tripods"]
    tripod_centers = rs.tools.mirror_tripod_centers(nodes, tripods)
    offset = rs.mirror_alignment.mirror_alignment.PAP_offset_in_z(
        focal_length, tripod_centers
    )
    # Expext the offset to be zero
    assert np.abs(offset) < 1e-6


def test_principal_aperture_plane_offset_z_for_hybrid():
    config = rs.config.example
    config["reflector"]["optics"]["davies_cotton_over_parabola_ratio"] = 0.5
    reflector = rs.factory.generate_reflector(rs.Geometry(config))
    focal_length = reflector["geometry"].focal_length
    nodes = reflector["nodes"]
    tripods = reflector["mirror_tripods"]
    tripod_centers = rs.tools.mirror_tripod_centers(nodes, tripods)
    offset = rs.mirror_alignment.mirror_alignment.PAP_offset_in_z(
        focal_length, tripod_centers
    )
    # Expext the offset to be half the pure parabola offset
    assert offset < 0


def test_principal_aperture_plane_offset_z_for_pure_parabola():
    config = rs.config.example
    config["reflector"]["optics"]["davies_cotton_over_parabola_ratio"] = 0.0
    reflector = rs.factory.generate_reflector(rs.Geometry(config))
    focal_length = reflector["geometry"].focal_length
    nodes = reflector["nodes"]
    tripods = reflector["mirror_tripods"]
    tripod_centers = rs.tools.mirror_tripod_centers(nodes, tripods)
    offset = rs.mirror_alignment.mirror_alignment.PAP_offset_in_z(
        focal_length, tripod_centers
    )
    # Expext the offset to be maximal
    assert offset < 0
