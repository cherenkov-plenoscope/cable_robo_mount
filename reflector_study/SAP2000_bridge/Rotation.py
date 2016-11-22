import numpy as np

class Rotation(object):
    def __init__(self, structural_dict):
        self.angle_from_zenith = structural_dict['position']['angle_from_zenith']


    def _set_up_new_position(self):
        self.rotational_matrix = np.matrix([[np.cos(self.angle_from_zenith),  0, np.sin(self.angle_from_zenith)],
                                            [0,                               1,                              0],
                                            [-np.sin(self.angle_from_zenith), 0, np.cos(self.angle_from_zenith)]])

    def __repr__(self):
        info = 'Rotation'
        info+= '(Angle_of_the dish_from_zenith: '+str(self.angle_from_zenith)-90+'°"
        return info
