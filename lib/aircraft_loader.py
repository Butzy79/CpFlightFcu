import json
import re

# ALT:V041130 = FL130
# DOT ALT: L0126 OFF: L1126


class AircraftLoader:
    speed = {"op": False, "value": 100, "init": False, "dash": False, "dot": False}
    heading = {"op": False, "value": 100, "init": False, "dash": False, "dot": False}
    qnh_cp = {"op": False, "value": 1015, "init": False}
    qnh_fo = {"op": False, "value": 1015, "init": False}
    @staticmethod
    def load_json_config(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def set_dot_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_var_dot = aircraft_array.get("speed").get('extra_dot')
        heading_var_dot = aircraft_array.get("heading").get('extra_dot')

        speed_dot_value = bool(vr.get(f"({speed_var_dot})"))
        heading_dot_value = bool(vr.get(f"({heading_var_dot})"))

        if speed_dot_value != self.speed["dot"]:
            self.speed["dash"] = speed_dot_value
            sock.sendall((cpflight_cmds.get("speed").get("dot_on") + "\n" if speed_dot_value else
                          cpflight_cmds.get("speed").get("dot_off") + "\n").encode())

        if heading_dot_value != self.heading["dash"]:
            self.heading["dash"] = heading_dot_value
            sock.sendall((cpflight_cmds.get("heading").get("dot_on") + "\n" if heading_dot_value else
                          cpflight_cmds.get("heading").get("dot_off") + "\n").encode())
        return True

    def set_dash_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_var_dash = aircraft_array.get("speed").get('extra_dash')
        heading_var_dash = aircraft_array.get("heading").get('extra_dash')

        speed_dash_value = bool(vr.get(f"({speed_var_dash})"))
        heading_dash_value = bool(vr.get(f"({heading_var_dash})"))

        if speed_dash_value != self.speed["dash"]:
            self.speed["dash"] = speed_dash_value
            sock.sendall((cpflight_cmds.get("speed").get("dash_on") + "\n" if speed_dash_value else
                          cpflight_cmds.get("speed").get("dash_off") + "\n").encode())

        if heading_dash_value != self.heading["dash"]:
            self.heading["dash"] = heading_dash_value
            sock.sendall((cpflight_cmds.get("heading").get("dash_on") + "\n" if heading_dash_value else
                          cpflight_cmds.get("heading").get("dash_off") + "\n").encode())
        return True

    def set_speed_fcu(self, speed_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.speed["op"]:
            return False
        speed_var = speed_array.get('rx') if self.speed["init"] else speed_array.get('in')
        speed_value = int(vr.get(f"({speed_var})"))
        self.speed["value"] = speed_value
        sock.sendall((cpflight_cmds.get("tx").format(value=speed_value) + "\n").encode())
        return True
    
    def set_heading_fcu(self, heading_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.heading["op"]:
            return False
        heading_var = heading_array.get('rx') if self.heading["init"] else heading_array.get('in')
        heading_value = int(vr.get(f"({heading_var})"))
        self.heading["value"] = heading_value
        sock.sendall((cpflight_cmds.get("tx").format(value=str(heading_value).zfill(3)) + "\n").encode())
        return True
    
    def set_qnh_cp_fcu(self, qnh_cp_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.qnh_cp["op"]:
            return False
        qnh_cp_var = qnh_cp_array.get('rx') if self.qnh_cp["init"] else qnh_cp_array.get('in')
        qnh_cp_value = int(vr.get(f"({qnh_cp_var})"))
        self.qnh_cp["value"] = qnh_cp_value
        sock.sendall((cpflight_cmds.get("tx").format(value=qnh_cp_value) + "\n").encode())
        return True
    
    def set_qnh_fo_fcu(self, qnh_fo_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.qnh_fo["op"]:
            return False
        qnh_fo_var = qnh_fo_array.get('rx') if self.qnh_cp["init"] else qnh_fo_array.get('in')
        qnh_fo_value = int(vr.get(f"({qnh_fo_var})"))
        self.qnh_cp["value"] = qnh_fo_value
        sock.sendall((cpflight_cmds.get("tx").format(value=qnh_fo_value) + "\n").encode())
        return True  

    # Blocker
    def set_opblocker(self, what:str, value:bool) -> bool:
        try:
            getattr(self, what)["op"] = value
            return True
        except Exception:
            return False

    ### Reading from FCU and set into the sim. Dynamic calls.
    def set_speed_aircraft(self, value:str, config, vr) -> bool:
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['speed']['tx']:
            vr.set(f"{cl_val} (>{el})")
        self.speed["value"] = cl_val
        self.speed["init"] = True
        self.speed["op"] = False

    def set_heading_aircraft(self, value:str, config, vr):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['heading']['tx']:
            incr = cl_val - self.heading["value"]
            vr.set(f"(L:E_FCU_HEADING) + {incr} +  (>L:E_FCU_HEADING)")
        self.heading["value"] = cl_val
        self.heading["init"] = True
        self.heading["op"] = False

    def set_qnh_cp_aircraft(self, value:str, config, vr):
        cl_val = int(re.sub(r'\D', '', value))
        self.qnh_cp['value'] += cl_val
        for el in config['qnh_cp']['tx']:
            vr.set(f"{self.qnh_cp['value']} (>{el})")
        self.qnh_cp["init"] = True
        self.qnh_cp["op"] = False

    def set_qnh_fo_aircraft(self, value:str, config, vr):
        cl_val = int(re.sub(r'\D', '', value))
        self.qnh_fo['value'] += cl_val
        for el in config['qnh_fo']['tx']:
            vr.set(f"{self.qnh_fo['value']} (>{el})")
        self.qnh_fo["init"] = True
        self.qnh_fo["op"] = False

