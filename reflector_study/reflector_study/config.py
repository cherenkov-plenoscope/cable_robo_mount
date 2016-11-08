import json

def write(config, path):
    with open(path, 'w') as outfile:
        json.dump(config, outfile, indent=4)

def read(path):
    config = {} 
    with open(path, 'r') as input_file:
        config = json.load(input_file)
    return config
