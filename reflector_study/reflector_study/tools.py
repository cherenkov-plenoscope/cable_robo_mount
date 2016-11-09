def node_position(nodes, ijk):
    return nodes[ijk[0], ijk[1], ijk[2]]


def node_in_range(nodes, ijk):
    i_valid = ijk[0] >= 0 and ijk[0] < nodes.shape[0]
    j_valid = ijk[1] >= 0 and ijk[1] < nodes.shape[1]
    k_valid = ijk[2] >= 0 and ijk[2] < nodes.shape[2]
    return i_valid and j_valid and k_valid


def bar_start_and_end_position(nodes, bar):
    start = node_position(nodes, bar[0])
    end = node_position(nodes, bar[1])
    return start, end


def bar_in_range(nodes, bar):
    start_is_in_range = node_in_range(nodes, bar[0])
    end_is_in_range = node_in_range(nodes, bar[1])
    return start_is_in_range and end_is_in_range


def bar_length(nodes, bar):
    start = node_position(nodes, bar[0])
    end = node_position(nodes, bar[1])
    return np.linalg.norm(end - start)
