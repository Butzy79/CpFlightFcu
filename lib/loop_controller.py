import threading
import time

class LoopController:
    def __init__(self, get_interval_callback):
        """
        get_interval_callback: function returning the loop interval (float).
        """
        self.get_interval = get_interval_callback
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            interval = self.get_interval()
            print("[Loop Tick] Do something with aircraft data here...")
            time.sleep(interval)
