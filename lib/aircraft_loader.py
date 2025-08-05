import json
import re
import time


class AircraftLoader:
    speed = {"op": False, "value": 100, "init": False, "dash": False, "dot": False, "mach": False}
    heading = {"op": False, "value": 100, "init": False, "dash": False, "dot": False, "trk": False}
    qnh_cp = {"op": False, "value": 1013.0, "init": False}
    qnh_fo = {"op": False, "value": 1013.0, "init": False}
    altitude = {"op": False, "value": 1000, "init": False, "dot": False, "dash": False}
    vs = {"op": False, "value": 0, "init": False, "dash": False}
    btn_gen = {"op": False}
    led_gen = {"op": False}
    led_fcu = {"led_loc": False, "led_ap1": False, "led_ap2": False, "led_athr": False, "led_exped": False, "led_appr": False}
    led_cp_efis = {"led_cp_fd": False, "led_cp_ls": False, "led_cp_cstr": False, "led_cp_wpt": False, "led_cp_vord": False, "led_cp_ndb": False, "led_cp_arpt": False}

    def _reset_leds_command(self, led_control:str, new_value:bool, cpfligh)-> str:
        self.led_cp_efis = {
            k: (k == led_control and new_value) if not k.endswith(("_fd", "_ls")) else self.led_cp_efis[k]
            for k in self.led_cp_efis
        }
        return " ".join(cpfligh[k]["led_on" if v else "led_off"] for k, v in self.led_cp_efis.items()) + "\n"

    @staticmethod
    def load_json_config(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def esthim_qnh(alt_indicata_ft, alt_vera_ft):
        alt_indicata_m = alt_indicata_ft * 0.3048
        alt_vera_m = alt_vera_ft * 0.3048
        delta_h = alt_vera_m - alt_indicata_m
        qnh = 1013.25 * (1 - (delta_h / 44330)) ** 5.255
        return round(qnh, 2)

    def set_initial_values(self, aircraft_array: int, cpflight_cmds:dict, sock, vr):
        self.led_fcu = {k: not bool(vr.get(f"({v.get('rx')})")) for k, v in aircraft_array.items() if
                        k in self.led_fcu and v.get("rx")}
        self.led_cp_efis = {k: not bool(vr.get(f"({v.get('rx')})")) for k, v in aircraft_array.items() if
                        k in self.led_cp_efis and v.get("rx")}

        dashes = ['speed', 'heading', 'altitude', 'vs']
        for dash in dashes:
            getattr(self, dash)["dash"] = not bool(vr.get(f"({aircraft_array.get(dash).get('extra_dash')})"))

        dots = ['speed', 'heading', 'altitude']
        for dot in dots:
            getattr(self, dot)["dot"] = not bool(vr.get(f"({aircraft_array.get(dash).get('extra_dot')})"))

        self.speed["nack"] = not bool(vr.get(f"({aircraft_array.get('speed').get('extra_mach')})"))
        self.heading["trk"] = not bool(vr.get(f"({aircraft_array.get('heading').get('extra_trk')})"))

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
        altitude_var_dash = aircraft_array.get("altitude").get('extra_dash')
        vs_var_dash = aircraft_array.get("vs").get('extra_dash')

        speed_dash_value = bool(vr.get(f"({speed_var_dash})"))
        heading_dash_value = bool(vr.get(f"({heading_var_dash})"))
        altitude_value = bool(vr.get(f"({altitude_var_dash})"))
        vs_dash_value = bool(vr.get(f"({vs_var_dash})"))

        if speed_dash_value != self.speed["dash"]:
            self.speed["dash"] = speed_dash_value
            sock.sendall((cpflight_cmds.get("speed").get("dash_on") + "\n" if speed_dash_value else
                          cpflight_cmds.get("speed").get("dash_off") + "\n").encode())

        if heading_dash_value != self.heading["dash"]:
            self.heading["dash"] = heading_dash_value
            sock.sendall((cpflight_cmds.get("heading").get("dash_on") + "\n" if heading_dash_value else
                          cpflight_cmds.get("heading").get("dash_off") + "\n").encode())

        if altitude_value != self.altitude["dash"]:
            self.altitude["dash"] = altitude_value
            sock.sendall((cpflight_cmds.get("altitude").get("dash_on") + "\n" if altitude_value else
                          cpflight_cmds.get("altitude").get("dash_off") + "\n").encode())

        if vs_dash_value != self.vs["dash"]:
            self.vs["dash"] = vs_dash_value
            sock.sendall((cpflight_cmds.get("vs").get("dash_on") + "\n" if vs_dash_value else
                          cpflight_cmds.get("vs").get("dash_off") + "\n").encode())
        return True

    def set_type_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        speed_mach_var = aircraft_array.get("speed").get('extra_mach')
        heading_var_trk = aircraft_array.get("heading").get('extra_trk')

        speed_mach_value = bool(vr.get(f"({speed_mach_var})"))
        heading_trk_value = bool(vr.get(f"({heading_var_trk})"))
        if speed_mach_value != self.speed["mach"]:
            self.speed["mach"] = speed_mach_value
            sock.sendall((cpflight_cmds.get("speed").get("mach_on") + "\n" if speed_mach_value else
                          cpflight_cmds.get("speed").get("mach_off") + "\n").encode())

        if heading_trk_value != self.heading["trk"]:
            self.heading["trk"] = heading_trk_value
            sock.sendall((cpflight_cmds.get("heading").get("trk_on") + "\n" if heading_trk_value else
                          cpflight_cmds.get("heading").get("trk_off") + "\n").encode())
        return True

    def set_led_fcu(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        for key in self.led_fcu.keys():
            rx_expr = aircraft_array.get(key, {}).get("rx")
            if rx_expr is None:
                continue
            value = bool(vr.get(f"({rx_expr})"))
            if self.led_fcu[key] != value:
                self.led_fcu[key] = value
                cmd = cpflight_cmds.get(key, {}).get("led_on" if value else "led_off")
                if cmd:
                    sock.sendall((cmd + "\n").encode())
        return True

    def set_led_efis_cp(self, aircraft_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        for key in self.led_cp_efis.keys():
            rx_expr = aircraft_array.get(key, {}).get("rx")
            if rx_expr is None:
                continue
            value = bool(vr.get(f"({rx_expr})"))
            if self.led_cp_efis[key] != value:
                self.led_cp_efis[key] = value
                cmd = cpflight_cmds.get(key, {}).get("led_on" if value else "led_off")
                if cmd:
                    sock.sendall((cmd + "\n").encode())
        return True

    #next functions need to respect interval timer
    def set_speed_fcu(self, speed_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.speed["op"]:
            return False
        speed_var = speed_array.get('rx') if self.speed["init"] else speed_array.get('in')
        speed_value = int(vr.get(f"({speed_var})"))
        if speed_value != self.speed["value"]:
            self.speed["value"] = speed_value
            speed_value = f".{speed_value}" if speed_value< 100 else speed_value
            sock.sendall((cpflight_cmds.get("tx").format(value=speed_value) + "\n").encode())
        return True

    def set_heading_fcu(self, heading_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.heading["op"]:
            return False
        heading_var = heading_array.get('rx') if self.heading["init"] else heading_array.get('in')
        heading_value = int(vr.get(f"({heading_var})"))
        if heading_value != self.heading["value"]:
            self.heading["value"] = heading_value
            sock.sendall((cpflight_cmds.get("tx").format(value=str(heading_value).zfill(3)) + "\n").encode())
        return True

    def set_altitude_fcu(self, altitude_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.altitude["op"]:
            return False
        altitude_var = altitude_array.get('rx') if self.altitude["init"] else altitude_array.get('in')
        altitude_value = int(vr.get(f"({altitude_var})"))
        if altitude_value != self.altitude["value"]:
            self.altitude["value"] = altitude_value
            sock.sendall((cpflight_cmds.get("tx").format(value=f"{altitude_value:05d}") + "\n").encode())
        return True

    def set_vs_fcu(self, vs_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.vs["op"]:
            return False
        vs_var = vs_array.get('rx') if self.vs["init"] else vs_array.get('in')
        vs_value = int(vr.get(f"({vs_var})"))
        if vs_value != self.vs["value"]:
            self.vs["value"] = vs_value
            sock.sendall((cpflight_cmds.get("tx").format(value=f"{vs_value:+05d}") + "\n").encode())
        return True

    def _get_value_qhn_to_unit(self, vr, mode_hpa_var, rx_hpa:str, rx_inhg:str,
                               limit_hpa:list, limit_inhg:list, increment=0, force_mode=False) -> tuple[bool, float, str]:
        if force_mode:
            qnh_cp_mode_hpa = bool(mode_hpa_var)
        else:
            qnh_cp_mode_hpa = bool(vr.get(f'({mode_hpa_var})'))
        if qnh_cp_mode_hpa:
            qnh_cp_value = float(vr.get(f'({rx_hpa})')) + increment
            if qnh_cp_value > limit_hpa[1]:
                qnh_cp_value = limit_hpa[1]
            if qnh_cp_value < limit_hpa[0]:
                qnh_cp_value = limit_hpa[0]
        else:
            qnh_cp_value = float(vr.get(f'({rx_inhg})')) + (increment/100)
            if qnh_cp_value > limit_inhg[1]:
                qnh_cp_value = limit_inhg[1]
            if qnh_cp_value < limit_inhg[0]:
                qnh_cp_value = limit_inhg[0]
        cmd_send = f"{int(qnh_cp_value):04d}" if qnh_cp_mode_hpa else f"{qnh_cp_value:05.2f}"
        return qnh_cp_mode_hpa, qnh_cp_value, cmd_send

    def set_qnh_cp_efis(self, qnh_cp_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.qnh_cp["op"]:
            return False
        qnh_cp_mode_hpa, qnh_cp_value, cmd_send = self._get_value_qhn_to_unit(
            vr,
            qnh_cp_array.get('mode_hpa'),
            qnh_cp_array.get('rx_hpa') if self.qnh_cp["init"] else qnh_cp_array.get('in_hpa'),
            qnh_cp_array.get('rx_inhg') if self.qnh_cp["init"] else qnh_cp_array.get('in_inhg'),
            limit_hpa=qnh_cp_array.get('hpa_range'),
            limit_inhg=qnh_cp_array.get('inhg_range'),
            increment=0
        )
        if qnh_cp_value != self.qnh_cp["value"]:
            self.qnh_cp["value"] = qnh_cp_value
            sock.sendall((cpflight_cmds.get("tx").format(value=cmd_send) + "\n").encode())
        return True
    
    def set_qnh_fo_efis(self, qnh_fo_array: int, cpflight_cmds:dict, sock, vr) -> bool:
        if self.qnh_fo["op"]:
            return False
        # qnh_fo_var = qnh_fo_array.get('rx') if self.qnh_cp["init"] else qnh_fo_array.get('in')
        # qnh_fo_value = int(vr.get(f"({qnh_fo_var})"))
        # if self.qnh_cp["value"] != qnh_fo_value:
        #     self.qnh_cp["value"] = qnh_fo_value
        #     sock.sendall((cpflight_cmds.get("tx").format(value=qnh_fo_value) + "\n").encode())
        return True  

    # Blocker

    def set_opblocker(self, what:str, value:bool) -> bool:
        try:
            if what.startswith('btn_'):
                self.btn_gen["op"] = value
            elif what.startswith('led_'):
                self.led_gen["op"] = value
            elif what.startswith('qnh_cp_'):
                self.qnh_cp["op"] = value
            elif what.startswith('qnh_fo_'):
                self.qnh_fo["op"] = value
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
        for _ in range(2):
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

    #EFIS CPT
    def set_qnh_cp_inc_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['qnh_cp']['tx']:
            current = vr.get(f"({el})")
            vr.set(f"{int(current + cl_val)} (>{el})")
        qnh_cp_mode_hpa, qnh_cp_value, cmd_send = self._get_value_qhn_to_unit(
            vr,
            config['qnh_cp']['mode_hpa'],
            config['qnh_cp']['rx_hpa'],
            config['qnh_cp']['rx_inhg'],
            config['qnh_cp']['hpa_range'],
            config['qnh_cp']['inhg_range'],
            increment=cl_val
        )
        sock.sendall((cpfligh["qnh_cp"]["tx"].format(value=cmd_send)+ "\n").encode())
        self.qnh_cp["value"] = qnh_cp_value
        self.qnh_cp["init"] = True
        self.qnh_cp["op"] = False

    def set_qnh_cp_dec_aircraft(self, value:str, config, vr, sock, cpfligh):
        cl_val = int(re.sub(r'\D', '', value))
        for el in config['qnh_cp']['tx']:
            current = vr.get(f"({el})")
            vr.set(f"{int(current - cl_val)} (>{el})")
        qnh_cp_mode_hpa, qnh_cp_value, cmd_send = self._get_value_qhn_to_unit(
            vr,
            config['qnh_cp']['mode_hpa'],
            config['qnh_cp']['rx_hpa'],
            config['qnh_cp']['rx_inhg'],
            config['qnh_cp']['hpa_range'],
            config['qnh_cp']['inhg_range'],
            increment=-cl_val
        )
        sock.sendall((cpfligh["qnh_cp"]["tx"].format(value=cmd_send)+ "\n").encode())
        self.qnh_cp["value"] = qnh_cp_value
        self.qnh_cp["init"] = True
        self.qnh_cp["op"] = False

    def set_btn_cp_qnh_push_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_qnh_push']['tx']:
            vr.set(f"({el}) -- (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_qnh_pull_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_qnh_pull']['tx']:
            vr.set(f"({el}) ++ (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_inHg_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_inHg']['tx']:
            vr.set(f"0 (>{el})")
        qnh_cp_mode_hpa, qnh_cp_value, cmd_send = self._get_value_qhn_to_unit(
            vr,
            False,
            config['qnh_cp']['rx_hpa'],
            config['qnh_cp']['rx_inhg'],
            config['qnh_cp']['hpa_range'],
            config['qnh_cp']['inhg_range'],
            increment=0,
            force_mode=True
        )
        sock.sendall((cpfligh["qnh_cp"]["tx"].format(value=cmd_send)+ "\n").encode())

        self.btn_gen["op"] = False

    def set_btn_cp_hPa_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_hPa']['tx']:
            vr.set(f"1 (>{el})")
        qnh_cp_mode_hpa, qnh_cp_value, cmd_send = self._get_value_qhn_to_unit(
            vr,
            True,
            config['qnh_cp']['rx_hpa'],
            config['qnh_cp']['rx_inhg'],
            config['qnh_cp']['hpa_range'],
            config['qnh_cp']['inhg_range'],
            increment=0,
            force_mode = True
        )
        sock.sendall((cpfligh["qnh_cp"]["tx"].format(value=cmd_send)+ "\n").encode())
        self.btn_gen["op"] = False

    def set_btn_cp_ils_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_ils']['tx']:
            vr.set(f"0 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_vor_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_vor']['tx']:
            vr.set(f"1 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_nav_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_nav']['tx']:
            vr.set(f"2 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_arc_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_arc']['tx']:
            vr.set(f"3 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_plan_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_plan']['tx']:
            vr.set(f"4 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_1_adf_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_1_adf']['tx']:
            vr.set(f"0 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_1_off_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_1_off']['tx']:
            vr.set(f"1 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_1_vor_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_1_vor']['tx']:
            vr.set(f"2 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_2_adf_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_2_adf']['tx']:
            vr.set(f"0 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_2_off_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_2_off']['tx']:
            vr.set(f"1 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_2_vor_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_2_vor']['tx']:
            vr.set(f"2 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_10_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_10']['tx']:
            vr.set(f"0 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_20_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_20']['tx']:
            vr.set(f"1 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_40_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_40']['tx']:
            vr.set(f"2 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_80_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_80']['tx']:
            vr.set(f"3 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_160_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_160']['tx']:
            vr.set(f"5 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_range_320_aircraft(self, value: str, config, vr, sock, cpfligh):
        for el in config['btn_cp_range_320']['tx']:
            vr.set(f"5 (>{el})")
        self.btn_gen["op"] = False

    def set_btn_cp_fd_aircraft(self, value: str, config, vr, sock, cpfligh):
        new_value = not self.led_cp_efis['led_cp_fd']
        for el in config['btn_cp_fd']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((cpfligh["led_cp_fd"]["led_on" if new_value else "led_off"] + "\n").encode())
        self.led_cp_efis["led_cp_fd"] = new_value
        self.btn_gen["op"] = False

    def set_btn_cp_ls_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_ls'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_ls']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((cpfligh[which_led]["led_on" if new_value else "led_off"] + "\n").encode())
        self.led_cp_efis[which_led] = new_value
        self.btn_gen["op"] = False

    def set_btn_cp_cstr_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_cstr'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_cstr']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((self._reset_leds_command(which_led, new_value, cpfligh)).encode())
        self.btn_gen["op"] = False

    def set_btn_cp_wpt_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_wpt'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_wpt']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((self._reset_leds_command(which_led, new_value, cpfligh)).encode())
        self.btn_gen["op"] = False

    def set_btn_cp_vord_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_vord'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_vord']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((self._reset_leds_command(which_led, new_value, cpfligh)).encode())
        self.btn_gen["op"] = False

    def set_btn_cp_ndb_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_ndb'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_ndb']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((self._reset_leds_command(which_led, new_value, cpfligh)).encode())
        self.btn_gen["op"] = False

    def set_btn_cp_arpt_aircraft(self, value: str, config, vr, sock, cpfligh):
        which_led = 'led_cp_arpt'
        new_value = not self.led_cp_efis[which_led]
        for el in config['btn_cp_arpt']['tx']:
            actual = vr.get(f"({el})")
            vr.set(f"{int(actual+2)} (>{el})")
        sock.sendall((self._reset_leds_command(which_led, new_value, cpfligh)).encode())
        self.btn_gen["op"] = False

    #EFIS FO
    def set_qnh_fo_aircraft(self, value:str, config, vr, sock, cpfligh):
        pass