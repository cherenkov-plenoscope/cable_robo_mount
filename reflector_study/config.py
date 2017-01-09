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
            'path': 'C:\Program Files\Computers and Structures\SAP2000 19\sap2000.exe',
            'working_directory': 'C:\\Users\\Spiros Daglas\\Desktop\\SAP2000_working_directory\\example_1'
            }
        },
    'structure_spatial_position': {
        'translational_vector_xyz': [0.0, 0.0, 0.0], #not used anymore. created from the tait bryan angle Ry
        'rotational_vector_Rx_Ry_Rz': [0.0, 10.0, 0.0]
        },
    'reflector': {
        'main': {
            'max_outer_radius': 15,
            'min_inner_radius': 1.0,
            'number_of_layers': 3,
            'x_over_z_ratio': 1.2,
            'security_distance_from_ground': 2.6
            },
        'optics': {
            'focal_length': 45,
            'davies_cotton_over_parabola_ratio': 0.0
            },
        'facet': {
            'gap_in_between': 0.02,
            'inner_hex_radius': 0.6,
            'surface_weight': 25.0,
            'actuator_weight': 5.0
            },
        'material': {
            'specific_weight': 78.5,
            'e_modul': 210e6,
            'yielding_point': 460000.0,
            'ultimate_point': 360000.0,
            'security_factor': 1.05
            },
        'bars': {
            'outer_diameter': 0.051,
            'thickness': 0.01,
            'imperfection_factor': 0.49,
            'buckling_length_factor': 0.9
            }
        },
    'tension_ring':{
        'width': 1.8,
        'support_position': 10,
        'material': {
            'specific_weight': 78.5,
            'e_modul': 210e6,
            'yielding_point': 460000.0,
            'ultimate_point': 360000.0,
            'security_factor': 1.05
            },
        'bars': {
            'outer_diameter': 0.127,
            'thickness': 0.016,
            'imperfection_factor': 0.49,
            'buckling_length_factor': 0.9
            }
        },
    'cables':{
        'material': {
            'e_modul': 73.9e6, #according to Bridon Endurance Dyform 34LR PI
            'specific_weight': 86.2, #according to Bridon Endurance Dyform 34LR PI
            'yielding_point': 1671000.0,
            'ultimate_point': 1671000.0,
            'security_factor': 1.05
            },
        'cross_section_area': 0.0000581
    },
    'load_scenario': {
        'security_factor': {
            'dead': 1.00,
            'live': 1.00,
            'wind': 1.00
            },
        'wind': {
            'direction': 0.0, #OK
            'speed': 55, #m/s.OK
            'terrain_factor': 1, ##Terrain 1.OK
            'orography_factor': 1, ##No increase of the wind due to mountains etc.OK
            'K1': 1, ##Turbulence factor. No accurate information available.OK
            'CsCd': 1.2, ## usually 1. But our structure very prone to dynamic efects, so Cd very conservative 1.2.OK
            'wind_density': 1.25, #wind density.OK
            'cpei': 1.5 #according to EC1-4 Z.7.3(freistehende Dächer) und Z. 7.2 Tab.7.4a (big?, although a preciser definition is impossible), OK
            },
        'seismic': {
            'acceleration': 3.6
            }
        },
    'star_light_analysis': {
        'photons_per_square_meter': 1000,
        'sensor': {
            'bin_width_deg': 0.0005,
            'region_of_interest_deg': 0.5
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
