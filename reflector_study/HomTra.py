import numpy as np

class HomTra(object):
    """
    The concept of Homogeneous Transformations is taken from the text book 
   
    "Robotics -- Modelling, Planning and Control" 
    by Bruno Siciliano, Lorenzo Sciavicco, Luigi Villani and Guiseppe Oriolo.
   
    The chapter on kinematics serves an excellent introduction into 3D concepts
    and is highly recomended for all questions on:
   
    - Pose of a rigid body
    - Rotation Matrix
      - Elementary Rotations
      - Representation of a Vector
      - Rotation of a Vector
    - Composition of Rotation Matrices
    - Euler Angles
    - ZYZ Angles
    - RPY Angles
    - Angle and Axis
    - Unit Quaternion
    - Homogeneous Transformation
    """

    def __init__(self):
        self.T = np.zeros(shape=(3,4), dtype=np.float64)
        self.T[0,0] = 1.0
        self.T[1,1] = 1.0
        self.T[2,2] = 1.0

    def set_translation(self, pos):
        self.T[0,3] = pos[0]
        self.T[1,3] = pos[1]
        self.T[2,3] = pos[2]

    def set_rotation_axis_and_angle(self, axis, phi):
        axis = axis/np.linalg.norm(axis)
        rx = axis[0]
        ry = axis[1]
        rz = axis[2]
        sinR = np.sin(phi)
        cosR = np.cos(phi)
        # first row
        self.T[0,0] = cosR +  rx*rx*(1.0-cosR);
        self.T[0,1] = rx*ry*(1.0-cosR)-rz*sinR;
        self.T[0,2] = rx*rz*(1.0-cosR)+ry*sinR;
        # second row
        self.T[1,0] = ry*rx*(1.0-cosR)+rz*sinR;
        self.T[1,1] = cosR +  ry*ry*(1.0-cosR);
        self.T[1,2] = ry*rz*(1.0-cosR)-rx*sinR;
        # third row
        self.T[2,0] = rz*rx*(1.0-cosR)-ry*sinR;
        self.T[2,1] = rz*ry*(1.0-cosR)+rx*sinR;
        self.T[2,2] = cosR +  rz*rz*(1.0-cosR);

    def transformed_position(self, pos):
        return np.array([
            #x
            pos[0]*self.T[0,0] + 
            pos[1]*self.T[0,1] + 
            pos[2]*self.T[0,2] + self.T[0,3],
            #y
            pos[0]*self.T[1,0] + 
            pos[1]*self.T[1,1] + 
            pos[2]*self.T[1,2] + self.T[1,3],
            #z
            pos[0]*self.T[2,0] + 
            pos[1]*self.T[2,1] + 
            pos[2]*self.T[2,2] + self.T[2,3]
        ])

    def transformed_position_inverse(self, pos):
        return np.array([
            #x
            pos[0]*self.T[0,0] + 
            pos[1]*self.T[1,0] + 
            pos[2]*self.T[2,0] - (  self.T[0,0]*self.T[0,3] + 
                                    self.T[1,0]*self.T[1,3] + 
                                    self.T[2,0]*self.T[2,3]),
            #y
            pos[0]*self.T[0,1] + 
            pos[1]*self.T[1,1] + 
            pos[2]*self.T[2,1] - (  self.T[0,1]*self.T[0,3] + 
                                    self.T[1,1]*self.T[1,3] + 
                                    self.T[2,1]*self.T[2,3]),
            #z
            pos[0]*self.T[0,2] + 
            pos[1]*self.T[1,2] + 
            pos[2]*self.T[2,2] - (  self.T[0,2]*self.T[0,3] + 
                                    self.T[1,2]*self.T[1,3] + 
                                    self.T[2,2]*self.T[2,3])
        ])

    def transformed_orientation(self, ori):
        return np.array([
            #x
            pos[0]*self.T[0,0] + 
            pos[1]*self.T[0,1] + 
            pos[2]*self.T[0,2],
            #y
            pos[0]*self.T[1,0] + 
            pos[1]*self.T[1,1] + 
            pos[2]*self.T[1,2],
            #z
            pos[0]*self.T[2,0] + 
            pos[1]*self.T[2,1] + 
            pos[2]*self.T[2,2]
        ])


    def transformed_orientation_inverse(self, ori):
        return np.array([
            #x
            pos[0]*self.T[0,0] + 
            pos[1]*self.T[1,0] + 
            pos[2]*self.T[2,0],
            #y
            pos[0]*self.T[0,1] + 
            pos[1]*self.T[1,1] + 
            pos[2]*self.T[2,1],
            #z
            pos[0]*self.T[0,2] + 
            pos[1]*self.T[1,2] + 
            pos[2]*self.T[2,2]
        ])        

    def __repr__(self):
        out = 'HomTra('
        out+= 'R00: '+str(self.T[0,0])+' '
        out+= 'R01: '+str(self.T[0,1])+' '
        out+= 'R02: '+str(self.T[0,2])+' '
        out+= 'T0: '+str(self.T[0,3])+' '
        out+= 'R10: '+str(self.T[1,0])+' '
        out+= 'R11: '+str(self.T[1,1])+' '
        out+= 'R12: '+str(self.T[1,2])+' '
        out+= 'T1: '+str(self.T[1,3])+' '
        out+= 'R20: '+str(self.T[2,0])+' '
        out+= 'R21: '+str(self.T[2,1])+' '
        out+= 'R22: '+str(self.T[2,2])+' '
        out+= 'T2: '+str(self.T[2,3])
        out+= ')'
        return out

    def multiply(self, mul):
        # Matrix multiplication 
        T = self.T
        G = mul.T

        out = HomTra()
        out.T[0,0] = T[0,0]*G[0,0] + T[0,1]*G[1,0] + T[0,2]*G[2,0]# + T[0,3]*      0.0
        out.T[0,1] = T[0,0]*G[0,1] + T[0,1]*G[1,1] + T[0,2]*G[2,1]# + T[0,3]*      0.0
        out.T[0,2] = T[0,0]*G[0,2] + T[0,1]*G[1,2] + T[0,2]*G[2,2]# + T[0,3]*      0.0
        out.T[0,3] = T[0,0]*G[0,3] + T[0,1]*G[1,3] + T[0,2]*G[2,3] + T[0,3]#*      1.0   

        out.T[1,0] = T[1,0]*G[0,0] + T[1,1]*G[1,0] + T[1,2]*G[2,0]# + T[1,3]*      0.0
        out.T[1,1] = T[1,0]*G[0,1] + T[1,1]*G[1,1] + T[1,2]*G[2,1]# + T[1,3]*      0.0
        out.T[1,2] = T[1,0]*G[0,2] + T[1,1]*G[1,2] + T[1,2]*G[2,2]# + T[1,3]*      0.0
        out.T[1,3] = T[1,0]*G[0,3] + T[1,1]*G[1,3] + T[1,2]*G[2,3] + T[1,3]#*      1.0

        out.T[2,0] = T[2,0]*G[0,0] + T[2,1]*G[1,0] + T[2,2]*G[2,0]# + T[2,3]*      0.0
        out.T[2,1] = T[2,0]*G[0,1] + T[2,1]*G[1,1] + T[2,2]*G[2,1]# + T[2,3]*      0.0
        out.T[2,2] = T[2,0]*G[0,2] + T[2,1]*G[1,2] + T[2,2]*G[2,2]# + T[2,3]*      0.0
        out.T[2,3] = T[2,0]*G[0,3] + T[2,1]*G[1,3] + T[2,2]*G[2,3] + T[2,3]#*      1.0

        #out.T[0,0] = T[3,0]*G[0,0] + T[3,1]*G[1,0] + T[3,2]*G[2,0] + T[3,3]*G[3,0];
        #out.T[0,0] = T[3,0]*G[0,1] + T[3,1]*G[1,1] + T[3,2]*G[2,1] + T[3,3]*G[3,1];
        #out.T[0,0] = T[3,0]*G[0,2] + T[3,1]*G[1,2] + T[3,2]*G[2,2] + T[3,3]*G[3,2];
        #out.T[0,0] = T[3,0]*G[0,3] + T[3,1]*G[1,3] + T[3,2]*G[2,3] + T[3,3]*G[3,3];
        return out

    def inverse(self):
        out = HomTra()
        T = self.T
        out.T[0,0] = T[0,0]
        out.T[0,1] = T[1,0]
        out.T[0,2] = T[2,0]
        out.T[0,3] = -(T[0,0]*T[0,3] + T[1,0]*T[1,3] + T[2,0]*T[2,3])

        out.T[1,0] = T[0,1]
        out.T[1,1] = T[1,1]
        out.T[1,2] = T[2,1]
        out.T[1,3] = -(T[0,1]*T[0,3] + T[1,1]*T[1,3] + T[2,1]*T[2,3])

        out.T[2,0] = T[0,2]
        out.T[2,1] = T[1,2]
        out.T[2,2] = T[2,2]
        out.T[2,3] = -(T[0,2]*T[0,3] + T[1,2]*T[1,3] + T[2,2]*T[2,3])
        return out


    def is_close_to(self, A, max_distance=1e-9):
        for row in range(3):
            for col in range(4):
                if np.abs(self.T[row,col] - A.T[row,col]) > max_distance:
                    return False
        return True

    def rotation_x(self):
        return self.T[:,0]

    def rotation_y(self):
        return self.T[:,1]

    def rotation_z(self):
        return self.T[:,2]

    def translation(self):
        return self.T[:,3]