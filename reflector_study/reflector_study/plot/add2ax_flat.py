

def add2ax_bars(ax, nodes, bars):
    for bar in bars:
        start = nodes[bar[0]]
        end = nodes[bar[1]]
        ax.plot([start[0], end[0]],
                [start[1], end[1]],
                [start[2], end[2]],'b')


def add2ax_mirror_tripods(ax, nodes, mirror_tripods):
    for mirror_tripod in mirror_tripods:
        n1 = nodes[mirror_tripod[0]]
        n2 = nodes[mirror_tripod[1]]
        n3 = nodes[mirror_tripod[2]]
        ax.plot([n1[0], n2[0]],
                [n1[1], n2[1]],
                [n1[2], n2[2]],'r',linewidth=3.0)
        ax.plot([n2[0], n3[0]],
                [n2[1], n3[1]],
                [n2[2], n3[2]],'r',linewidth=3.0)
        ax.plot([n3[0], n1[0]],
                [n3[1], n1[1]],
                [n3[2], n1[2]],'r',linewidth=3.0)
