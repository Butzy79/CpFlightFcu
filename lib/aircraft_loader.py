import json
import re
import time


class AircraftLoader:
    speed = {"op": False, "value": 100, "init": False, "dash": False, "dot": False, "mach": False}
    heading = {"op": False, "value": 100, "init": False, "dash": False, "dot": False, "trk": False}
    qnh_cp = {"op": False, "value": 1015, "init": False}
    qnh_fo = {"op": False, "value": 1015, "init": False}
    altitude = {"op": False, "value": 1000, "init": False, "dot": False}
    vs = {"op": False, "value": 0, "init": False, "dash": False}
    btn_gen = {"op": False}

    @staticmethod
    def load_json_config(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    def set_dot_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_var_dot = aircraft_array.get("speed").get('extra_dot')
        heading_var_dot = aircraft_array.get("heading").get('extra_dot')
        altitude_var_dot = aircraft_array.get("altitude").get('extra_dot')

        speed_dot_value = bool(vr.get(f"({speed_var_dot})"))
        heading_dot_value = bool(vr.get(f"({heading_var_dot})"))
        altitude_dot_value = bool(vr.get(f"({altitude_var_dot})"))

        if speed_dot_value != self.speed["dot"]:
            self.speed["dot"] = speed_dot_value
            sock.sendall((cpflight_cmds.get("speed").get("dot_on") + "\n" if speed_dot_value else
                          cpflight_cmds.get("speed").get("dot_off") + "\n").encode())

        if heading_dot_value != self.heading["dot"]:
            self.heading["dot"] = heading_dot_value
            sock.sendall((cpflight_cmds.get("heading").get("dot_on") + "\n" if heading_dot_value else
                          cpflight_cmds.get("heading").get("dot_off") + "\n").encode())

        if altitude_dot_value != self.altitude["dot"]:
            self.altitude["dot"] = altitude_dot_value
            sock.sendall((cpflight_cmds.get("altitude").get("dot_on") + "\n" if altitude_dot_value else
                          cpflight_cmds.get("altitude").get("dot_off") + "\n").encode())
        return True

    def set_dash_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_var_dash = aircraft_array.get("speed").get('extra_dash')
        heading_var_dash = aircraft_array.get("heading").get('extra_dash')
        vs_var_dash = aircraft_array.get("vs").get('extra_dash')

        speed_dash_value = bool(vr.get(f"({speed_var_dash})"))
        heading_dash_value = bool(vr.get(f"({heading_var_dash})"))
        vs_dash_value = bool(vr.get(f"({vs_var_dash})"))

        self.speed["dash"] = speed_dash_value
        sock.sendall((cpflight_cmds.get("speed").get("dash_on") + "\n" if speed_dash_value else
                      cpflight_cmds.get("speed").get("dash_off") + "\n").encode())

        self.heading["dash"] = heading_dash_value
        sock.sendall((cpflight_cmds.get("heading").get("dash_on") + "\n" if heading_dash_value else
                      cpflight_cmds.get("heading").get("dash_off") + "\n").encode())

        self.vs["dash"] = vs_dash_value
        sock.sendall((cpflight_cmds.get("vs").get("dash_on") + "\n" if vs_dash_value else
                      cpflight_cmds.get("vs").get("dash_off") + "\n").encode())
        return True

    def set_type_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_mach_var = aircraft_array.get("speed").get('extra_mach')
        heading_var_trk = aircraft_array.get("heading").get('extra_trk')

        speed_mach_value = bool(vr.get(f"({speed_mach_var})"))
        heading_trk_value = bool(vr.get(f"({heading_var_trk})"))

        self.speed["mach"] = speed_mach_value
        sock.sendall((cpflight_cmds.get("speed").get("mach_on") + "\n" if speed_mach_value else
                      cpflight_cmds.get("speed").get("mach_off") + "\n").encode())

        self.heading["trk"] = heading_trk_value
        sock.sendall((cpflight_cmds.get("heading").get("trk_on") + "\n" if heading_trk_value else
                      cpflight_cmds.get("heading").get("trk_off") + "\n").encode())
        return True

    def set_speed_fcu(self, speed_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.speed["op"]:
            return False
        speed_var = speed_array.get('rx') if self.speed["init"] else speed_array.get('in')
        speed_value = int(vr.get(f"({speed_var})"))
        self.speed["value"] = speed_value
        speed_value = f".{speed_value}" if speed_value< 100 else speed_value
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

    def set_altitude_fcu(self, altitude_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.altitude["op"]:
            return False
        altitude_var = altitude_array.get('rx') if self.altitude["init"] else altitude_array.get('in')
        altitude_value = int(vr.get(f"({altitude_var})"))
        self.altitude["value"] = altitude_value
        sock.sendall((cpflight_cmds.get("tx").format(value=f"{altitude_value:05d}") + "\n").encode())
        return True

    def set_vs_fcu(self, vs_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.vs["op"]:
            return False
        vs_var = vs_array.get('rx') if self.vs["init"] else vs_array.get('in')
        vs_value = int(vr.get(f"({vs_var})"))
        self.vs["value"] = vs_value
        sock.sendall((cpflight_cmds.get("tx").format(value=f"{vs_value:+05d}") + "\n").encode())
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
            if what.startswith('btn_'):
                self.btn_gen["value"] = value
            else:
                getattr(self, what)["op"] = value
            return True
        except Exception:
            return False

    ### Reading from FCU and set into the sim. Dynamic calls.
    def set_speed_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['speed']['tx']:
            speed_abs = vr.get(f"({config['speed']['tx_inc']})")
            speed = vr.get(f"({el})")
            new_speed = cl_val - speed
            vr.set(f"{cl_val} (>{el})")
            vr.set(f"{new_speed + speed_abs} (>{config['speed']['tx_inc']})")
        self.speed["value"] = cl_val
        self.speed["init"] = True
        self.speed["op"] = False

    def set_heading_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        sock.sendall((cpfligh.get("heading").get("tx").format(value=value) + "\n").encode())
        for x in range(2):
            for el in config['heading']['tx']:
                incr = cl_val - vr.get(f"({config['heading']['rx']})")
                current = vr.get(f"({el})")
                vr.set(f"{current+incr} +  (>{el})")
                time.sleep(0.4)
        self.heading["value"] = cl_val
        self.heading["init"] = True
        self.heading["op"] = False

    def set_altitude_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['altitude']['tx']:
            altitude_abs = vr.get(f"({config['altitude']['tx_inc']})")
            altitude = vr.get(f"({el})")
            is_1000 = vr.get(f"({config['altitude']['scale']})")
            new_altitude = (cl_val - altitude) / (1000 if is_1000 else 100)
            vr.set(f"{altitude_abs+new_altitude} (>{config['altitude']['tx_inc']})")
            vr.set(f"{cl_val} (>{el})")
        self.altitude["value"] = cl_val
        self.altitude["init"] = True
        self.altitude["op"] = False

    def set_vs_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(value)
        sock.sendall((cpfligh.get("vs").get("tx").format(value=value) + "\n").encode())
        for el in config['vs']['tx']:
            vs_abs = vr.get(f"({config['vs']['tx_inc']})")
            vs = vr.get(f"({el})")
            new_vs = (cl_val - vs) / 100
            vr.set(f"{vs_abs+new_vs} (>{config['vs']['tx_inc']})")
            vr.set(f"{cl_val} (>{el})")
        self.vs["value"] = cl_val
        self.vs["init"] = True
        self.vs["op"] = False

    def set_qnh_cp_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        self.qnh_cp['value'] += cl_val
        for el in config['qnh_cp']['tx']:
            vr.set(f"{self.qnh_cp['value']} (>{el})")
        self.qnh_cp["init"] = True
        self.qnh_cp["op"] = False

    def set_qnh_fo_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        self.qnh_fo['value'] += cl_val
        for el in config['qnh_fo']['tx']:
            vr.set(f"{self.qnh_fo['value']} (>{el})")
        self.qnh_fo["init"] = True
        self.qnh_fo["op"] = False

    def set_btn_mach_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_mach']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_loc_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_loc']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_hdgtrk_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_hdgtrk']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.vs["value"] = 0
        sock.sendall((cpfligh.get("vs").get("tx").format(value="+0000") + "\n").encode())
        self.btn_gen["op"] = False

    def set_btn_ap1_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_ap1']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_ap2_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_ap2']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_athr_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_athr']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_metric_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_metric']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_exped_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_exped']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_appr_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_appr']['tx']:
            current = int(vr.get(f"({el})"))
            if current % 2:
                vr.set(f"{current+2} ++ (>{el})")
            else:
                vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_int100_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_int100']['tx']:
            vr.set(f"0 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_int1000_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_int1000']['tx']:
            vr.set(f"1 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_push_speed_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_push_speed']['tx']:
            vr.set(f"({el}) -- (>{el})")
        self.btn_gen["op"] = False

    def set_btn_pull_speed_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_pull_speed']['tx']:
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_push_heading_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_push_heading']['tx']:
            vr.set(f"({el}) -- (>{el})")
        self.btn_gen["op"] = False

    def set_btn_pull_heading_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_pull_heading']['tx']:
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_push_altitude_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_push_altitude']['tx']:
            vr.set(f"({el}) -- (>{el})")
        self.btn_gen["op"] = False

    def set_btn_pull_altitude_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_pull_altitude']['tx']:
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_push_vs_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_push_vs']['tx']:
            vr.set(f"({el}) -- (>{el})")
        self.vs["value"] = 0
        sock.sendall((cpfligh.get("vs").get("tx").format(value="+0000") + "\n").encode())
        self.btn_gen["op"] = False

    def set_btn_pull_vs_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_pull_vs']['tx']:
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False