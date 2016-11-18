import numpy as np

#node_position simply is the nodes[i]
#bar_length

def bar_length(nodes, bar):
    start = nodes[bar[0]]
    end = nodes[bar[1]]
    return np.linalg.norm(end - start)
