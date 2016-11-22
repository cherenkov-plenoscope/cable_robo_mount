import reflector_study as rs
import numpy as np

def test_angle_in_between_bars():
    nodes = np.array([[1,0,0], [0,0,0], [0,1,0], [-1, 0, 0]])
    bars = np.array([[0, 1], [1, 2]])
    assert rs.tools.angle_between_bars(bars[0], bars[1], nodes) == np.pi/2

    other_bars = np.array([[0, 1], [0, 2]])
    angle = rs.tools.angle_between_bars(other_bars[0], other_bars[1], nodes)    
    assert  np.abs(np.pi/4 - angle) < 1e-9

    assert rs.tools.angle_between_bars(bars[0], bars[0], nodes) == 0.0

    bars2 = np.array([[1, 0], [1, 3]])
    assert rs.tools.angle_between_bars(bars2[0], bars2[1], nodes) == np.pi