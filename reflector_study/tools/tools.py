import numpy as np

def bar_length(nodes, bar):
    start = nodes[bar[0]]
    end = nodes[bar[1]]
    return np.linalg.norm(end - start)

def angle_between_bars(bar1, bar2, nodes):
    Vec1 = nodes[bar1[1]] - nodes[bar1[0]]
    Vec2 = nodes[bar2[1]] - nodes[bar2[0]]
    return np.arccos(sum(Vec1.T * Vec2.T)/(np.linalg.norm(Vec1) * np.linalg.norm(Vec2)))

def list_of_angles_between_neighbouring_bars(joints, bars, nodes):
    end_list = []
    shape = 0
    for i in range(len(joints)):
        for j in range(len(joints[i])-1):
            bar1 = bars[joints[i][j]]
            bar2 = bars[joints[i][j+1]]
            end_list.append([angle_between_bars(bar1=bar1, bar2=bar2, nodes=nodes)])
    return end_list


def mirror_tripod_center(nodes, mirror_tripod):
    A = nodes[mirror_tripod[0]]
    B = nodes[mirror_tripod[1]]
    C = nodes[mirror_tripod[2]]
    return (A + B + C)/3.0


def mirror_tripod_centers(nodes, mirror_tripods):
    tripod_centers = np.zeros(shape=(mirror_tripods.shape[0],3), dtype=np.float64)
    for i, tripod in enumerate(mirror_tripods):
        tripod_centers[i,:] = mirror_tripod_center(nodes, tripod)
    return np.array(tripod_centers)


def mirror_tripod_x(nodes, mirror_tripod):
    A = nodes[mirror_tripod[0]]
    B = nodes[mirror_tripod[1]]
    AB = B - A
    return AB/np.linalg.norm(AB)


def mirror_tripod_z(nodes, mirror_tripod):
    A = nodes[mirror_tripod[0]]
    B = nodes[mirror_tripod[1]]
    C = nodes[mirror_tripod[2]]
    AB = B - A
    AC = C - A
    Z = np.cross(AB, AC)
    return Z/np.linalg.norm(Z)


def mirror_tripod_y(nodes, mirror_tripod):
    z_axis = mirror_tripod_z(nodes, mirror_tripod)
    x_axis = mirror_tripod_x(nodes, mirror_tripod)
    return np.cross(x_axis, z_axis)