import numpy as np
from .. import tools
from ..HomTra import HomTra


def mean_distance_between(focal_point, facet_centers):
    """
    Returns the average distance between the focal_point position and all
    the individual mirror facet center positions.

    Parameter
    ---------
    focal_point     3D position

    facet_centers   A list of 3D positions
    """
    sum_of_distances = 0.0
    for facet_center in facet_centers:
        sum_of_distances += np.linalg.norm(focal_point - facet_center)
    number_of_facets = facet_centers.shape[0]
    return sum_of_distances/number_of_facets


def PAP_offset_in_z(
    focal_length,
    facet_centers,
    max_iterations=10000,
    precision=1e-4):
    """
    Returns the position offset in z direction of the factory's frame to the
    Principal Aperture Plane (PAP) of the reflector.

    Parameter
    ---------
    focal_length    The focal length of the overall segmented imaging reflector

    facet_centers   A list of the 3D facet center positions

    precision       The precision needed on the PAP offset to quit the iteration

    max_iterations  An upper limit before quiting iteration without convergence

    Note
    ----
    This offset is expected to be 0.0 for the Davies-Cotton geometry and >0.0
    for the parabolic geometry.
    """
    focal_piont = np.array([0.0, 0.0, focal_length])
    iteration = 0
    while True:
        iteration += 1
        mean_dist = mean_distance_between(focal_piont, facet_centers)
        delta_z = mean_dist - focal_length
        if delta_z < precision:
            break

        if iteration > max_iterations:
            raise RuntimeError(
                'Unable to converge principal plane offset after '+
                str(max_iterations)+
                ' iterations.')

        focal_piont[2] = focal_piont[2] - 0.5*delta_z
    return focal_piont[2] - focal_length


def ideal_reflector2facet(focal_piont, facet_center):
    """
    Returns an ideal homogenoues transformation reflector2facet for a mirror
    facet located at facet_center.

    Parameter
    ---------
    focal_piont     The 3D focal point in the reflector frame

    facet_center    A 3D mirror facet center position in the reflector frame
    """
    unit_z = np.array([0.0, 0.0, 1.0])
    connection = focal_piont - facet_center
    connection /= np.linalg.norm(connection)
    rotation_axis = np.cross(unit_z, connection)
    angle_to_unit_z = np.arccos(np.dot(unit_z, connection))
    ideal_angle = angle_to_unit_z/2.0
    reflector2facet = HomTra()
    reflector2facet.set_translation(facet_center)
    reflector2facet.set_rotation_axis_and_angle(rotation_axis, ideal_angle)
    return reflector2facet


def ideal_reflector2facets(focal_length, facet_centers, PAP_offset):
    """
    Returns a list of ideal homogenoues transformation reflector2facet for all
    mirror facets on a reflector.

    Parameter
    ---------
    focal_length    The focal length of the overall segmented imaging reflector

    facet_centers   A list of mirror facet centers in the reflector frame

    PAP_offset      The principal aperture offset in the reflector frame
    """
    focal_piont_Rframe = np.array([0.0, 0.0, focal_length + PAP_offset])
    reflector2facets = []
    for facet_center in facet_centers:
        reflector2facets.append(
            ideal_reflector2facet(
                focal_piont_Rframe,
                facet_center))
    return reflector2facets


def mirror_facet_centers(reflector):
    """
    Returns a list of mirror facet center positions calculated from the
    mirror tripod center positions.

    Parameter
    ---------
    reflector       The reflector dictionary
    """
    nodes = reflector['nodes']
    tripods = reflector['mirror_tripods']
    tripod_centers = tools.mirror_tripod_centers(nodes, tripods)
    facet_centers = tripod_centers.copy()
    facet_centers[:,2] += reflector['geometry'].bar_outer_diameter
    return facet_centers


def make_reflector2tripods(reflector):
    """
    Returns a list of homogenoues transformations from the reflector frame to
    the mirror tripod centers

    Parameter
    ---------
    reflector       The reflector dictionary
    """
    nodes = reflector['nodes']
    tripods = reflector['mirror_tripods']
    reflector2tripods = []
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
        reflector2tripods.append(t)
    return reflector2tripods


def ideal_alignment(reflector):
    """
    Returns the ideal alignment of the mirror facets for a given reflector.

        tripod2facet                        A list of homogenoues
                                            transformations from a mirror
                                            tripod frame to the corresponding
                                            mirror facet frame

        principal_aperture_plane_offset     The positional offset to the
                                            principal aperture plane of the
                                            segmented reflector in the reflector
                                            factory frame

    Parameter
    ---------
    reflector       The reflector dictionary
    """
    facet_centers = mirror_facet_centers(reflector)
    focal_length = reflector['geometry'].focal_length
    PAP_offset = PAP_offset_in_z(
        focal_length=focal_length,
        facet_centers=facet_centers)
    reflector2facets = ideal_reflector2facets(
        focal_length=focal_length,
        facet_centers=facet_centers,
        PAP_offset=PAP_offset)
    reflector2tripods = make_reflector2tripods(reflector)
    tripods2facets = []
    for i in range(len(reflector2facets)):
        reflector2facet = reflector2facets[i]
        reflector2tripod = reflector2tripods[i]
        tripod2facet = reflector2tripod.inverse().multiply(reflector2facet)
        tripods2facets.append(tripod2facet)
    return {
        'tripods2facets': tripods2facets,
        'principal_aperture_plane_offset': PAP_offset
    }


def reflector2facets(reflector, alignment):
    """
    Returns a list of homogenoues transformations from the reflector frame to
    each mirror facet frame.

    Parameter
    ---------
    reflector       The reflector dictionary

    alignment       The alignment dictionary
    """
    reflector2tripods = make_reflector2tripods(reflector)
    reflector2facets = []
    for i in range(len(reflector2tripods)):
        tripod2facet = alignment['tripods2facets'][i]
        reflector2tripod = reflector2tripods[i]
        reflector2facet = reflector2tripod.multiply(tripod2facet)
        reflector2facets.append(reflector2facet)
    return reflector2facets
