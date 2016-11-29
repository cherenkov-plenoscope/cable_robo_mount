import reflector_study as rs
import numpy as np

def test_HomTra_init():

    t = rs.HomTra()
    # translation shall be zero
    assert t.T[0,3] == 0.0
    assert t.T[1,3] == 0.0
    assert t.T[2,3] == 0.0

    # rotation shall be eye3
    assert t.T[0,0] == 1.0
    assert t.T[0,1] == 0.0
    assert t.T[0,2] == 0.0

    assert t.T[1,0] == 0.0
    assert t.T[1,1] == 1.0
    assert t.T[1,2] == 0.0

    assert t.T[2,0] == 0.0
    assert t.T[2,1] == 0.0
    assert t.T[2,2] == 1.0

def test_HomTra_inverse_translation_z():
    t = rs.HomTra()
    t.set_translation([0, 0, 3])
    assert t.T[0,3] == 0.0
    assert t.T[1,3] == 0.0
    assert t.T[2,3] == 3.0

    t_inv = t.inverse()
    assert t_inv.T[0,3] == 0.0
    assert t_inv.T[1,3] == 0.0
    assert t_inv.T[2,3] == -3.0   

    assert t.is_close_to(t_inv.inverse())

def test_HomTra_inverse_translation_y():
    t = rs.HomTra()
    t.set_translation([0, 3, 0])
    assert t.T[0,3] == 0.0
    assert t.T[1,3] == 3.0
    assert t.T[2,3] == 0.0

    t_inv = t.inverse()
    assert t_inv.T[0,3] == 0.0
    assert t_inv.T[1,3] == -3.0
    assert t_inv.T[2,3] == 0.0

    assert t.is_close_to(t_inv.inverse())

def test_HomTra_inverse_translation_x():
    t = rs.HomTra()
    t.set_translation([3, 0, 0])
    assert t.T[0,3] == 3.0
    assert t.T[1,3] == 0.0
    assert t.T[2,3] == 0.0

    t_inv = t.inverse()
    assert t_inv.T[0,3] == -3.0
    assert t_inv.T[1,3] == 0.0
    assert t_inv.T[2,3] == 0.0  

    assert t.is_close_to(t_inv.inverse())

def test_HomTra_is_close_to():
    t = rs.HomTra()
    assert t.is_close_to(t)

    u = rs.HomTra()
    assert t.is_close_to(u)
    u.set_translation([1.0, 2.0, 3.0])
    assert not t.is_close_to(u)

def test_HomTra_all():
    t = rs.HomTra()
    t.set_rotation_axis_and_angle([0.0,0.0,1.0], np.rad2deg(90.0))
    t.set_translation([0.0, 1.0, 0.0])

    A = np.array([1.0, 0.0, 0.0])
    B = np.array([0.0, 1.0, 0.0])
    C = np.array([0.0, 0.0, 1.0])

    A_t = t.transformed_position(A)
    B_t = t.transformed_position(B)
    C_t = t.transformed_position(C)

    t_inv = t.inverse()

    assert np.isclose(t_inv.transformed_position(A_t), A, 1e-9).all()
    assert np.isclose(t_inv.transformed_position(B_t), B, 1e-9).all()
    assert np.isclose(t_inv.transformed_position(C_t), C, 1e-9).all()

    assert np.isclose(t.transformed_position_inverse(A), t.inverse().transformed_position(A), 1e-9).all()
    assert np.isclose(t.transformed_position_inverse(B), t.inverse().transformed_position(B), 1e-9).all()
    assert np.isclose(t.transformed_position_inverse(C), t.inverse().transformed_position(C), 1e-9).all()

def test_tait_bryan_eye():
    Rx = 0.0
    Ry = 0.0
    Rz = 0.0

    t = rs.HomTra()
    t.set_rotation_tait_bryan_angles(Rx, Ry, Rz)

    # rotation shall be eye3
    assert t.T[0,0] == 1.0
    assert t.T[0,1] == 0.0
    assert t.T[0,2] == 0.0

    assert t.T[1,0] == 0.0
    assert t.T[1,1] == 1.0
    assert t.T[1,2] == 0.0

    assert t.T[2,0] == 0.0
    assert t.T[2,1] == 0.0
    assert t.T[2,2] == 1.0