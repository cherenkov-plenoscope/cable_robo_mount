import numpy as np


def generate_camera_space_frame_quint(light_field_sensor_radius=5.0):
    """
    Adopted from
    http://robohub.org/cable-driven-parallel-robots-motion-simulation-in-a-new-dimension/
    """
    number_of_edges = 5
    inner_radius = light_field_sensor_radius
    outer_radius = inner_radius/(np.cos(np.pi/number_of_edges))

    off = +np.pi/4
    r = outer_radius
    nodes = np.array([
        # lower layer
        [ r*np.cos(2*np.pi*0.0+off), r*np.sin(2*np.pi*0.0+off), 0],  # 0
        [ r*np.cos(2*np.pi*0.2+off), r*np.sin(2*np.pi*0.2+off), 0],  # 1
        [ r*np.cos(2*np.pi*0.4+off), r*np.sin(2*np.pi*0.4+off), 0],  # 2
        [ r*np.cos(2*np.pi*0.6+off), r*np.sin(2*np.pi*0.6+off), 0],  # 3
        [ r*np.cos(2*np.pi*0.8+off), r*np.sin(2*np.pi*0.8+off), 0],  # 4
        # upper layer
        [ r*np.cos(2*np.pi*0.1+off), r*np.sin(2*np.pi*0.1+off), r],  # 5
        [ r*np.cos(2*np.pi*0.3+off), r*np.sin(2*np.pi*0.3+off), r],  # 6
        [ r*np.cos(2*np.pi*0.5+off), r*np.sin(2*np.pi*0.5+off), r],  # 7
        [ r*np.cos(2*np.pi*0.7+off), r*np.sin(2*np.pi*0.7+off), r],  # 8
        [ r*np.cos(2*np.pi*0.9+off), r*np.sin(2*np.pi*0.9+off), r],  # 9
        # central node
        [                     0,                     0, 1.5*r],  # 10
    ])

    bars = np.array([
        # lower layer
        [0,1],
        [1,2],
        [2,3],
        [3,4],
        [4,0],
        # upper layer
        [5,6],
        [6,7],
        [7,8],
        [8,9],
        [9,5],
        # upper pyramide
        [5,10],
        [6,10],
        [7,10],
        [8,10],
        [9,10],
        # between layer 1
        [0,5],
        [1,6],
        [2,7],
        [3,8],
        [4,9],
        # between layer 1
        [0,9],
        [1,5],
        [2,6],
        [3,7],
        [4,8],
    ], dtype=np.uint64)

    return {
        'nodes': nodes,
        'bars': bars,
        'cable_supports': {
            'lower': [1,2,3,4],
            'upper': [5,6,8,9],
        }
    }


def generate_camera_space_frame(
    light_field_sensor_radius=5.0,
    camera_housing_hight=1.0
):
    """
    The space frame of the camera to be hang in the Cable-Robo-Mount.

    According to:
    'Design of a light weight supporting structure for next generation
    telescopes, Semester Project Report Spring 2016'
    Figure 104.
    """
    chh = camera_housing_hight
    psr = light_field_sensor_radius

    cube_hight = psr*np.sqrt(2)

    nodes = np.array([
        # lower layer
        [ psr,   0, chh],  # 0
        [   0, psr, chh],  # 1
        [-psr,   0, chh],  # 2
        [   0,-psr, chh],  # 3
        # upper layer
        [ psr,   0, chh + cube_hight],  # 4
        [   0, psr, chh + cube_hight],  # 5
        [-psr,   0, chh + cube_hight],  # 6
        [   0,-psr, chh + cube_hight],  # 7
        # center nodes
        [ psr/np.sqrt(2), psr/np.sqrt(2), chh + cube_hight/2],  # 8
        [-psr/np.sqrt(2), psr/np.sqrt(2), chh + cube_hight/2],  # 9
        [-psr/np.sqrt(2),-psr/np.sqrt(2), chh + cube_hight/2],  # 10
        [ psr/np.sqrt(2),-psr/np.sqrt(2), chh + cube_hight/2],  # 11
        [              0,              0, chh + cube_hight + psr/(2*np.sqrt(2))],  # 12
        # central node
        [              0,              0, chh + cube_hight/2],  # 13
    ])

    bars = np.array([
        # lower layer
        [0,1],
        [1,2],
        [2,3],
        [3,0],
        # upper layer
        [4,5],
        [5,6],
        [6,7],
        [7,4],
        # vertical bars
        [0,4],
        [1,5],
        [2,6],
        [3,7],
        # diamond in sector +x+y
        [0,8],
        [1,8],
        [4,8],
        [5,8],
        # diamond in sector -x+y
        [1,9],
        [2,9],
        [5,9],
        [6,9],
        # diamond in sector -x-y
        [2,10],
        [3,10],
        [6,10],
        [7,10],
        # diamond in sector +x-y
        [3,11],
        [0,11],
        [7,11],
        [4,11],
        # diamond on top
        [4,12],
        [5,12],
        [6,12],
        [7,12],
        # diagonal in sector +x+y
        [0,5],
        # diagonal in sector -x+y
        [1,6],
        # diagonal in sector -x-y
        [2,7],
        # diagonal in sector +x-y
        [3,4],
        # diagonal on top
        [4,6],
        # inner bars to center node
        [13, 0],
        [13, 1],
        [13, 2],
        [13, 3],
        [13, 4],
        [13, 5],
        [13, 6],
        [13, 7],
    ], dtype=np.uint64)

    cable_supports = np.array([])

    return {
        'nodes': nodes,
        'bars': bars,
        'cable_supports': cable_supports,
    }


