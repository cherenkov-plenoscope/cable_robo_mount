import numpy as np
from .. import tools


def mean_distance_between(focal_point, facet_centers):
    sum_of_distances = 0.0
    for facet_center in facet_centers:
        sum_of_distances += np.linalg.norm(focal_point - facet_center)
    number_of_facets = facet_centers.shape[0]
    return sum_of_distances/number_of_facets


def PAP_offset_in_z(
    focal_length, 
    tripod_centers, 
    max_iterations=10000, 
    precision=1e-4):
    """
    Position offset in z direction of the factory's frame to the actual 
    Principal Aperture Plane (PAP) of the reflector.
    """

    focal_piont = np.array([0.0, 0.0, focal_length])
    iteration = 0
    while True:
        iteration += 1
        mean_dist = mean_distance_between(focal_piont, tripod_centers)
        delta_z = mean_dist - focal_length
        if delta_z < precision or iteration > max_iterations:
            break
        focal_piont[2] = focal_piont[2] - 0.5*delta_z
    return focal_piont[2] - focal_length


def optimal_mirror_alignment(reflector):
    tripod_centers = tools.mirror_tripod_centers(reflector['nodes'], reflector['mirror_tripods'])
    pa_plane_offset = estimate_principal_aperture_plane_offset_in_z(
        reflector, 
        tripod_centers)
    focal_piont = np.array([0.0, 0.0, reflector['geometry'].focal_length])
