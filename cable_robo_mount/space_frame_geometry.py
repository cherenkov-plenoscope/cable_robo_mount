import numpy as np
from .optical_geometry import z_hybrid


def flat_space_frame_addresses_to_cartesian(
    i, j, k, scale=1.0, x_over_z_ratio=1.0
):
    x = np.sqrt(3) * (j + 0.5 * k) - 2.0 / np.sqrt(3.0)
    y = i + 0.5 * k
    z = k * x_over_z_ratio
    return scale * np.array([x, y, z])


def dish_space_frame_addresses_to_cartesian(
    i,
    j,
    k,
    focal_length,
    davies_cotton_over_parabola_ratio=0.0,
    scale=1.0,
    x_over_z_ratio=1.0,
):
    xyz = flat_space_frame_addresses_to_cartesian(
        i, j, k, scale=scale, x_over_z_ratio=x_over_z_ratio
    )

    radius = np.hypot(xyz[0], xyz[1])
    xyz[2] = xyz[2] + z_hybrid(
        radius, focal_length, davies_cotton_over_parabola_ratio
    )
    return xyz
