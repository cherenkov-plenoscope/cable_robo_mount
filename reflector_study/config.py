import json
#everything in kN, m
example = {
    'system': {
        'mctracer': {
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
    'structure_spatial_position': {
        'translational_vector_xyz': [0.0 ,0.0, 0.0],
        'rotational_vector_Rx_Ry_Rz': [0.0, 45.0, 0.0]
        },
    'reflector': {
        'main': {
            'max_outer_radius': 10.0,
            'min_inner_radius': 2.0,
            'number_of_layers': 5,
            'x_over_z_ratio': 1.2
            },
        'optics': {
            'focal_length': 75.0,
            'davies_cotton_over_parabola_ratio': 0.0
            },
        'facet': {
            'gap_in_between': 0.02,
            'inner_hex_radius': 0.6,
            'surface_weight': 25.0,
            'actuator_weight': 5.0
            },
        'material': {
            'e_modul': 210e6,
            'yielding_point': 460000.0,
            'ultimate_point': 360000.0,
            'security_factor': 1.05
            },
        'bars': {
            'outer_diameter': 0.0424,
            'thickness': 0.0026,
            'imperfection_factor': 0.49,
            'buckling_length_factor': 0.9
            }
        },
    'tension_ring':{
        'width': 4,
        'support_position': 15,
        },
    'load_scenario': {
        'security_factor': {
            'dead': 1.35,
            'live': 1.35,
            'wind': 1.5
            },
        'wind': {
            'direction': 0.0,
            'speed': 55, #m/s
            'terrain_factor': 1, ##
            'orography_factor': 1, ##
            'K1': 1, ##
            'CsCd': 2, ## usually 1. But our structure very prone to dynamic efects.
            'wind_density': 1.25, #wind density
            'security_distance_from_ground': 5
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