def apply_shrinkink(nodes, hight_of_section, top_width, base_width):
    """
    applys an hight (z-axis) dependend shrinking (in x and y) to the nodes.

    Parameter
    ---------
    nodes               The nodes to be shrunk in x and y.

    hight_of_section    The overall hight of a single section.

    top_width           The x, y width of the upper most layer in a section.

    base_width          The x, y width of the lowest layer in a section.
    """
    thinning = (base_width - top_width)/hight_of_section

    for i in range(nodes.shape[0]):
        node_hight_in_section = nodes[i,2]
        relative_hight_in_section = node_hight_in_section/hight_of_section
        nodes[i][0] *= 1 - relative_hight_in_section*thinning
        nodes[i][1] *= 1 - relative_hight_in_section*thinning
    return nodes


def generate_tower_section_type_A(hight, base_width, top_width):
    """
    The camera tower space frame section according to:
    Figure 109,
    'Design of a light weight supporting structure for next generation
    telescopes, Semester Project Report Spring 2016'

    The space frame of nodes and bars contains the entire structure, so it can
    not be concatenated without removing the duplicate nodes which are shared
    between the sections.

    Paramter
    --------
    hight       The hight of this section.

    base_width  The width in x and y of the base (the lowest layer h0).

    top_width   The width in x and y of the top (the upper most layer h2).
    """
    r = base_width/2
    h = hight

    h0 = 0
    h1 = hight*1/4
    h2 = hight*2/4
    h3 = hight*3/4
    h4 = hight

    r0 = 0
    r1 = r*1/4
    r2 = r*2/4
    r3 = r*3/4
    r4 = r
    #        |-----r-----|
    #
    #   --   o-----o-----o  h4
    #    |   |   /  \   /
    #    |   | /     \ /
    #    |   o--------o     h3
    #    |   | \     /
    #    |   |    \ /
    #    h   o-----o        h2
    #    |   |\   /
    #    |   | \ /
    #    |   o--o           h1
    #    |   | /
    #    |   |/
    #   --   0              h0

    nodes = np.array([

        # h0 layer
        #        1                       0
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #        2                       3
        [ r4, r4, h0],  # 0
        [-r4, r4, h0],  # 1
        [-r4,-r4, h0],  # 2
        [ r4,-r4, h0],  # 3

        # h1 layer
        #        5---13              8---4
        #        |                       |
        #        9                       12
        #
        #
        #
        #
        #
        #
        #
        #        14                      11
        #        |                       |
        #        6---10             15---7
        [ r4, r4, h1],  # 4
        [-r4, r4, h1],  # 5
        [-r4,-r4, h1],  # 6
        [ r4,-r4, h1],  # 7

        [ r3, r4, h1],  # 8
        [-r4, r3, h1],  # 9
        [-r3,-r4, h1],  # 10
        [ r4,-r3, h1],  # 11

        [ r4, r3, h1],  # 12
        [-r3, r4, h1],  # 13
        [-r4,-r3, h1],  # 14
        [ r3,-r4, h1],  # 15

        # h2 layer
        #        17--25             20---16
        #        |                       |
        #        21                      24
        #
        #
        #
        #
        #
        #
        #
        #        26                      23
        #        |                       |
        #        18--22             27---19
        [ r4, r4, h2],  # 16
        [-r4, r4, h2],  # 17
        [-r4,-r4, h2],  # 18
        [ r4,-r4, h2],  # 19

        [ r2, r4, h2],  # 20
        [-r4, r2, h2],  # 21
        [-r2,-r4, h2],  # 22
        [ r4,-r2, h2],  # 23

        [ r4, r2, h2],  # 24
        [-r2, r4, h2],  # 25
        [-r4,-r2, h2],  # 26
        [ r2,-r4, h2],  # 27

        # h3 layer
        #        29--37             32---28
        #        |                       |
        #        33                      36
        #
        #
        #
        #
        #
        #
        #
        #        38                      35
        #        |                       |
        #        30--34             39---31
        [ r4, r4, h3],  # 28
        [-r4, r4, h3],  # 29
        [-r4,-r4, h3],  # 30
        [ r4,-r4, h3],  # 31

        [ r1, r4, h3],  # 32
        [-r4, r1, h3],  # 33
        [-r1,-r4, h3],  # 34
        [ r4,-r1, h3],  # 35

        [ r4, r1, h3],  # 36
        [-r1, r4, h3],  # 37
        [-r4,-r1, h3],  # 38
        [ r1,-r4, h3],  # 39

        # h4 layer
        #        41----49----53----44----40
        #        |        65    60       |
        #        45    57          56    48
        #        | 61                    |
        #        |                    64 |  relative_hight = 1/3
        #        |                       |
        #        54                      52
        #        |                       |
        #        |  66                   |
        #        |                    63 |
        #        50    58          59    47
        #        |        62    67       |
        #        42----46----55----51----43
        [ r4, r4, h4],  # 40
        [-r4, r4, h4],  # 41
        [-r4,-r4, h4],  # 42
        [ r4,-r4, h4],  # 43

        [ r2, r4, h4],  # 44
        [-r4, r2, h4],  # 45
        [-r2,-r4, h4],  # 46
        [ r4,-r2, h4],  # 47

        [ r4, r2, h4],  # 48
        [-r2, r4, h4],  # 49
        [-r4,-r2, h4],  # 50
        [ r2,-r4, h4],  # 51

        [ r4, r0, h4],  # 52
        [-r0, r4, h4],  # 53
        [-r4,-r0, h4],  # 54
        [ r0,-r4, h4],  # 55

        [ r2, r2, h4],  # 56
        [-r2, r2, h4],  # 57
        [-r2,-r2, h4],  # 58
        [ r2,-r2, h4],  # 59

        [ r1, r3, h4],  # 60
        [-r3, r1, h4],  # 61
        [-r1,-r3, h4],  # 62
        [ r3,-r1, h4],  # 63

        [ r3, r1, h4],  # 64
        [-r1, r3, h4],  # 65
        [-r3,-r1, h4],  # 66
        [ r1,-r3, h4],  # 67
    ])

    bars = np.array([
        # layer 0 - 1
        [0,4],
        [0,8],
        [0,12],

        [1,13],
        [5,9],
        [5,13],

        [2,14],
        [6,10],
        [6,14],

        [3,7],
        [3,11],
        [3,15],

        # layer 1
        [4,8],
        [4,12],

        [1,5],
        [1,9],

        [2,6],
        [2,10],

        [7,11],
        [7,15],
        # layer 1 - 2
        [4,16],
        [8,20],
        [12,24],
        [8,16],
        [12,16],

        [5,17],
        [9,21],
        [13,25],
        [9,17],
        [13,17],

        [6,18],
        [10,22],
        [14,26],
        [10,18],
        [14,18],

        [7,19],
        [11,23],
        [15,27],
        [11,19],
        [15,19],
        # layer 2
        [16,20],
        [16,24],

        [17,21],
        [17,25],

        [18,22],
        [18,26],

        [19,23],
        [19,27],
        # layer 2 - 3
        [16,28],
        [20,32],
        [24,36],
        [24,28],
        [20,28],

        [17,29],
        [21,33],
        [25,37],
        [25,29],
        [21,29],

        [18,30],
        [22,34],
        [26,38],
        [26,30],
        [22,30],

        [19,31],
        [23,35],
        [27,39],
        [27,31],
        [23,31],
        # layer 3
        [32,28],
        [36,28],

        [33,29],
        [37,29],

        [34,30],
        [38,30],

        [35,31],
        [39,31],
        # layer 3 - 4
        [28,40],
        [32,53],
        [36,52],
        [32,44],
        [28,44],
        [36,48],
        [28,48],

        [29,41],
        [33,54],
        [37,53],
        [33,45],
        [29,45],
        [37,49],
        [29,49],

        [30,42],
        [34,55],
        [38,54],
        [34,46],
        [30,46],
        [38,50],
        [30,50],

        [31,43],
        [35,52],
        [39,55],
        [35,47],
        [31,47],
        [39,51],
        [31,51],

        # outer ring
        [40,44],
        [40,48],
        [44,53],
        [48,52],

        [41,45],
        [41,49],
        [45,54],
        [49,53],

        [42,46],
        [42,50],
        [46,55],
        [50,54],

        [43,47],
        [43,51],
        [47,52],
        [51,55],
        # long diagonals
        [52,64],
        [64,56],
        [56,60],
        [60,53],

        [53,65],
        [65,57],
        [57,61],
        [61,54],

        [54,66],
        [66,58],
        [58,62],
        [62,55],

        [55,67],
        [67,59],
        [59,63],
        [63,52],
        # small parallels
        [60,65],
        [61,66],
        [62,67],
        [63,64],

        # small diagonals
        [44,60],
        [48,64],

        [45,61],
        [49,65],

        [46,62],
        [50,66],

        [47,63],
        [51,67],
        # outer parallels
        [44,56],
        [48,56],

        [49,57],
        [45,57],

        [50,58],
        [46,58],

        [51,59],
        [47,59],

        # outer diagonals
        [44,48],
        [49,45],
        [50,46],
        [51,47],
    ], dtype=np.uint64)

    nodes = apply_shrinkink(
        nodes=nodes,
        hight_of_section=hight,
        top_width=top_width,
        base_width=base_width)

    return {
        'nodes': nodes,
        'bars': bars,
    }


