import numpy as np
from ..non_flat_tools import mirror_tripod_x
from ..non_flat_tools import mirror_tripod_y
from ..non_flat_tools import mirror_tripod_z
from ..non_flat_tools import mirror_tripod_center


class HomogenousTransformation(object):
	def __init__(self, rot, trans):
		self.rot = rot
		self.trans = trans

	def inverse(self):
		inv_rot = np.zeros(shape=(3,3))

		self.rot = rot
		self.trans = trans

def mirror_tripods_2_mctracer(nodes, mirror_tripods):

    for mirror_tripod in mirror_tripods:
        x = mirror_tripod_x(nodes,mirror_tripod)
        y = mirror_tripod_y(nodes,mirror_tripod)
        z = mirror_tripod_z(nodes,mirror_tripod)
        translation = mirror_tripod_center(nodes, mirror_tripod)

        rot = np.zeros(shape=(3,3))
        rot[0,:] = x
        rot[1,:] = y
        rot[2,:] = z
