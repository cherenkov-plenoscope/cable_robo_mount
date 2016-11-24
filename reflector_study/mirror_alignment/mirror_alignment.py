import numpy as np
from .. import tools
from ..HomTra import HomTra

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


def ideal_mirror_facet_HomTra_in_Rframe(focal_piont, facet_center):
    unit_z = np.array([0.0, 0.0, 1.0])

    connection = focal_piont - facet_center
    connection /= np.linalg.norm(connection)

    rot_axis = np.cross(unit_z, connection)
    angle_to_unit_z = np.arccos(np.dot(unit_z, connection))

    ideal_angle = angle_to_unit_z/2.0

    t = HomTra()
    t.set_translation(facet_center)
    t.set_rotation_axis_and_angle(rot_axis, ideal_angle)
    return t


def ideal_mirror_facet_HomTras_in_Rframe(reflector):
    nodes = reflector['nodes']
    tripods = reflector['mirror_tripods']
    focal_length = reflector['geometry'].focal_length

    tripod_centers = tools.mirror_tripod_centers(nodes, tripods)
    facet_centers = tripod_centers.copy()
    facet_centers[:,2] += reflector['geometry'].facet_inner_hex_radius/10.0

    PAP_offset = PAP_offset_in_z(focal_length, facet_centers)

    # Rframe is the reflector frame
    focal_piont_Rframe = np.array([0.0, 0.0, focal_length + PAP_offset])

    mirror_facet_HomTras_Rframe = []
    for facet_center in facet_centers:
        mirror_facet_HomTras_Rframe.append(ideal_mirror_facet_HomTra_in_Rframe(
            focal_piont_Rframe,
            facet_center))

    return mirror_facet_HomTras_Rframe


def mmirror_tripod_HomTras_in_Rframe(reflector):
    nodes = reflector['nodes']
    tripods = reflector['mirror_tripods']
    mirror_tripod_HomTras_Rframe = []
    for tripod in tripods:
        center = tools.mirror_tripod_center(nodes, tripod)
        Rx = tools.mirror_tripod_x(nodes, tripod)
        Ry = tools.mirror_tripod_y(nodes, tripod)
        Rz = tools.mirror_tripod_z(nodes, tripod)
        t = HomTra()
        t.T[:,0] = Rx
        t.T[:,1] = Ry
        t.T[:,2] = Rz
        t.T[:,3] = center
        mirror_tripod_HomTras_Rframe.append(t)
    return mirror_tripod_HomTras_Rframe


def ideal_alignments_tripod2facet(reflector):
    facet_HomTras = ideal_mirror_facet_HomTras_in_Rframe(reflector)
    tripod_HomTras = mmirror_tripod_HomTras_in_Rframe(reflector)

    tripod2facet = []
    for i in range(len(facet_HomTras)):
        T_reflector2facet = facet_HomTras[i]
        T_reflector2tripod = tripod_HomTras[i]
        T_tripod2facet = T_reflector2tripod.inverse().multiply(T_reflector2facet)
        tripod2facet.append(T_tripod2facet)
    return tripod2facet


def reflector2facets(reflector, alignment_tripod2facet):
    tripod_HomTras = mmirror_tripod_HomTras_in_Rframe(reflector)

    reflector2facet = []
    for i in range(len(tripod_HomTras)):
        T_tripod2facet = alignment_tripod2facet[i]
        T_reflector2tripod = tripod_HomTras[i]
        T_reflector2facet = T_reflector2tripod.multiply(T_tripod2facet)
        reflector2facet.append(T_reflector2facet)
    return reflector2facet