def generate_tower_section_type_B(hight, base_width, top_width):
    """
    The camera tower space frame section according to:
    Figure 110,
    'Design of a light weight supporting structure for next generation
    telescopes, Semester Project Report Spring 2016'

    The space frame of nodes and bars contains the entire structure, so it can
    not be concatenated without removing the duplicate nodes which are shared
    between the sections.

    Paramter
    --------
    hight       The hight of this section.

    base_width  The width in x and y of the base (the lowest layer h0).

    top_width   The width in x and y of the top (the upper most layer h2).
    """

    r = base_width/2
    h = hight

    h0 = 0
    h1 = hight*1/2
    h2 = hight*1

    r0 = 0
    r1 = r

    nodes = np.array([
        # layer 0
        #
        #   1-----4-----0
        #   |           |
        #   |           |
        #   5           7
        #   |           |
        #   |           |
        #   2-----6-----3
        [ r1, r1, h0],  # 0
        [-r1, r1, h0],  # 1
        [-r1,-r1, h0],  # 2
        [ r1,-r1, h0],  # 3

        [ r0, r1, h0],  # 4
        [-r1, r0, h0],  # 5
        [-r0,-r1, h0],  # 6
        [ r1,-r0, h0],  # 7

        # layer 1
        #
        #   9-----------8
        #   |           |
        #   |           |
        #   |           |
        #   |           |
        #   |           |
        #   10----------11
        [ r1, r1, h1],  # 8
        [-r1, r1, h1],  # 9
        [-r1,-r1, h1],  # 10
        [ r1,-r1, h1],  # 11
        # layer 2
        #
        #   13----16----12
        #   |           |
        #   |           |
        #   17          19
        #   |           |
        #   |           |
        #   14----18----15
        [ r1, r1, h2],  # 12
        [-r1, r1, h2],  # 13
        [-r1,-r1, h2],  # 14
        [ r1,-r1, h2],  # 15

        [ r0, r1, h2],  # 16
        [-r1, r0, h2],  # 17
        [-r0,-r1, h2],  # 18
        [ r1,-r0, h2],  # 19
    ])

    bars = np.array([
        # layer 0
        # [0, 4],
        # [4, 1],

        # [1, 5],
        # [5, 2],

        # [2, 6],
        # [6, 3],

        # [3, 7],
        # [7, 0],
        # diagonals
        # [4, 5],
        # [5, 6],
        # [6, 7],
        # [7, 4],
        # layer 0 - 1
        # vertical
        [0, 8],
        [1, 9],
        [2, 10],
        [3, 11],
        # diagonal
        [8, 4],
        [4, 9],

        [9, 5],
        [5, 10],

        [10, 6],
        [6, 11],

        [11, 7],
        [7, 8],
        # layer 1
        # none

        # layer 1 - 2
        # verticals
        [8, 12],
        [9, 13],
        [10, 14],
        [11, 15],

        # diagonals
        [8, 16],
        [9, 16],

        [9, 17],
        [10, 17],

        [10, 18],
        [11, 18],

        [11, 19],
        [8, 19],
        # layer 2
        #   13----16----12
        #   |           |
        #   |           |
        #   17          19
        #   |           |
        #   |           |
        #   14----18----15
        [12, 16],
        [16, 13],

        [13, 17],
        [17, 14],

        [14, 18],
        [18, 15],

        [15, 19],
        [19, 12],
        # diagonals
        [16, 17],
        [17, 18],
        [18, 19],
        [19, 16],
    ], dtype=np.uint64)

    nodes = apply_shrinkink(
        nodes=nodes,
        hight_of_section=hight,
        top_width=top_width,
        base_width=base_width)

    return {
        'nodes': nodes,
        'bars': bars,
    }


