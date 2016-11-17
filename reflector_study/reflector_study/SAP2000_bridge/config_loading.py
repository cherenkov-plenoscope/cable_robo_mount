import json

structural_dict = {
        'material': {
            'yielding_point': 235000.0, #in kPa
            "ultimate_point": 360000.0}, #in kPa
        "bar_properties": {
            'outter_radius': 0.05,
            'thickness': 0.001},
        'mirror_facet_weight': {
            'surface_weight': 25.0,
            'actuator_weight': 5.0,
            "wind_speed": 0.0,
            "seismic_acceleration": 3.6},
        }


def write(config, path):
    with open(path, 'w') as outfile:
        json.dump(config, outfile, indent=4)

def read(path):
    config = {}
    with open(path, 'r') as input_file:
        config = json.load(input_file)
    return config
