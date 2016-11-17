import numpy as np
from .xml import cylinder
from ..tools import bar_start_and_end_position


def space_frame2mctracer(nodes, bars, radius, color):
    xml = ''
    for i, bar in enumerate(bars):
        start_pos, end_pos = bar_start_and_end_position(nodes, bar)
        xml += cylinder(
            name='bar_'+str(i), 
            start_pos=start_pos, 
            end_pos=end_pos, 
            radius=radius, 
            color=color)
    return xml