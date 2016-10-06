import numpy as np

def tuple3(vec):
    return '['+str(vec[0])+','+str(vec[1])+','+str(vec[2])+']'

def mct_hexagonal_imaging_mirror_facet(
    name,
    position,
    rotation,
    outer_radius,
    curvature_radius,
    reflection_vs_wavelength,):

    xml = ''
    xml+= '<sphere_cap_hexagonal>\n'
    xml+= '    <set_frame '
    xml+=           'name="'+name+'" '
    xml+=           'pos="'+tuple3(position)+'" '
    xml+=           'rot="'+tuple3(rotation)+'">\n'
    xml+= '    <set_surface '
    xml+=           'reflection_vs_wavelength="'+reflection_vs_wavelength+'" '
    xml+=           'color="[75,75,75]"/>\n'
    xml+= '    <set_sphere_cap_hexagonal '
    xml+=           'curvature_radius="'+str(curvature_radius)+'" '
    xml+=           'outer_radius="'+str(outer_radius)+'"/>\n'
    xml+= '</sphere_cap_hexagonal>\n'
    return xml

class SegmentedImagingReflectorHexagonalFacets(object):

    def __init__(self):

        self.focal_length = 1.
        self.facet_outer_radius = 1.
        self.facet_center_positions = np.zeros(shape=(100,3))
        self.facet_surface_normals = np.zeros(shape=(100,3))
        self.facet_surface_normals[:,2] = np.ones(100)

        self.facet_z_rotation = 0.0


    def read(self, path):
        # some read in magic here
        pass


    def mean_distance_facet_centers_to_target_focal_point(self):
        target_focal_point = np.array([0.0, 0.0, self.focal_length])
        links = target_focal_point - self.facet_center_positions
        distances = np.linalg.norm(links, axis=1)
        return distances.mean()


    def _normal2rotation(self, normal):
        return np.array([normal[0], normal[1], self.facet_z_rotation])


    def mct_xml(self, reflection_vs_wavelength='mirror_reflectivity'):

        facet_curvature_radius = 2.0*self.focal_length
        xml = ''

        for i in range(self.facet_center_positions.shape[0]):
            facet_position = self.facet_center_positions[i]
            facet_rotation = self._normal2rotation(self.facet_surface_normals[i])
            name = 'facet_'+str(i)

            xml += mct_hexagonal_imaging_mirror_facet(
                name=name,
                position=facet_position,
                rotation=facet_rotation,
                outer_radius=self.facet_outer_radius,
                curvature_radius=facet_curvature_radius,
                reflection_vs_wavelength=reflection_vs_wavelength)
            xml+='\n'

        return xml


