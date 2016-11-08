import pytest
import reflector_study as rs
import tempfile
import os

def test_hybrid_shape():
    focal_length = 150.0
    radius = 50.0
    assert rs.optical_geometry.z_parabola(radius, focal_length) == rs.optical_geometry.z_hybrid(radius, focal_length, dc_over_pa=0.0)
    assert rs.optical_geometry.z_davies_cotton(radius, focal_length) == rs.optical_geometry.z_hybrid(radius, focal_length, dc_over_pa=1.0)