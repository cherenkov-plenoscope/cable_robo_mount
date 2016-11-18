import numpy as np

#node_position simply is the nodes[i]
#bar_length

def bar_length(nodes, bar):
    start = nodes[bar[0]]
    end = nodes[bar[1]]
    return np.linalg.norm(end - start)

def bars_length(nodes, bars):
    bars_length = []
    for i in range((bars.shape[0])):
        bars_length.append(bar_length(nodes, bars[i]))
    return bars_length
