import re
import threading
import time
import socket
import select
import serial

from typing import Optional

from lib.aircraft_loader import AircraftLoader
from lib.sim_fs import SimFS
from modules.parser_simconnect import SimConnectParser
from modules.parser_variable_requests import ParserVariableRequests


class LoopController:
    def __init__(self, get_interval_callback, obj_aircraft: AircraftLoader):
        """
        get_interval_callback: function returning the loop interval (float).
        """
        self.fw_compatible = None # None = Not verified, 1 = Compatible, 0 = Not Compatible
        self.get_interval = get_interval_callback
        self.running = False
        self.sim_running = False
        self.autostart = False
        self.thread = None
        self.socket_thread = None
        self.ready_to_stop = False

        self.aircraft = obj_aircraft
        self.current_config = None
        self.cpflight = None

        self.sm = None
        self.vr = None
        self.sock = None

        self.sim_status = False
        self.fcu_status = False
        self.is_lan_fcu = True

        self.pause_loop_until = 0
        self.pause_loop_check_until = 0

    def find_matching_block(self, s):
        for key, value in self.cpflight.items():
            if isinstance(value, dict) and "rx" in value:
                pattern = value["rx"]
                if re.match(pattern, s):
                    return key
        return None

    def is_sim_running(self) -> bool:
        return self.sim_running

    def is_sim_ready_to_stop(self):
        return self.ready_to_stop

    def check_status(self, autostart, config, cpflight, is_critical_on, is_lan_fcu) -> bool:
        if is_critical_on:
            return False
        self.is_lan_fcu = is_lan_fcu
        self.autostart = autostart
        if not autostart or not SimFS.is_fs_running():
            return False
        if self.sim_running:
            return True
        now = time.time()
        if now < self.pause_loop_check_until:
            return False
        self.pause_loop_check_until = now + 2
        self.sm = SimConnectParser()
        self.vr = ParserVariableRequests(self.sm)
        self.vr.clear_sim_variables()
        if not self.vr:
            return False
        sim_load = bool(self.vr.get(f"({config.get('fcu',{}).get('power_on')})"))
        if sim_load:
            self.sim_running = True
            self.pause_loop_check_until = time.time() + 2
            self.start(config, cpflight, self.is_lan_fcu)
            return True
        return False

    def start(self, config, cpflight, is_lan_fcu) -> tuple[bool, Optional[str]]:
        if self.running:
            return True, None

        self.current_config = config
        self.cpflight = cpflight
        self.is_lan_fcu = is_lan_fcu
        try:
            self.sm = SimConnectParser()
            self.vr = ParserVariableRequests(self.sm)
            self.vr.clear_sim_variables()
        except Exception as e:
            return False, str(e)

        try:
            if not self.is_lan_fcu:
                self.sock = SerialSocketWrapper(self.cpflight.get("USB_PORT"), self.cpflight.get("USB_BAUD"))
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.cpflight.get('IP'), self.cpflight.get('PORT')))
                self.sock.setblocking(False)

            # turn led on:
            self.sock.sendall((self.cpflight.get("POWER_ON") + "\n").encode())
            # self.sock.sendall((self.cpflight.get("LED_ALL_ON") + "\n").encode())

            self.running = True
            self.sim_running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.socket_thread = threading.Thread(target=self._socket_listener_loop, daemon=True)

            self.thread.start()
            self.socket_thread.start()
            return True, None
        except Exception as e:
            connection_type = "LAN" if self.is_lan_fcu else "USB"
            return False, f"CpFlight Connection error ({connection_type}): {e}"

    def stop(self):
        self.running = False
        self.sim_running = False
        self.sm = None
        self.ready_to_stop = False
        self.vr = None
        self.sim_status = False
        self.fcu_status = False
        if self.sock:
            try:
                # turn power off:
                self.sock.sendall((self.cpflight.get("POWER_OFF") + "\n").encode())
                time.sleep(3)
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                print(f"CpFlight Connection error: {e}")
                pass
            self.sock = None

    def _run_loop(self):
        self.aircraft.set_initial_values(self.current_config, self.cpflight, self.sock, self.vr)
        while self.running:
            try:
                if not self.sim_running:
                    self.stop()
                # Dash and Dot Control need to be here
                self.aircraft.set_dash_fcu( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_dot_fcu( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_type_fcu( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_led_fcu( self.current_config, self.cpflight, self.sock, self.vr)

                now = time.time()
                if now < self.pause_loop_until:
                    time.sleep(0.1)
                    continue
                interval = self.get_interval()
                # Read from SimConnect and send to hardware

                self.aircraft.set_speed_fcu(
                    self.current_config.get('speed'),
                    self.cpflight.get('speed'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_heading_fcu(
                    self.current_config.get('heading'),
                    self.cpflight.get('heading'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_altitude_fcu(
                    self.current_config.get('altitude'),
                    self.cpflight.get('altitude'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_vs_fcu(
                    self.current_config.get('vs'),
                    self.cpflight.get('vs'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_qnh_cp_efis(
                    self.current_config.get('qnh_cp'),
                    self.cpflight.get('qnh_cp'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_qnh_fo_efis(
                    self.current_config.get('qnh_fo'),
                    self.cpflight.get('qnh_fo'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_led_efis_cp( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_led_efis_fo( self.current_config, self.cpflight, self.sock, self.vr)

                self.aircraft.set_fcu_brightness(
                    self.current_config.get('fcu'),
                    self.cpflight.get('fcu'),
                    self.sock,
                    self.vr
                )

                if self.autostart:
                    if not bool(self.vr.get(f"({self.current_config.get('fcu', {}).get('power_off')})")):
                        self.ready_to_stop = True

                self.sim_status = True
                time.sleep(interval)
            except Exception as e:
                print(e)
                time.sleep(1)

    def _socket_listener_loop(self):
        while self.running and self.sock:
            try:
                data = None
                if self.is_lan_fcu:
                    readable, _, _ = select.select([self.sock], [], [], 0.1)
                    if self.sock in readable:
                        data = self.sock.recv(1024)
                        if not data:
                            self.stop()
                            break
                else:
                    # Solo per USB: niente select, polling diretto
                    data = self.sock.recv(1024)

                if data:
                    self.fcu_status = True
                    value_from_fcu = re.sub(r'[\x00-\x1F\x7F]', '', data.decode(errors="ignore")).strip()

                    if self.fw_compatible is None:
                        if self.cpflight.get('FW_COMPATIBLE') and self.cpflight.get('fcu', {}).get(
                                'fw_value_rx') and value_from_fcu.startswith(
                                self.cpflight.get('fcu', {}).get('fw_value_rx')):
                            fw_version = value_from_fcu.split(self.cpflight.get('fcu', {}).get('fw_value_rx'))[1]
                            if fw_version and fw_version == self.cpflight.get('FW_COMPATIBLE', ""):
                                self.fw_compatible = True
                            elif fw_version and fw_version != self.cpflight.get('FW_COMPATIBLE', ""):
                                self.fw_compatible = False

                    what = self.find_matching_block(value_from_fcu)
                    if self.aircraft.set_opblocker(what, True):
                        pattern = self.cpflight.get(what).get('rx')
                        match = re.match(fr"{pattern}", value_from_fcu)
                        value = match.group(1) if match else None
                        if value:
                            method_name = f"set_{what}_aircraft"
                            getattr(self.aircraft, method_name)(value, self.current_config, self.vr, self.sock,
                                                                self.cpflight)
                            self.pause_loop_until = time.time() + 2

                time.sleep(0.05)

            except BlockingIOError:
                pass
            except Exception as e:
                print("Listener loop error:", e)

class SerialSocketWrapper:
    def __init__(self, port, baud=38400, timeout=0.5):
        self.ser = serial.Serial(port, baud, timeout=timeout)

    def sendall(self, data: bytes):
        if isinstance(data, str):
            data = data.encode()
        self.ser.write(data)

    def recv(self, bufsize: int = 1024) -> bytes:
        time.sleep(0.05)
        if self.ser.in_waiting:
            return self.ser.read(self.ser.in_waiting)
        return b""

    def shutdown(self, how):
        pass

    def connect(self):
        pass

    def setblocking(self):
        pass

    def close(self):
        self.ser.close()