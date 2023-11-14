import reflector_study as rs
import numpy as np


def test_mirror_tripod_reference_frame():
    nodes = np.array(
        [
            [-23.18, -7.74804061, 1.99114844],
            [-24.4, -5.63493863, 2.09037511],
            [-25.62, -1.40873466, 2.19456311],
        ]
    )
    tripod = np.array([0, 1, 2])

    expected_center = (nodes[0] + nodes[1] + nodes[2]) / 3
    center = rs.tools.mirror_tripod_center(nodes, tripod)
    assert np.linalg.norm(center - expected_center) < 1e-6

    x = rs.tools.mirror_tripod_x(nodes, tripod)
    y = rs.tools.mirror_tripod_y(nodes, tripod)
    z = rs.tools.mirror_tripod_z(nodes, tripod)

    assert np.abs(np.dot(x, y)) < 1e-9
    assert np.abs(np.dot(y, z)) < 1e-9
    assert np.abs(np.dot(z, x)) < 1e-9

    assert np.abs(np.linalg.norm(x) - 1) < 1e-9
    assert np.abs(np.linalg.norm(y) - 1) < 1e-9
    assert np.abs(np.linalg.norm(z) - 1) < 1e-9
