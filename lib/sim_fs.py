import psutil
import time

class SimFS:

    @staticmethod
    def is_fs_running(timeout=3000):
        start_time = time.monotonic()
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in (
                        'FlightSimulator.exe',
                        'FlightSimulator2024.exe'
                ):
                    return True
                if (time.monotonic() - start_time) * 1000 >= timeout:
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
