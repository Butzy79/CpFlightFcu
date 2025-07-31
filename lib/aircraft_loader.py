import json

def load_aircraft_config(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
