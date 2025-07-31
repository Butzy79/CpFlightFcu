import json
import os


class AircraftLoader:
    speed = {"op": False, "value": 100}

    @staticmethod
    def load_json_config(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def set_speed(self, speed_value: int) -> bool:
        if self.speed["op"]:
            return False
        self.speed["value"] = speed_value
        return True
