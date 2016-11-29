import json

example = {
    'optics': {
        'focal_length': 75.0,
        'davies_cotton_over_parabola_ratio': 0.0,
        'max_outer_radius': 10.0,
        'min_inner_radius': 2.0,
        'gap_between_facets': 0.02,
        'facet_inner_hex_radius': 0.6},
    'space_frame': {
        'material': {
            'yielding_point': 1337.0,
        },
        'bar':{
            'outer_radius': 0.05,
            'thickness': 0.001,
        },
        'mirror_facet_weight': {
            'surface_weight': 25.0,
            'actuator_weight': 5.0
        },
        'number_of_layers': 2,
        'x_over_z_ratio': 1.2
    }
}

def write(config, path):
    with open(path, 'w') as outfile:
        json.dump(config, outfile, indent=4)

def read(path):
    config = {}
    with open(path, 'r') as input_file:
        config = json.load(input_file)
    return config
