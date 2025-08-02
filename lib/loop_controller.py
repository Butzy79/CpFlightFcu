import re
import threading
import time
import socket
import select
from typing import Optional

from lib.aircraft_loader import AircraftLoader
from modules.parser_simconnect import SimConnectParser
from modules.parser_variable_requests import ParserVariableRequests


class LoopController:
    def __init__(self, get_interval_callback, obj_aircraft: AircraftLoader):
        """
        get_interval_callback: function returning the loop interval (float).
        """
        self.get_interval = get_interval_callback
        self.running = False
        self.thread = None
        self.socket_thread = None

        self.aircraft = obj_aircraft
        self.current_config = None

        self.sm = None
        self.vr = None
        self.sock = None
        
        self.pause_loop_until = 0

    def find_matching_block(self, s):
        for key, value in self.cpflight.items():
            if isinstance(value, dict) and "rx" in value:
                pattern = value["rx"]
                if re.match(pattern, s):
                    return key
        return None

    def start(self, config, cpflight) -> tuple[bool, Optional[str]]:
        if self.running:
            return True, None

        self.current_config = config
        self.cpflight = cpflight
        try:
            self.sm = SimConnectParser()
            self.vr = ParserVariableRequests(self.sm)
            self.vr.clear_sim_variables()
        except Exception as e:
            return False, str(e)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.cpflight.get('IP'), self.cpflight.get('PORT')))
            self.sock.setblocking(False)
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.socket_thread = threading.Thread(target=self._socket_listener_loop, daemon=True)

            self.thread.start()
            self.socket_thread.start()
            return True, None
        except Exception as e:
            return False, f"CpFlight Connection error: {e}"

    def stop(self):
        self.running = False
        self.sm = None
        self.vr = None
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _run_loop(self):
        while self.running:
            try:
                # Dash and Dot Control need to be here
                self.aircraft.set_dash_fcu( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_dot_fcu( self.current_config, self.cpflight, self.sock, self.vr)
                self.aircraft.set_type_fcu( self.current_config, self.cpflight, self.sock, self.vr)

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
                self.aircraft.set_qnh_cp_fcu(
                    self.current_config.get('qnh_cp'),
                    self.cpflight.get('qnh_cp'),
                    self.sock,
                    self.vr
                )
                self.aircraft.set_qnh_fo_fcu(
                    self.current_config.get('qnh_fo'),
                    self.cpflight.get('qnh_fo'),
                    self.sock,
                    self.vr
                )
                time.sleep(interval)
            except Exception as e:
                time.sleep(1)

    def _socket_listener_loop(self):
        while self.running and self.sock:
            try:
                readable, _, _ = select.select([self.sock], [], [], 0.1)
                if self.sock in readable:
                    try:
                        data = self.sock.recv(1024)
                        if not data:
                            self.stop()
                            break
                        value_from_fcu = re.sub(r'[\x00-\x1F\x7F]', '', data.decode(errors="ignore")).strip()
                        what = self.find_matching_block(value_from_fcu)
                        if self.aircraft.set_opblocker(what, True):
                            pattern = self.cpflight.get(what).get('rx')
                            match = re.match(fr"{pattern}", value_from_fcu)
                            value = match.group(1) if match else None
                            if value:
                                method_name = f"set_{what}_aircraft"
                                getattr(self.aircraft, method_name)(value, self.current_config, self.vr)
                                self.pause_loop_until = time.time() + 2
                    except BlockingIOError:
                        pass
                    except Exception:
                        pass
            except Exception as e:
                pass