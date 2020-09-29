import numpy as np

def z_parabola(distance_to_z_axis, focal_length):
    """
    Returns the z coordinate on a monolithic, parabolic reflector dish.

    Parameter
    ---------
    distance_to_z_axis  The distance from the optical axis.

    focal_length        The focal length of the imaging system.
    """
    return 1.0/(4.0*focal_length)*distance_to_z_axis**2;

def z_davies_cotton(distance_to_z_axis, focal_length):
    return focal_length - np.sqrt(focal_length**2 - distance_to_z_axis**2)

def z_hybrid(distance_to_z_axis, focal_length, dc_over_pa=0.0):
    z_dc = z_davies_cotton(distance_to_z_axis, focal_length)
    z_pa = z_parabola(distance_to_z_axis, focal_length)
    return dc_over_pa*z_dc + (1 - dc_over_pa)*z_pa


def z_sphere(distance_to_z_axis, curvature_radius):
    assert curvature_radius >= distance_to_z_axis
    return curvature_radius - np.sqrt(
        curvature_radius ** 2 -
        distance_to_z_axis ** 2
    )
