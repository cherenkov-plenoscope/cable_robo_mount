import numpy as np

def bar_length(nodes, bar):
    start = nodes[bar[0]]
    end = nodes[bar[1]]
    return np.linalg.norm(end - start)

def find_angle_between_two_bars(bar1, bar2, nodes):
    Vec1 = nodes[bar1[1]] - nodes[bar1[0]]
    Vec2 = nodes[bar2[1]] - nodes[bar2[0]]
    angle_in_rad = np.arccos(sum(Vec1.T * Vec2.T)/(np.linalg.norm(Vec1) * np.linalg.norm(Vec2)))
    angle_in_degrees = np.degrees(angle_in_rad)
    return angle_in_degrees

def list_of_angles_between_neighbouring_bars(joints, bars, nodes):
    end_list = []
    shape = 0
    for i in range(len(joints)):
        for j in range(len(joints[i])-1):
            bar1 = bars[joints[i][j]]
            bar2 = bars[joints[i][j+1]]
            end_list.append([find_angle_between_two_bars(bar1=bar1, bar2=bar2, nodes=nodes)])
    return end_list
