

def add2ax_bars(ax, nodes, bars):
    for bar in bars:
        start = nodes[bar[0]]
        end = nodes[bar[1]]
        ax.plot([start[0], end[0]],
                [start[1], end[1]],
                [start[2], end[2]],'b')
