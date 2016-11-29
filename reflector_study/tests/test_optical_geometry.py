import reflector_study as rs
import tempfile
import os
import numpy as np

def test_hybrid_shape():
    focal_length = 150.0
    radius = 50.0
    assert rs.optical_geometry.z_parabola(radius, focal_length) == rs.optical_geometry.z_hybrid(radius, focal_length, dc_over_pa=0.0)
    assert rs.optical_geometry.z_davies_cotton(radius, focal_length) == rs.optical_geometry.z_hybrid(radius, focal_length, dc_over_pa=1.0)

def test_davies_cotton_shape():
    focal_length = 150.0
    max_radius = 50.0
    focal_point = np.array([0.0, focal_length])

    radii = np.linspace(0.0, max_radius, 100)
    for radius in radii:
        z = rs.optical_geometry.z_davies_cotton(radius, focal_length)
        mirror_facet_pos = np.array([radius, z])
        assert np.linalg.norm(mirror_facet_pos - focal_point) - focal_length < 1e-6