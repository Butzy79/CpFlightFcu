import json
from typing import re


class AircraftLoader:
    speed = {"op": False, "value": 100}
    heading = {"op": False, "value": 100}
    qnh_cp = {"op": False, "value": 1015}
    qnh_fo = {"op": False, "value": 1015}
    @staticmethod
    def load_json_config(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def set_speed_fcu(self, speed_value: int, cpflight_comd:str, sock) -> bool:
        if self.speed["op"]:
            return False
        self.speed["value"] = speed_value
        sock.sendall((cpflight_comd.format(value=speed_value) + "\n").encode())
        return True

    def set_opblocker(self, what:str, value:bool) -> bool:
        try:
            getattr(self, what)["op"] = value
            return True
        except Exception:
            return False

    def set_speed_aircraft(self, value:str, config, vr) -> bool:
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['speed']['tx']:
            vr.set(f"{cl_val} (>L:{el})")
        self.speed["value"] = cl_val
        self.speed["op"] = False

    def set_heading_aircraft(self, value:str, config, vr):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['heading']['tx']:
            vr.set(f"{cl_val} (>L:{el})")
        self.heading["value"] = cl_val
        self.heading["op"] = False

