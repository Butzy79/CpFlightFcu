import threading
import time
import socket
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
        self.aircraft = obj_aircraft
        self.current_config = None

        self.sm = None
        self.vr = None

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
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.cpflight.get('IP'), self.cpflight.get('PORT')))
            sock.setblocking(False)
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            return True, None
        except Exception as e:
            return False, f"CpFlight Connection error: {e}"

    def stop(self):
        self.running = False
        self.sm = None
        self.vr = None

    def _run_loop(self):
        while self.running:
            interval = self.get_interval()
            #speed
            self.aircraft.set_speed(int(self.vr.get(self.current_config.get('speed').get("rx"))))
            time.sleep(interval)