def generate_camera_tower(
    hight=161,
    top_width=4.2,
    base_width=19.6,
    bar_radius=None
):
    """
    Returns a dict describing the nodes and bars of one entire camera support
    tower according to Figure 111.

    relative hight
    |
    1.0  --------------- top
    |    type B without thinning (diamind like)
    0.85
    |    type B with thinning (diamind like)
    0.7
    |
    |    type A with thinning (triangle like)
    |
    |
    |
    0.0  --------------- ground

    Thinning=0.0464 taken from Spyridon and Gerogios report, meassured in
    Figure 111.

    Parameter
    ---------
    hight           The overall desired hight of the tower. The resulting tower
                    will be at least this high, but can be higher to fit all
                    sections as a whole.

    top_width       The width of the tower at its top.

    base_width      The width of the tower at its base.


    Default
    -------
    The default dimensions are for the 70m class ACP.
    """

    if bar_radius is None:
        bar_radius = top_width/33  # no reason here, just looks good.

    nodes = np.zeros(shape=(0, 3))
    bars = np.zeros(shape=(0, 2), dtype=np.uint64)

    section_base_width = base_width
    section_base_hight = 0
    thinning = 0.5*(base_width - top_width)/(0.85*hight)

    use_thinning = True
    while section_base_hight < hight:

        if section_base_hight < 0.7*hight:
            section = generate_tower_section_type_A(
                hight=section_base_width,
                base_width=section_base_width,
                top_width=section_base_width*(1-thinning)**2)
        elif section_base_hight < 0.85*hight:
            section = generate_tower_section_type_B(
                hight=section_base_width,
                base_width=section_base_width,
                top_width=section_base_width*(1-thinning)**2)
        else:
            section = generate_tower_section_type_B(
                hight=section_base_width,
                base_width=section_base_width,
                top_width=section_base_width)
            use_thinning = False

        for j in range(section['nodes'].shape[0]):
            section['nodes'][j, 2] += section_base_hight

        for k in range(section['bars'].shape[0]):
            section['bars'][k] += nodes.shape[0]

        nodes = np.concatenate((nodes, section['nodes']), axis=0)
        bars = np.concatenate((bars, section['bars']), axis=0)

        section_base_hight += section_base_width

        if use_thinning:
            section_base_width *= (1-thinning)**2

    return {
        'nodes': nodes,
        'bars': bars,
        'bar_radius': bar_radius
    }


def generate_camera_cables(reflector):
    f = reflector['geometry'].focal_length
    D = reflector['geometry'].max_outer_radius*2
    Az = 0.0
