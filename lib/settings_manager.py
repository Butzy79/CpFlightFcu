import json
import os

DEFAULT_SETTINGS = {
    "window": {
        "x": 100,
        "y": 100,
        "width": 400,
        "height": 400
    }
}

SETTINGS_PATH = "settings.json"

class SettingsManager:
    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get_window_geometry(self, update_available:bool=False):
        w = self.settings["window"]["width"]
        h = self.settings["window"]["height"] if not update_available else self.settings["window"]["height"] + 25
        x = self.settings["window"]["x"]
        y = self.settings["window"]["y"]
        return f"{w}x{h}+{x}+{y}"

    def update_window_position(self, x, y):
        self.settings["window"]["x"] = x
        self.settings["window"]["y"] = y

    def update_window_size(self, width, height, update_available):
        self.settings["window"]["width"] = width
        self.settings["window"]["height"] = height if not update_available else height - 25
