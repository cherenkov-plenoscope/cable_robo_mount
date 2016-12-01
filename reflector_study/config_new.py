import json

example = {
    'system': {
        'ssh_connection': {
            'hostname': '192.168.56.101',
            'username': 'spiros',
            'key_path': 'C:\\Users\\Spiros Daglas\\Desktop\\ssh\\spiros',
            'run_path_linux': '/home/spiros/Desktop/run',
            'ray_tracer_propagation_path_linux': '/home/spiros/Desktop/build/mctPropagate'
            },
        'sap2000': {
            'path': 'C:\Program Files\Computers and Structures\SAP2000 19\sap2000.exe'
            }
        },
    'reflector': {
        'position_from_zenith': 30,
        'main': {
            'max_outer_radius': 10.0,
            'min_inner_radius': 2.0,
            'number_of_layers': 2,
            'x_over_z_ratio': 1.2
            },
        'dish_optics': {
            'focal_length': 75.0,
            'davies_cotton_over_parabola_ratio': 0.0
            },
        'facets': {
            'gap_between_facets': 0.02,
            'facet_inner_hex_radius': 0.6,
            'surface_weight': 25.0,
            'actuator_weight': 5.0
            },
        'material': {
            'e-modul': 210000,
            'yielding_point': 235000.0,
            'ultimate_point': 360000.0,
            'security_factor': 1.05
            },
        'bars': {
            'outer_radius': 0.05,
            'thickness': 0.001,
            'imperfection_factor': 0.49,
            'buckling_length_factor': 0.9
            }
        },
    'load_scenario': {
        'wind': {
            'wind_speed': 0.0
                },
        'seismic': {
            'acceleration': 3.6
            }
        },
    'star_light_analysis': {
        'photons_per_square_meter': 1000,
        'sensor': {
            'bin_width_deg': 0.001,
            'region_of_interest_deg': 1
            },
        'ground': {
            'bin_width_m': 0.1
            }
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
